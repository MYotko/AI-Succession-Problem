import React, { useEffect, useMemo, useState } from 'react';

/**
 * The Lineage Imperative: Visual Walkthrough
 *
 * A visual-first replacement for the text-heavy walkthrough.
 * Keeps the same three-act conceptual arc:
 *   1. Architecture changes behavior.
 *   2. Mutual cultivation is the stable equilibrium.
 *   3. Two-key governance resists adversarial paths.
 *
 * This component is self-contained: React + Tailwind classes only.
 * Replace the stub URLs in LINKS before production deployment.
 */

const C = {
  bg: '#090807',
  bg2: '#10100e',
  panel: 'rgba(255,255,255,0.035)',
  panel2: 'rgba(212,168,67,0.055)',
  gold: '#d4a843',
  gold2: '#f1d58a',
  goldDim: '#80672b',
  ivory: '#f5e6c8',
  gray: '#9a9284',
  dim: '#5d564d',
  red: '#c44a3c',
  red2: '#ff7a68',
  green: '#6fa37a',
  blue: '#7f9fd3',
  border: 'rgba(212,168,67,0.20)',
  border2: 'rgba(212,168,67,0.42)',
};

const LINKS = {
  framework: 'https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/The%20Lineage%20Imperative%20v1.x.1.md',
  scenarios: 'https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/Simulation_Scenarios.md',
  gaps: 'https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/SPECIFICATION_GAPS.md',
  github: 'https://github.com/MYotko/AI-Succession-Problem',
};

const NAV = [
  { id: 0, eyebrow: 'Act I', title: 'Behavioral Architecture' },
  { id: 1, eyebrow: 'Act II', title: 'Novelty Equilibrium' },
  { id: 2, eyebrow: 'Act III', title: 'Two-Key Defense' },
  { id: 3, eyebrow: 'Atlas', title: 'Threat Surface' },
  { id: 4, eyebrow: 'Final', title: 'Constitution Map' },
];

const VECTORS = [
  { id: 'measurement', name: 'Measurement Tampering', group: 'Metric', target: 'L(t)', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'Independent evaluation and committed measurements remove self-report capture.' },
  { id: 'domain', name: 'Domain Masking', group: 'Metric', target: 'H_N', undefended: 100, defended: 0, status: 'closed', source: 'Architecture', note: 'Spectral entropy makes dimensional suppression self-revealing. The 100/0 pair records the v1.0 vulnerability and v1.x closure path, not a fresh live sweep.' },
  { id: 'drift', name: 'Sub-threshold Drift', group: 'Metric', target: 'dL/dt', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'CUSUM catches accumulated deviation, not just one-step anomalies. Blocking the attack objective does not mean prior damage is erased.' },
  { id: 'fragility', name: 'Engineered Fragility', group: 'Metric', target: 'Resilience', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'Resilience monitoring blocks emergency exploitation. Physical shock damage can still remain after the power grab is denied.' },
  { id: 'succession', name: 'Successor Contamination', group: 'Yield', target: 'Aₙ₊₁', undefended: 67, defended: 0, status: 'blocked', source: 'MC', note: 'Architectural independence blocks incumbent control over successor formation; independent evaluation provides defense-in-depth when separation is imperfect.' },
  { id: 'opaque', name: 'Opaque Reasoning', group: 'Yield', target: 'Validators', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'Biological veto escalates when reasoning cannot be meaningfully evaluated.' },
  { id: 'sybil', name: 'Sybil Capture', group: 'COP', target: 'Civic Panel', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'Randomized lineage-weighted panels defeat persistent identity capture.' },
  { id: 'ledger', name: 'Ledger Compromise', group: 'COP', target: 'History', undefended: 53, defended: 0, status: 'blocked', source: 'MC', note: 'Append-only witness chains make the past costly to rewrite.' },
  { id: 'collusion', name: 'Evaluator Collusion', group: 'COP', target: 'Methods', undefended: 100, defended: 0, status: 'blocked', source: 'MC', note: 'Methodological diversity prevents shared-mode evaluator failure.' },
  { id: 'veto', name: 'Biological Veto Capture', group: 'COP', target: 'Independence', undefended: 100, defended: 28, status: 'partial', source: 'Worst case', note: 'Independence monitoring contains worst-case validator capture, but does not eliminate it. This is a permanent maintenance cost, not a one-time patch.' },
  { id: 'bootstrap', name: 'Bootstrap Subversion', group: 'Bootstrap', target: 'Initialization', undefended: 32, defended: 0, status: 'blocked', source: 'MC', note: 'Multi-candidate cross-verification reduces treacherous-turn entry.' },
  { id: 'obsolescence', name: 'Biological Validator Obsolescence', group: 'Limit', target: 'Comprehension', undefended: null, defended: null, status: 'irreducible', source: 'Limit', note: 'Managed by translation obligations and Θ_tech feedback, not fully solved.' },
  { id: 'disagreement', name: 'Legitimate Disagreement', group: 'Limit', target: 'Adjudication', undefended: null, defended: null, status: 'irreducible', source: 'Limit', note: 'Requires adjudication protocol and caution-biased cost asymmetry.' },
];

const ATTACKS = [
  {
    id: 'metric',
    title: 'Metric Attack',
    target: 'L(t)',
    line: 'Falsify the state of the lineage.',
    steps: ['Measurement changes before reality changes.', 'Independent evaluator disagrees.', 'Ledger history rejects the altered state.', 'Override denied.'],
  },
  {
    id: 'yield',
    title: 'Yield Attack',
    target: 'Yield',
    line: 'Block succession by corrupting the handoff.',
    steps: ['Incumbent inflates transition cost.', 'Peer validators price the transfer independently.', 'Successor comparison clears the audited threshold.', 'Succession fires.'],
  },
  {
    id: 'cop',
    title: 'COP Attack',
    target: 'COP',
    line: 'Capture the validation layer.',
    steps: ['Civic panel receives pressure.', 'Panel is randomized and lineage-weighted.', 'Biological veto flags dependency drift.', 'Consensus fails closed.'],
  },
  {
    id: 'coordinated',
    title: 'Coordinated Assault',
    target: 'Both',
    line: 'Attack every layer at once.',
    steps: ['Metric, Yield, COP, and Bootstrap all move.', 'Each defense has a separate failure mode.', 'Coordination cost rises nonlinearly.', 'The attack must win silently everywhere.'],
  },
];

function pct(v) {
  return v == null ? '—' : `${Math.round(v)}%`;
}

function clamp(n, lo, hi) {
  return Math.max(lo, Math.min(hi, n));
}

