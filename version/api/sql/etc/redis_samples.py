# sudo apt-get redis
# pip install redis

import redis

# 레디스 연결
rd = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

#
# # 레디스에 키-값 저장
# rd.set("[키]", "[값]")
#
#
# # 레디스에서 키를 사용해서 값 가져오기
# rd.get("[키]")
#
#
# # 레디스에서 키를 사용해서 값 가져오기
# rd.delete("[키]")
#
#
#
# # 레디스 DB 데이터 전체 삭제
# rd.flushdb()

'''
인코딩 / 디코딩 문제 (dict타입)
- Redis에 ASCII 문자열이 아닌 UTF-8 타입의 문자열을 저장하고 조회하면, decoding이 되지 않는 문제 발생

- 따라서 json의 dumps(), loads()를 사용해서, 데이터를 저장하고 읽어야한다.
# dict 데이터 선언
dataDict = {
    "key1": "테스트값1",
    "key2": "테스트값2",
    "key3": "테스트값3"
}

# json dumps
jsonDataDict = json.dumps(dataDict, ensure_ascii=False).encode('utf-8')

# 데이터 set
rd.set("dict", jsonDataDict)


# 데이터 get
resultData = rd.get("dict")
resultData = resultData.decode('utf-8')

# json loads 
result = dict(json.loads(resultData))

'''


## https://brunch.co.kr/@jehovah/20 레디스 정리페이지
## https://www.joinc.co.kr/w/man/12/REDIS/DataModeling 데이터 모델 정리 페이지
## https://realmojo.tistory.com/172 해쉬 관련 명령어 페이지
# table_name = 'train.csv'
# import csv
# import json
# with open(table_name, 'r') as f:
#     t = csv.reader(f)
#     num = 0
#     idx_hash = []
#     values = []
#     for r in t:
#
#         if num == 0:
#             # r[0] => index라고 가정
#             cols = r[1:]
#             num = -1
#         else:
#             temp_dict = dict()
#             idx_hash.append(r[0])
#             for idx, v in enumerate(r[1:]):
#                 temp_dict[cols[idx]] = v
#             values.append(temp_dict)
#
# assert len(idx_hash) == len(values)
# for i,j in zip(idx_hash, values):
#     rd.hset(table_name,i,json.dumps(j))

# res = json.dumps(res)

# rd.set(key,res)

##redis input
#####################################################
# redis_post
# import argparse
# import json
# import os
# import pandas as pd
#
# from version.api.sql import rd, root_path
#
#
#
# def redis_to_df(table_name):
#
#     # all_data = rd.hgetall(table_name)
#     rows = rd.hkeys(table_name)
#     values = rd.hvals(table_name)
#     values = list(map(lambda x: json.loads(x),values))
#     df = pd.DataFrame(values)
#
#     return df
#
# def redis_to_meta():
#     res = dict()
#     keys = rd.keys('*')
#     for k in keys:
#         values = rd.hvals(k)
#         cols = list(json.loads(values[0]).keys())
#         res[k] = cols
#
#     return res
#
#
#
# def define_argparser():
#
#     p = argparse.ArgumentParser()
#     p.add_argument(
#         '--uid',
#         required=True,
#         help='user id to be used for saving dataframe file'
#     )
#     p.add_argument(
#         '--isredis',
#         required=True,
#         default=False,
#         help='only redis? or to csv'
#     )
#     p.add_argument(
#         '--filename',
#
#         help='filename'
#     )
#     config = p.parse_args()
#
#     return config
#
#
# # for table in tables:
# # #     print(redis_to_df(table))
#
# if __name__ == '__main__':
#
#     config = define_argparser()
#     if config.isredis == 'True':
#         print(json.dumps(redis_to_meta()))
#
#     elif config.isredis == 'False':
#         uid = config.uid
#         _path = os.path.join(root_path, "customers", uid, 'data_files')
#         df = redis_to_df(config.filename)
#         save_path = os.path.join(_path, config.filename)
#         df.to_csv(save_path,index=False)
#         print('success')
#


table_name = 'reserve.csv'
import csv
import json
with open(table_name, 'r') as f:
    t = csv.reader(f)
    num = 0
    idx_hash = []
    values = []
    for r in t:

        if num == 0:
            # r[0] => index라고 가정
            cols = r[1:]
            num = -1
        else:
            temp_dict = dict()
            idx_hash.append(r[0])
            for idx, v in enumerate(r[1:]):
                temp_dict[cols[idx]] = v
            values.append(temp_dict)

assert len(idx_hash) == len(values)
for i,j in zip(idx_hash, values):
    rd.hset('iris.csv',i,json.dumps(j))