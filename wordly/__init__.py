import numpy as np
import scipy as sp
import pandas as pd
import datadotworld as dw

import collections
import logging
import locale


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class Dimension:
    DS = {}
    logger = logging.getLogger(__name__)

    @classmethod
    def dataset(cls, uri, table):
        if uri not in cls.DS:
            cls.DS[uri] = dw.load_dataset(uri, auto_update=True)

        ds = cls.DS[uri]
        try:
            return ds.tables[table]
        except KeyError:
            cls.logger.error(
                "No table:`%s` in dataset:`%s`, did you mean one of `%s`?",
                table, uri, ', '.join(list(wordly.Dimension.DS['samayo/country-names'].tables)),
            )

        return None


    @classmethod
    @property
    def countries(cls):
        return list(map(lambda od: od['country'], cls.dataset('samayo/country-names', 'countries')))

    def __init__(self, name, dataset, key, value, numeric=False, unit=None, cleaner=lambda _: _):
        self._unit = unit
        DimensionCls = collections.namedtuple(name.capitalize(), ["norm", "raw"])
        self._ds = dict(map(
            lambda od: (od[key], DimensionCls(norm=cleaner(od[value]), raw=od[value])),
            dataset,
        ))

        df = pd.DataFrame.from_dict(self._ds, orient='index')
        if numeric: df['norm'] = pd.to_numeric(df['norm'])
        df = df.drop(['raw'], axis=1)
        df = df.rename(columns=dict(norm=name))

        self._df = df[df.index.isin(Dimension.countries)]


    @property
    def dataframe(self):
        return self._df

    def __call__(self, country=None):
        return self._df if country is None else self._df[self._df.index==country]

def countries():
    return Dimension.countries

def df():
    dimensions = []

    dsuri = 'samayo/country-names'
    table = 'country_continent'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='continent', dataset=dataset,
            key='country', value='continent',
        )
    )

    dsuri = 'samayo/country-names'
    table = 'country_region_in_world'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='region', dataset=dataset,
            key='country', value='region',
        )
    )

    dsuri ='edmadrigal/world-population-json'
    table='worldpopulation'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='population', dataset=dataset,
            key='country', value='population',
            unit='count', numeric=True,
        )
    )

    dsuri = 'samayo/country-names'
    table = 'country_by_costline'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='coastline', dataset=dataset,
            key='country', value='km',
            unit='km', numeric=True,
        )
    )

    dsuri = 'samayo/country-names'
    table = 'country_by_elevation'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='elevation', dataset=dataset,
            key='country', value='average',
            cleaner=lambda raw: locale.atof(raw.strip('m')), # 1,234m -> 1234
            unit='m', numeric=True,
        )
    )

    dsuri = 'samayo/country-names'
    table = 'country_surface_area'
    dataset = Dimension.dataset(dsuri, table)
    if dataset: dimensions.append(
        Dimension(
            name='area', dataset=dataset,
            key='country', value='area',
            unit='km.km', numeric=True,
        )
    )

    return pd.concat(map(lambda d: d.dataframe, dimensions), axis=1)


