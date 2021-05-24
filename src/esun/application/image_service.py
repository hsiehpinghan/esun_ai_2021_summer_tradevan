import os
import hashlib

from datetime import datetime
from esun.domain.image_classifier import ImageClassifier


class ImageService():
    CAPTAIN_EMAIL = os.environ['CAPTAIN_EMAIL']
    SALT = os.environ['SALT']

    def get_response(self, esun_uuid: str, image_64_encoded: str):
        classifier = ImageClassifier(id=esun_uuid,
                                     image_64_encoded=image_64_encoded)
        return {'esun_uuid': esun_uuid,
                'server_uuid': self.generate_server_uuid(),
                'server_timestamp': self.generate_server_timestamp(),
                'answer': classifier.get_answer()}

    def generate_server_uuid(self):
        s = hashlib.sha256()
        data = (ImageService.CAPTAIN_EMAIL + str(int(datetime.now().utcnow().timestamp())
                                                 ) + ImageService.SALT).encode("utf-8")
        s.update(data)
        server_uuid = s.hexdigest()
        return server_uuid

    def generate_server_timestamp(self):
        return int(datetime.now().utcnow().timestamp())
