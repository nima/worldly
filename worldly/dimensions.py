import logging

import datadotworld as dw
import pandas as pd


class Dimension:
    COLLECTIONS = {}
    TABLES = {}
    logger = logging.getLogger(__name__)

    @classmethod
    def dataset(cls, uri, table, cleaner=None):
        key = f"{uri}.{table}"
        if key in cls.TABLES:
            return cls.TABLES[key]

        if uri in cls.COLLECTIONS:
            collection = cls.COLLECTIONS[uri]
        else:
            collection = dw.load_dataset(uri, auto_update=True)
            cls.COLLECTIONS[uri] = collection

        if table not in collection.tables:
            cls.logger.error(
                "No table:`%s` in dataset:`%s`, did you mean one of `%s`?",
                table, uri, ', '.join(list(collection.tables.keys())),
            )
            return None

        ds = collection.tables[table]

        if cleaner:
            column, retype = cleaner
            for i, od in ((i, od) for i, od in enumerate(ds) if od[column]):
                ds[i].update({column: retype(od[column])})

        cls.TABLES[key] = ds

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
        else:
            raise RuntimeError(f"Invalid parameter value `datacls:{datacls}`")

        df.index.name = key
        df = df.astype(dtype={name: dtype})
        df = df[df.index.isin(Dimension.countries)]
        self._df = df

    @property
    def unit(self):
        return self._unit

    @property
    def dataframe(self):
        return self._df

    def __call__(self, country=None):
        return self._df if country is None else self._df[self._df.index == country]
