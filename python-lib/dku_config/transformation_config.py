import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role

from dku_config import DkuConfig


class TransformationConfig(DkuConfig):
    def __init__(self, config):
        super().__init__()
        self.load(config)

    def load(self, config):
        self._load_input_output_datasets()
        self.add_param(
            name="transformation_type",
            value=config.get("transformation_type"),
            checks=[{
                "type": "in",
                "op": ["seasonal_decomposition"]
            }],
            required=True
        )

        if self.transformation_type == "seasonal_decomposition":
            self._load_input_parameters(config)
            self.add_param(
                name="time_decomposition_method",
                value=config.get("time_decomposition_method"),
                checks=[{
                    "type": "in",
                    "op": ["STL", "classical"]
                }],
                required=True # change it to False and add a specific condition
            )
            if self.time_decomposition_method == "STL":
                self._load_STL_parameters(config)

    def _load_input_output_datasets(self):
        self.add_param(
            name="input_dataset_name",
            value=get_input_names_for_role("input_dataset")[0],
            checks=[{
                "type": "is_type",
                "op": str
            }],
            required=True
        )
        self.add_param(
            name="input_dataset",
            value=dataiku.Dataset(self.input_dataset_name),
            required=True
        )
        self.add_param(
            name="output_dataset_name",
            value=get_output_names_for_role("transformation_dataset")[0],
            checks=[{
                "type": "is_type",
                "op": str
            }],
            required=True
        )
        self.add_param(
            name="output_dataset",
            value=dataiku.Dataset(self.output_dataset_name),
            required=True
        )

    def _load_input_parameters(self, config):
        input_dataset_columns = [p["name"] for p in self.input_dataset.read_schema()]
        self.add_param(
            name="time_column",
            value=config.get("time_column"),
            checks=[{"type": "is_type",
                     "op": str
                     },
                    {"type": "in",
                     "op": input_dataset_columns,
                     "err_msg": f"Invalid time column selection: {config.get('time_column')}"
                     }],
            required=True
        )
        self.add_param(
            name="target_columns",
            value=config.get("target_columns"),
            checks=[{"type": "is_type",
                     "op": list
                     },
                    {"type": "in",
                     "op": input_dataset_columns,
                     "err_msg": f"Invalid target column(s) selection: {config.get('target_columns')}"
                     }],
            required=True
        )

        if config.get("frequency_unit") not in ["W", "H", "min"]:
            frequency_value = config.get("frequency_unit")
        elif config.get("frequency_unit") == "W":
            frequency_value = f"W-{config.get('frequency_end_of_week', 1)}"
        elif config.get("frequency_unit") == "H":
            frequency_value = f"{config.get('frequency_step_hours', 1)}H"
        elif config.get("frequency_unit") == "min":
            frequency_value = f"{config.get('frequency_step_minutes', 1)}min"
        else:
            frequency_value = None

        self.add_param(
            name="frequency",
            value=frequency_value,
            required=True
        )

        long_format = config.get("additional_columns", False)
        is_long_format_valid = True
        if long_format and len(config.get("timeseries_identifiers")) == 0:
            is_long_format_valid = False

        self.add_param(
            name="long_format",
            value=long_format,
            checks=[{"type": "custom",
                     "cond": is_long_format_valid,
                     "err_msg": "Long format is selected but no time series identifiers were provided"
                     }],
            required=False
        )

        self.add_param(
            name="timeseries_identifiers",
            value=config.get("timeseries_identifiers"),
            checks=[{"type": "is_type",
                     "op": list
                     },
                    {"type": "in",
                     "op": input_dataset_columns,
                     "err_msg": f"Invalid time series identifiers selection: {config.get('timeseries_identifiers')}"
                     }],
            required=False
        )

    def _load_STL_parameters(self, config):
        seasonal = config.get("seasonal_stl")
        self.add_param(
            name="seasonal",
            value=seasonal,
            checks=[
                {
                    "type": "is_type",
                    "op":int
                },
                {
                    "type":"sup_eq",
                    "op":7

                },
                {
                    "type":"custom",
                    "cond": seasonal % 2 == 1,
                    "err_msg": "The seasonal smoother should be an odd integer."
                }]
        )


