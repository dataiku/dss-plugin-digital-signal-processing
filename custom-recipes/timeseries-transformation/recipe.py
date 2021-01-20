import dataiku
from dataiku.customrecipe import *
import pandas as pd
from statsmodels.tsa.seasonal import STL

#SETTINGS
input_dataset_name = get_input_names_for_role("input_dataset")[0]
input_dataset = dataiku.Dataset(input_dataset_name)

transformation_dataset_name = get_output_names_for_role("transformation_dataset")[0]
transformation_dataset = dataiku.Dataset(transformation_dataset_name)

config = get_recipe_config()
time_column = config.get("time_column", None)
target_column = config.get("target_column", None)
seasonal = config.get("seasonal_stl", None)
frequency = config.get("frequency_unit",None)

#RUN
df = input_dataset.get_dataframe()
start_date = df[time_column].min()

values = df[target_column].values
ts = pd.Series(values, index=pd.date_range(start_date, periods=len(values), freq=frequency), name = 'target')

parameters = {"endog":ts,"seasonal":seasonal}

stl = STL(**parameters)
results = stl.fit()

df["{}_trend_0".format(target_column)] = results.trend.values
df["{}_seasonal_0".format(target_column)] = results.seasonal.values
df["{}_residuals_0".format(target_column)] = results.resid.values

# Recipe outputs
transformation_dataset.write_with_schema(df)
