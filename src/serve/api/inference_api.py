from fastapi import FastAPI, HTTPException
import logging

from repository.mlflow_repository import MlflowRepository
from service.mlflow_model_service import MlflowModelService
from service.prediction_service import PredictionService

from api.message_config.prediction_messages import PredictionResponse, PredictionRequest

from logger.prometheus_logger import PrometheusLogger

class InferenceApi():
    def __init__(self) -> None:
        # this should really be a motivater to add injection...
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.prometheus_logger = PrometheusLogger()

        self.mlflow_repository = MlflowRepository()
        self.mlflow_model_service = MlflowModelService(self.mlflow_repository)
        self.prediction_service = PredictionService(self.mlflow_model_service, self.prometheus_logger)

        self.app = FastAPI(
            title="Inference Service",
            description="Part of a demo to show absolute basic skills in MLOps",
            version="0.1.0"
        )

        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.post(
            path="/predict",
            response_model=PredictionResponse,
            summary="Make a prediction based on a list of float inputs",
            description="Make a prediction based on a list of float inputs", # this is a demo, no need to exhaust ourselfs
        )
        async def predict(request: PredictionRequest):
            try:
                return self.prediction_service.predict(request.features)

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Unexpected eror in prediction: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error"
                )
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "model_loaded": self.mlflow_model_service.model is not None}
        
        @self.app.get("/models")
        async def list_models():
            try:
                model_names = self.mlflow_repository.get_all_model_names()
                return {"models": model_names}
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch models: {str(e)}"
                )
