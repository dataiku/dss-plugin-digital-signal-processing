import itertools
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


class TimeseriesDecomposition():
    def __init__(self, recipe_config):
        self.config = recipe_config
        self.parameters = format_parameters(recipe_config)

    def fit(self, df):
        if self.config.long_format:
            ts_indexes = self._get_indexes_for_long_ts(df)
            decomposed_df = pd.DataFrame()
            for index in ts_indexes:
                ts_df = df.loc[index]
                decomposed_df = decomposed_df.append(self._decompose_df(ts_df))
        else:
            decomposed_df = self._decompose_df(df)
        return decomposed_df

    def _decompose_df(self,df):
        time_index = df[self.config.time_column].values
        for target_column in self.config.target_columns:
            target_values = df[target_column].values
            ts = self._prepare_ts(target_values, time_index)
            decomposition = self._decompose(ts)
            decomposed_df = self._write_decomposition(decomposition, df, target_column)
        return decomposed_df

    def _prepare_ts(self,target_values,time_index):
        return pd.Series(target_values, index=time_index)

    def _decompose(self, ts):
        if self.config.time_decomposition_method == "STL":
            if self.config.model_stl == "multiplicative":
                ts = np.log(ts)
                self.parameters["endog"] = ts
                stl = STL(**self.parameters)
                results = stl.fit()
                results._trend = np.exp(results.trend)
                results._seasonal = np.exp(results.seasonal)
                results._resid = np.exp(results.resid)
            elif self.config.model_stl == "additive":
                self.parameters["endog"] = ts
                stl = STL(**self.parameters)
                results = stl.fit()
        else:
            pass
        return results

    def _write_decomposition(self, decomposition, df, target_column):
        df["{}_trend_0".format(target_column)] = decomposition.trend.values
        df["{}_seasonal_0".format(target_column)] = decomposition.seasonal.values
        df["{}_residuals_0".format(target_column)] = decomposition.resid.values
        return df

    def _get_indexes_for_long_ts(self, df):
        identifiers = []
        for identifier_name in self.config.timeseries_identifiers:
            identifiers.append(df[identifier_name].unique())
        ts_indexes = []
        for combination in itertools.product(*identifiers):
            ts_df = df
            for i, column in enumerate(self.config.timeseries_identifiers):
                ts_df = ts_df.query(f"{column}=={combination[i]}")
            ts_indexes.append(ts_df.index)
        return ts_indexes


def format_parameters(config):
    parameters = {}
    if config.time_decomposition_method == "STL":
        parameters["seasonal"] = config.seasonal
    elif config.time_decomposition_method == "classical":
        pass
    return parameters

