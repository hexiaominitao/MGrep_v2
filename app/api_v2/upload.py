import os

from flask_restful import (reqparse, Resource, request)
from flask import (current_app)
from werkzeug.datastructures import FileStorage
from sqlalchemy import and_

from app.models import db
from app.models.run_info import RunInfo, SeqInfo
from app.libs.ext import file_sam
from app.libs.upload import save_json_file, excel_to_dict, get_excel_title, get_seq_info, excel2dict, df2dict, time_set


class SampleInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True, help='样本信息登记表')
        super(SampleInfoUpload, self).__init__()

    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        dict_sample = excel_to_dict(file, '样本信息登记表')
        dir_app = current_app.config['PRE_REPORT']
        dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
        save_json_file(dir_sample, dict_sample, '样本信息登记表')
        os.remove(file)
        return {'msg': '样本信息保存成功！！'}


class RunInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(RunInfoUpload, self).__init__()

    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        try:
            title = get_excel_title(file)
            print(title)
            if title in ['S5', 'PGM', 's5', 'pgm']:
                df_seq = get_seq_info(file)
                for name, df in df_seq:
                    if name:
                        dict_run = df2dict(df)
                        for dict_val in dict_run.values():
                            run = RunInfo.query.filter(RunInfo.name == name).first()
                            if run:
                                pass
                            else:
                                run = RunInfo(name=name, platform=title,
                                              start_T=time_set(dict_val.get('上机时间')),
                                              end_T=time_set(dict_val.get('结束时间')))
                                db.session.add(run)
                                db.session.commit()
                            seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('迈景编号')).first()
                            if seq:
                                pass
                            else:
                                seq = SeqInfo(sample_name=dict_val.get('迈景编号'), sample_mg=dict_val.get('申请单号'),
                                              item=dict_val.get('检测内容'), barcode=dict_val.get('Barcode编号'),
                                              note=dict_val.get('备注'))
                                db.session.add(seq)
                                run.seq_info.append(seq)
                            db.session.commit()
            else:
                dict_run = excel2dict(file)
                for dict_val in dict_run.values():
                    run = RunInfo.query.filter(RunInfo.name == dict_val.get('Run name')).first()
                    if run:
                        pass
                    else:
                        run = RunInfo(name=dict_val.get('Run name'), platform=title,
                                      start_T=time_set(dict_val.get('上机时间')),
                                      end_T=time_set(dict_val.get('下机时间')))
                        db.session.add(run)
                        db.session.commit()
                    seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('样本编号')).first()
                    if seq:
                        pass
                    else:
                        seq = SeqInfo(sample_name=dict_val.get('样本编号'),
                                      item=dict_val.get('检测项目'), barcode=dict_val.get('index(P7+P5)'),
                                      note=dict_val.get('备注'))
                        db.session.add(seq)
                        run.seq_info.append(seq)
                    db.session.commit()
            msg = '文件上传成功!'
        except IOError:
            msg = '文件有问题,请检查后再上传!!!!!'
        os.remove(file)
        return {'msg': msg}, 200
