import locale
import random

import numpy as np
import pandas as pd

from worldly import quiz
from worldly import questions
from worldly import dimensions


def aQuiz():
    qz = quiz.Quiz()

    name = 'continent'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_continent')
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    qz.extend(name, dimension)

    name = 'region'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_region_in_world')
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    qz.extend(name, dimension)

    name = 'population'
    dataset = dimensions.Dimension.dataset('edmadrigal/world-population-json', 'worldpopulation')
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='count', dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    name = 'area'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_surface_area', cleaner=('area', np.int64))
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='kilometers square', dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    name = 'density'
    dimension = dimensions.Dimension(
        name=name,
        key='country', column=name,
        datacls='dataseries', data=qz['population'] / qz['area'],
        unit='people per squared kilometer', dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    name = 'coastline'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_by_costline', cleaner=('km', np.int64))
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column='km',
        unit='kilometers', dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    name = 'elevation'
    dataset = dimensions.Dimension.dataset(
        'samayo/country-names', 'country_by_elevation',
        cleaner=('average', lambda d: np.int64(locale.atof(d.strip('m'))))
    )
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column='average',
        unit='meters', dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    name = 'government'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_government_type')
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    qz.extend(name, dimension)

    name = 'independence'
    dataset = dimensions.Dimension.dataset('samayo/country-names', 'country_independence_date')
    dimension = dimensions.Dimension(
        name=name, data=dataset,
        key='country', column=name,
        dtype=pd.Int64Dtype(),
    )
    qz.extend(name, dimension)

    return qz


def someQuestions():

    range = lambda n: f"{10 ** n:,} and {10 ** (n + 1):,}"

    return [
        questions.Question(
            dimension='population',
            question=lambda d, gb, u: f"With a {d} between {range(gb)}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        questions.Question(
            dimension='area',
            question=lambda d, gb, u: f"With a {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        questions.Question(
            dimension='density',
            question=lambda d, gb, u: f"With a {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        questions.Question(
            dimension='coastline',
            question=lambda d, gb, u: f"With {d} stretching between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        questions.Question(
            dimension='elevation',
            question=lambda d, gb, u: f"With an average {d} between {range(gb)} {u}",
            group_by=lambda x: int(np.log10(x)),
            filter_out=lambda x: x == 0,
        ),
        questions.Question(
            dimension='independence',
            question=lambda d, gb, u: f"Declared {d} in {gb}",
        ),
        questions.Question(
            dimension='region',
            question=lambda d, gb, u: f"Situated in the {d} {gb}",
        ),
        questions.Question(
            dimension='government',
            question=lambda d, gb, u: f"Ruled by a {gb} {d}",
        ),
    ]

def aRound():
    myQuiz = aQuiz()
    myQuestions = someQuestions()
    random.shuffle(myQuestions)

    theQuestions, theAnswer = [], None
    for q, a in myQuiz.qna(myQuestions):
        theQuestions.append(f"Q. {q}? ({len(a.index)} answers)")
        theAnswer = ', '.join(a.index)

    return theQuestions, theAnswer
