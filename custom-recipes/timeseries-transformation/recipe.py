from dataiku.customrecipe import get_recipe_config

from dku_config.stl_config import STLConfig
from dku_config.classical_config import ClassicalConfig
from timeseries_transformation.preparation import TimeseriesPreparator
from timeseries_transformation.stl_decomposition import STLDecomposition
from timeseries_transformation.classical_decomposition import ClassicalDecomposition


config = get_recipe_config()
if config.get("transformation_type") == "seasonal_decomposition":
    if config.get("time_decomposition_method") == "STL":
        dku_config = STLConfig()
    elif config.get("time_decomposition_method") == "classical":
        dku_config = ClassicalConfig()
dku_config.add_parameters(config)

input_df = dku_config.input_dataset.get_dataframe()
timeseries_preparator = TimeseriesPreparator(
    time_column_name=dku_config.time_column,
    frequency=dku_config.frequency,
    target_columns_names=dku_config.target_columns,
    timeseries_identifiers_names=dku_config.timeseries_identifiers
)

df_prepared = timeseries_preparator.prepare_timeseries_dataframe(input_df)

if dku_config.transformation_type == "seasonal_decomposition":
    if dku_config.time_decomposition_method == "STL":
        decomposition = STLDecomposition(dku_config)
    elif dku_config.time_decomposition_method == "classical":
        decomposition = ClassicalDecomposition(dku_config)
    transformed_df = decomposition.fit(df_prepared)
else:
    transformed_df = input_df


# Recipe outputs
transformation_df = dku_config.output_dataset.write_with_schema(transformed_df)
