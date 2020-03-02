from flask_restful import Api
from app.api_v2 import api_v2

my_api = Api(api_v2)

# 用户相关
from app.api_v2.user import LoginView, LoginOut, GetInfo

my_api.add_resource(LoginView, '/user/login')
my_api.add_resource(LoginOut, '/user/logout')
my_api.add_resource(GetInfo, '/user/get_info')

# 文件上传
from app.api_v2.upload import SampleInfoUpload, RunInfoUpload

my_api.add_resource(SampleInfoUpload, '/upload/sample_info_upload')  # 样本信息上传
my_api.add_resource(RunInfoUpload, '/upload/run_info_upload')  # 上机信息上传

# 获取数据
from app.api_v2.get_data import GetAllSample, GetRunInfo, GetSeqInfo

my_api.add_resource(GetAllSample, '/data/get_sample_info')  # 样本信息获取
my_api.add_resource(GetRunInfo, '/data/get_run_info/')
my_api.add_resource(GetSeqInfo, '/data/get_seq_info/')

# admin
from app.api_v2.admin import AdminSample, AdminTemplate

my_api.add_resource(AdminSample, '/admin/sample/')
my_api.add_resource(AdminTemplate, '/admin/template/')