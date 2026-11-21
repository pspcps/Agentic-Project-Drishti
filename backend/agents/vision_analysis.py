import logging
import os
from functools import cached_property

from google.api_core.exceptions import GoogleAPIError, NotFound, PreconditionFailed
from google.cloud import firestore, storage

from comms.pubsub import PubSubComms
from utils.firestore_utils import get_firestore_client
from utils.image_analysis import AnalysisError, IMAGE_FORMATS, MAX_IMAGE_BYTES, vertex_analyzer

logger = logging.getLogger(__name__)
VISION_BUCKET = os.getenv("DRISHTI_VISION_BUCKET", "project-drishti-central1-bucket-vision")


class VisionAnalysisAgent:
    @cached_property
    def analyzer(self):
        return vertex_analyzer()

    @cached_property
    def storage_client(self):
        return storage.Client()

    @cached_property
    def db(self):
        return get_firestore_client()

    @cached_property
    def comms(self):
        return PubSubComms("media-uploads")

    def handle_media_event(self, event):
        file_url, zone, doc_id = (event[key] for key in ("fileUrl", "zone", "docId"))
        media = self.db.collection("media").document(doc_id)
        try:
            snapshot = media.get(timeout=5, retry=None)
            metadata = snapshot.to_dict() or {}
            object_path = metadata.get("objectPath")
            if (not isinstance(object_path, str) or not object_path.startswith("uploads/")
                    or file_url != f"https://storage.googleapis.com/{VISION_BUCKET}/{object_path}"
                    or metadata.get("fileUrl") != file_url or metadata.get("zone") != zone):
                raise AnalysisError("invalid_upload", "Use an image uploaded for the selected zone.", 422)
            blob = self.storage_client.bucket(VISION_BUCKET).blob(object_path)
            blob.reload(timeout=5, retry=None)
            if blob.content_type not in IMAGE_FORMATS:
                raise AnalysisError("unsupported_type", "Choose a JPEG or PNG image.", 415)
            if not blob.size or blob.size > MAX_IMAGE_BYTES:
                raise AnalysisError("invalid_size", "Choose a nonempty image up to 5 MiB.", 413)
            data = blob.download_as_bytes(
                if_generation_match=blob.generation, raw_download=True, timeout=10, retry=None,
            )
        except (NotFound, PreconditionFailed) as exc:
            raise AnalysisError("upload_missing", "Upload the image again before running analysis.", 422) from exc
        except GoogleAPIError as exc:
            raise AnalysisError("storage_unavailable", "Could not read the upload. Try again shortly.", 503) from exc

        analysis = self.analyzer.analyze(data, blob.content_type)
        result = {"success": True, **analysis, "fileUrl": file_url, "zone": zone, "docId": doc_id}
        if event.get("autoIncident") and analysis["status"] != "uncertain":
            try:
                batch = self.db.batch()
                batch.update(media, {
                    **analysis, "processed": True, "analysisTimestamp": firestore.SERVER_TIMESTAMP,
                })
                batch.update(self.db.collection("zones").document(zone), {
                    "currentOccupancy": analysis["personCount"],
                })
                batch.commit(timeout=5, retry=None)
                if analysis["status"] == "detected":
                    self.comms.publish(result, timeout=5)
            except Exception:
                logger.exception("Could not complete automatic incident processing")
                result["automationWarning"] = "Image analyzed. Automatic incident processing did not confirm completion. Review the result manually."
        return result
