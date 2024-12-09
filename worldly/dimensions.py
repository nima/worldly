import logging

import datadotworld as dw
import pandas as pd
import numpy as np

from typing import Callable


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
    def __init__(self, name: str, data: dict, dtype: type, unit: str = None) -> None:
        self._unit = unit
        self._name = name
        self._type = dtype()

        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, pd.Series):
            df = pd.DataFrame(index=data.index, data=data, columns=[name])
        elif isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, columns=[name], orient="index")
        else:
            raise RuntimeError(
                f"Only know how to handle `dict` and `pd.Series` data types; not `{type(data)}`"
            )

        df = df.dropna()
        df = df.astype(dtype={name: self._type})
        df = df[df.index.isin(DataDotWorld.countries())]
        self._df = df

    def __call__(self):
        return self._df

    def __getitem__(self, country):
        return self._df[self._df.index == country][self.name].values[0]

    @property
    def log10(self):
        return self._group_by_log(np.log10)

    @property
    def log2(self):
        return self._group_by_log(np.log2)

    @property
    def log(self):
        return self._group_by_log(np.log)

    def _group_by_log(self, fn):
        dataframe = self.dataframe[self.name]
        return (
            dataframe.reset_index()
            .assign(
                **{
                    fn.__name__: lambda n: np.round(
                        fn(np.maximum(n[self.name], 1))
                    ).astype(int)
                }
            )
            .groupby(fn.__name__)
            .agg({"index": list})
            .rename(columns={"index": "countries"})
        )

    def _group_by_category(self):
        dataframe = self.dataframe[self.name]
        return (
            dataframe.reset_index()
            .groupby(self.name)
            .agg({"index": list})
            .rename(columns={"index": "countries"})
        )

    def group(self, fn=np.log):
        # Numeric (e.g., population), or Categorical (e.g., continent)?
        numeric = isinstance(self._type, pd.Int64Dtype)
        dataframe = self._group_by_log(fn) if numeric else self._group_by_category()

        return (
            dataframe.assign(l=lambda df: df["countries"].apply(len))
            .assign(
                p=lambda df: df["countries"].apply(
                    lambda l: 100 * len(l) / len(self._df)
                )
            )
            .sort_values(by=[fn.__name__ if numeric else "p"])
        )

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

    @property
    def effectiveness(self):
        return self._effectiveness
