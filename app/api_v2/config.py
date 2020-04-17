import os

from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.libs.get_data import read_json, splitN


class TemplateItem(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    def get(self):
        dir_app = current_app.config['PRE_REPORT']
        dir_pgm_remplate = os.path.join(dir_app, 'template_config', 'template_pgm.json')
        config = read_json(dir_pgm_remplate, 'config')
        gene_card = read_json(dir_pgm_remplate, 'gene_card')
        transcript = read_json(dir_pgm_remplate, 'transcript')

        template_item = {'item': [{'value': cc['item'], 'label': cc['item']} for cc in config]}
        return jsonify(template_item)

