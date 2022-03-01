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
                table, uri, ', '.join(list(worldly.Dimension.DS['samayo/country-names'].tables)),
            )

        return None


    @classmethod
    @property
    def countries(cls):
        return list(map(lambda od: od['country'], cls.dataset('samayo/country-names', 'countries')))

    def __init__(self, name, data, key, value, numeric=False, datacls='dataset', unit=None, cleaner=lambda _: _):
        self._unit = unit

        if datacls == 'dataset':
            self._ds = dict(map(lambda od: (od[key], cleaner(od[value])), data))
            df = pd.DataFrame.from_dict(self._ds, columns=[name], orient='index')
        elif datacls == 'dataseries':
            self._ds = {}
            df = pd.DataFrame(index=data.index, data=data, columns=[value])

        df.index.name = key
        if numeric: df[name] = pd.to_numeric(df[name])

        self._df = df[df.index.isin(Dimension.countries)]


    @property
    def dataframe(self):
        return self._df

    def __call__(self, country=None):
        return self._df if country is None else self._df[self._df.index==country]

def countries():
    return Dimension.countries

dimensions = {}
def df():
    name = 'continent'
    dataset = Dimension.dataset('samayo/country-names', 'country_continent')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value=name,
    )

    name = 'region'
    dataset = Dimension.dataset('samayo/country-names', 'country_region_in_world')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value=name,
    )

    name='population'
    dataset = Dimension.dataset('edmadrigal/world-population-json', 'worldpopulation')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value=name,
        unit='count', numeric=True,
    )

    name = 'coastline'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_costline')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value='km',
        unit='km', numeric=True,
    )

    name = 'elevation'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_elevation')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value='average',
        cleaner=lambda raw: locale.atof(raw.strip('m')), # 1,234m -> 1234
        unit='m', numeric=True,
    )

    name = 'area'
    dataset = Dimension.dataset('samayo/country-names', 'country_surface_area')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', value=name,
        unit='km.km', numeric=True,
    )

    name = 'density'
    dimensions[name] = Dimension(
        name=name,
        key='country', value=name,
        datacls='dataseries', data=dimensions['population'].dataframe['population'] / dimensions['area'].dataframe['area'],
        unit='count/km/km', numeric=True,
    )

    return pd.concat(map(lambda d: d.dataframe, dimensions.values()), axis=1)

