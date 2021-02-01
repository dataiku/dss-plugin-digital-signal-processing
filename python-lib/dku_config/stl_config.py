import numpy as np

from dku_config.transformation_config import TransformationConfig


class STLConfig(TransformationConfig):
    def __init__(self):
        super().__init__()

    def add_parameters(self, config):
        super().add_parameters(config)
        input_df = self.input_dataset.get_dataframe()
        self.load_settings(config, input_df)
        if self.advanced:
            self.load_advanced_parameters(config)

    def load_settings(self, config, input_df=None, *args, **kwargs):
        super(STLConfig, self).load_settings(config, input_df, *args, **kwargs)
        self.add_param(
            name="transformation_type",
            value=config.get("transformation_type"),
            required=True
        )

        self.add_param(
            name="time_decomposition_method",
            value=config.get("time_decomposition_method"),
            required=True
        )

        seasonal = config.get("seasonal_stl")
        is_seasonal_odd = True
        if seasonal:
            is_seasonal_odd = (seasonal % 2 == 1)
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
                    "cond": is_seasonal_odd,
                    "err_msg": "The seasonal smoother should be an odd integer."
                }],
            required=True
        )

        model_stl = config.get("model_stl")

        valid_model = True
        negative_column = ""
        if model_stl == "multiplicative":
            for target_column in self.target_columns:
                target_values = input_df[target_column].values
                if np.any(target_values <= 0):
                    valid_model = False
                    negative_column = target_column
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
                    "err_msg": f"{negative_column}, the targeted column contains negative values, yet, a multiplicative STL model only works with positive time series. You may choose an additive STL model or a classic decomposition method instead. "
                }
            ],
            required=True
        )

        self.add_param(
            name="advanced",
            value=config.get("expert_stl", False),
            checks=[
                {
                    "type": "is_type",
                    "op": bool
                }
            ],
            required=True
        )

    def load_advanced_parameters(self, config):
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
                    "err_msg": "This field is invalid. The keys should be in the following iterable: [seasonal_deg, trend_deg,low_pass_deg]"
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
                    "cond": all((x.isnumeric() and float(x).is_integer() and int(x) % 2 == 1) or (x == "") for x in
                                additional_smoothers.values()),
                    "err_msg": "This field is invalid. The values should be odd positive integers."
                }
            ],
            required=False
        )
