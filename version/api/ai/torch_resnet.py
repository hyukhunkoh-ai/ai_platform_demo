import datetime
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F


from version.fastprogress import master_bar, progress_bar
from version.api.parsers import Converter
from plot_utils import Resnet_Plot_Class
from version.config import root_path
from version.api.sql import conn, cursor

from version.api.ai.ai_utils import Base_insert, define_argparser, Base_subprocess
from version.api.ai.ai_utils import process_torch_data, process_cols




now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
model = 'Resnet'
isnn = True
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#######################################################################


class Resnet():
    '''
    This is Resnet model
    '''
    def __init__(self, x, y=None, lr=0.001, epochs=30, bs=16, classes=3, load_model=None, mode='train'):
        self.init_model(load_model, classes,x[:bs])
        self.init_params(x, y, lr, epochs, bs, classes, mode)

    def train(self, uid): # uid, modelname for save path
        self.uid = uid
        self.model.train()
        ########
        train_loader = self.make_data_loader('train')
        ########
        tpath = os.path.join(root_path, 'customers', uid, 'progress.txt')
        mb = master_bar(range(1, self.epochs + 1))
        ########
        _isadd_linear = False
        for epoch in mb:
            #####
            mb.main_bar.comment = f'epoch iter bar'
            #####
            train_loss = 0
            correct = 0
            total = 0

            for batch_idx, (data, target) in zip(progress_bar(range(len(train_loader)), parent=mb), train_loader):
                mb.child.comment = f'batch iter bar'
                with open(tpath, 'w') as f:
                    f.write(mb.html_code)
                data, target = data.to(device), target.to(device)
                output = self.model(data)
                ###########
                loss = self.criterion(output, target)  # -로그 라이클리 후드
                #########
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                ###############

                train_loss += loss.item()
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()

                ##########



                #############

            # 트레인 결과출력
            self.t_acc = 100 * correct / total
            self.model.acc_list.append(self.t_acc)
            self.t_loss = train_loss / (batch_idx + 1)
            self.model.loss_list.append(self.t_loss)
        ###########
        # mb.write(f'Finished epoch: {epoch}.')

        # print('train epoch : {} [{}/{}]| loss: {:.3f} | acc: {:.3f}'.format(
        #     epoch, batch_idx, len(train_loader) - 1, self.t_loss, self.t_acc))

        mb.show()
        with open(tpath, 'w') as f:
            f.write(mb.html_code)
            f.write("<div style='display:none'>END__EPOCH</div>")


        ############

    def predict(self):
        self.model.eval()
        # Test mode
        test_loader = self.make_data_loader('predict')

        with torch.no_grad():
            i = 0
            for batch_idx, (inputs) in enumerate(test_loader):
                inputs = inputs[0].to(device)
                if i == 0:
                    self.preds = self.model(inputs)
                    i = -1
                else:
                    self.preds = torch.cat((self.preds, self.model(inputs)), 0)

        # print('test epoch : {} [{}/{}]| loss: {:.3f} | acc: {:.3f}'.format(
        #     epoch, batch_idx, len(test_loader) - 1, self.tt_loss , self.tt_acc))

    def init_model(self, load_model, classes,sample_x):
        if load_model != None:
            self.model = load_model.to(device)

        elif load_model == None:
            num_blocks = [2, 2, 2]
            self.model = ResLayer(ResBlock, num_blocks, classes,sample_x).to(device)

    def init_params(self, x, y, lr, epochs, bs, classes, mode):
        self.lr = lr
        self.epochs = epochs
        self.mode = mode
        if mode == 'train':
            self.criterion = nn.CrossEntropyLoss()
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            self.x = x
            self.y = y
            self.bs = bs
            self.classes = classes
            self.t_acc, self.tt_acc, self.t_loss, self.tt_loss = 0, 0, 0, 0

        elif mode == 'retrain':
            self.criterion = nn.CrossEntropyLoss()
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            self.x = x
            self.y = y
            self.bs = bs
            self.classes = classes
            self.t_acc, self.tt_acc, self.t_loss, self.tt_loss = 0, 0, 0, 0

        elif mode == 'predict':
            self.x = x
            self.bs = bs


    def make_data_loader(self,mode_type):
        if mode_type == 'train':
            tensor_data = torch.utils.data.TensorDataset(torch.Tensor(np.array(self.x)).to(device),
                                                   torch.Tensor(np.array(self.y)).type(torch.LongTensor).to(device))
            loader = torch.utils.data.DataLoader(tensor_data, batch_size=self.bs, shuffle=True)
        elif mode_type == 'predict':
            tensor_data = torch.utils.data.TensorDataset(torch.Tensor(np.array(self.x)).to(device))
            loader = torch.utils.data.DataLoader(tensor_data, batch_size=self.bs)
        else:
            loader = None

        return loader

    def __repr__(self):
        res = f'{self.__class__.__name__}'
        print(f"{res} is RESNET HANDLER")

    def get_result(self):
        return {'train_acc': self.t_acc, 'pred_acc': self.tt_acc, 'train_loss': self.t_loss,
                'preds_loss': self.tt_loss}

    def get_model(self):
        return self.model

    def get_predict(self):
        get_answer = nn.Softmax()
        res = get_answer(self.preds).to('cpu').numpy().argmax(-1)
        # res = get_answer(self.preds).to('cpu').numpy()
        return res

    def __getattr__(self, item):
        return getattr(self.model, item)

    def res_plot(self,chart_name):
        res = dict()
        plot_tool = Resnet_Plot_Class(chart_name,self.uid)

        list_batches = ['mean_list', 'std_list']
        list_epochs = ['loss_list', 'acc_list']
        for batch_cat in list_batches:
            cat_values = getattr(self.model, batch_cat)
            plot_tool.plot_batch(cat_values, batch_cat)
        for epoch_cat in list_epochs:
            cat_values = getattr(self.model, epoch_cat)
            if epoch_cat == 'acc_list':
                value = max(cat_values)
                for idx,temp in enumerate(cat_values):
                    if temp == value:
                        _epoch = idx + 1
                        break
                label = f'epoch({_epoch}) :{round(value,3)}'
                plot_tool.plot_epoch(cat_values, epoch_cat,title=label)
            else:
                plot_tool.plot_epoch(cat_values, epoch_cat)


        return res

