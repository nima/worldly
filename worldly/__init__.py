import locale
import logging
import random

import dataclasses
import numpy as np
import pandas as pd
import typing

from worldly.dimensions import Dimension

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def countries():
    return Dimension.countries


@dataclasses.dataclass
class Question:
    dimension: str
    question: str
    group_by: typing.Callable[typing.Any, typing.Any] = lambda _: _
    filter_out: typing.Callable[typing.Any, bool] = None


class Quiz:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._dimensions = {}

    def __getitem__(self, name):
        return self._dimensions[name].dataframe[name]

    def extend(self, name, dimension):
        """
        :param name: Name of the new name
        :type name: str
        :param dimension: The Dimension itself
        :type dimension: Dimension
        """
        if dimension is not None:
            self._dimensions[name] = dimension
        else:
            Quiz.logger.warning("Refusing to add empty name:`%s`", name)

    def country(self, name):
        try:
            return self.df().loc[name]
        except KeyError:
            Quiz.logger.error("No such country:%s; known countries are:%s", name, ", ".join(self.df.index))

    def df(self, dimension=None):
        if dimension is None:
            return pd.concat(map(lambda d: d.dataframe, self._dimensions.values()), axis=1)
        else:
            return self._dimensions[dimension].dataframe

    def qna(self, questions):
        qna = []
        for q in questions:
            # select the dimension's dataframe
            dimension = self._dimensions[q.dimension]
            df = dimension.dataframe.dropna()

            # if this is not the first question, limit the selection to the last question's answers
            if len(qna):
                _, whitelist = qna[-1]
                df = df[df.index.isin(whitelist.index)]
                if len(df) == 0: continue

            # filter out garbage
            if q.filter_out is not None:
                remove = df[q.filter_out(df[q.dimension])].index
                df = df.drop(remove)
                if len(df) == 0: continue

            # group by
            df['_'] = df[q.dimension].apply(q.group_by)
            group = random.sample(df['_'].to_list(), 1).pop()
            answers = df[df['_'] == group].drop(columns=['_'])

            # append the generated question and answer
            qna.append((q.question(q.dimension, group, dimension.unit), answers))

        return qna


def quiz():
    quiz = Quiz()

    name = 'continent'
    dataset = Dimension.dataset('samayo/country-names', 'country_continent')
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    quiz.extend(name, dimension)

    name = 'region'
    dataset = Dimension.dataset('samayo/country-names', 'country_region_in_world')
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    quiz.extend(name, dimension)

    name = 'population'
    dataset = Dimension.dataset('edmadrigal/world-population-json', 'worldpopulation')
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='count', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'area'
    dataset = Dimension.dataset('samayo/country-names', 'country_surface_area', cleaner=('area', np.int64))
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='kilometers square', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'density'
    dimension = Dimension(
        name=name,
        key='country', column=name,
        datacls='dataseries', data=quiz['population']/quiz['area'],
        unit='people per squared kilometer', dtype=pd.Float32Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'coastline'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_costline', cleaner=('km', np.int64))
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column='km',
        unit='kilometers', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'elevation'
    dataset = Dimension.dataset(
        'samayo/country-names', 'country_by_elevation',
        cleaner=('average', lambda d: np.int64(locale.atof(d.strip('m'))))
    )
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column='average',
        unit='meters', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'government'
    dataset = Dimension.dataset('samayo/country-names', 'country_government_type')
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )
    quiz.extend(name, dimension)

    name = 'independence'
    dataset = Dimension.dataset('samayo/country-names', 'country_independence_date')
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    return quiz
