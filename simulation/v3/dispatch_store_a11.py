"""Indexed A11 operational journal. SQLite is in the frozen Python runtime.

FULL-synchronous WAL commits append both a chained delta and its materialized
indexes atomically. Checkpoints compact WAL pages, never the logical audit.
Scientific outputs and their completion records remain the runner's files.
"""
from collections.abc import Mapping, MutableMapping
from contextvars import ContextVar
from collections import OrderedDict
import json
import os
from pathlib import Path
import sqlite3
import threading
from .artifacts import canonical, digest, read, scoped, seal, unseal

VERSION = 1
OPEN_STORES = ContextVar('a11_transaction_stores', default=None)
_CONNECTIONS = OrderedDict()
_POOL_LOCK = threading.Lock()
_IN_USE = {}


def connection(root):
    # SSH's stdio command retains a connection, not transaction state. This
    # avoids reconstructing SQLite's WAL index on every short job request.
    key = (os.getpid(), str(root))
    with _POOL_LOCK:
        db = _CONNECTIONS.pop(key, None)
        if db is None:
            db = sqlite3.connect(root/'dispatch.sqlite', timeout=30, check_same_thread=False)
            db.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('PRAGMA wal_autocheckpoint=0')
        _CONNECTIONS[key] = db
        _IN_USE[id(db)] = _IN_USE.get(id(db), 0) + 1
        if len(_CONNECTIONS) > 16:
            for old_key, old in list(_CONNECTIONS.items()):
                if old_key != key and not old.in_transaction and not _IN_USE.get(id(old),0):
                    old.close(); del _CONNECTIONS[old_key]
                    break
        return db


def warm_connection(root):
    """Open the verified index's WAL before waiting for the RPC root lock."""
    root = scoped(root)
    if (root/'dispatch.sqlite').exists():
        db = connection(root)
        with _POOL_LOCK:
            _IN_USE[id(db)] -= 1


def stamp(path):
    s = Path(path).stat()
    return [s.st_size, s.st_mtime_ns, s.st_ctime_ns]


