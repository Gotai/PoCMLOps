FROM runtime-base:latest AS base


RUN pip install onnxruntime

COPY src/edge/ .

CMD ["python", "edge_deploy.py"]
