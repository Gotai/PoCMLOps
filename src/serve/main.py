from dotenv import load_dotenv
from api.inference_api import InferenceApi

load_dotenv()

api = InferenceApi()
app = api.app