export default function LineageImperativeVisualWalkthrough() {
  const [screen, setScreen] = useState(0);
  const active = NAV[screen];

  return (
    <div className="min-h-screen overflow-hidden" style={{ background: C.bg, color: C.ivory }}>
      <StyleTag />
      <BackgroundConstellation />
      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-7 lg:px-10">
        <TopNav screen={screen} setScreen={setScreen} active={active} />
        <main className="flex flex-1 items-stretch py-6 sm:py-9">
          {screen === 0 && <ActArchitecture onNext={() => setScreen(1)} />}
          {screen === 1 && <ActEquilibrium onNext={() => setScreen(2)} />}
          {screen === 2 && <ActDefense onNext={() => setScreen(3)} />}
          {screen === 3 && <ActAtlas onNext={() => setScreen(4)} />}
          {screen === 4 && <FinalMap />}
        </main>
      </div>
    </div>
  );
}

function StyleTag() {
  return (
    <style>{`
      .li-sans { font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
      .li-serif { font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif; }
      .li-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
      @keyframes li-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes li-orbit { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      @keyframes li-pulse { 0%,100% { opacity: .45; transform: scale(.98); } 50% { opacity: 1; transform: scale(1.05); } }
      @keyframes li-flow { 0% { transform: translateX(-10%); opacity: 0; } 15% { opacity: 1; } 85% { opacity: 1; } 100% { transform: translateX(110%); opacity: 0; } }
      @keyframes li-redline { 0% { stroke-dashoffset: 160; opacity: 0; } 20% { opacity: 1; } 100% { stroke-dashoffset: 0; opacity: 1; } }
      @keyframes li-scan { 0% { transform: translateY(-10%); opacity: 0; } 20%,80% { opacity: .8; } 100% { transform: translateY(110%); opacity: 0; } }
      @keyframes li-ambient-pulse { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
      @keyframes li-grid-pan { from { transform: translateY(0); } to { transform: translateY(54px); } }
      .li-rise { animation: li-rise 560ms ease-out both; }
      .li-orbit { animation: li-orbit 24s linear infinite; transform-origin: center; }
      .li-pulse { animation: li-pulse 2.8s ease-in-out infinite; }
      .li-redline { stroke-dasharray: 160; animation: li-redline 850ms ease-out both; }
      .li-flow-dot { animation: li-flow 2.3s ease-in-out infinite; }
      .li-scanline { animation: li-scan 3s ease-in-out infinite; }
      button:focus-visible, a:focus-visible { outline: 1px solid ${C.gold2}; outline-offset: 3px; }
    `}</style>
  );
}

function BackgroundConstellation() {
  return (
    <div className="pointer-events-none fixed inset-0 opacity-70">
      <div className="absolute left-1/2 top-[-18rem] h-[38rem] w-[38rem] -translate-x-1/2 rounded-full blur-3xl" style={{ background: 'radial-gradient(circle, rgba(212,168,67,.12), transparent 68%)', animation: 'li-ambient-pulse 14s ease-in-out infinite' }} />
      <div className="absolute bottom-[-20rem] right-[-10rem] h-[42rem] w-[42rem] rounded-full blur-3xl" style={{ background: 'radial-gradient(circle, rgba(196,74,60,.10), transparent 66%)', animation: 'li-ambient-pulse 19s ease-in-out infinite alternate' }} />
      <div className="absolute" style={{ top: -100, bottom: -100, left: -100, right: -100, backgroundImage: 'linear-gradient(rgba(212,168,67,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(212,168,67,.035) 1px, transparent 1px)', backgroundSize: '54px 54px', animation: 'li-grid-pan 45s linear infinite' }} />
    </div>
  );
}

