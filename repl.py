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


    @classmethod
    @property
    def countries(cls):
        return list(map(lambda od: od['country'], cls._dataset('samayo/country-names', 'countries')))

    def __init__(self, name, dataset, table, key, value, unit=None, normalizer=lambda _: _):
        self._unit = unit
        DimensionCls = collections.namedtuple(name.capitalize(), ["norm", "raw"])
        self._ds = dict(map(
            lambda od: (od[key], DimensionCls(norm=normalizer(od[value]), raw=od[value])),
            self._dataset(dataset, table) # List of OrderedDict
        ))

        df = pd.DataFrame.from_dict(self._ds, orient='index').drop(['raw'], axis=1).rename(columns=dict(norm=name))
        self._df = df[df.index.isin(Dimension.countries)]


    def __call__(self, country=None):
        return self._df if country is None else self._df[self._df.index==country]


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

df = pd.concat([dimPopulation(), dimCoastline(), dimContinent()], axis=1)
