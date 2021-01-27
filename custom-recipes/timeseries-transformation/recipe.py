from dataiku.customrecipe import get_recipe_config

from dku_config.transformation_config import TransformationConfig
from timeseries_transformation.preparation import TimeseriesPreparator
from timeseries_transformation.decomposition import TimeseriesDecomposition

config = get_recipe_config()
dku_config = TransformationConfig(config)
input_df = dku_config.input_dataset.get_dataframe()

timeseries_preparator = TimeseriesPreparator(
    time_column_name=dku_config.time_column,
    frequency=dku_config.frequency,
    target_columns_names=dku_config.target_columns,
    timeseries_identifiers_names=dku_config.timeseries_identifiers
)

df_prepared = timeseries_preparator.prepare_timeseries_dataframe(input_df)

if dku_config.transformation_type == "seasonal_decomposition":
    decomposition = TimeseriesDecomposition(dku_config)
    transformed_df = decomposition.fit(df_prepared)
else:
    transformed_df = input_df


# Recipe outputs
transformation_df = dku_config.output_dataset.write_with_schema(transformed_df)
