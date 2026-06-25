curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, 1.2, 2.8, 3.1]}'

curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [1.0, 2.0, 3.0, 4.0]}'

# Check health
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models
