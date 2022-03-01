import autoreload

import numpy as np
import scipy as sp
import pandas as pd
import datadotworld as dw

import worldly

c = worldly.countries()
quiz = worldly.quiz()

quiz.qna(
    'population',
    filter_out=lambda x: x == 0,
    group_by=lambda x: int(np.log10(x)),
    question=lambda d, gb: f"{d} between {10 ** (gb - 1):,} and {10 ** (gb):,}",
)

quiz.qna(
    'area',
    filter_out=lambda x: x == 0,
    group_by=lambda x: int(np.log10(x)),
    question=lambda d, gb: f"{d} between {10 ** (gb - 1):,} and {10 ** (gb):,}",
)
