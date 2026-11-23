"""Value-free check labels and invocation-local computation phase tracking."""
import ast
from contextvars import ContextVar
from functools import lru_cache, wraps
from pathlib import Path
from .common import Refusal

_state = ContextVar("stage2_refusal_phase", default=None)


def invocation(function):
    @wraps(function)
    def tracked(*args, **kwargs):
        state = {"phase": "input_verification"}
        token = _state.set(state)
        try:
            return function(*args, **kwargs)
        except BaseException as exc:
            exc.reading_phase = state["phase"]
            raise
        finally:
            _state.reset(token)
    return tracked


def computation_started():
    state = _state.get()
    if state is not None:
        state["phase"] = "after_computation_started"


@lru_cache(maxsize=1)
def check_messages():
    # Only literal check messages from our identity-bound source are public.
    # This is not an input-data scan. Dynamic labels below use schema names,
    # never an arbitrary value interpolated into a failure message.
    messages = set()
    for path in Path(__file__).parent.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                label = (node.args[1] if node.func.id == "require" and len(node.args) > 1 else
                         node.args[0] if node.func.id == "Refusal" and node.args else None)
                if isinstance(label, ast.Constant) and isinstance(label.value, str):
                    messages.add(label.value)
    return messages


def reason(exc):
    message = str(exc)
    if getattr(exc,'reading_phase',None)=='after_computation_started':
        permitted={'input changed','output target exists','reader source changed','excluded root inventory key','helper cell selection'}
        return message if isinstance(exc,Refusal) and message in permitted else 'computation failed'
    if isinstance(exc, Refusal):
        if message in check_messages():
            return message
        for prefix in ("input hash: ", "input changed: ", "frozen analysis target: ", "fixture write scope: "):
            if message.startswith(prefix):
                return prefix[:-2]
    # A native validator's literal message is safe; never emit its dynamic
    # f-string/format result, OS filename, missing input value or JSON excerpt.
    frames = []
    tb = exc.__traceback__
    while tb is not None:
        module = tb.tb_frame.f_globals.get("__name__", "")
        if module.startswith((__package__ + ".", "v3.")):
            frames.append((module, tb.tb_frame.f_code, tb.tb_lineno))
        tb = tb.tb_next
    if not isinstance(exc, (Refusal, OSError, KeyError, TypeError)) and frames:
        module, code, line = frames[-1]
        source = Path(code.co_filename).resolve()
        from v3.artifacts import ROOT
        native = ROOT.resolve()
        if module.startswith("v3.") and source.parent == native and source.suffix == ".py":
            for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Raise) and node.lineno <= line <= node.end_lineno:
                    call = node.exc
                    if isinstance(call, ast.Call) and call.args and isinstance(call.args[0], ast.Constant):
                        if isinstance(call.args[0].value, str) and message == call.args[0].value:
                            return message
    import json
    category = ("invalid JSON input" if isinstance(exc, json.JSONDecodeError) else
                "required file absent" if isinstance(exc, FileNotFoundError) else
                "file access denied" if isinstance(exc, PermissionError) else
                "file operation failed" if isinstance(exc, OSError) else
                "required key absent" if isinstance(exc, KeyError) else
                "invalid input type" if isinstance(exc, TypeError) else "check failed")
    return category


def label(exc):
    phase = getattr(exc, "reading_phase", "input_verification")
    if phase not in ("input_verification", "after_computation_started"):
        phase = "input_verification"
    return {"status": "refused", "reason_class": reason(exc), "phase": phase}