class ResLayer(nn.Module):
    # num class는 클래시피케이션 개수, block은 레지듀얼블락, num_blocks는 블락을 몇개 엮을지
    '''
    ResNet layer
    '''
    def __init__(self, block, num_blocks, num_classes,sample_x=None):
        super().__init__()
        # 처음에는 8채널로 시작
        self.layers = self.out_layer(block, num_blocks, num_classes,sample_x)
        self.mean_list = [[] for _ in range(len(self.layers))]
        self.std_list = [[] for _ in range(len(self.layers))]
        self.loss_list = []
        self.acc_list = []


    def out_layer(self,block, num_blocks, num_classes,sample_x):
        self.num_classes = num_classes
        _layers = []
        _x = torch.Tensor(np.array(sample_x))
        _layers.append(nn.Conv1d(1, 8, kernel_size=3,
                               stride=1, padding=1))
        _layers.append(self._make_layer(block, 8, 16, num_blocks[0], stride=1))
        _layers.append(nn.MaxPool1d(2))
        _layers.append(self._make_layer(block, 16, 32, num_blocks[1], stride=1))
        _layers.append(nn.MaxPool1d(2))
        _layers.append(self._make_layer(block, 32, 64, num_blocks[2], stride=1))
        _layers.append(nn.Flatten())
        for l in _layers:
            _x = l(_x)
        lin1_num = _x.shape[-1]
        lin1_outnum = lin1_num / 2**4
        _layers.append(nn.Linear(lin1_num, int(lin1_outnum)))
        _layers.append(nn.ReLU())
        _layers.append(nn.Linear(int(lin1_outnum), self.num_classes))

        return nn.ModuleList(nn.Sequential(*_layers))


    def _make_layer(self, block, in_plane, planes, num_blocks, stride):
        # 입력받은 블락 개수만큼 엮어서 레이어 생성
        self.in_plane = in_plane
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_plane, planes, stride))
            self.in_plane = planes * block.expansion
        return nn.Sequential(*layers)


    def forward(self, x):
        for i,layer in enumerate(self.layers):
            x = layer(x)
            self.mean_list[i].append(x.data.mean().item())
            self.std_list[i].append(x.data.std().item())
        return x

class ResBlock(nn.Module):
    '''
    ResNet Blocks
    '''
    expansion = 1

    def __init__(self, in_planes, planes, stride=1, kernel_size=3):
        super().__init__()

        self.bn1 = nn.BatchNorm1d(in_planes)
        self.conv1 = nn.Conv1d(in_planes, planes, kernel_size=kernel_size,stride=stride, padding=1)
        self.bn2 = nn.BatchNorm1d(planes)
        self.conv2 = nn.Conv1d(planes, planes, kernel_size=kernel_size,
                               stride=stride, padding=1)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_planes, self.expansion * planes,
                          kernel_size=1, stride=stride),
                nn.BatchNorm1d(self.expansion * planes)
            )

    def forward(self, x):
        h = self.bn1(x)
        h = F.relu(h)
        h = self.conv1(h)
        h = F.relu(self.bn2(h))
        h = self.conv2(h)

        return self.shortcut(x) + h



