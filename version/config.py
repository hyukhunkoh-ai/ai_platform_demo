import os
host_addr = '0.0.0.0'
port_num = '8080'

db_ip = '192.168.0.67'
db_port = 3306
db_id = 'mct'
db_ps = '1234'
# db_ip = '127.0.0.1'
# db_id = 'root'
db_name = 'ai_platform'


redis_ip = '127.0.0.1'
redis_port = 6379

root_path = os.path.dirname(os.path.realpath(__file__))

db_table_list = ['cols_view', 'EngineLive', 'log_history', 'logins', 'model_name', 'Results','ResultLive']