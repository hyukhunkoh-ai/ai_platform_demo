# if request.method == 'GET':
#     uid = session.get('loginid', None)
#
#     py_path = os.path.join(root_path, 'api', 'sql', 'redis_load.py')
#
#     p = subprocess.run(
#         args=[sys.executable, py_path,'--uid', uid,'--isredis','False','--filename',filename], capture_output=True, encoding='utf-8')
#
#     if p.stdout == '':
#         print(p.stderr)
#         raise ValueError('sub terminal error')
#     if filename.strip()[-4:] != '.csv':
#         filename = filename.strip() + '.csv'
#     else:
#         filename = filename.strip()
#     file_path = os.path.join(root_path, 'customers', uid, 'data_files', filename)
#     read_file = open(file_path, "rb")
#
#     @after_this_request
#     def remove_file(response):
#         os.remove(file_path)
#         return response
#
# return send_file(read_file,attachment_filename=filename)