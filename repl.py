import autoreload

import random

import numpy as np
import scipy as sp
import pandas as pd
#from Levenshtein import distance as ld
import datadotworld as dw

from operator import mul
from functools import reduce

import worldly

def countries():
    return worldly.dimensions.Dimension.countries

print("""
To play a round:
>>> worldly.play.ask(*worldly.play.aRound())

""")
