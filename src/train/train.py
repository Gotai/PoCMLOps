import argparse
import json
import os
import mlflow
from mlflow.models import infer_signature
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class Network(nn.Module):
    def __init__(self, n_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x)


def main(data_path: str, model_path: str):
    df = pd.read_parquet(data_path)
    X = torch.tensor(df.drop("target", axis=1).values, dtype=torch.float32)
    y = torch.tensor(df["target"].values[:, None], dtype=torch.float32)

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")) # TODO move to global config
    mlflow.set_experiment("tabular-demo")
    with mlflow.start_run():
        mlflow.log_params({"epochs": 20, "lr": 1e-3, "batch_size": 128})

        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=128, shuffle=True)
        model = Network(X.shape[1])
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=1e-3)

        for epoch in range(20):
            epoch_loss = 0.0
            for xb, yb in loader:
                pred = model(xb)
                loss = criterion(pred, yb)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            mlflow.log_metric("train_loss", epoch_loss / len(loader), step=epoch)

        example_input = X
        example_output = model(example_input)
        signature = infer_signature(example_input.numpy(), example_output.detach().numpy())
        torch.save(model.state_dict(), model_path)
        mlflow.log_artifact(model_path, artifact_path="model")
        mlflow.pytorch.log_model(model, name="pytorch-model", input_example=example_input.numpy(), signature=signature)

        metrics = {"final_loss": epoch_loss / len(loader)}
        with open("metrics.json", "w") as f:
            json.dump(metrics, f)
        mlflow.log_artifact("metrics.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path")
    parser.add_argument("model_path")
    args = parser.parse_args()
    main(args.data_path, args.model_path)
