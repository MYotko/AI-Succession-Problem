"""No exception text, traceback, warning or estimator value reaches a stream."""
import warnings
warnings.simplefilter("ignore")
import sys
from pathlib import Path
FILES=("reading.json","values.json","contributing_runs.json","incidence_per_run.json","LADDER.json","SEAL.json")

def main():
    args=None; out=None; was_new=False
    try:
        import argparse
        from .common import Refusal
        class Parser(argparse.ArgumentParser):
            def error(self,message):
                raise Refusal('command line arguments')
        parser=Parser(add_help=False)
        parser.add_argument("command",choices=("collect","verify","read"))
        parser.add_argument("--inputs",required=True)
        parser.add_argument("--out")
        parser.add_argument("--component",choices=("A10","A6","both"),default="both")
        args=parser.parse_args()
        from .common import require
        require(args.out is not None, "output argument required")
        out=Path(args.out) if args.out else Path(args.inputs).resolve().parent/"verify_refusal"
        was_new=not out.exists()
        from .reader import execute
        import numpy as np
        warnings.simplefilter("ignore"); np.seterr(all="ignore")
        execute(args.command,args.inputs,args.out,args.component)
        return 0
    except BaseException as exc:
        # Even imports and argument errors are contained; no exception string is emitted.
        try:
            from .common import Refusal,write
            from .refusal import label
            record=label(exc)
            if not isinstance(exc,Refusal): record["exception_class"]=type(exc).__name__
        except BaseException:
            record=dict(status='refused',phase='input_verification',reason_class='reader initialization failed',exception_class=type(exc).__name__)
            write=None
        unsafe=record['reason_class'] in ('output overlaps an input root','output inside reader checkout','output destination exists')
        if out is not None and was_new and not unsafe and write is not None:
            # A11.1: a read publishes only after all checks pass. A publication
            # fault preserves every partial file, including atomic-write temps.
            try:
                if args is None or args.command!='read':
                    for n in ("inputs.json","collection.json","verify.json"):
                        p=out/n
                        if p.is_file():p.unlink()
                write(out/"refusal.json",record,preserve_on_failure=args is not None and args.command=='read')
            except BaseException: pass
        print("REFUSED: "+record["phase"]+": "+record["reason_class"])
        if "exception_class" in record: print("EXCEPTION: "+record["exception_class"])
        return 1
if __name__=="__main__": sys.exit(main())