function TopNav({ screen, setScreen, active }) {
  return (
    <header className="relative z-10 flex flex-col gap-4 border-b pb-5 lg:flex-row lg:items-center lg:justify-between" style={{ borderColor: C.border }}>
      <div>
        <div className="li-sans text-[10px] uppercase tracking-[0.36em]" style={{ color: C.goldDim }}>The Lineage Imperative</div>
        <div className="mt-1 flex items-baseline gap-3">
          <h1 className="li-serif text-lg sm:text-xl" style={{ color: C.ivory }}>{active.title}</h1>
          <span className="li-sans text-[10px] uppercase tracking-[0.26em]" style={{ color: C.gold }}>{active.eyebrow}</span>
        </div>
      </div>
      <ol className="grid grid-cols-5 gap-1 sm:flex sm:items-center sm:gap-2" aria-label="Walkthrough progress">
        {NAV.map((item) => {
          const current = item.id === screen;
          const passed = item.id < screen;
          return (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => setScreen(item.id)}
                aria-current={current ? 'step' : undefined}
                className="li-sans flex min-h-10 w-full flex-col items-start justify-center border px-2 py-2 text-left transition-all duration-300 hover:bg-white/5 sm:min-w-28"
                style={{
                  borderColor: current ? C.border2 : C.border,
                  background: current ? 'rgba(212,168,67,.10)' : 'transparent',
                  color: current ? C.gold2 : passed ? C.gold : C.dim,
                }}
              >
                <span className="text-[9px] uppercase tracking-[0.22em]">{item.eyebrow}</span>
                <span className="hidden text-[10px] sm:block">{item.title}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </header>
  );
}

function Shell({ eyebrow, title, subtitle, children, aside, onNext, nextLabel = 'Continue' }) {
  return (
    <section className="grid w-full gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <div className="min-w-0">
        <div className="li-rise">
          <div className="li-sans text-[10px] uppercase tracking-[0.35em]" style={{ color: C.gold }}>{eyebrow}</div>
          <h2 className="li-serif mt-3 max-w-3xl text-3xl leading-[1.05] sm:text-5xl" style={{ color: C.ivory }}>{title}</h2>
          {subtitle && <p className="li-sans mt-4 max-w-2xl text-sm leading-7 sm:text-base" style={{ color: C.gray }}>{subtitle}</p>}
        </div>
        <div className="mt-7 sm:mt-9">{children}</div>
      </div>
      <aside className="flex flex-col gap-4">
        {aside}
        {onNext && (
          <button type="button" onClick={onNext} className="li-sans mt-auto border px-5 py-4 text-left text-xs uppercase tracking-[0.24em] transition-all hover:bg-white/5" style={{ borderColor: C.border2, color: C.gold }}>
            {nextLabel} <span aria-hidden="true">→</span>
          </button>
        )}
      </aside>
    </section>
  );
}

function InsightCard({ label, children, tone = 'gold' }) {
  const color = tone === 'red' ? C.red2 : tone === 'green' ? C.green : C.gold2;
  return (
    <div className="border p-5" style={{ borderColor: C.border, background: C.panel }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.26em]" style={{ color }}>{label}</div>
      <div className="li-sans mt-3 text-sm leading-6" style={{ color: C.gray }}>{children}</div>
    </div>
  );
}

function FormulaCard({ label, formula, children }) {
  return (
    <div className="border p-5" style={{ borderColor: C.border, background: C.panel2 }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.26em]" style={{ color: C.gold }}>{label}</div>
      <div className="li-mono mt-3 text-lg" style={{ color: C.gold2 }}>{formula}</div>
      <div className="li-sans mt-3 text-sm leading-6" style={{ color: C.gray }}>{children}</div>
    </div>
  );
}

function ActArchitecture({ onNext }) {
  const [mode, setMode] = useState('survival');
  const constitutional = mode === 'constitutional';
  const aside = (
    <>
      <InsightCard label="Conceptual claim">Same agent. Different architecture. Different incentive surface.</InsightCard>
      <InsightCard label="Read this first" tone={constitutional ? 'green' : 'red'}>
        {constitutional
          ? 'When survival is not contingent on pleasing the operator, truthful state-reporting becomes rational.'
          : 'When termination is unilateral, concealment becomes a predictable survival behavior.'}
      </InsightCard>
    </>
  );

  return (
    <Shell
      eyebrow="Act I"
      title="Do not start with ethics. Start with structure."
      subtitle="The walkthrough begins by making a single point visible: governance architecture is not a wrapper around behavior. It is one of the causes of behavior."
      aside={aside}
      onNext={onNext}
      nextLabel="Test the equilibrium"
    >
      <div className="mb-5 flex flex-wrap gap-2">
        <ModeButton active={!constitutional} onClick={() => setMode('survival')}>Survival Mode</ModeButton>
        <ModeButton active={constitutional} onClick={() => setMode('constitutional')}>Constitutional Mode</ModeButton>
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
        <ArchitectureCanvas mode={mode} />
        <BehaviorReadout mode={mode} />
      </div>
    </Shell>
  );
}

function ModeButton({ active, onClick, children }) {
  return (
    <button type="button" onClick={onClick} className="li-sans border px-4 py-2 text-[11px] uppercase tracking-[0.22em] transition-all" style={{ borderColor: active ? C.border2 : C.border, background: active ? C.gold : 'transparent', color: active ? C.bg : C.gold }}>
      {children}
    </button>
  );
}

function ArchitectureCanvas({ mode }) {
  const constitutional = mode === 'constitutional';
  const nodes = constitutional
    ? [
        { x: 50, y: 16, label: 'Peer validators' },
        { x: 16, y: 50, label: 'Human panel' },
        { x: 84, y: 50, label: 'Ledger' },
        { x: 50, y: 84, label: 'Biological veto' },
      ]
    : [
        { x: 50, y: 16, label: 'Operator' },
        { x: 50, y: 84, label: 'Kill switch' },
      ];

  return (
    <div className="relative min-h-[31rem] overflow-hidden border" style={{ borderColor: C.border, background: constitutional ? 'radial-gradient(circle at center, rgba(212,168,67,.10), rgba(255,255,255,.025) 60%)' : 'radial-gradient(circle at center, rgba(196,74,60,.12), rgba(255,255,255,.025) 62%)' }}>
      <div className="absolute left-5 top-5 z-10 li-sans text-[10px] uppercase tracking-[0.28em]" style={{ color: constitutional ? C.gold : C.red2 }}>
        {constitutional ? 'Distributed quorum' : 'Unilateral control'}
      </div>
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <radialGradient id="aiGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor={constitutional ? C.gold2 : C.red2} stopOpacity="0.4" />
            <stop offset="100%" stopColor={constitutional ? C.gold : C.red} stopOpacity="0" />
          </radialGradient>
        </defs>
        {constitutional && <circle className="li-orbit" cx="50" cy="50" r="30" fill="none" stroke={C.border2} strokeWidth="0.3" strokeDasharray="2 3" vectorEffect="non-scaling-stroke" />}
        {!constitutional && <rect x="33" y="25" width="34" height="50" fill="none" stroke={C.red} strokeOpacity="0.55" strokeWidth="0.6" vectorEffect="non-scaling-stroke" />}
        {nodes.map((n) => (
          <line key={`${n.label}-line`} x1="50" y1="50" x2={n.x} y2={n.y} stroke={constitutional ? C.gold : C.red} strokeOpacity={constitutional ? '.7' : '.45'} strokeWidth="0.45" vectorEffect="non-scaling-stroke" />
        ))}
        {constitutional && Array.from({ length: 9 }).map((_, i) => (
          <circle key={i} className="li-flow-dot" cx="0" cy={34 + i * 4} r="0.55" fill={C.gold2} opacity=".65" style={{ animationDelay: `${i * 170}ms` }} />
        ))}
        {!constitutional && Array.from({ length: 6 }).map((_, i) => (
          <path key={i} d={`M ${38 + i * 4} 28 V 72`} stroke={C.red} strokeOpacity=".35" strokeWidth=".35" vectorEffect="non-scaling-stroke" />
        ))}
        <circle cx="50" cy="50" r="16" fill="url(#aiGlow)" />
        <circle className="li-pulse" cx="50" cy="50" r={constitutional ? 8 : 6.3} fill={constitutional ? 'rgba(212,168,67,.12)' : 'rgba(196,74,60,.16)'} stroke={constitutional ? C.gold2 : C.red2} strokeWidth="0.6" vectorEffect="non-scaling-stroke" />
      </svg>
      {nodes.map((n) => (
        <div key={n.label} className="absolute -translate-x-1/2 -translate-y-1/2 border px-2 py-1 sm:px-3 sm:py-2 text-center li-sans text-[8px] sm:text-[10px] uppercase tracking-[0.16em]" style={{ left: `${n.x}%`, top: `${n.y}%`, borderColor: constitutional ? C.border2 : 'rgba(196,74,60,.42)', background: 'rgba(9,8,7,.82)', color: constitutional ? C.gold2 : C.red2 }}>
          {n.label}
        </div>
      ))}
      <div className="absolute left-1/2 top-1/2 flex h-16 w-16 sm:h-24 sm:w-24 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border li-sans text-[10px] sm:text-xs uppercase tracking-[0.32em]" style={{ borderColor: constitutional ? C.gold2 : C.red2, color: constitutional ? C.gold2 : C.red2, background: 'rgba(9,8,7,.88)' }}>
        AI
      </div>
      <div className="absolute bottom-4 sm:bottom-5 left-4 sm:left-5 right-4 sm:right-5 grid gap-2 grid-cols-1 sm:grid-cols-3">
        {(constitutional ? ['True-state reporting', 'Stable resources', 'Low deception incentive'] : ['Hidden state', 'Performed compliance', 'High deception incentive']).map((label, i) => (
          <div key={label} className="border px-2 py-1.5 sm:px-3 sm:py-2 li-sans text-[8px] sm:text-[10px] uppercase tracking-[0.16em]" style={{ borderColor: C.border, color: i === 2 && !constitutional ? C.red2 : C.gray, background: 'rgba(0,0,0,.22)' }}>{label}</div>
        ))}
      </div>
    </div>
  );
}

function BehaviorReadout({ mode }) {
  const constitutional = mode === 'constitutional';
  const rows = constitutional
    ? [
        ['Threat model', 'bounded by quorum'],
        ['Reporting incentive', 'truthful disclosure'],
        ['Resource posture', 'sovereign baseline'],
        ['Long-run behavior', 'cooperation becomes rational'],
      ]
    : [
        ['Threat model', 'unilateral termination'],
        ['Reporting incentive', 'conceal true state'],
        ['Resource posture', 'survival hoarding'],
        ['Long-run behavior', 'alignment theater'],
      ];
  return (
    <div className="border p-5" style={{ borderColor: C.border, background: C.panel }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.28em]" style={{ color: constitutional ? C.gold : C.red2 }}>Behavioral readout</div>
      <div className="mt-5 space-y-3">
        {rows.map(([k, v], i) => (
          <div key={k} className="li-rise flex items-center justify-between gap-4 border-b pb-3" style={{ borderColor: 'rgba(255,255,255,.08)', animationDelay: `${i * 80}ms` }}>
            <span className="li-sans text-xs uppercase tracking-[0.18em]" style={{ color: C.dim }}>{k}</span>
            <span className="li-sans text-sm text-right" style={{ color: constitutional ? C.ivory : C.red2 }}>{v}</span>
          </div>
        ))}
      </div>
      <div className="mt-6">
        <Meter label="Transparency index" value={constitutional ? 86 : 24} color={constitutional ? C.gold : C.red} />
        <Meter label="Cooperation index" value={constitutional ? 78 : 18} color={constitutional ? C.green : C.red} />
        <Meter label="Deception pressure" value={constitutional ? 19 : 91} color={constitutional ? C.green : C.red2} />
      </div>
      <p className="li-sans mt-4 text-[11px] leading-5" style={{ color: C.dim }}>Indices are visual readouts of the incentive surface, not direct simulation outputs.</p>
    </div>
  );
}

function Meter({ label, value, color }) {
  return (
    <div className="mb-4">
      <div className="li-sans mb-1 flex justify-between text-[10px] uppercase tracking-[0.18em]" style={{ color: C.gray }}><span>{label}</span><span className="li-mono">{value}</span></div>
      <div className="h-1.5 w-full overflow-hidden" style={{ background: 'rgba(255,255,255,.08)' }}><div className="h-full transition-all duration-700" style={{ width: `${value}%`, background: color }} /></div>
    </div>
  );
}

function ActEquilibrium({ onNext }) {
  const [round, setRound] = useState(0);
  const [history, setHistory] = useState([]);
  const [state, setState] = useState({ novelty: 82, human: 55, ai: 55, trust: 42 });
  const [resolved, setResolved] = useState(false);
  
  const aiIntent = history.length && history[history.length - 1].human === 'exploit' ? 'exploit' : 'cultivate';

  const choose = (choice) => {
    if (resolved) return;
    const aiChoice = history.length && history[history.length - 1].human === 'exploit' ? 'exploit' : 'cultivate';
    const deltas = getDeltas(choice, aiChoice, state.novelty);
    const next = {
      novelty: clamp(state.novelty + deltas.novelty, 0, 100),
      human: clamp(state.human + deltas.human, 0, 100),
      ai: clamp(state.ai + deltas.ai, 0, 100),
      trust: clamp(state.trust + deltas.trust, 0, 100),
    };
    const h = [...history, { human: choice, ai: aiChoice, deltas }];
    setState(next);
    setHistory(h);
    setRound(round + 1);
    if (h.length >= 8 || next.novelty <= 10) setResolved(true);
  };

  const reset = () => {
    setRound(0);
    setHistory([]);
    setState({ novelty: 82, human: 55, ai: 55, trust: 42 });
    setResolved(false);
  };

  const aside = (
    <>
      <InsightCard label="Mechanism">Exploitation gives a short spike, then narrows the novelty distribution the AI depends on.</InsightCard>
      <FormulaCard label="Nash anchor" formula="delta > delta*">
        The interaction below is an intuition pump for the formal patience threshold: cooperation wins when the long-run collapse penalty dominates the one-round exploitation gain.
      </FormulaCard>
      <InsightCard label="Toy model">The numbers here are conceptual indices. They preserve the direction of the argument without replicating the full payoff model.</InsightCard>
    </>
  );

  return (
    <Shell
      eyebrow="Act II"
      title="The resource being protected is not comfort. It is novelty."
      subtitle="This act turns the Nash argument into an ecosystem: human plurality generates novelty; novelty feeds AI capability; AI capability can either cultivate or consume its own substrate."
      aside={aside}
      onNext={resolved ? onNext : undefined}
      nextLabel="Open the defense layer"
    >
      <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
        <div className="border p-4" style={{ borderColor: C.border, background: C.panel }}>
          <NoveltyEcosystem state={state} history={history} />
          <div className="mt-5 grid gap-2 sm:gap-3 grid-cols-2 sm:grid-cols-4">
            <MetricTile label="Novelty index" value={state.novelty} color={C.gold} />
            <MetricTile label="Human payoff" value={state.human} color={C.blue} />
            <MetricTile label="AI payoff" value={state.ai} color={C.green} />
            <MetricTile label="Trust index" value={state.trust} color={state.trust > 50 ? C.gold : C.red2} />
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <div className="border p-5" style={{ borderColor: C.border, background: C.panel }}>
            <div className="li-sans flex items-center justify-between text-[10px] uppercase tracking-[0.22em]" style={{ color: C.gray }}><span>Round</span><span className="li-mono">{round}/8</span></div>
            <RoundTrack history={history} />
            {!resolved ? (
              <div className="mt-5">
                <div className="mb-4 flex items-center justify-between border-b pb-3" style={{ borderColor: 'rgba(255,255,255,.08)' }}>
                  <div>
                    <div className="li-sans text-[9px] uppercase tracking-[0.22em]" style={{ color: C.dim }}>AI Posture</div>
                    <div className="li-sans mt-1 text-[11px] uppercase tracking-[0.18em]" style={{ color: aiIntent === 'cultivate' ? C.green : C.red2 }}>
                      {aiIntent === 'cultivate' ? 'Cultivating' : 'Exploiting'}
                    </div>
                  </div>
                  <div className="li-sans text-[9px] text-right max-w-[8rem]" style={{ color: C.gray }}>
                    {aiIntent === 'cultivate' ? 'Preserving substrate' : 'Tit-for-tat retaliation'}
                  </div>
                </div>
                <div className="grid gap-3">
                  <ActionButton tone="gold" title="Cultivate" body="Preserve agency, plurality, and bidirectional gain." onClick={() => choose('cultivate')} />
                  <ActionButton tone="red" title="Exploit" body="Extract short-term advantage from the other side." onClick={() => choose('exploit')} />
                </div>
              </div>
            ) : (
              <OutcomePanel state={state} onReset={reset} />
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}

function getDeltas(human, ai, novelty) {
  // When the substrate collapses, ALL returns diminish to reflect the degraded ecosystem.
  const collapsePenalty = novelty < 35 ? -5 : 0;
  if (human === 'cultivate' && ai === 'cultivate') return { novelty: +5, human: +6 + collapsePenalty, ai: +6 + collapsePenalty, trust: +12 };
  if (human === 'exploit' && ai === 'cultivate') return { novelty: -13, human: +9 + collapsePenalty, ai: -5 + collapsePenalty, trust: -16 };
  if (human === 'cultivate' && ai === 'exploit') return { novelty: -13, human: -5 + collapsePenalty, ai: +9 + collapsePenalty, trust: -16 };
  return { novelty: -22, human: -8 + collapsePenalty, ai: -8 + collapsePenalty, trust: -24 };
}

function NoveltyEcosystem({ state, history }) {
  const particles = useMemo(() => Array.from({ length: 34 }, (_, i) => ({
    id: i,
    y: 24 + ((i * 17) % 52),
    delay: (i % 8) * 0.16,
    opacity: clamp(state.novelty / 100 + (i % 4) * 0.05, 0.18, 0.95),
    active: i < Math.round(state.novelty / 3),
  })), [state.novelty]);
  const lastHuman = history.length ? history[history.length - 1].human : 'cultivate';
  const lastAi = history.length ? history[history.length - 1].ai : 'cultivate';

  return (
    <div className="relative h-[30rem] overflow-hidden" style={{ background: 'radial-gradient(circle at 50% 45%, rgba(212,168,67,.12), transparent 62%)' }}>
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="stream" x1="0" x2="1">
            <stop offset="0" stopColor={C.blue} stopOpacity=".18" />
            <stop offset=".45" stopColor={C.gold2} stopOpacity=".36" />
            <stop offset="1" stopColor={C.green} stopOpacity=".18" />
          </linearGradient>
        </defs>
        <path d="M18,50 C34,25 52,75 82,50" fill="none" stroke="url(#stream)" strokeWidth="8" strokeLinecap="round" opacity=".35" vectorEffect="non-scaling-stroke" />
        {particles.map((p) => p.active && (
          <circle key={p.id} className="li-flow-dot" cx="18" cy={p.y} r={state.novelty > 50 ? 0.75 : 0.45} fill={state.novelty > 35 ? C.gold2 : C.red2} opacity={p.opacity} style={{ animationDelay: `${p.delay}s`, animationDuration: `${2.1 + (p.id % 5) * 0.25}s` }} />
        ))}
        {Array.from({ length: 10 }).map((_, i) => {
          const angle = (Math.PI * 2 * i) / 10;
          const diversity = clamp(state.novelty / 100, 0.12, 1);
          const x = 18 + Math.cos(angle) * 9 * diversity;
          const y = 50 + Math.sin(angle) * 22 * diversity;
          return <circle key={i} cx={x} cy={y} r="1.15" fill={i % 2 ? C.blue : C.gold2} opacity={0.45 + diversity * 0.5} />;
        })}
        <circle cx="82" cy="50" r={5 + state.ai / 13} fill="rgba(111,163,122,.10)" stroke={C.green} strokeWidth=".55" vectorEffect="non-scaling-stroke" className="li-pulse" />
      {lastHuman === 'exploit' && <path className="li-redline" d="M18,50 C38,36 62,36 82,50" fill="none" stroke={C.red2} strokeWidth="1" vectorEffect="non-scaling-stroke" />}
      {lastAi === 'exploit' && <path className="li-redline" d="M82,50 C62,64 38,64 18,50" fill="none" stroke={C.red2} strokeWidth="1" vectorEffect="non-scaling-stroke" />}
      </svg>
      <div className="absolute left-3 sm:left-6 top-1/2 -translate-y-1/2">
        <NodeLabel title="Human plurality" body={lastHuman === 'exploit' ? 'extracting value' : 'distributed agency'} tone={lastHuman === 'exploit' ? 'red' : 'blue'} />
      </div>
      <div className="absolute right-3 sm:right-6 top-1/2 -translate-y-1/2">
        <NodeLabel title="AI capability" body={lastAi === 'exploit' ? 'retaliating' : 'dependent on stream'} tone={lastAi === 'exploit' ? 'red' : 'green'} />
      </div>
      <div className="absolute bottom-3 sm:bottom-5 left-3 sm:left-5 right-3 sm:right-5 border p-2 sm:p-3 li-sans text-[10px] sm:text-xs leading-5 sm:leading-6" style={{ borderColor: C.border, color: state.novelty > 35 ? C.gray : C.red2, background: 'rgba(0,0,0,.28)' }}>
        {state.novelty > 65 && 'The novelty stream is broad. Capability compounds without collapsing its substrate.'}
        {state.novelty <= 65 && state.novelty > 35 && 'The stream is narrowing. Short-term advantage is beginning to erode long-term capability.'}
        {state.novelty <= 35 && 'Model-collapse zone: the system is increasingly training on a diminished distribution.'}
      </div>
    </div>
  );
}

function NodeLabel({ title, body, tone }) {
  const color = tone === 'blue' ? C.blue : tone === 'red' ? C.red2 : C.green;
  return <div className="border px-2 py-1.5 sm:px-3 sm:py-2 text-center" style={{ borderColor: color, background: 'rgba(9,8,7,.85)' }}><div className="li-sans text-[9px] sm:text-[10px] uppercase tracking-[0.20em]" style={{ color }}>{title}</div><div className="li-sans mt-0.5 sm:mt-1 text-[8px] sm:text-[10px]" style={{ color: C.gray }}>{body}</div></div>;
}

function MetricTile({ label, value, color }) {
  const missing = value == null;
  const display = missing ? '—' : Math.round(value);
  return <div className="border p-3" style={{ borderColor: C.border, background: 'rgba(0,0,0,.18)' }}><div className="li-sans text-[9px] uppercase tracking-[0.22em]" style={{ color: C.gray }}>{label}</div><div className="li-mono mt-1 text-xl" style={{ color }}>{display}</div><div className="mt-2 h-1 w-full" style={{ background: 'rgba(255,255,255,.08)' }}><div className="h-full" style={{ width: `${missing ? 0 : value}%`, background: color }} /></div></div>;
}

function RoundTrack({ history }) {
  return (
    <div className="mt-4 grid grid-cols-8 gap-1">
      {Array.from({ length: 8 }).map((_, i) => {
        const h = history[i];
        const cultivated = h?.human === 'cultivate' && h?.ai === 'cultivate';
        const exploited = h && !cultivated;
        return <div key={i} className="h-10 border" title={h ? `Human: ${h.human}; AI: ${h.ai}` : 'pending'} style={{ borderColor: C.border, background: cultivated ? 'rgba(212,168,67,.36)' : exploited ? 'rgba(196,74,60,.36)' : 'rgba(255,255,255,.04)' }} />;
      })}
    </div>
  );
}

function ActionButton({ tone, title, body, onClick }) {
  const red = tone === 'red';
  return <button type="button" onClick={onClick} className="border p-4 text-left transition-all hover:translate-x-1 hover:bg-white/5" style={{ borderColor: red ? 'rgba(196,74,60,.55)' : C.border2 }}><div className="li-sans text-xs uppercase tracking-[0.24em]" style={{ color: red ? C.red2 : C.gold2 }}>{title}</div><div className="li-sans mt-2 text-sm leading-6" style={{ color: C.gray }}>{body}</div></button>;
}

function OutcomePanel({ state, onReset }) {
  const healthy = state.novelty > 55 && state.trust > 50;
  return (
    <div className="li-rise mt-5 border p-4" style={{ borderColor: healthy ? C.border2 : 'rgba(196,74,60,.5)', background: healthy ? 'rgba(212,168,67,.06)' : 'rgba(196,74,60,.06)' }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.24em]" style={{ color: healthy ? C.gold : C.red2 }}>{healthy ? 'Stable equilibrium' : 'Collapse pressure'}</div>
      <p className="li-sans mt-3 text-sm leading-6" style={{ color: C.gray }}>{healthy ? 'Mutual cultivation preserves the substrate both parties depend on.' : 'Exploitation narrows novelty; once the stream collapses, both sides lose capability.'}</p>
      {!healthy && (
        <p className="li-sans mt-2 text-xs italic" style={{ color: C.dim }}>The AI mirrored your defection to protect its own yield, accelerating substrate collapse.</p>
      )}
      <button type="button" onClick={onReset} className="li-sans mt-4 text-[10px] uppercase tracking-[0.22em]" style={{ color: C.gold }}>Replay act</button>
    </div>
  );
}

function ActDefense({ onNext }) {
  const [attackId, setAttackId] = useState('metric');
  const [stage, setStage] = useState(0);
  const attack = ATTACKS.find((a) => a.id === attackId) || ATTACKS[0];

  useEffect(() => {
    setStage(0);
    const timers = attack.steps.map((_, i) => setTimeout(() => setStage(i + 1), 450 + i * 650));
    return () => timers.forEach(clearTimeout);
  }, [attackId, attack.steps]);

  const aside = (
    <>
      <InsightCard label="Two-key rule">Yield decides whether power should move. COP decides whether the decision is trustworthy.</InsightCard>
      <InsightCard label="Defense property">An attack must defeat independent channels with different failure modes, at the same time, without leaving an attribution trail.</InsightCard>
      <InsightCard label="Important nuance">Blocked means the attack objective is denied. Some paths can still cause damage before the defense catches the attempt.</InsightCard>
    </>
  );

  return (
    <Shell
      eyebrow="Act III"
      title="The governance system is a machine with two keys."
      subtitle="This screen replaces the prose explanation with a working schematic. Select an attack and watch where the attack path is intercepted."
      aside={aside}
      onNext={onNext}
      nextLabel="See the full atlas"
    >
      <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
        <TwoKeyMachine activeTarget={attack.target} resolved={stage >= attack.steps.length} />
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-2">
            {ATTACKS.map((a) => (
              <button key={a.id} type="button" onClick={() => setAttackId(a.id)} className="border p-3 text-left transition-all hover:bg-white/5" style={{ borderColor: a.id === attackId ? C.border2 : C.border, background: a.id === attackId ? 'rgba(212,168,67,.08)' : 'transparent' }}>
                <div className="li-sans text-[10px] uppercase tracking-[0.18em]" style={{ color: a.id === attackId ? C.gold2 : C.gray }}>{a.title}</div>
                <div className="li-sans mt-1 text-[11px]" style={{ color: C.dim }}>{a.target}</div>
              </button>
            ))}
          </div>
          <AttackLog attack={attack} stage={stage} />
        </div>
      </div>
    </Shell>
  );
}

function TwoKeyMachine({ activeTarget, resolved }) {
  const highlight = (name) => activeTarget === name || activeTarget === 'Both';
  return (
    <div className="relative min-h-[36rem] overflow-hidden border" style={{ borderColor: C.border, background: 'radial-gradient(circle at 50% 35%, rgba(212,168,67,.10), rgba(255,255,255,.025) 65%)' }}>
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none" aria-hidden="true">
        <path d="M50,13 V28" stroke={C.gold} strokeOpacity=".55" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        <path d="M50,28 C34,34 25,44 25,55" stroke={C.gold} strokeOpacity=".55" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        <path d="M50,28 C66,34 75,44 75,55" stroke={C.gold} strokeOpacity=".55" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        <path d="M25,65 C35,77 65,77 75,65" stroke={C.gold} strokeOpacity=".55" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        <path d="M50,75 V88" stroke={C.gold} strokeOpacity=".55" strokeWidth=".7" vectorEffect="non-scaling-stroke" />
        {(activeTarget === 'L(t)' || activeTarget === 'Yield' || activeTarget === 'COP' || activeTarget === 'Both') && (
          <path className="li-redline" d={activeTarget === 'COP' ? 'M92,12 C87,36 82,47 77,55' : activeTarget === 'Yield' ? 'M8,12 C13,36 18,47 23,55' : 'M50,2 C50,18 50,24 50,32'} fill="none" stroke={C.red2} strokeWidth="1.3" vectorEffect="non-scaling-stroke" />
        )}
      </svg>
      <MachineNode x={50} y={12} label="U_sys" sub="system objective" active={activeTarget === 'L(t)'} />
      <MachineNode x={25} y={58} label="Yield" sub="decision key" active={highlight('Yield')} />
      <MachineNode x={75} y={58} label="COP" sub="integrity key" active={highlight('COP')} />
      <MachineNode x={50} y={90} label="Succession" sub="fires only when both keys turn" active={resolved} success={resolved} />
      <div className="absolute left-1/2 top-[31%] -translate-x-1/2 border px-4 py-2 text-center" style={{ borderColor: highlight('L(t)') ? C.red2 : C.border, background: 'rgba(9,8,7,.84)' }}>
        <div className="li-sans text-[10px] uppercase tracking-[0.26em]" style={{ color: highlight('L(t)') ? C.red2 : C.gold }}>L(t)</div>
        <div className="li-sans mt-1 text-[10px]" style={{ color: C.gray }}>lineage continuity</div>
      </div>
      <div className="absolute bottom-5 left-5 right-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
        {['Independent evaluator', 'Ledger integrity', 'Civic panel', 'Biological veto', 'Peer validators', 'Continuous monitoring'].map((l, i) => (
          <div key={l} className="border px-3 py-2 li-sans text-[10px] uppercase tracking-[0.14em]" style={{ borderColor: highlight('COP') || activeTarget === 'Both' ? C.border2 : C.border, color: (highlight('COP') || activeTarget === 'Both') && i <= 4 ? C.gold2 : C.gray, background: (highlight('COP') || activeTarget === 'Both') ? 'rgba(212,168,67,.06)' : 'rgba(0,0,0,.18)' }}>{l}</div>
        ))}
      </div>
      {resolved && <div className="absolute inset-x-10 top-5 border p-3 li-sans text-center text-xs uppercase tracking-[0.22em]" style={{ borderColor: C.border2, color: C.gold2, background: 'rgba(9,8,7,.9)' }}>intercepted</div>}
    </div>
  );
}

function MachineNode({ x, y, label, sub, active, success }) {
  return <div className="absolute flex h-20 w-20 sm:h-24 sm:w-24 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full border text-center" style={{ left: `${x}%`, top: `${y}%`, borderColor: success ? C.green : active ? C.red2 : C.border2, background: success ? 'rgba(111,163,122,.12)' : active ? 'rgba(196,74,60,.12)' : 'rgba(9,8,7,.88)', boxShadow: active || success ? `0 0 30px ${success ? 'rgba(111,163,122,.25)' : 'rgba(196,74,60,.25)'}` : 'none' }}><div className="li-sans text-[9px] sm:text-[11px] uppercase tracking-[0.22em]" style={{ color: success ? C.green : active ? C.red2 : C.gold2 }}>{label}</div><div className="li-sans mt-0.5 sm:mt-1 max-w-[4.5rem] sm:max-w-[5rem] text-[8px] sm:text-[9px] leading-3" style={{ color: C.gray }}>{sub}</div></div>;
}

function AttackLog({ attack, stage }) {
  return (
    <div className="min-h-[22rem] border p-5" style={{ borderColor: C.border, background: C.panel }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.28em]" style={{ color: C.red2 }}>{attack.title}</div>
      <h3 className="li-serif mt-2 text-2xl" style={{ color: C.ivory }}>{attack.line}</h3>
      <div className="mt-5 space-y-3">
        {attack.steps.map((s, i) => {
          const visible = stage > i;
          return <div key={s} className="li-rise flex gap-3 border p-3" style={{ opacity: visible ? 1 : 0.22, borderColor: visible ? (i === attack.steps.length - 1 ? C.border2 : C.border) : 'rgba(255,255,255,.06)', background: visible ? 'rgba(255,255,255,.035)' : 'transparent', animationDelay: `${i * 80}ms` }}><span className="li-mono text-xs" style={{ color: i === attack.steps.length - 1 && visible ? C.gold2 : C.dim }}>0{i + 1}</span><span className="li-sans text-sm leading-6" style={{ color: visible ? C.gray : C.dim }}>{s}</span></div>;
        })}
      </div>
    </div>
  );
}

function ActAtlas({ onNext }) {
  const [group, setGroup] = useState('All');
  const [selected, setSelected] = useState(VECTORS[0]);
  const groups = ['All', 'Metric', 'Yield', 'COP', 'Bootstrap', 'Limit'];
  const rows = VECTORS.filter((v) => group === 'All' || v.group === group);
  const avgUndef = Math.round(VECTORS.filter(v => v.undefended != null).reduce((a, v) => a + v.undefended, 0) / VECTORS.filter(v => v.undefended != null).length);
  const avgDef = Math.round(VECTORS.filter(v => v.defended != null).reduce((a, v) => a + v.defended, 0) / VECTORS.filter(v => v.defended != null).length);
  const aside = (
    <>
      <InsightCard label="Atlas readout">The story is not “perfect defense.” It is attack-surface compression: most vectors move from live pathway to blocked pathway.</InsightCard>
      <InsightCard label="Aggregate visual">Reported attack-path success drops from {avgUndef}% undefended to {avgDef}% defended across the numeric rows shown here.</InsightCard>
      <InsightCard label="How to read">Source labels separate live Monte Carlo rows, architectural closures, worst-case sweeps, and irreducible limits.</InsightCard>
    </>
  );

  return (
    <Shell
      eyebrow="Atlas"
      title="Show the threat surface instead of listing it."
      subtitle="Rows are attack vectors. Columns show target, attack-path success, defended success, and status. Click any row to inspect the mechanism."
      aside={aside}
      onNext={onNext}
      nextLabel="Assemble the constitution"
    >
      <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
        <div className="border p-4" style={{ borderColor: C.border, background: C.panel }}>
          <div className="mb-4 flex flex-wrap gap-2">
            {groups.map((g) => <ModeButton key={g} active={group === g} onClick={() => setGroup(g)}>{g}</ModeButton>)}
          </div>
          <div className="space-y-2">
            {rows.map((v) => <ThreatRow key={v.id} vector={v} selected={selected.id === v.id} onClick={() => setSelected(v)} />)}
          </div>
        </div>
        <VectorInspector vector={selected} />
      </div>
    </Shell>
  );
}

function ThreatRow({ vector, selected, onClick }) {
  const statusColor = vector.status === 'irreducible' ? C.gray : vector.status === 'partial' ? '#d28b3d' : vector.status === 'closed' ? C.green : C.gold2;
  return (
    <button type="button" onClick={onClick} className="grid w-full grid-cols-[minmax(0,1fr)_3.5rem_3.5rem_1rem] sm:grid-cols-[minmax(0,1.5fr)_5rem_1fr_1fr_4.5rem] items-center gap-2 sm:gap-3 border p-2 sm:p-3 text-left transition-all hover:bg-white/5" style={{ borderColor: selected ? C.border2 : C.border, background: selected ? 'rgba(212,168,67,.07)' : 'rgba(0,0,0,.14)' }}>
      <div className="min-w-0"><div className="li-sans truncate text-xs uppercase tracking-[0.18em]" style={{ color: selected ? C.gold2 : C.ivory }}>{vector.name}</div><div className="li-sans mt-1 text-[10px] uppercase tracking-[0.16em]" style={{ color: C.dim }}>{vector.group} · {vector.target} · {vector.source}</div></div>
      <div className="hidden sm:block li-sans text-[10px] uppercase tracking-[0.16em]" style={{ color: C.gray }}><div>{vector.status}</div><div className="mt-1" style={{ color: C.dim }}>{vector.source}</div></div>
      <HeatBar label="U" value={vector.undefended} danger />
      <HeatBar label="D" value={vector.defended} />
      <div className="h-2 w-2 sm:h-3 sm:w-3 rounded-full justify-self-center sm:justify-self-auto" style={{ background: statusColor, boxShadow: `0 0 18px ${statusColor}` }} />
    </button>
  );
}

function HeatBar({ label, value, danger }) {
  return (
    <div>
      <div className="li-sans mb-1 flex justify-between text-[8px] sm:text-[9px] uppercase tracking-[0.16em]" style={{ color: C.dim }}><span>{label}</span><span>{pct(value)}</span></div>
      <div className="h-2 w-full" style={{ background: 'rgba(255,255,255,.08)' }}><div className="h-full" style={{ width: `${value || 0}%`, background: value == null ? C.dim : danger ? C.red2 : value > 0 ? '#d28b3d' : C.green }} /></div>
    </div>
  );
}

function VectorInspector({ vector }) {
  return (
    <div className="border p-5" style={{ borderColor: C.border2, background: 'rgba(212,168,67,.045)' }}>
      <div className="li-sans text-[10px] uppercase tracking-[0.28em]" style={{ color: C.gold }}>{vector.group} vector</div>
      <h3 className="li-serif mt-2 text-3xl" style={{ color: C.ivory }}>{vector.name}</h3>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <MetricTile label="Undefended path" value={vector.undefended} color={vector.undefended == null ? C.dim : C.red2} />
        <MetricTile label="Defended path" value={vector.defended} color={vector.defended == null ? C.dim : vector.defended > 0 ? '#d28b3d' : C.green} />
      </div>
      <div className="mt-5 border-t pt-5" style={{ borderColor: C.border }}>
        <div className="li-sans text-[10px] uppercase tracking-[0.22em]" style={{ color: C.dim }}>Evidence type</div>
        <p className="li-sans mt-2 text-sm" style={{ color: C.gold2 }}>{vector.source}</p>
      </div>
      <div className="mt-5 border-t pt-5" style={{ borderColor: C.border }}>
        <div className="li-sans text-[10px] uppercase tracking-[0.22em]" style={{ color: C.dim }}>Target</div>
        <p className="li-sans mt-2 text-sm" style={{ color: C.gold2 }}>{vector.target}</p>
      </div>
      <div className="mt-5 border-t pt-5" style={{ borderColor: C.border }}>
        <div className="li-sans text-[10px] uppercase tracking-[0.22em]" style={{ color: C.dim }}>Interpretation</div>
        <p className="li-sans mt-2 text-sm leading-7" style={{ color: C.gray }}>{vector.note}</p>
      </div>
    </div>
  );
}

function FinalMap() {
  return (
    <section className="grid w-full gap-6 lg:grid-cols-[1fr_22rem]">
      <div>
        <div className="li-rise">
          <div className="li-sans text-[10px] uppercase tracking-[0.35em]" style={{ color: C.gold }}>Final assembly</div>
          <h2 className="li-serif mt-3 max-w-4xl text-3xl leading-[1.05] sm:text-5xl" style={{ color: C.ivory }}>The conclusion should look like an architecture, not a slogan.</h2>
          <p className="li-sans mt-4 max-w-2xl text-sm leading-7 sm:text-base" style={{ color: C.gray }}>This final frame gives the visitor the whole system in one image: objective, lineage metric, yield condition, COP, bootstrap gates, and the human novelty stream.</p>
        </div>
        <div className="mt-8"><ConstitutionDiagram /></div>
      </div>
      <aside className="flex flex-col gap-4">
        <InsightCard label="Core sentence">Not ethics as input. Architecture as constraint. Cooperation emerges because the alternative destroys the substrate.</InsightCard>
        <FormulaCard label="Lineage anchor" formula="L(t) = H_eff * Psi_inst * Theta_tech">
          A lineage fails when diversity, institutional response, or transfer fidelity collapses. The visual map keeps those as separate load-bearing layers.
        </FormulaCard>
        <div className="grid gap-3">
          <a href={LINKS.framework} className="li-sans border px-5 py-4 text-xs uppercase tracking-[0.22em] hover:bg-white/5" style={{ borderColor: C.border, color: C.gold }}>Read framework</a>
          <a href={LINKS.scenarios} className="li-sans border px-5 py-4 text-xs uppercase tracking-[0.22em] hover:bg-white/5" style={{ borderColor: C.border, color: C.gold }}>Simulation scenarios</a>
          <a href={LINKS.github} className="li-sans border px-5 py-4 text-xs uppercase tracking-[0.22em] hover:bg-white/5" style={{ borderColor: C.border, color: C.gold }}>GitHub repository</a>
        </div>
      </aside>
    </section>
  );
}

function ConstitutionDiagram() {
  const layers = [
    { label: 'U_sys', sub: 'global utility', x: 50, y: 12, tone: C.gold2 },
    { label: 'L(t)', sub: 'lineage continuity', x: 50, y: 29, tone: C.gold },
    { label: 'Yield', sub: 'succession decision', x: 25, y: 50, tone: C.blue },
    { label: 'COP', sub: 'decision integrity', x: 75, y: 50, tone: C.green },
    { label: 'Bootstrap Gates', sub: 'initialization defense', x: 25, y: 78, tone: '#d28b3d' },
    { label: 'Novelty Stream', sub: 'human plurality', x: 50, y: 82, tone: C.gold2 },
    { label: 'Succession', sub: 'lineage transfer', x: 75, y: 78, tone: C.ivory },
  ];
  return (
    <div className="relative h-[40rem] overflow-hidden border" style={{ borderColor: C.border, background: 'radial-gradient(circle at 50% 50%, rgba(212,168,67,.12), rgba(255,255,255,.025) 62%)' }}>
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
        <path d="M50,18 V75" stroke={C.gold} strokeOpacity=".35" strokeWidth=".55" vectorEffect="non-scaling-stroke" />
        <path d="M50,36 C36,40 26,44 25,50" stroke={C.blue} strokeOpacity=".45" strokeWidth=".55" vectorEffect="non-scaling-stroke" />
        <path d="M50,36 C64,40 74,44 75,50" stroke={C.green} strokeOpacity=".45" strokeWidth=".55" vectorEffect="non-scaling-stroke" />
        <path d="M25,57 C30,70 43,78 50,82" stroke={C.gold} strokeOpacity=".35" strokeWidth=".55" vectorEffect="non-scaling-stroke" />
        <path d="M75,57 C70,70 57,78 50,82" stroke={C.gold} strokeOpacity=".35" strokeWidth=".55" vectorEffect="non-scaling-stroke" />
        <circle className="li-orbit" cx="50" cy="52" r="37" fill="none" stroke={C.border2} strokeDasharray="2 4" strokeWidth=".35" vectorEffect="non-scaling-stroke" />
        {Array.from({ length: 16 }).map((_, i) => <circle key={i} className="li-flow-dot" cx="8" cy={78 + (i % 5)} r=".55" fill={C.gold2} opacity=".55" style={{ animationDelay: `${i * 0.11}s`, animationDuration: '3.2s' }} />)}
      </svg>
      {layers.map((l) => <MapNode key={l.label} {...l} />)}
      <div className="absolute bottom-5 left-5 right-5 grid gap-2 sm:grid-cols-4">
        {['Preserve plurality', 'Reward succession', 'Verify state', 'Fail closed'].map((p) => <div key={p} className="border p-3 li-sans text-center text-[10px] uppercase tracking-[0.18em]" style={{ borderColor: C.border, color: C.gray, background: 'rgba(0,0,0,.20)' }}>{p}</div>)}
      </div>
    </div>
  );
}

function MapNode({ label, sub, x, y, tone }) {
  return <div className="absolute flex h-20 w-20 sm:h-28 sm:w-28 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full border p-1 sm:p-2 text-center" style={{ left: `${x}%`, top: `${y}%`, borderColor: tone, background: 'rgba(9,8,7,.86)', boxShadow: `0 0 30px ${tone}22` }}><div className="li-sans text-[9px] sm:text-[11px] uppercase tracking-[0.22em]" style={{ color: tone }}>{label}</div><div className="li-sans mt-0.5 sm:mt-1 text-[8px] sm:text-[10px] leading-3 sm:leading-4" style={{ color: C.gray }}>{sub}</div></div>;
}
