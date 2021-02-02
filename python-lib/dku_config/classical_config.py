import json
from dku_config.transformation_config import TransformationConfig


class ClassicalConfig(TransformationConfig):
    def __init__(self):
        super().__init__()

    def add_parameters(self, config):
        super().add_parameters(config)
        self.load_settings(config)
        if self.advanced:
            self.load_advanced_parameters(config)

    def load_settings(self, config, *args, **kwargs):
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

        self.add_param(
            name="model",
            value=config.get("classical_model", "additive"),
            checks=[
                {
                    "type": "in",
                    "op": ["additive", "multiplicative"]
                }],
            required=True
        )

        self.add_param(
            name="advanced",
            value=config.get("expert_classical", False),
            checks=[
                {
                    "type": "is_type",
                    "op": bool
                }
            ],
            required=True
        )

    def load_advanced_parameters(self, config):

        advanced_params = config.get("advanced_params_classical", {})
        self.add_param(
            name="advanced_params",
            value=advanced_params,
            checks=[
                {
                    "type": "is_type",
                    "op": dict
                },
                {
                    "type": "custom",
                    "cond": all(
                        x in ["filt", "two_sided", "extrapolate_trend", ""] for x in advanced_params.keys()),
                    "err_msg": "This field is invalid. The keys should be in the following iterable: [filt, two_sided,extrapolate_trend]"
                }
            ],
            required=False
        )

        filt = self.advanced_params.get("filt")
        if filt:
            filt = json.loads(filt)
            self.add_param(
                name="filt",
                value=filt,
                checks=[
                    {
                        "type": "is_type",
                        "op": list
                    }
                ],
                required=False
            )

        two_sided = self.advanced_params.get("two_sided", "True")
        if not two_sided:
            two_sided = "True"

        self.add_param(
            name="two_sided",
            value=two_sided,
            checks=[
                {
                    "type": "in",
                    "op": ["True", "False"]
                }
            ],
            required=False
        )

        extrapolate_trend = self.advanced_params.get("extrapolate_trend")
        if extrapolate_trend:
            if extrapolate_trend.isnumeric():
                numeric_extrapolate = float(extrapolate_trend)
                valid_extrapolate = (numeric_extrapolate.is_integer() and numeric_extrapolate >= 0)
            else:
                valid_extrapolate = (extrapolate_trend == "freq")

            self.add_param(
                name="extrapolate_trend",
                value=extrapolate_trend,
                checks=[
                    {
                        "type": "custom",
                        "cond": valid_extrapolate,
                        "err_msg": "Extrapolate trend should be a positive integer or equal to 'freq'"

                     }
                ],
                required=False
            )
