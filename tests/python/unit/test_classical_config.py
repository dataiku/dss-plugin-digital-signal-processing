import pandas as pd
import pytest

from dku_config.dss_parameter import DSSParameterError
from dku_config.classical_config import ClassicalConfig


class TestClassicalConfig:

    def test_load_settings(self):
        config = {"classical_model": "additive"}
        dku_config = ClassicalConfig(config)
        input_dataset_columns = ["date", "target", "value2"]
        dku_config.load_input_parameters(config, input_dataset_columns)
        assert dku_config.load_settings(config) is None

        #config.pop("seasonal_stl")
        #with pytest.raises(DSSParameterError):
        #    _ = dku_config.load_settings(config, input_df)

    def test_load_advanced_parameters(self):
        dku_config = ClassicalConfig()
        config = {"transformation_type": "seasonal_decomposition", "time_decomposition_method": "STL",
                  "frequency_unit": "D",
                  "model_stl": "additive", "seasonal_stl": "7", "expert_stl": True, "robust_stl": True,
                  "seasonal_degree_stl": "1",
                  "trend_degree_stl": "0", "lowpass_degree_stl": "0", "time_column": "date",
                  "long_format": False, "target_columns": ["target"],
                  "stl_degree_kwargs": {"seasonal_deg": "1", "trend_deg": "", "low_pass_deg": "1"},
                  "stl_speed_jump_kwargs": {"seasonal_jump": '', "trend_jump": "12", "low_pass_jump": ''},
                  "stl_smoothers_kwargs": {"trend": "13", "low_pass": ''}}
        input_dataset_columns = ["date", "target"]
        dku_config.load_input_parameters(config, input_dataset_columns)

        assert dku_config.load_advanced_parameters(config) is None

        config["stl_smoothers_kwargs"]["trend"] = "2"
        with pytest.raises(DSSParameterError):
            _ = dku_config.load_advanced_parameters(config)

        config["stl_smoothers_kwargs"]["trend"] = "3"
        config["stl_degree_kwargs"]["seasonal_deg"] = "2"
        with pytest.raises(DSSParameterError):
            _ = dku_config.load_advanced_parameters(config)
        config["stl_degree_kwargs"]["seasonal_deg"] = "1"

        config["stl_smoothers_kwargs"]["wrong_field"] = "3"
        with pytest.raises(DSSParameterError):
            _ = dku_config.load_advanced_parameters(config)

        config["stl_smoothers_kwargs"].pop("wrong_field")
        config["stl_smoothers_kwargs"]["trend"] = "12"
        with pytest.raises(DSSParameterError):
            _ = dku_config.load_advanced_parameters(config)