# resnet 생성


###############################################


class Resnet_insert(Base_insert):
    def __init__(self,config,conn,cursor):
        super(Resnet_insert, self).__init__(config,conn,cursor)
        self.hyper_parameter = str({'epcohs': self.config.epochs, 'lr': self.config.lr, 'bs': self.config.bs})
        self.loss = self.config.loss

    def train_insert(self):
        super(Resnet_insert, self).train_insert()



class Supprocess_run(Base_subprocess):
    '''
    subprocess.run(
        args=[sys.executable, py_path, '--data_file', dataset, '--mode', 'retrain', '--model_file', model_file, '--uid',
              uid, '--epochs', ep, '--lr', lr, '--bs', bs], capture_output=True, encoding='utf-8')
    '''

    def __init__(self, config, mode='train', col_list=None, src_type='csv',num_cols=None):
        '''
        necessary input :  config, mode, src_type
        optional : col_list, num_cols
        '''
        super(Supprocess_run, self).__init__(config,model,now,root_path,mode,isnn,column_list=col_list,src_type=src_type,num_cols=num_cols)
        self.name = self.model + "_" + self.uid + "_" + self.now + '.0.pt'

    def train(self):
        x, process_y = process_torch_data(self.x, self.y)

        resnet = Resnet(x,process_y,self.lr,self.epochs,self.bs,self.num_outputs)
        temp_path = os.path.join(root_path, 'customers', self.uid, 'model', "{}".format(self.name))
        temp_path = self.model_name_duplicate_check(temp_path)
        resnet.train(self.uid)
        resnet.res_plot(self.name)
        result = resnet.get_result()
        trained_model = resnet.get_model()

        torch.save(trained_model, temp_path)

        self.loss = result['train_loss']
        self.acc = result['train_acc']

        self.set_train_config()

        return self.config, resnet
    #

    def retrain(self):
        x, process_y = process_torch_data(self.x, self.y)

        retrain_model = torch.load(self.model_path)
        resnet = Resnet(x, process_y, self.lr, self.epochs, self.bs, self.num_outputs,load_model=retrain_model)
        resnet.train(self.uid)
        temp_path = os.path.join(root_path, 'customers', self.uid, 'model', "{}".format(self.new_name))
        temp_path = self.model_retrain_times_check(temp_path)
        temp_path = self.model_name_duplicate_check(temp_path, retrain=True)
        result = resnet.get_result()
        resnet.res_plot(self.new_name)
        retrained_model = resnet.get_model()


        torch.save(retrained_model, temp_path)

        self.loss = result['train_loss']
        self.acc = result['train_acc']

        self.set_retrain_config()

        return self.config, resnet

    def predict(self):

        x, _ = process_torch_data(self.x, None)

        load_model = torch.load(self.model_path)
        resnet = Resnet(x, load_model=load_model, mode='predict')  # x,y,lr,epochs,bs,labels 개수
        resnet.predict()
        result = resnet.get_predict()

        df = pd.DataFrame(result).reset_index()
        df.columns = ['x_row','preds']
        converter = Converter()
        converter.df_to_redis(self.config.filename, df)
        self.set_predict_config()

        return self.config, resnet




if __name__ == '__main__':
    config = define_argparser()

    mode = config.mode
    src_type = config.src_type.strip()
    columns, num_cols = process_cols(config)

    run = Supprocess_run(config, mode, col_list=columns,src_type=src_type,num_cols=num_cols)

    if mode == 'train':
        train_config, resnet = run.train()
        insert = Resnet_insert(train_config,conn,cursor)
        insert.train_insert()
        print(train_config.eval)
        print(train_config.train_name)


    elif mode == 'predict':
        predict_config, resnet = run.predict()
        insert = Resnet_insert(predict_config,conn,cursor)
        insert.predict_insert()
        print(predict_config.pred_name)

    elif mode == 'retrain':
        retrain_config, resnet = run.retrain()
        insert = Resnet_insert(retrain_config, conn, cursor)
        insert.retrain_insert()
        print(retrain_config.eval)
        print(retrain_config.retrain_name)
