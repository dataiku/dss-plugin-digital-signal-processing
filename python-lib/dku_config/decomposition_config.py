import numpy as np
from dku_config.transformation_config import TransformationConfig
from dku_config.utils import MultiplicativeCheck


class DecompositionConfig(TransformationConfig):
    def __init__(self):
        super().__init__()

    def add_parameters(self, config):
        super().add_parameters(config)
        input_df = self.input_dataset.get_dataframe()
        self.load_settings(config, input_df)
        if self.advanced:
            self.load_advanced_parameters(config)

    def _check_multiplicative_model(self, model, input_df):
        if model == "multiplicative":
            for target_column in self.target_columns:
                target_values = input_df[target_column].values
                if np.any(target_values <= 0):
                    return MultiplicativeCheck(False, target_column)
            return MultiplicativeCheck(True)
        else:
            return MultiplicativeCheck(True)