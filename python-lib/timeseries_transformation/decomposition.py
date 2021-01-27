import pandas as pd
from statsmodels.tsa.seasonal import STL


class TimeseriesDecomposition():
    def __init__(self, recipe_config):
        self.config = recipe_config
        self.parameters = format_parameters(recipe_config)

    def fit(self, df):
        if self.config.time_decomposition_method == "STL":
            return self._write_stl(df)
        elif self.config.time_decomposition_method == "classical":
            return self._fit_classic(df)

    def _write_stl(self, df):
        if self.config.long_format:
            pass
        else:
            for target_column in self.config.target_columns:
                target_values = df[target_column].values
                ts = pd.Series(target_values, index=df[self.config.time_column].values)
                decomposition = self._fit_STL(ts)
                df["{}_trend_0".format(target_column)] = decomposition.trend.values
                df["{}_seasonal_0".format(target_column)] = decomposition.seasonal.values
                df["{}_residuals_0".format(target_column)] = decomposition.resid.values
            return df

    def _fit_stl_long_format(self, df):
        pass

    def _fit_classic(self, df):
        pass

    def _fit_STL(self, ts):
        self.parameters["endog"] = ts
        stl = STL(**self.parameters)
        results = stl.fit()
        return results


def format_parameters(config):
    parameters = {}
    if config.time_decomposition_method == "STL":
        parameters["seasonal"] = config.seasonal
    elif config.time_decomposition_method == "classical":
        pass
    return parameters
