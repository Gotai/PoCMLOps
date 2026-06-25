
from prometheus_client import Counter, Histogram, start_http_server

import logging

class PrometheusLogger():
    def __init__(self) -> None:
        # this should really be a motivater to add injection...
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        SERVER_PORT = 8001 # TODO global config

        self.request_count = Counter(
            name="request_total",
            documentation="Total API requests",
            labelnames=["endpoint", "status"]
        )

        self.request_latency = Histogram(
            name="request_latency_secounds",
            documentation="Latency of API requests",
            labelnames=["endpoint"],
            buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
        )

        start_http_server(SERVER_PORT)
        self.logger.info(f"Prometheus metrics server started on port: {SERVER_PORT}")

    def increment_request_count(self, endpoint_name, status):
        self.request_count.labels(
            endpoint=endpoint_name,
            status=status
        ).inc()
