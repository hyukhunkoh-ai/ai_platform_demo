from flask import Blueprint

api = Blueprint('api', __name__)

from version.api.flask import ai_post, excel_post, log_post, live_engine_post, view_post, redis_post, live_model_chart_post, live_result_post

