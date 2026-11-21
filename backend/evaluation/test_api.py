"""HTTP regressions for the upload and analysis routes with cloud services faked."""

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import upload, vision
from agents.vision_analysis import VISION_BUCKET, VisionAnalysisAgent
from utils.image_analysis import ImageAnalyzer, MAX_IMAGE_BYTES

IMAGE = (Path(__file__).parent / "images" / "clear-fire.png").read_bytes()
PATH = "uploads/sample.png"
URL = f"https://storage.googleapis.com/{VISION_BUCKET}/{PATH}"
EVENT = {"zone": "demo", "docId": "sample", "fileUrl": URL, "autoIncident": True}


class MediaRoutesTest(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(upload.router, prefix="/api")
        app.include_router(vision.router, prefix="/api")
        self.client = TestClient(app)
        agent = VisionAnalysisAgent()
        agent.db = Mock()
        agent.storage_client = Mock()
        agent.comms = Mock()
        self.media = agent.db.collection.return_value.document.return_value
        self.media.get.return_value.to_dict.return_value = {
            "fileUrl": URL, "zone": "demo", "objectPath": PATH,
        }
        self.blob = agent.storage_client.bucket.return_value.blob.return_value
        self.blob.content_type = "image/png"
        self.blob.size = len(IMAGE)
        self.blob.generation = 1
        self.blob.download_as_bytes.return_value = IMAGE
        self.generate = Mock()
        agent.analyzer = ImageAnalyzer(self.generate, pause=lambda _: None)
        patcher = patch.object(vision, "vision_agent", agent)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.agent = agent

    def analyze(self, event=EVENT):
        return self.client.post("/api/analyze-media", json=event)

    def test_incomplete_event_is_rejected_before_cloud_read(self):
        self.assertEqual(self.analyze({"zone": "demo"}).status_code, 422)
        self.media.get.assert_not_called()

    def test_upload_metadata_mismatch_is_rejected_before_download(self):
        self.assertEqual(self.analyze({**EVENT, "zone": "different"}).json()["code"], "invalid_upload")
        self.blob.download_as_bytes.assert_not_called()

    def test_oversized_stored_object_is_rejected_before_download(self):
        self.blob.size = MAX_IMAGE_BYTES + 1
        self.assertEqual(self.analyze().status_code, 413)
        self.blob.download_as_bytes.assert_not_called()

    def test_timeout_is_failure_and_does_not_publish(self):
        self.generate.side_effect = httpx.ReadTimeout("injected")
        response = self.analyze()
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["status"], "analysis_failed")
        self.assertEqual(self.generate.call_count, 2)
        self.agent.comms.publish.assert_not_called()
        self.agent.db.batch.assert_not_called()

    def test_wrong_model_types_are_failure_and_do_not_persist(self):
        self.generate.return_value = '{"personCount":"0","fireDetected":"false"}'
        response = self.analyze()
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["code"], "invalid_model_response")
        self.assertEqual(self.generate.call_count, 1)
        self.agent.db.batch.assert_not_called()

    def test_definitive_and_uncertain_results_have_distinct_side_effects(self):
        for fire, uncertain, expected in [
            (True, False, "detected"),
            (False, False, "no_detection"),
            (True, True, "uncertain"),
        ]:
            with self.subTest(expected=expected):
                self.agent.comms.reset_mock()
                self.agent.db.batch.reset_mock()
                self.generate.return_value = json.dumps({
                    "personCount": 0, "crowdDensity": "low", "smokeDetected": False,
                    "fireDetected": fire, "stampedeDetected": False, "medicalEmergency": False,
                    "potentialRisk": fire, "incidentRecommended": fire, "uncertain": uncertain,
                    "incidentType": "fire" if fire else "none", "suggestedAction": "Review the frame.",
                })
                response = self.analyze()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["status"], expected)
                self.assertEqual(self.agent.db.batch.call_count, int(not uncertain))
                self.assertEqual(self.agent.comms.publish.call_count, int(expected == "detected"))

    def test_signed_upload_requires_supported_type_and_size(self):
        payload = {"filename": "sample.png", "zone": "demo", "type": "vision", "mimetype": "image/png"}
        endpoint = "/api/upload/presigned-url"
        with patch.object(upload.storage, "Client") as client:
            self.assertEqual(self.client.post(endpoint, json=payload).status_code, 413)
            invalid = {**payload, "size": 80, "mimetype": "video/mp4"}
            self.assertEqual(self.client.post(endpoint, json=invalid).status_code, 415)
            client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
