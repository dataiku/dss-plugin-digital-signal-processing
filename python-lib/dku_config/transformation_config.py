import numpy as np

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
                required=True  # change it to False and add a specific condition
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
        if len(config.get("timeseries_identifiers")) == 0:
            is_long_format_valid = False
        self.add_param(
            name="long_format",
            value=long_format,
            checks=[{"type": "custom",
                     "cond": is_long_format_valid,
                     "err_msg": "Long format is selected but no time series identifiers were provided"
                     }]
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
                    "op": int
                },
                {
                    "type": "sup_eq",
                    "op": 7

                },
                {
                    "type": "custom",
                    "cond": seasonal % 2 == 1,
                    "err_msg": "The seasonal smoother should be an odd integer."
                }],
            required=True
        )

        model_stl = config.get("model_stl")

        valid_model = True
        negative_column = ""
        input_dataset = self.input_dataset.get_dataframe()
        if model_stl == "multiplicative":
            for target_colum in self.target_columns:
                target_values = input_dataset[target_colum].values
                if np.any(target_values <= 0):
                    valid_model = False
                    negative_column = target_colum
                    break

        self.add_param(
            name="model_stl",
            value=config.get("model_stl"),
            checks=[
                {
                    "type": "in",
                    "op": ["additive", "multiplicative"]
                },
                {
                    "type": "custom",
                    "cond": valid_model,
                    "err_msg": f"The targeted column {negative_column} contains negative values, yet, a multiplicative STL model only works with positive time series. You may choose an additive STL model or a classic decomposition method instead. "
                }
            ],
            required=True
        )

        self.add_param(
            name="expert_stl",
            value=config.get("expert_stl", False),
            checks=[
                {
                    "type": "is_type",
                    "op": bool
                }
            ],
            required=True
        )

        if self.expert_stl:
            self._load_STL_advanced_parameters(config)

    def _load_STL_advanced_parameters(self, config):
        self.add_param(
            name="robust_stl",
            value=config.get("robust_stl", False),
            checks=[
                {
                    "type": "is_type",
                    "op": bool
                }
            ],
            required=False
        )

        degree_kwargs = config.get("stl_degree_kwargs", {})
        self.add_param(
            name="loess_degrees",
            value=degree_kwargs,
            checks=[
                {
                    "type": "is_type",
                    "op": dict
                },
                {
                    "type": "custom",
                    "cond": all(
                        x in ["seasonal_deg", "trend_deg", "low_pass_deg", ""] for x in degree_kwargs.keys()),
                    "err_msg": "This field is invalid. The keys should be in the following iterable: [seasonal_jump, trend_jump,low_pass_jump]"
                },
                {
                    "type": "custom",
                    "cond": all(x in ["0", "1", ""] for x in degree_kwargs.values()),
                    "err_msg": "This field is invalid. The degrees used for Loess estimation should be equal to 0 and 1"
                }
            ],
            required=False
        )

        speed_up_kwargs = config.get("stl_speed_jump_kwargs", {})

        self.add_param(
            name="speed_jumps",
            value=speed_up_kwargs,
            checks=[
                {
                    "type": "is_type",
                    "op": dict
                },
                {
                    "type": "custom",
                    "cond": all(
                        x in ["seasonal_jump", "trend_jump", "low_pass_jump", ""] for x in speed_up_kwargs.keys()),
                    "err_msg": "This field is invalid. The keys should be in the following iterable: [seasonal_jump, trend_jump,low_pass_jump]"
                },
                {
                    "type": "custom",
                    "cond": all((x.isnumeric() and float(x).is_integer() and float(x) >= 0) or (x == "") for x in
                                speed_up_kwargs.values()),
                    "err_msg": "This field is invalid. The values should be positive integers."
                }
            ],
            required=False
        )

        additional_smoothers = config.get("stl_smoothers_kwargs", {})

        self.add_param(
            name="additional_smoothers",
            value=additional_smoothers,
            checks=[
                {
                    "type": "is_type",
                    "op": dict
                },
                {
                    "type": "custom",
                    "cond": all(
                        x in ["trend", "low_pass", ""] for x in additional_smoothers.keys()),
                    "err_msg": "This field is invalid. The keys should be in the following iterable: [trend, low_pass]"
                },
                {
                    "type": "custom",
                    "cond": all((x.isnumeric() and float(x).is_integer() and int(x) % 2 != 1) or (x == "") for x in
                                additional_smoothers.values()),
                    "err_msg": "This field is invalid. The values should be odd positive integers."
                }
            ],
            required=False
        )
