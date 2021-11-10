from version.api.sql import rd
import json
import pandas as pd


class Converter():
    def __init__(self):
        pass

    def partial_from_csv_to_html(self,from_name, start_num=0, end_num=50, successive=False,extract_cols=None):
        '''
        input : csv_file_path, row_start, row_end, full html/part html, columns
        output : html code
        content : convert csv file to html code
        '''
        if from_name.strip()[-4:] == '.csv':
            inname = from_name.strip()
        else:
            inname = from_name.strip() + '.csv'

        start_num = int(start_num)
        end_num = int(end_num)
        csv = pd.read_csv(inname)
        self.total_length = len(csv)
        csv = csv.reset_index()
        csv = csv.iloc[start_num:end_num, :]

        csv.columns = ['idx'] + list(csv.columns[1:])
        if extract_cols:
            csv = csv[['idx'] + extract_cols]

        if not successive: return self.compose_html(csv)


        elif successive: return self.successive_compose_html(csv)


    # html 파일을 직접 다른 파이썬으로 전달
    def partial_from_redis_to_html(self,key, start_num=0, end_num=50,successive=False,extract_cols=None):
        '''
        input : redis table name, row_start, row_end, full html/part html, columns
        output : html code
        content : convert redis data to html code
        '''

        inname = key.strip()

        start_num = int(start_num)
        end_num = int(end_num)

        values = rd.hvals(inname)
        values = list(map(lambda x: json.loads(x), values))
        df = pd.DataFrame(values)
        self.total_length = len(df)

        df = df.iloc[start_num:end_num, :]
        df = df.reset_index()

        df.columns = ['idx'] + list(df.columns[1:])
        if extract_cols:
            df = df[['idx'] + extract_cols]

        if not successive: return self.compose_html(df)

        elif successive: return self.successive_compose_html(df)

    # at first from,to name foramt is directory format -- ~/train.csv
    # input from_name is changed into dataframe type
    def partial_from_html_to_csv(self,html, to_name, start_num=0, end_num=50):
        '''
        input : html, save_filepath, row_start, row_end
        output : None
        content : convert html_code to csv file merging with original csv file
        '''
        df = pd.read_html(html, index_col=0)[0].reset_index(drop=True)
        outname = to_name.strip()

        if outname[-4:] != '.csv':
            outname = outname + '.csv'

        start_num = int(start_num)
        end_num = int(end_num)

        original_csv = pd.read_csv(outname)

        temp_df = pd.DataFrame()

        for new in df.columns:
            if new in original_csv.columns:
                temp_df[new] = original_csv[new]
            else:
                temp_df[new] = None


        head_df = temp_df[:start_num]
        tail_df = temp_df[end_num:]

        res = pd.concat([head_df, df])
        res = pd.concat([res, tail_df])
        res = res.reset_index(drop=True)

        res.to_csv(outname,index=False)




    # actually from name is df
    def partial_from_html_to_csv_by_redis(self,html, to_name, start_num=0, end_num=50):
        '''
        input : html, save_filepath, row_start, row_end
        output : None
        content : convert html_code to csv file merging with redis file
        '''
        if to_name.strip()[-4:] == '.csv':
            outname = to_name.strip()
        else:
            outname = to_name.strip() + '.csv'
        df = pd.read_html(html, index_col=0)[0].reset_index(drop=True)
        start_num = int(start_num)
        end_num = int(end_num)


        values = rd.hvals(to_name.split('/')[-1]) # name가져오기
        values = list(map(lambda x: json.loads(x), values))
        original_csv = pd.DataFrame(values)


        temp_df = pd.DataFrame()
        # 열 다르면 추가
        for new in df.columns:
            if new in original_csv.columns:
                temp_df[new] = original_csv[new]
            else:
                temp_df[new] = None

        # if len(df) != (end_num - start_num): # 행의 개수가 변했을 경우
        head_df = temp_df[:start_num]
        tail_df = temp_df[end_num:]
        res = pd.concat([head_df, df])
        res = pd.concat([res, tail_df])
        res = res.reset_index(drop=True)

        res.to_csv(outname, index=False)



    def df_to_redis(self, name,df):
        '''
        input : tablename, dataframe
        put dataframe into redis
        '''
        redis_table = df.apply(lambda obj: obj.to_json(), axis=1)
        for k, v in redis_table.to_dict().items():
            rd.hset(name, k, v)

    def redis_to_df(self, name):
        '''
        input: tablename
        pull redis data and convert it into dataframe
        '''
        df = pd.DataFrame(list(map(lambda x: json.loads(x), rd.hvals(name))))
        return df

    def for_apply(self, obj):
        '''
        make tr(of html-table) with object(consisting of <td>s)
        used for dataframe.apply
        '''
        res = '<tr id="r{}" class="rows">'.format(int(obj.name) + 1)
        for idx, item in enumerate(obj):
            obj[idx] = item[:4] + 'data-col_id="c{}"'.format(idx + 1) + item[4:]
        con = "\n".join(obj)
        res += con + '</tr>'
        return res

    def compose_html(self,data):
        '''
        make dataframe to html
        input : dataframe
        output : converted html
        '''
        cols = ['<th data-col_id="c1" align="center" width="30px" > idx </th>']
        cols += [f'<th data-col_id="c{idx + 2}" align="center">' + i + '</th>' for idx, i in enumerate(data.columns[1:])]

        columns = "\n".join(cols)

        data = data.applymap(lambda x: '<td contenteditable="true" class="column" >' + str(x) + '</td>')
        data = data.apply(self.for_apply, axis=1)
        row_content = "\n".join(data.values)

        html = '''
            <table width="100%" id="main_table" cellpadding="1" cellspacing="0">
              <thead id="cell_heads" >
                <tr style="text-align: center;" id="row_cols">\n
        '''
        html += columns
        html += '''
            </tr>
          </thead>
          <tbody id="cell_contents" contenteditable="true">
        '''
        html += row_content
        html += '''
            </tbody>
        </table>
        '''
        return html

    def successive_compose_html(self,data):
        '''
        make dataframe to html content, not the whole frame
        input : dataframe
        output : converted html content
        '''
        data = data.applymap(lambda x: '<td contenteditable="true" class="column" >' + str(x) + '</td>')
        data = data.apply(self.for_apply, axis=1)
        row_content = "\n".join(data.values)
        return row_content



#config.model_fn이런식으로 접근

