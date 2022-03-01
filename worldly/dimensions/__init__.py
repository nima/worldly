import logging

import pandas as pd
import datadotworld as dw


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
