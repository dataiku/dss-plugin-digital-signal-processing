# Code for custom code recipe timeseries-transformation (imported from a Python recipe)

# To finish creating your custom recipe from your original PySpark recipe, you need to:
#  - Declare the input and output roles in recipe.json
#  - Replace the dataset names by roles access in your code
#  - Declare, if any, the params of your custom recipe in recipe.json
#  - Replace the hardcoded params values by acccess to the configuration map

# See sample code below for how to do that.
# The code of your original recipe is included afterwards for convenience.
# Please also see the "recipe.json" file for more information.

# import the classes for accessing DSS objects from the recipe
import dataiku
# Import the helpers for custom recipes
from dataiku.customrecipe import *

# Inputs and outputs are defined by roles. In the recipe's I/O tab, the user can associate one
# or more dataset to each input and output role.
# Roles need to be defined in recipe.json, in the inputRoles and outputRoles fields.

# To  retrieve the datasets of an input role named 'input_A' as an array of dataset names:
input_A_names = get_input_names_for_role('input_A_role')
# The dataset objects themselves can then be created like this:
input_A_datasets = [dataiku.Dataset(name) for name in input_A_names]

# For outputs, the process is the same:
output_A_names = get_output_names_for_role('main_output')
output_A_datasets = [dataiku.Dataset(name) for name in output_A_names]


# The configuration consists of the parameters set up by the user in the recipe Settings tab.

# Parameters must be added to the recipe.json file so that DSS can prompt the user for values in
# the Settings tab of the recipe. The field "params" holds a list of all the params for wich the
# user will be prompted for values.

# The configuration is simply a map of parameters, and retrieving the value of one of them is simply:
my_variable = get_recipe_config()['parameter_name']

# For optional parameters, you should provide a default value in case the parameter is not present:
my_variable = get_recipe_config().get('parameter_name', None)

# Note about typing:
# The configuration of the recipe is passed through a JSON object
# As such, INT parameters of the recipe are received in the get_recipe_config() dict as a Python float.
# If you absolutely require a Python int, use int(get_recipe_config()["my_int_param"])


#############################
# Your original recipe
#############################

import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
from statsmodels.tsa.seasonal import STL

dataset_airline_passengers = dataiku.Dataset("train_by_date_prepared")
df = dataset_airline_passengers.get_dataframe()

time_column = "date_parsed"
target_column = "sales"


start_date = df[time_column].min()

values = df[target_column].values
ts = pd.Series(values, index=pd.date_range(start_date, periods=len(values), freq='D'), name = 'target')

parameters = {"endog":ts,"seasonal":365}

stl = STL(**parameters)
results = stl.fit()

df["trend"] = results.trend.values
df["seasonal"] = results.seasonal.values
df["residuals"] = results.resid.values
df["decision_tool"] = results.seasonal.values - results.resid.values

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Recipe outputs
decomposition = dataiku.Dataset("decomposition")
decomposition.write_with_schema(df)