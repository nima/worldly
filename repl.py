import autoreload

import random

import numpy as np
import scipy as sp
import pandas as pd
import datadotworld as dw

import worldly
from worldly import Question

questions = [
    Question(
        dimension='population',
        question=lambda d, gb, u: f"With a {d} between {10 ** gb:,} and {10 ** (gb+1):,}",
        group_by=lambda x: int(np.log10(x)),
        filter_out=lambda x: x == 0,
    ),
    Question(
        dimension='area',
        question=lambda d, gb, u: f"With a {d} between {10 ** (gb - 1):,} and {10 ** (gb):,} {u}",
        group_by=lambda x: int(np.log10(x)),
        filter_out=lambda x: x == 0,
    ),
    Question(
        dimension='density',
        question=lambda d, gb, u: f"With a {d} between {10 ** (gb - 1):,} and {10 ** (gb):,} {u}",
        group_by=lambda x: int(np.log10(x)),
        filter_out=lambda x: x == 0,
    ),
    Question(
        dimension='coastline',
        question=lambda d, gb, u: f"With {d} stretching between {10 ** (gb - 1):,} and {10 ** (gb):,} {u}",
        group_by=lambda x: int(np.log10(x)),
        filter_out=lambda x: x == 0,
    ),
    Question(
        dimension='elevation',
        question=lambda d, gb, u: f"With an average {d} between {10 ** (gb - 1):,} and {10 ** (gb):,} {u}",
        group_by=lambda x: int(np.log10(x)),
        filter_out=lambda x: x == 0,
    ),
    Question(
        dimension='independence',
        question=lambda d, gb, u: f"Declared {d} in {gb}",
    ),
    Question(
        dimension='region',
        question=lambda d, gb, u: f"Situated in the {d} {gb}",
    ),
    Question(
        dimension='government',
        question=lambda d, gb, u: f"Ruled by a {gb} {d}",
    ),
]

def quiz():
    quiz = worldly.quiz()

    random.shuffle(questions)
    for q, a in quiz.qna(questions):
        print(f"Q. {q}")
        answers = a.index
        print(f"A. {', '.join(a.index) if len(a.index) < 7 else ('(%d countries)' % len(a.index)) }")
        print()
