import logging

import datadotworld as dw
import pandas as pd


class DataDotWorld:
    COLLECTIONS = {}
    TABLES = {}
    logger = logging.getLogger(__name__)

    @classmethod
    def table(cls, uri, table, column, cast=lambda _: _, index="country"):
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
                table,
                uri,
                ", ".join(list(collection.tables.keys())),
            )
            return None

        raw = filter(lambda kv: kv[column] is not None, collection.tables[table])

        try:
            cls.TABLES[key] = dict(map(lambda od: (od[index], cast(od[column])), raw))
        except KeyError:
            print(
                f"Failed on `{list(raw)[0]}` using column:`{column}`, index:`{index}`"
            )
            raise

        return cls.TABLES[key]

    @classmethod
    def countries(cls):
        return cls.table("samayo/country-names", "countries", "country").keys()


class Dimension:
    def __init__(self, name, data, unit=None, dtype="object"):
        if isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, columns=[name], orient="index")
        elif isinstance(data, pd.Series):
            df = pd.DataFrame(index=data.index, data=data, columns=[name])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise RuntimeError(
                f"Only know how to handle `dict` and `pd.Series` data types; not `{type(data)}`"
            )

        self._unit = unit
        self._name = name

        df = df.astype(dtype={name: dtype})
        df = df[df.index.isin(DataDotWorld.countries())]
        self._df = df

    def __call__(self):
        return self._df

    def __getitem__(self, country):
        return self._df[self._df.index == country][self.name].values[0]

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @property
    def dataframe(self):
        return self._df

    @property
    def series(self):
        return self._df[self._name]

    @property
    def countries(self):
        return set(self._df.index)
