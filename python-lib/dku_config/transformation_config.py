import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role

from dku_config.dku_config import DkuConfig


class TransformationConfig(DkuConfig):
    def __init__(self):
        super().__init__()

    def add_parameters(self, config):
        input_name = get_input_names_for_role("input_dataset")[0]
        output_name = get_output_names_for_role("transformation_dataset")[0]
        self.load_input_output_datasets(input_name, output_name)

    def load_input_output_datasets(self, input_dataset_name, output_dataset_name):
        self.add_param(
            name="input_dataset_name",
            value=input_dataset_name,
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
            value=output_dataset_name,
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

    def load_settings(self, config, *args, **kwargs):
        pass

    def advanced_parameters(self, config):
        pass

