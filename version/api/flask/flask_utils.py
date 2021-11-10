import json
import re

class Ai_post_utils():
    '''
    This is for ai_post.py
    '''

    @staticmethod
    def make_num_cols(column_list):
        '''
        input : columns
        output : length of columns
        content : get the len(x.columns) or ''
        '''
        if column_list == '[]' or column_list == []:
            num_cols = ''
        else:
            column_list_for_num = column_list.strip().split(',')
            if 'target' in column_list_for_num:
                column_list_for_num.remove('target')
            elif 'label' in column_list_for_num:
                column_list_for_num.remove('label')
            num_cols = len(column_list_for_num)
        return num_cols

    @staticmethod
    def hyper_parmas_spliter(hyper_params):
        '''
        input : hyper_parameter string
        output : epoch,learning rate,batch size
        content : string are split into parameters
        '''
        if hyper_params[-1] != '}':
            hyper_params = "{" + hyper_params + "}"

        try:
            hyper_params = json.loads(hyper_params)  # "epoch: 3, lr: 4, bs: 5"
            ep = str(hyper_params['epoch'])
            lr = str(hyper_params['lr'])
            bs = str(hyper_params['bs'])
        except:
            ep = '30'
            lr = '0.001'
            bs = '16'
        return ep, lr, bs



class Excel_post_utils():
    '''
    This is for ai_post.py
    '''

    @staticmethod
    def filter_html(html, attribute, content):
        '''
        input : html, attribute, value
        output : filtered html
        content : delete btn,tr,th tag with attrubute:value
        '''
        html = re.sub('<button.*?/button>', "", html)
        html = re.sub(f'<tr.*?{attribute}="{content}".*?/tr>', "", html)
        html = re.sub(f'<th.*?{attribute}="{content}".*?/th>', "", html)
        return html


