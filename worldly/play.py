import locale
import random

import numpy as np
import pandas as pd

# from Levenshtein import distance as ld

from worldly.dimensions import Dimension, DataDotWorld
from worldly.questions import Question
from worldly import quiz


def quiz_bank():
    qz = quiz.Quiz(
        [
            Dimension(
                name="landlocked",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_landlocked", "land_locked"
                ),
                dtype=pd.BooleanDtype,
            ),
            Dimension(
                name="continent",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_continent", "continent"
                ),
                dtype=pd.CategoricalDtype,
            ),
            Dimension(
                name="region",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_region_in_world", "region"
                ),
                dtype=pd.CategoricalDtype,
            ),
            Dimension(
                name="government",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_government_type", "government"
                ),
                dtype=pd.CategoricalDtype,
            ),
            Dimension(
                name="population",
                data=DataDotWorld.table(
                    "edmadrigal/world-population-json", "worldpopulation", "population"
                ),
                dtype=pd.Int64Dtype,
            ),
            Dimension(
                name="area",
                data=DataDotWorld.table(
                    "samayo/country-names",
                    "country_surface_area",
                    "area",
                    cast=np.int64,
                ),
                dtype=pd.Int64Dtype,
                unit="kilometers square",
            ),
            Dimension(
                name="coastline",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_by_costline", "km", cast=np.int64
                ),
                dtype=pd.Int64Dtype,
                unit="kilometers",
            ),
            Dimension(
                name="elevation",
                data=DataDotWorld.table(
                    "samayo/country-names",
                    "country_by_elevation",
                    "average",
                    cast=lambda d: np.int64(locale.atof(d.strip("m"))),
                ),
                dtype=pd.Int64Dtype,
                unit="meters",
            ),
            Dimension(
                name="independence",
                data=DataDotWorld.table(
                    "samayo/country-names", "country_independence_date", "independence"
                ),
                dtype=pd.Int64Dtype,
                unit="year",
            ),
            Dimension(
                name="gdp",
                data=DataDotWorld.table(
                    "worldbank/gdp-ranking", "gdp", "us_dollars", index="economy"
                ),
                dtype=pd.Int64Dtype,
                unit="millions of UD dollars",
            ),
        ]
    )

    qz.add_dimension(
        Dimension(
            name="density",
            data=qz.population.series / qz.area.series,
            unit="people per squared kilometer",
            dtype=pd.Int64Dtype,
        ),
    )

    return qz


def someQuestions():

    range = lambda n: f"{10 ** n:,} and {10 ** (n + 1):,}"

    return [
        Question(
            dimension="population",
            question=lambda d, gb, u: f"With a {d} between {range(gb)}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        Question(
            dimension="area",
            question=lambda d, gb, u: f"With a {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        Question(
            dimension="density",
            question=lambda d, gb, u: f"With a {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        Question(
            dimension="coastline",
            question=lambda d, gb, u: f"With {d} stretching between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        Question(
            dimension="elevation",
            question=lambda d, gb, u: f"With an average {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        Question(
            dimension="independence",
            question=lambda d, gb, u: f"Declared {d} in {gb}",
        ),
        Question(
            dimension="region",
            question=lambda d, gb, u: f"Situated in the {d} {gb}",
        ),
        Question(
            dimension="landlocked",
            question=lambda d, gb, u: f"{'Is' if gb else 'Is not'} a land-locked country",
        ),
        Question(
            dimension="government",
            question=lambda d, gb, u: f"Ruled by a {gb} {d}",
        ),
        Question(
            dimension="gdp",
            question=lambda d, gb, u: f"GDP ranging from {range(gb)}, in {u}",
            group_by=lambda x: int(np.log10(x)),
        ),
    ]


def aRound():
    myQuestions = someQuestions()
    random.shuffle(myQuestions)
    myQuiz = quiz_bank()

    theQuestions, theAnswer = [], None
    for q, a in myQuiz.qna(myQuestions):
        theQuestions.append(f"{q}? ({len(a.index)} answers)")
        theAnswer = ", ".join(a.index)

    return theQuestions, theAnswer


def ask(theQuestions, theAnswer) -> bool:
    for aQuestion in theQuestions:
        anAnswer = input(f"{aQuestion}? ")
        if anAnswer.lower() == theAnswer.lower():
            print(f"Correct!")
            return True
        else:
            print(f"Wrong")
            # print(f"Wrong (hint: LD={ld(anAnswer.lower(), theAnswer.lower())})")

    return False
