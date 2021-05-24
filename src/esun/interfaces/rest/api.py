import os
import sys

from absl import logging
from esun.application.image_service import ImageService
from flask import Blueprint, jsonify, request

bp = Blueprint('api', __name__, url_prefix='')
image_service = ImageService()


@bp.route('/inference', methods=['POST'])
def inference():
    logging.set_verbosity(logging.INFO)
    data = request.get_json(force=True)
    logging.info(data)
    image_64_encoded = data['image']
    resp = None
    try:
        resp = image_service.get_response(esun_uuid=data['esun_uuid'],
                                          image_64_encoded=image_64_encoded)
    except:
        msg = sys.exc_info()[0]
        logging.exception(msg)
        if data['retry'] >= 2:
            return {'esun_uuid': data['esun_uuid'],
                    'server_uuid': image_service.generate_server_uuid(),
                    'server_timestamp': image_service.generate_server_timestamp(),
                    'answer': 'isnull'}
        else:
            raise Exception(msg)
    output = jsonify(resp)
    logging.info(output.get_data(as_text=True))
    return output
