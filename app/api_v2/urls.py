from flask_restful import Api
from app.api_v2 import api_v2

my_api = Api(api_v2)

# 用户相关
from app.api_v2.user import LoginView, LoginOut, GetInfo

my_api.add_resource(LoginView, '/user/login')
my_api.add_resource(LoginOut, '/user/logout')
my_api.add_resource(GetInfo, '/user/get_info')

# 文件上传
from app.api_v2.upload import SampleInfoUpload, RunInfoUpload, MutationUpload, OKRUpload, IrUpload, SampleRecordUpload

my_api.add_resource(SampleInfoUpload, '/upload/sample_info_upload')  # 样本信息上传
my_api.add_resource(RunInfoUpload, '/upload/run_info_upload')  # 上机信息上传
my_api.add_resource(MutationUpload, '/upload/mutation_upload/')  # 突变结果上传
my_api.add_resource(OKRUpload, '/upload/okr/')
my_api.add_resource(IrUpload, '/upload/ir_upload/')
my_api.add_resource(SampleRecordUpload, '/upload/sample_record/')

# 获取数据
from app.api_v2.get_data import GetAllSample, GetRunInfo, GetSeqInfo

my_api.add_resource(GetAllSample, '/data/get_sample_info')  # 样本信息获取
my_api.add_resource(GetRunInfo, '/data/get_run_info/')
my_api.add_resource(GetSeqInfo, '/data/get_seq_info/')

# okr
from app.api_v2.okr import OkrAnnotate, OkrResult
my_api.add_resource(OkrAnnotate, '/data/okr/')
my_api.add_resource(OkrResult, '/data/okrfile/')

# admin
from app.api_v2.admin import AdminSample, AdminTemplate, AdminUser

my_api.add_resource(AdminSample, '/admin/sample/')
my_api.add_resource(AdminTemplate, '/admin/template/')
my_api.add_resource(AdminUser, '/admin/user/')

# 报告
from app.api_v2.report import ReportStart, GetMutationList, ReportStage, EditMutation,\
    AnnotateMutation, AnnotateCheck, ExportReport

my_api.add_resource(ReportStart, '/report/start/') # 开始
my_api.add_resource(GetMutationList, '/report/mutation_list/')
my_api.add_resource(ReportStage, '/report/report_stage/')  # 改变报告状态
my_api.add_resource(EditMutation, '/report/edit_mutation/')  # 编辑突变
my_api.add_resource(AnnotateMutation, '/report/annotate_mutation/')  # 突变注释
# my_api.add_resource(AnnotateCheck, '/report/annotate_check/')  # 注释复核
my_api.add_resource(ExportReport, '/report/export_report/')  # 生成报告

# 前端配置

from app.api_v2.config import TemplateItem

my_api.add_resource(TemplateItem, '/config/template_item/')

# 样本录入

from app.api_v2.sample_record import SampleInfoRecord
my_api.add_resource(SampleInfoRecord, '/sample_record/')