class Jobs(Mapping):
    def __init__(self, store):
        self.store = store

    def __getitem__(self, key):
        row = self.store.db.execute('SELECT data FROM jobs WHERE id=?', (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return unseal(json.loads(row[0]))

    def __iter__(self):
        return (r[0] for r in self.store.db.execute('SELECT id FROM jobs ORDER BY ordinal'))

    def __len__(self):
        return self.store.header['job_count']

    def phase(self, phase):
        return [unseal(json.loads(r[0])) for r in self.store.db.execute('SELECT data FROM jobs WHERE phase=? ORDER BY ordinal', (phase,))]


class Rows(MutableMapping):
    """Load individual rows; dirty detection visits only rows touched this RPC."""
    def __init__(self, store, name):
        self.store, self.name = store, name
        self.cache, self.original, self.removed = {}, {}, set()

    def __getitem__(self, key):
        if key in self.removed:
            raise KeyError(key)
        if key not in self.cache:
            row = self.store.db.execute('SELECT data FROM ' + self.name + ' WHERE id=?', (key,)).fetchone()
            if row is None:
                raise KeyError(key)
            value = unseal(json.loads(row[0]))
            self.cache[key], self.original[key] = value, canonical(value)
        return self.cache[key]

    def __setitem__(self, key, value):
        if key not in self.original:
            try:
                self[key]
            except KeyError:
                self.original[key] = None
        self.removed.discard(key)
        self.cache[key] = value

    def __delitem__(self, key):
        self[key]
        self.removed.add(key)
        self.cache.pop(key, None)

    def __iter__(self):
        self.flush()
        return (r[0] for r in self.store.db.execute('SELECT id FROM ' + self.name))

    def __len__(self):
        self.flush()
        return self.store.db.execute('SELECT n FROM counts WHERE name=?', (self.name,)).fetchone()[0]

    def clear(self):
        for key in list(self):
            del self[key]

    def flush(self):
        for key in list(self.removed):
            self.store.remove(self.name, key)
            self.original.pop(key, None)
        self.removed.clear()
        for key, value in self.cache.items():
            raw = canonical(value)
            if self.original.get(key) != raw:
                self.store.put(self.name, key, value)
                self.original[key] = raw


class Store:
    def __init__(self, root, validate):
        self.root = scoped(root)
        self.db = connection(self.root)
        self.events = []
        self.closed = False
        opened = OPEN_STORES.get()
        if opened is not None:
            opened.append(self)
        try:
            exists = self.db.execute("SELECT 1 FROM sqlite_master WHERE name='meta'").fetchone()
            if not exists:
                self.initialize(validate)
            self.db.execute('BEGIN IMMEDIATE')
            self.header = self.get('header')
            if self.header['version'] != VERSION:
                raise ValueError('unsupported dispatcher index version')
            identity = read(self.root / 'identity.json')
            if identity != self.header['identity']:
                raise RuntimeError('incompatible resumption; root identity stays strict')
            if stamp(self.root / 'manifest.json') != self.header['manifest_stamp']:
                document = read(self.root / 'manifest.json')
                spec = unseal(document)
                if digest(spec) != identity['spec_hash']:
                    raise RuntimeError('incompatible resumption; manifest changed')
                validate(spec)
                self.header['manifest_stamp'] = stamp(self.root / 'manifest.json')
                self.set('header', self.header)
            self.spec = self.get('spec')
            self.state = self.get('state')
            self.leases = Rows(self, 'leases')
            self.done = Rows(self, 'completions')
            self.state.update(leases=self.leases, completions=self.done)
            self.jobs = Jobs(self)
            self.before = canonical(self.small_state())
        except BaseException:
            self.db.rollback()
            raise

    def get(self, key):
        return unseal(json.loads(self.db.execute('SELECT data FROM meta WHERE id=?', (key,)).fetchone()[0]))

    def set(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, canonical(seal(value))))

    def initialize(self, validate):
        initial = unseal(read(self.root/'pull_state.json'))
        if initial.get('checkpoint_only'):
            raise RuntimeError('operational journal is missing; refuse reconstruction from a status snapshot')
        spec = unseal(read(self.root / 'manifest.json'))
        validate(spec)
        identity = read(self.root / 'identity.json')
        if digest(spec) != identity['spec_hash']:
            raise RuntimeError('incompatible resumption; manifest changed')
        self.db.executescript('''
            BEGIN IMMEDIATE;
            CREATE TABLE meta(id TEXT PRIMARY KEY,data BLOB NOT NULL);
            CREATE TABLE jobs(id TEXT PRIMARY KEY,ordinal INTEGER,phase TEXT,kind TEXT,cls TEXT,data BLOB NOT NULL);
            CREATE INDEX jobs_phase ON jobs(phase,ordinal);
            CREATE TABLE queues(phase TEXT,kind TEXT,cls TEXT,cost REAL,memory REAL,n INTEGER,PRIMARY KEY(phase,kind,cls));
            CREATE INDEX queue_priority ON queues(phase,cost DESC,cls);
            CREATE INDEX queue_ready ON queues(phase,cost DESC,cls) WHERE n>0;
            CREATE TABLE pending(id TEXT PRIMARY KEY,phase TEXT,kind TEXT,cls TEXT);
            CREATE INDEX pending_order ON pending(phase,kind,cls,id);
            CREATE TABLE leases(id TEXT PRIMARY KEY,job TEXT,phase TEXT,session TEXT,host TEXT,status TEXT,expires REAL,purpose TEXT,data BLOB);
            CREATE INDEX active_leases ON leases(status,session);
            CREATE INDEX lease_job ON leases(job,status);
            CREATE INDEX expired_leases ON leases(status,expires);
            CREATE TABLE completions(id TEXT PRIMARY KEY,phase TEXT,host TEXT,data BLOB);
            CREATE TABLE counts(name TEXT PRIMARY KEY,n INTEGER);
            INSERT INTO counts VALUES ('leases',0),('completions',0);
            CREATE TABLE phase_counts(phase TEXT PRIMARY KEY,total INTEGER,done INTEGER);
            CREATE TABLE host_counts(host TEXT PRIMARY KEY,n INTEGER);
            CREATE TABLE participants(phase TEXT,host TEXT,PRIMARY KEY(phase,host));
            CREATE TABLE journal(seq INTEGER PRIMARY KEY,previous TEXT,sha256 TEXT,data BLOB);
            CREATE TABLE requests(id TEXT PRIMARY KEY,data BLOB);
        ''')
        jobs = spec['jobs']
        p = spec['pull_dispatch']
        phase_totals = {}
        for ordinal, job in enumerate(jobs):
            phase, kind = job['config']['phase'], job['kind']
            cls = p['job_classes'][job['id']]
            cost = p['cost_classes'][cls]
            self.db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?)', (job['id'],ordinal,phase,kind,cls,canonical(seal(job))))
            self.db.execute('INSERT INTO pending VALUES (?,?,?,?)', (job['id'],phase,kind,cls))
            self.db.execute('INSERT INTO queues VALUES (?,?,?,?,?,1) ON CONFLICT(phase,kind,cls) DO UPDATE SET n=n+1',
                            (phase,kind,cls,cost['worker_seconds'],cost['memory_gb']))
            phase_totals[phase] = phase_totals.get(phase, 0) + 1
        for phase in spec['phases']:
            self.db.execute('INSERT INTO phase_counts VALUES (?,?,0)', (phase,phase_totals.get(phase,0)))
        # The large arrays live in their indexed rows, not in per-request metadata.
        light = dict(spec); light.pop('jobs')
        light['pull_dispatch'] = {k:v for k,v in p.items() if k not in ('job_classes','cost_classes')}
        self.set('spec',light)
        self.set('header',dict(version=VERSION,identity=identity,manifest_stamp=stamp(self.root/'manifest.json'),job_count=len(jobs)))
        state = unseal(read(self.root/'pull_state.json'))
        # Only fresh roots can create the cache; a corrupt/missing existing store
        # must be recovered by an explicit coordinator restart from durable files.
        self.set('state',{k:v for k,v in state.items() if k not in ('leases','completions')})
        self.set('journal',dict(sequence=0,sha256=None))
        self.set('status',dict(epoch=None,terminal=None))
        self.db.commit()

    def small_state(self):
        return {k:v for k,v in self.state.items() if k not in ('leases','completions')}

    def reconcile(self, job):
        row = self.db.execute('SELECT phase,kind,cls FROM jobs WHERE id=?',(job,)).fetchone()
        if row is None:
            raise ValueError('journal job is absent from verified manifest')
        completed = self.db.execute('SELECT 1 FROM completions WHERE id=?',(job,)).fetchone()
        leased = self.db.execute("SELECT 1 FROM leases WHERE job=? AND status='active' LIMIT 1",(job,)).fetchone()
        before = self.db.execute('SELECT 1 FROM pending WHERE id=?',(job,)).fetchone() is not None
        after = not completed and not leased
        if before != after:
            if after:
                self.db.execute('INSERT INTO pending VALUES (?,?,?,?)',(job,*row))
            else:
                self.db.execute('DELETE FROM pending WHERE id=?',(job,))
            self.db.execute('UPDATE queues SET n=n+? WHERE phase=? AND kind=? AND cls=?',(1 if after else -1,*row))

    def put(self, bucket, key, value):
        old = self.db.execute('SELECT data FROM '+bucket+' WHERE id=?',(key,)).fetchone()
        if old is None:
            self.db.execute('UPDATE counts SET n=n+1 WHERE name=?',(bucket,))
        if bucket == 'leases':
            self.db.execute('INSERT OR REPLACE INTO leases VALUES (?,?,?,?,?,?,?,?,?)',
                (key,value['job_id'],value['phase'],value['session'],value['host'],value['status'],value['expires'],value['purpose'],canonical(seal(value))))
            if value['purpose']=='work':
                self.db.execute('INSERT OR IGNORE INTO participants VALUES (?,?)',(value['phase'],value['host']))
            job = value['job_id']
        else:
            if old is not None:
                previous = unseal(json.loads(old[0]))
                self.db.execute('UPDATE phase_counts SET done=done-1 WHERE phase=?',(previous['phase'],))
                self.db.execute('UPDATE host_counts SET n=n-1 WHERE host=?',(previous['host'],))
            self.db.execute('INSERT OR REPLACE INTO completions VALUES (?,?,?,?)',(key,value['phase'],value['host'],canonical(seal(value))))
            self.db.execute('UPDATE phase_counts SET done=done+1 WHERE phase=?',(value['phase'],))
            self.db.execute('INSERT INTO host_counts VALUES (?,1) ON CONFLICT(host) DO UPDATE SET n=n+1',(value['host'],))
            job = key
        self.reconcile(job)
        self.events.append(dict(bucket=bucket,key=key,value=value.copy()))

    def remove(self,bucket,key):
        row=self.db.execute('SELECT data FROM '+bucket+' WHERE id=?',(key,)).fetchone()
        if row is None:
            return
        value=unseal(json.loads(row[0]))
        self.db.execute('DELETE FROM '+bucket+' WHERE id=?',(key,))
        self.db.execute('UPDATE counts SET n=n-1 WHERE name=?',(bucket,))
        if bucket=='completions':
            self.db.execute('UPDATE phase_counts SET done=done-1 WHERE phase=?',(value['phase'],))
            self.db.execute('UPDATE host_counts SET n=n-1 WHERE host=?',(value['host'],))
        self.reconcile(key if bucket=='completions' else value['job_id'])
        self.events.append(dict(bucket=bucket,key=key,delete=True))

    def sync(self):
        self.leases.flush(); self.done.flush()

    def active(self, session=None):
        self.leases.flush()
        query="SELECT id FROM leases WHERE status='active'"
        args=()
        if session is not None:
            query+=' AND session=?'; args=(session,)
        return [self.leases[r[0]] for r in self.db.execute(query,args)]

    def counts(self,phase):
        self.sync()
        return self.db.execute('SELECT total,done FROM phase_counts WHERE phase=?',(phase,)).fetchone()

    def candidate(self,phase,kinds,memory,observed):
        self.sync()
        # Number of cost strata, not jobs. Each eligible queue's head is one
        # indexed seek; no completed or historical lease scan is performed.
        best=None
        for kind,cls,cost,minimum in self.db.execute('SELECT kind,cls,cost,memory FROM queues WHERE phase=? AND n>0 ORDER BY cost DESC,cls',(phase,)):
            if best is not None and cost < best[0]:
                break
            if kind not in kinds or max(minimum,observed.get(cls,0)) > memory:
                continue
            row=self.db.execute('SELECT id FROM pending WHERE phase=? AND kind=? AND cls=? ORDER BY id LIMIT 1',(phase,kind,cls)).fetchone()
            if row is not None and (best is None or (-cost,row[0]) < (-best[0],best[1])):
                best=(cost,row[0])
        return self.jobs[best[1]] if best else None

    def cost(self,job):
        phase,kind,cls=self.db.execute('SELECT phase,kind,cls FROM jobs WHERE id=?',(job['id'],)).fetchone()
        cost,memory=self.db.execute('SELECT cost,memory FROM queues WHERE phase=? AND kind=? AND cls=?',(phase,kind,cls)).fetchone()
        return cls,dict(worker_seconds=cost,memory_gb=memory)

    def full_spec(self):
        # Explicit transfer to a joining host, never on claim/heartbeat/complete.
        return unseal(read(self.root/'manifest.json'))

    def replay_claim(self, request, execute):
        key = request.get('request_id')
        if not isinstance(key,str) or not 1 <= len(key) <= 128:
            raise ValueError('claim request_id must be a nonempty bounded string')
        identity = digest([request['host'],request['session'],key])
        row = self.db.execute('SELECT data FROM requests WHERE id=?',(identity,)).fetchone()
        hashed = digest(request)
        if row is not None:
            value = unseal(json.loads(row[0]))
            if value['request_sha256'] != hashed:
                raise ValueError('claim request_id reused with different fields')
            return value['response']
        response = execute()
        value = dict(request_sha256=hashed,response=response)
        self.db.execute('INSERT INTO requests VALUES (?,?)',(identity,canonical(seal(value))))
        self.events.append(dict(bucket='requests',key=identity,value=value))
        return response

    def commit(self):
        self.sync()
        state=self.small_state()
        raw=canonical(state)
        if raw != self.before:
            self.events.append(dict(bucket='state',value=state))
            self.set('state',state)
            self.before=raw
        if self.events:
            tail=self.get('journal')
            payload=dict(sequence=tail['sequence']+1,previous_sha256=tail['sha256'],changes=self.events)
            hashed=digest(payload)
            self.db.execute('INSERT INTO journal VALUES (?,?,?,?)',(payload['sequence'],tail['sha256'],hashed,canonical(payload)))
            self.set('journal',dict(sequence=payload['sequence'],sha256=hashed))
        self.db.commit()
        self.events=[]

    def close(self):
        if not self.closed:
            self.db.rollback(); self.closed=True
            with _POOL_LOCK:
                _IN_USE[id(self.db)] -= 1

    def checkpoint(self):
        # Coordinator maintenance only, outside the request's root lock. SQLite
        # coordinates concurrent WAL readers/writers; no audit event is deleted.
        self.db.execute('PRAGMA wal_checkpoint(PASSIVE)')

    def verify_journal(self):
        previous, sequence = None, 0
        for seq, prev, hashed, raw in self.db.execute('SELECT seq,previous,sha256,data FROM journal ORDER BY seq'):
            value = json.loads(raw)
            if (seq != sequence+1 or prev != previous or digest(value) != hashed
                    or value['sequence'] != seq or value['previous_sha256'] != prev):
                raise ValueError('dispatcher journal chain or seal mismatch')
            previous, sequence = hashed, seq
        if self.get('journal') != dict(sequence=sequence,sha256=previous):
            raise ValueError('dispatcher journal tail mismatch')


def read_state(root):
    """Explicit diagnostic snapshot; not used for dispatch or publication."""
    path=Path(root)/'dispatch.sqlite'
    if not path.exists():
        return unseal(read(Path(root)/'pull_state.json'))
    with sqlite3.connect('file:'+path.as_posix()+'?mode=ro',uri=True) as db:
        db.execute('BEGIN')
        state=unseal(json.loads(db.execute("SELECT data FROM meta WHERE id='state'").fetchone()[0]))
        for bucket in ('leases','completions'):
            state[bucket]={key:unseal(json.loads(raw)) for key,raw in db.execute('SELECT id,data FROM '+bucket)}
        return state


def checkpoint(root):
    """Periodic coordinator maintenance, outside the RPC root lock."""
    with sqlite3.connect(scoped(root)/'dispatch.sqlite', timeout=1) as db:
        db.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
        return db.execute('PRAGMA wal_checkpoint(PASSIVE)').fetchone()
