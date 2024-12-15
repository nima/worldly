import sys
import os

import importlib
import autoreload
from collections import defaultdict
from IPython import get_ipython

import random

import numpy as np
import scipy as sp
import pandas as pd

from operator import mul
from functools import reduce


################################################################################

import sys
import importlib
from IPython import get_ipython

_t0_imports = set()
_reloaded_modules = set()


def _initialize_t0_imports(*args, **kwargs):
    """Capture imports after the first cell is executed."""
    global _t0_imports
    if not _t0_imports:
        _t0_imports = set(sys.modules.keys())
        print(f"Captured {len(_t0_imports)} initial imports.")


_ipy = get_ipython()
if _ipy:
    _ipy.events.register("post_run_cell", _initialize_t0_imports)


def reload():
    """Reload modules imported after initialization."""
    global _t0_imports, _reloaded_modules
    if not _t0_imports:
        print("Initial imports not captured yet. Run a cell first.")
        return

    _t1_imports = set(sys.modules.keys())
    new_imports = _t1_imports - _t0_imports

    print(f"Found {len(new_imports)} new imports since initialization.")

    # Reload new imports
    for mod in new_imports:
        try:
            importlib.reload(sys.modules[mod])
            _reloaded_modules.add(mod)
            print(f"Reloaded: {mod}")
        except Exception as e:
            print(f"Could not reload {mod}: {e}")

    # Force reload submodules of explicitly imported modules
    for mod in _t0_imports:
        if mod.startswith("worldly"):
            try:
                importlib.reload(sys.modules[mod])
                _reloaded_modules.add(mod)
                print(f"Force reloaded: {mod}")
            except Exception as e:
                print(f"Could not force reload {mod}: {e}")


def resize():
    # pd.set_option("display.width", None)
    pd.set_option("display.width", os.get_terminal_size().columns)
    pd.set_option("display.max_columns", None)
    # pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_colwidth", os.get_terminal_size().columns - 32)


################################################################################


def countries():
    return worldly.dimensions.Dimension.countries


from Levenshtein import distance as ld
import datadotworld as dw
import worldly

print(
    """
# Try and set a reasonable terminal width
resize()

# Load modules and look at loaded dimension data
from worldly.play import quiz_bank
q = quiz_bank()
q.dimensions       # Review the set of dimensions available
q.area.group       # View the `area` dimension, numerically grouped (by logarithm)
q.continent.group  # View the `area` dimension, categorically grouped

# Merge dimensions
pd.merge(q.government.dataframe, q.continent.dataframe, left_index=True, right_index=True, how="inner")

# Play a game
worldly.play.ask(*worldly.play.aRound())

# Reload modules imported explicitly in the current repl session
reload()
"""
)
