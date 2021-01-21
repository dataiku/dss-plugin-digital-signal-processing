from dku_config import DkuConfig


class TransformationConfig(DkuConfig):
    def __init__(self, config):
        super().__init__()
        self.load(config)

    def load(self, config):
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
            if self.time_decomposition_method == "STL":
                self._load_STL_parameters(config)

    def _load_input_parameters(self,config):
        self.add_param(
            name="time_decomposition_method",
            value=config.get("time_decomposition_method"),
            checks=[{
                "type": "in",
                "op": ["STL", "classical"]
            }],
            required=True
        )
        self.add_param(
            name="time_column",
            value=config.get("time_column"),
            checks=[{
                "type": "is_type",
                "op": str
            }],
            required=True
        )
        self.add_param(
            name="target_column",
            value=config.get("target_column"),
            required=True
        )
        self.add_param(
            name="frequency",
            value=config.get("frequency_unit"),
            checks=[{
                "type": "in",
                "op": ["min","H","D","B","W","M","3M","6M","12M"]
            }],
            required=True
        )

    def _load_STL_parameters(self,config):
        seasonal = config.get("seasonal_stl")
        self.add_param(
            name="seasonal",
            value= seasonal,
            checks=[
                {
                    "type":"is_type",
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


