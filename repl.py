import autoreload

import random

import numpy as np
import scipy as sp
import pandas as pd
import datadotworld as dw

import worldly

def countries():
    return worldly.dimensions.Dimension.countries

print("""
questions, answer = worldly.play.round()
""")
