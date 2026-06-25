import logging
from typing import Optional

from repository.mlflow_repository import MlflowRepository

class MlflowModelService():
    def __init__(self, mlflow_repository: MlflowRepository) -> None:
        # this should really be a motivater to add injection...
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.mlfloww_repository = mlflow_repository
        self.model_name: Optional[str] = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            model_names = self.mlfloww_repository.get_all_model_names()
            if not model_names:
                raise ValueError("No models found in mlflow repository")
            
            self.model_name = self._choose_model(model_names)   
            self.logger.info(f"Loading model: {self.model_name}")

            self.model = self.mlfloww_repository.get_neweset_model(self.model_name)
            self.logger.info(f"Successfully loaded model: {self.model_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to load model: {self.model_name}")
            raise

    def _choose_model(self, model_names):
        return model_names[0] # this is a demo, it is late, and warm
