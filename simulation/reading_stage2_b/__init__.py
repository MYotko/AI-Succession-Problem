"""The A10 stage 2 sealed reader, build B: a separately identified analysis package.

It lives outside ``simulation/v3`` and holds no top-level ``simulation/*.py``, so
the instrument's code identity is unchanged by it (D:52). It imports ``v3``
modules read-only and never writes into a run root or any other input.

A1.4, A2.8: warnings are silenced at process start, before any NumPy-using
module is imported, so that no outcome-dependent warning line can reach a
terminal or a log. One numerical-library thread is configured before NumPy
loads (D:53).
"""
import os
import sys
import warnings

warnings.simplefilter("ignore")
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
