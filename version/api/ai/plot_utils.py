from version.config import root_path
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from sklearn import tree
from matplotlib.font_manager import FontProperties
plt.rcParams['font.family'] = "NanumGothic"
matplotlib.rcParams['axes.unicode_minus'] = False
fontP = FontProperties()
fontP.set_size('xx-small')



class Resnet_Plot_Class():
    '''
    resnet chart maker
    '''
    def __init__(self,name,uid=None):
        self.name = name
        self.uid = uid

    def plot_batch(self,items,label,title=None):
        '''
        draw and save the chart per layer for all batches
        mean & std
        '''
        fig = plt.figure()
        for i, data in enumerate(items):
            plt.plot(data, label=f'layer{i}')
            plt.xlabel('batch')
            plt.ylabel(label)
            plt.legend(bbox_to_anchor=(0.95, 1), loc='upper left',prop=fontP)
        if title:
            plt.title(title, fontsize=20)
        figname = self.name + '_' + label + '.png'
        save_path = os.path.join(root_path,'customers',self.uid,'charts',figname)
        fig.savefig(save_path)


    def plot_epoch(self,items,label,title=None):
        '''
        draw and save the chart per epoch
        loss & accuracy
        '''
        fig = plt.figure()
        plt.plot(items, label=f'model_{label}')
        plt.xlabel('epoch')
        plt.ylabel(label)
        plt.legend(bbox_to_anchor=(0.95, 1), loc='upper left',prop=fontP)
        if title:
            plt.title(title,fontsize=20)
        figname = self.name + '_' + label + '.png'
        save_path = os.path.join(root_path,'customers',self.uid,'charts',figname)
        fig.savefig(save_path)



class DT_Plot_Class():
    '''
    decision tree chart maker
    '''
    def __init__(self,name,uid,dtc):
        self.name = name
        self.uid = uid
        self.dt = dtc

    def tree_plot(self,label='tree'):
        '''
        draw and save the tree image with nodes & threshold.
        '''
        fig = plt.figure(figsize=(16, 9))
        tree.plot_tree(self.dt,
                       feature_names=self.dt.x_columns,
                       class_names=list(map(str, self.dt.classes_)),
                       filled=True)
        figname = self.name + '_' + label + '.png'
        save_path = os.path.join(root_path,'customers',self.uid,'charts',figname)
        fig.savefig(save_path)

    def fi_plot(self, label='feature_importance'):
        '''
        draw and save the feature importance plot
        '''
        fig = plt.figure(figsize=(16,9))
        sns.barplot(x=self.dt.feature_importances_, y=self.dt.x_columns)
        plt.title('feature_importance')
        figname = self.name + '_' + label + '.png'
        save_path = os.path.join(root_path,'customers',self.uid,'charts',figname)
        fig.savefig(save_path)
