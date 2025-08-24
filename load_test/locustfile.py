import os
import random
import time
from datetime import datetime

from locust import HttpUser, between, task

from proto import (
    eater_photo_pb2,
    get_recomendation_pb2,
    custom_date_food_pb2,
    delete_food_pb2,
    modify_food_record_pb2,
    manual_weight_pb2,
)


def bearer_headers() -> dict:
    token = os.getenv("TEST_USER_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def proto_headers(content_type: str = "application/protobuf") -> dict:
    return {"Content-Type": content_type, **bearer_headers()}


class ChaterUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        if not self.environment.host:
            self.environment.host = os.getenv(
                "TARGET_HOST",
                os.getenv("EATER_TARGET_HOST", "http://chater-ui.chater-ui.svc.cluster.local:5000"),
            )

    @task(3)
    def eater_today(self):
        self.client.get(
            "/eater_get_today", headers=bearer_headers(), name="GET /eater_get_today"
        )
