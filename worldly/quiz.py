import logging
import random

import pandas as pd


class Quiz:
    logger = logging.getLogger(__name__)

    def __init__(self, dimensions):
        self._dimensions = {d.name: d for d in dimensions}

    def __getattr__(self, name):
        return self._dimensions[name]

    def country(self, name):
        try:
            return self.df().loc[name]
        except KeyError:
            Quiz.logger.error("No such country:%s; known countries are:%s", name, ", ".join(self.df().index))

    def df(self, dimension=None):
        if dimension is None:
            return pd.concat(map(lambda d: d.dataframe, self._dimensions.values()), axis=1)
        else:
            return self._dimensions[dimension].dataframe

    def add_dimension(self, dimension):
        self._dimensions[dimension.name] = dimension

    def qna(self, questions):
        qna = []
        for q in questions:
            # select the dimension's dataframe
            dimension = self._dimensions[q.dimension]
            df = dimension.dataframe.dropna()

            # if this is not the first question, limit the selection to the last question's answers
            if len(qna):
                _, whitelist = qna[-1]
                df = df[df.index.isin(whitelist.index)]
                if len(df) == 0:
                    continue

            # filter out garbage
            if q.filter_out is not None:
                remove = df[q.filter_out(df[q.dimension])].index
                df = df.drop(remove)
                if len(df) == 0:
                    continue

            # group by
            df['_'] = df[q.dimension].apply(q.group_by)
            group = random.sample(df['_'].to_list(), 1).pop()
            answers = df[df['_'] == group].drop(columns=['_'])

            # append the generated question and answer
            qna.append((q.question(q.dimension, group, dimension.unit), answers))

        return qna

    @property
    def dimensions(self):
        return set(self._dimensions.keys())
