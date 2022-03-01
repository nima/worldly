import locale
import logging

import numpy as np
import pandas as pd

from worldly.dimensions import Dimension

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def countries():
    return Dimension.countries

class Quiz:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._dimensions = {}

    def __getitem__(self, name):
        return self._dimensions[name].dataframe[name]

    def extend(self, name, dimension):
        """
        :param name: Name of the new dimension
        :type name: str
        :param dimension: The Dimension itself
        :type dimension: Dimension
        """
        if dimension is not None:
            self._dimensions[name] = dimension
        else:
            Quiz.logger.warning("Refusing to add empty dimension:`%s`", name)

    def country(self, name):
        try:
            return self.df.loc[name]
        except KeyError:
            Quiz.logger.error("No such country:%s; known countries are:%s", name, ", ".join(self.df.index))

    @property
    def df(self):
        return pd.concat(map(lambda d: d.dataframe, self._dimensions.values()), axis=1)


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

    name = 'coastline'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_costline', cleaner=('km', np.int64))
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column='km',
        unit='km', dtype=pd.Int64Dtype(),
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
        unit='m', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'area'
    dataset = Dimension.dataset('samayo/country-names', 'country_surface_area', cleaner=('area', np.int64))
    dimension = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='km.km', dtype=pd.Int64Dtype(),
    )
    quiz.extend(name, dimension)

    name = 'density'
    dimension = Dimension(
        name=name,
        key='country', column=name,
        datacls='dataseries', data=quiz['population']/quiz['area'],
        unit='count/km/km', dtype=pd.Float32Dtype(),
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