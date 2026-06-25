import os

import mlflow
from mlflow.tracking import MlflowClient


class MlflowRepository():
    def __init__(self) -> None:
        self._init()
        self.client = MlflowClient()

    def _init(self):
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        self.registry_uri = os.getenv("MLFLOW_S3_ENDPOINT_URL")

        self._assert_valid_configuration()
        self.client = MlflowClient(tracking_uri=self.tracking_uri, registry_uri=self.registry_uri)
    
    def _assert_valid_configuration(self):
        if not self.tracking_uri:
            raise ValueError("MLFLOW_TRACKING_URI not found")
   
    def get_all_model_names(self):
        models = self.client.search_registered_models()
        return [model.name for model in models]

    def get_neweset_model(self, model_name):
        versions = self.client.search_model_versions(f"name='{model_name}'")

        if not versions:
            raise ValueError(f"No versions was found for model with name '{model_name}'")
        
        newest_version = max(versions, key=lambda x: x.version)
        model_uri = f"models:/{model_name}/{newest_version.version}"

        return mlflow.pytorch.load_model(model_uri)
