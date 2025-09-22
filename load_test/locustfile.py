import os
import random
from datetime import datetime, timezone

from locust import HttpUser, between, task, tag

from proto import (
    eater_photo_pb2,
    get_recomendation_pb2,
    delete_food_pb2,
    modify_food_record_pb2,
    manual_weight_pb2,
    today_food_pb2,
)


def bearer_headers() -> dict:
    token = os.getenv("TEST_USER_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def proto_headers(content_type: str = "application/protobuf") -> dict:
    return {"Content-Type": content_type, **bearer_headers()}


class ChaterUser(HttpUser):
    host = os.getenv(
        "TARGET_HOST",
        os.getenv("EATER_TARGET_HOST", "http://chater-ui.chater-ui.svc.cluster.local:5000"),
    )
    wait_time = between(0.5, 1.5)

    def on_start(self):
        if not self.environment.host:
            self.environment.host = os.getenv(
                "TARGET_HOST",
                os.getenv("EATER_TARGET_HOST", "http://chater-ui.chater-ui.svc.cluster.local:5000"),
            )


    def _get_latest_dish_time(self):
        try:
            resp = self.client.get(
                "/eater_get_today", headers=bearer_headers(), name="GET /eater_get_today (for time)"
            )
            if resp.status_code != 200 or not resp.content:
                return None
            tf = today_food_pb2.TodayFood()
            tf.ParseFromString(resp.content)
            if not tf.dishes_today:
                return None
            latest = max(tf.dishes_today, key=lambda d: d.time)
            return latest.time
        except Exception:
            return None

    @tag("full_flow")
    @task(1)
    def full_flow(self):
        # 1) Send photo
        image_path = os.getenv(
            "TEST_PHOTO_PATH",
            os.path.join(os.path.dirname(__file__), "image.png"),
        )
        try:
            with open(image_path, "rb") as f:
                photo_bytes = f.read()
            photo_msg = eater_photo_pb2.PhotoMessage()
            photo_msg.time = datetime.now(timezone.utc).isoformat()
            photo_msg.photo_data = photo_bytes
            photo_msg.photoType = os.getenv("TEST_PHOTO_TYPE", "default_prompt")
            self.client.post(
                "/eater_receive_photo",
                data=photo_msg.SerializeToString(),
                headers=proto_headers(),
                name="POST /eater_receive_photo",
            )
        except Exception:
            return

        # 2) Modify food record (x2 -> 200%)
        time_to_modify = self._get_latest_dish_time()
        if time_to_modify:
            mod = modify_food_record_pb2.ModifyFoodRecordRequest()
            mod.time = int(time_to_modify)
            mod.user_email = os.getenv("TEST_USER_EMAIL", "")
            mod.percentage = 200
            self.client.post(
                "/modify_food_record",
                data=mod.SerializeToString(),
                headers=proto_headers(),
                name="POST /modify_food_record",
            )

        # 3) Send manual weight (0-100)
        mw = manual_weight_pb2.ManualWeightRequest()
        mw.user_email = os.getenv("TEST_USER_EMAIL", "")
        mw.weight = random.randint(0, 100)
        self.client.post(
            "/manual_weight",
            data=mw.SerializeToString(),
            headers=proto_headers(),
            name="POST /manual_weight",
        )

        # 4) Get recommendation
        req = get_recomendation_pb2.RecommendationRequest()
        req.days = int(os.getenv("TEST_RECOMMENDATION_DAYS", "1"))
        self.client.post(
            "/get_recommendation",
            data=req.SerializeToString(),
            headers=proto_headers(),
            name="POST /get_recommendation",
        )

        # 5) Get today after changes
        self.client.get(
            "/eater_get_today", headers=bearer_headers(), name="GET /eater_get_today (post-modify)"
        )

        # 6) Delete the created/modified food record
        time_to_delete = time_to_modify or self._get_latest_dish_time()
        if time_to_delete:
            dreq = delete_food_pb2.DeleteFoodRequest()
            dreq.time = int(time_to_delete)
            self.client.post(
                "/delete_food",
                data=dreq.SerializeToString(),
                headers=proto_headers(),
                name="POST /delete_food",
            )
