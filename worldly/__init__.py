import numpy as np
import scipy as sp
import pandas as pd
import decimal as dc
import datadotworld as dw

import collections
import logging
import locale


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class Dimension:
    DS = {}
    logger = logging.getLogger(__name__)

    @classmethod
    def dataset(cls, uri, table, cleaner=None):
        if uri not in cls.DS:
            cls.DS[uri] = dw.load_dataset(uri, auto_update=True)

        ds = cls.DS[uri]
        try:
            ds = ds.tables[table]
        except KeyError:
            ds = None
            cls.logger.error(
                "No table:`%s` in dataset:`%s`, did you mean one of `%s`?",
                table, uri, ', '.join(list(Dimension.DS['samayo/country-names'].tables)),
            )

        if ds and cleaner:
            column, retype = cleaner
            for i, od in ((i, od) for i, od in enumerate(ds) if od[column]):
                ds[i].update({column: retype(od[column])})

        return ds


    @classmethod
    @property
    def countries(cls):
        return list(map(lambda od: od['country'], cls.dataset('samayo/country-names', 'countries')))

    def __init__(self, name, data, key, column, datacls='dataset', unit=None, dtype='object'):
        self._unit = unit

        if datacls == 'dataset':
            self._ds = dict(map(lambda od: (od[key], od[column]), data))
            df = pd.DataFrame.from_dict(self._ds, columns=[name], orient='index')
        elif datacls == 'dataseries':
            self._ds = {}
            df = pd.DataFrame(index=data.index, data=data, columns=[name])

        df.index.name = key
        df = df.astype(dtype={name: dtype})
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
        key='country', column=name,
    )

    name = 'region'
    dataset = Dimension.dataset('samayo/country-names', 'country_region_in_world')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )

    name='population'
    dataset = Dimension.dataset('edmadrigal/world-population-json', 'worldpopulation')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='count', dtype=pd.Int64Dtype(),
    )

    name = 'coastline'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_costline', cleaner=('km', np.int64))
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column='km',
        unit='km', dtype=pd.Int64Dtype(),
    )

    name = 'elevation'
    dataset = Dimension.dataset('samayo/country-names', 'country_by_elevation', cleaner=('average', lambda d: np.int64(locale.atof(d.strip('m')))))
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column='average',
        unit='m', dtype=pd.Int64Dtype(),
    )

    name = 'area'
    dataset = Dimension.dataset('samayo/country-names', 'country_surface_area', cleaner=('area', np.int64))
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        unit='km.km', dtype=pd.Int64Dtype(),
    )

    name = 'density'
    dimensions[name] = Dimension(
        name=name,
        key='country', column=name,
        datacls='dataseries', data=dimensions['population'].dataframe['population'] / dimensions['area'].dataframe['area'],
        unit='count/km/km', dtype=pd.Float32Dtype(),
    )

    name = 'government'
    dataset = Dimension.dataset('samayo/country-names', 'country_government_type')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column=name,
    )

    name = 'independence'
    dataset = Dimension.dataset('samayo/country-names', 'country_independence_date')
    if dataset: dimensions[name] = Dimension(
        name=name, data=dataset,
        key='country', column=name,
        dtype=pd.Int64Dtype(),
    )

    return pd.concat(map(lambda d: d.dataframe, dimensions.values()), axis=1)

