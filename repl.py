import autoreload

import numpy as np
import scipy as sp
import pandas as pd
import datadotworld as dw
import collections


class Dimension:
    DS = {}

    @classmethod
    def _dataset(cls, uri, table):
        if uri not in cls.DS:
            cls.DS[uri] = dw.load_dataset(uri, auto_update=True)

        return cls.DS[uri].tables[table]


    def __init__(self, name, dataset, table, key, value, unit=None, normalizer=lambda _: _):
        DimensionCls = collections.namedtuple(name.capitalize(), ["norm", "raw", "unit"])
        self._ds = dict(map(
            lambda od: (od[key], DimensionCls(norm=normalizer(od[value]), raw=od[value], unit=unit)),
            self._dataset(dataset, table) # List of OrderedDict
        ))

    def __call__(self, country=None):
        return self._ds if country is None else self._ds.get(country)


dimPopulation = Dimension(
    name='population',
    dataset='edmadrigal/world-population-json', table='worldpopulation',
    key='country', value='population', unit='count',
    normalizer=lambda raw: np.around(np.log(raw), 1),
)

dimContinent = Dimension(
    name='continent',
    dataset='samayo/country-names', table='country_continent',
    key='country', value='continent',
)

dimCoastline = Dimension(
    name='coastline',
    dataset='samayo/country-names', table='country_by_costline',
    key='country', value='km', unit='kilometers'
)
