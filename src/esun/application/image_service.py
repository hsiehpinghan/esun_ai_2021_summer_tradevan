import os
import hashlib

from cache import cache
from datetime import datetime
from esun.domain.image_entity import ImageEntity


class ImageService():
    CAPTAIN_EMAIL = os.environ['CAPTAIN_EMAIL']
    SALT = os.environ['SALT']

    def get_response(self, esun_uuid: str, image_64_encoded: str):
        word = cache.get(esun_uuid)
        if word is None:
            image_entity = ImageEntity(id=esun_uuid,
                                       image_64_encoded=image_64_encoded)
            word = image_entity.get_word()
            cache.set(esun_uuid, word)
        return {'esun_uuid': esun_uuid,
                'server_uuid': self._generate_server_uuid(),
                'server_timestamp': self._generate_server_timestamp(),
                'answer': word}

    def _generate_server_uuid(self):
        s = hashlib.sha256()
        data = (ImageService.CAPTAIN_EMAIL + str(int(datetime.now().utcnow().timestamp())
                                                 ) + ImageService.SALT).encode("utf-8")
        s.update(data)
        server_uuid = s.hexdigest()
        return server_uuid

    def _generate_server_timestamp(self):
        return int(datetime.now().utcnow().timestamp())
