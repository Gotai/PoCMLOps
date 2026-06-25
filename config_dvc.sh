# This assumes that dvc has been initalised inside this project
# that can be done using, if dvc is installed, via.
# dvc init

# Configure remote to MinIO (local S3)
dvc remote add -d minio s3://mlops-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin
