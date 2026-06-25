import torch
import logging
from fastapi import HTTPException

from service.mlflow_model_service import MlflowModelService
from logger.prometheus_logger import PrometheusLogger

class PredictionService():
    def __init__(self,
                 mlflow_model_service: MlflowModelService,
                 prometheus_logger: PrometheusLogger) -> None:

        self.ENDPOINT_NAME = "/predict"

        # this should really be a motivater to add injection...
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.prometheus_logger = prometheus_logger

        self.mlflow_model_service = mlflow_model_service

    def predict(self, features: list[float]):
        try:
            self.prometheus_logger.increment_request_count(self.ENDPOINT_NAME, "success")

            with self.prometheus_logger.request_latency.labels(endpoint=self.ENDPOINT_NAME).time():
                tensor = torch.tensor([features], dtype=torch.float32)

                with torch.no_grad():
                    prediction = self.mlflow_model_service.model(tensor)
                
                result = prediction.detach().cpu().numpy().tolist()[0][0]

                return {
                    "prediction": result,
                    "model_name": self.mlflow_model_service.model_name
                }
            
        except Exception as e:
            error_string = f"Prediction failed: {str(e)}"
            self.logger.error(error_string)
            self.prometheus_logger.increment_request_count(self.ENDPOINT_NAME, "error")
            raise HTTPException(
                status_code=400,
                detail=error_string
            )
