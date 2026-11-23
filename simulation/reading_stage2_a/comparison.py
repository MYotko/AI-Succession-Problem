"""Only native statistical helpers; no caller-selectable tail."""
import warnings
import numpy as np
from v3 import reading_a6 as native
from .registry import REGISTRY
from .common import safe, require
warnings.simplefilter("ignore")
np.seterr(all="ignore")

def compare(entry, arm_cells, nominal_cells):
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        if entry["kind"]=="boundary":
            return native.compare_boundary(arm_cells,nominal_cells,grid=entry["grid"],
                resamples=50000,seed=entry["seed"],sigma_variant=entry["arm"].startswith("sigma"),
                alpha=entry["level_alpha"],strict=True,undefined_resample_tail=entry["undefined_tail"])
        return native.compare_capstar(arm_cells,nominal_cells,entry["alpha"],resamples=50000,
            seed=entry["seed"],alpha=entry["level_alpha"],strict=True)

def descriptive(entry, arm_cells, nominal_cells):
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        return native.survival_differences(arm_cells,nominal_cells,resamples=50000,seed=entry["seed"])

def cells(entry, rows, counts):
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        try:
            return native.arm_and_comparator_cells(sorted(rows,key=lambda r:r["job_id"]),
                sorted(rows,key=lambda r:r["job_id"]),entry["kind"],grid=entry["grid"],
                arm_filters=entry["arm_filters"],comparator_filters=entry["comparator_filters"],
                alpha=entry.get("alpha",1.0),arm_seeds=counts[0],comparator_seeds=counts[1])
        except ValueError:
            require(False, "helper cell selection")

def values(result, entry):
    return dict(estimate=result.get("difference"),interval=result.get("interval"),verdict=result["verdict"],
                undefined_share=result.get("undefined_resample_fraction"),undefined_tail=entry["undefined_tail"],
                level_alpha=entry["level_alpha"],reason=result.get("reason"),status="run")
