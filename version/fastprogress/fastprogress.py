
__all__ = ['ProgressBar', 'MasterBar', 'NBProgressBar', 'NBMasterBar', 'NO_BAR', 'WRITER_FN', 'FLUSH', 'SAVE_PATH',
           'SAVE_APPEND', 'MAX_COLS', 'printing', 'ConsoleProgressBar', 'print_and_maybe_save', 'ConsoleMasterBar',
           'master_bar', 'progress_bar', 'force_console_behavior', 'workaround_empty_console_output']

# Cell
import time,os,shutil
from sys import stdout
from warnings import warn
from .core import *

# Cell
class ProgressBar():
    update_every,first_its = 0.2,5

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, master=None, comment=''):
        self.gen,self.parent,self.master,self.comment = gen,parent,master,comment
        self.total = len(gen) if total is None else total
        self.last_v = 0
        if parent is None: self.leave,self.display = leave,display
        else:
            self.leave,self.display=False,False
            parent.add_child(self)
        self.last_v = None

    def on_iter_begin(self):
        if self.master is not None: self.master.on_iter_begin()

    def on_interrupt(self):
        if self.master is not None: self.master.on_interrupt()

    def on_iter_end(self):
        if self.master is not None: self.master.on_iter_end()

    def on_update(self, val, text): pass

    def __iter__(self):
        if self.total != 0: self.update(0)
        try:
            for i,o in enumerate(self.gen):
                if i >= self.total: break
                yield o
                self.update(i+1)
        except Exception as e:
            self.on_interrupt()
            raise e

    def update(self, val):
        if self.last_v is None:
            self.on_iter_begin()
            self.last_v = 0
        if val == 0:
            self.start_t = self.last_t = time.time()
            self.pred_t,self.last_v,self.wait_for = 0,0,1
            self.update_bar(0)
        elif val <= self.first_its or val >= self.last_v + self.wait_for or val >= self.total:
            cur_t = time.time()
            avg_t = (cur_t - self.start_t) / val
            self.wait_for = max(int(self.update_every / (avg_t+1e-8)),1)
            self.pred_t = avg_t * self.total
            self.last_v,self.last_t = val,cur_t
            self.update_bar(val)
            if val >= self.total:
                self.on_iter_end()
                self.last_v = None

    def update_bar(self, val):
        elapsed_t = self.last_t - self.start_t
        remaining_t = format_time(self.pred_t - elapsed_t)
        elapsed_t = format_time(elapsed_t)
        end = '' if len(self.comment) == 0 else f' {self.comment}'
        if self.total == 0:
            warn("Your generator is empty.")
            self.on_update(0, '100% [0/0]')
        else: self.on_update(val, f'{100 * val/self.total:.2f}% [{val}/{self.total} {elapsed_t}<{remaining_t}{end}]')

# Cell
class MasterBar(ProgressBar):
    def __init__(self, gen, cls, total=None):
        self.main_bar = cls(gen, total=total, display=False, master=self)

    def on_iter_begin(self): pass
    def on_interrupt(self):  pass
    def on_iter_end(self):   pass
    def add_child(self, child): pass
    def write(self, line):      pass
    def update_graph(self, graphs, x_bounds, y_bounds): pass

    def __iter__(self):
        for o in self.main_bar:
            yield o

    def update(self, val): self.main_bar.update(val)

# Cell
if IN_NOTEBOOK:
    try:
        from IPython.display import clear_output, display, HTML
        import matplotlib.pyplot as plt
    except:
        warn("Couldn't import ipywidgets properly, progress bar will use console behavior")
        IN_NOTEBOOK = False

# Cell
class NBProgressBar(ProgressBar):
    def on_iter_begin(self):
        super().on_iter_begin()
        self.progress = html_progress_bar(0, self.total, "")
        # if self.display: self.out = display(HTML(self.progress), display_id=True) #edit
        self.is_active=True

    def on_interrupt(self):
        self.on_update(0, 'Interrupted', interrupted=True)
        super().on_interrupt()
        self.on_iter_end()

    def on_iter_end(self):
        # if not self.leave and self.display: self.out.update(HTML(''))#edit
        self.is_active=False
        super().on_iter_end()

    def on_update(self, val, text, interrupted=False):
        self.progress = html_progress_bar(val, self.total, text, interrupted)
        # if self.display: self.out.update(HTML(self.progress))#edit
        if self.parent is not None: self.parent.show()#edit

# Cell
class NBMasterBar(MasterBar):
    names = ['train', 'valid']
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False, total_time=False):
        super().__init__(gen, NBProgressBar, total)
        if order is None: order = ['pb1', 'text', 'pb2']
        self.hide_graph,self.order = hide_graph,order
        self.report,self.clean_on_interrupt,self.total_time = [],clean_on_interrupt,total_time
        self.inner_dict = {'pb1':self.main_bar, 'text':""}
        self.text,self.lines = "",[]

    def on_iter_begin(self):
        self.html_code = '\n'.join([html_progress_bar(0, self.main_bar.total, ""), ""])
        # self.out = display(HTML(self.html_code), display_id=True)#edit

    def on_interrupt(self):
        if self.clean_on_interrupt: self.out.update(HTML(''))

    def on_iter_end(self):
        if hasattr(self, 'imgs_fig'):
            plt.close()
            self.imgs_out.update(self.imgs_fig)
        if hasattr(self, 'graph_fig'):
            plt.close()
            self.graph_out.update(self.graph_fig)
        if self.text.endswith('<p>'): self.text = self.text[:-3]
        if self.total_time:
            total_time = format_time(time.time() - self.main_bar.start_t)
            self.text = f'Total time: {total_time} <p>' + self.text
        if hasattr(self, 'out'): self.out.update(HTML(self.text))

    def add_child(self, child):
        self.child = child
        self.inner_dict['pb2'] = self.child
        #self.show()

    def show(self):
        self.inner_dict['text'] = self.text
        to_show = [name for name in self.order if name in self.inner_dict.keys()]
        self.html_code = '\n'.join([getattr(self.inner_dict[n], 'progress', self.inner_dict[n]) for n in to_show])
        # self.out.update(HTML(self.html_code))#edit

    def write(self, line, table=False):
        if not table: self.text += line + "<p>"
        else:
            self.lines.append(line)
            self.text = text2html_table(self.lines)

    def show_imgs(self, imgs, titles=None, cols=4, imgsize=4, figsize=None):
        if self.hide_graph: return
        rows = len(imgs)//cols if len(imgs)%cols == 0 else len(imgs)//cols + 1
        plt.close()
        if figsize is None: figsize = (imgsize*cols, imgsize*rows)
        self.imgs_fig, imgs_axs = plt.subplots(rows, cols, figsize=figsize)
        if titles is None: titles = [None] * len(imgs)
        for img, ax, title in zip(imgs, imgs_axs.flatten(), titles): img.show(ax=ax, title=title)
        for ax in imgs_axs.flatten()[len(imgs):]: ax.axis('off')
        if not hasattr(self, 'imgs_out'): self.imgs_out = display(self.imgs_fig, display_id=True)
        else: self.imgs_out.update(self.imgs_fig)

    def update_graph(self, graphs, x_bounds=None, y_bounds=None, figsize=(6,4)):
        if self.hide_graph: return
        if not hasattr(self, 'graph_fig'):
            self.graph_fig, self.graph_ax = plt.subplots(1, figsize=figsize)
            self.graph_out = display(self.graph_ax.figure, display_id=True)
        self.graph_ax.clear()
        if len(self.names) < len(graphs): self.names += [''] * (len(graphs) - len(self.names))
        for g,n in zip(graphs,self.names): self.graph_ax.plot(*g, label=n)
        self.graph_ax.legend(loc='upper right')
        if x_bounds is not None: self.graph_ax.set_xlim(*x_bounds)
        if y_bounds is not None: self.graph_ax.set_ylim(*y_bounds)
        self.graph_out.update(self.graph_ax.figure)

# Cell
NO_BAR = False
WRITER_FN = print
FLUSH = True
SAVE_PATH = None
SAVE_APPEND = False
MAX_COLS = 160

# Cell
def printing():
    return False if NO_BAR else (stdout.isatty() or IN_NOTEBOOK)

# Cell
class ConsoleProgressBar(ProgressBar):
    fill:str='█'
    end:str='\r'

    def __init__(self, gen, total=None, display=True, leave=True, parent=None, master=None, txt_len=60):
        self.cols,_ = shutil.get_terminal_size((100, 40))
        if self.cols > MAX_COLS: self.cols=MAX_COLS
        self.length = self.cols-txt_len
        self.max_len,self.prefix = 0,''
        #In case the filling char returns an encoding error
        try: print(self.fill, end='\r', flush=FLUSH)
        except: self.fill = 'X'
        super().__init__(gen, total, display, leave, parent, master)

    def on_interrupt(self):
        super().on_interrupt()
        self.on_iter_end()

    def on_iter_end(self):
        if not self.leave and printing():
            print(f'\r{self.prefix}' + ' ' * (self.max_len - len(f'\r{self.prefix}')), end='\r', flush=FLUSH)
        super().on_iter_end()

    def on_update(self, val, text):
        if self.display:
            if self.length > self.cols-len(text)-len(self.prefix)-4:
                self.length = self.cols-len(text)-len(self.prefix)-4
            filled_len = int(self.length * val // self.total) if self.total else 0
            bar = self.fill * filled_len + '-' * (self.length - filled_len)
            to_write = f'\r{self.prefix} |{bar}| {text}'
            if val >= self.total: end = '\r'
            else: end = self.end
            if len(to_write) > self.max_len: self.max_len=len(to_write)
            if printing(): WRITER_FN(to_write, end=end, flush=FLUSH)

# Cell
def print_and_maybe_save(line):
    WRITER_FN(line)
    if SAVE_PATH is not None:
        attr = "a" if os.path.exists(SAVE_PATH) else "w"
        with open(SAVE_PATH, attr) as f: f.write(line + '\n')

# Cell
class ConsoleMasterBar(MasterBar):
    def __init__(self, gen, total=None, hide_graph=False, order=None, clean_on_interrupt=False, total_time=False):
        super().__init__(gen, ConsoleProgressBar, total)
        self.total_time = total_time

    def add_child(self, child):
        self.child = child
        v = 0 if self.main_bar.last_v is None else self.main_bar.last_v
        self.child.prefix = f'Epoch {v+1}/{self.main_bar.total} :'
        self.child.display = True

    def on_iter_begin(self):
        super().on_iter_begin()
        if SAVE_PATH is not None and os.path.exists(SAVE_PATH) and not SAVE_APPEND:
            with open(SAVE_PATH, 'w') as f: f.write('')

    def write(self, line, table=False):
        if table:
            text = ''
            if not hasattr(self, 'names'):
                self.names = [name + ' ' * (8-len(name)) if len(name) < 8 else name for name in line]
                text = '  '.join(self.names)
            else:
                for (t,name) in zip(line,self.names): text += t + ' ' * (2 + len(name)-len(t))
            print_and_maybe_save(text)
        else: print_and_maybe_save(line)
        if self.total_time:
            total_time = format_time(time() - self.start_t)
            print_and_maybe_save(f'Total time: {total_time}')

    def show_imgs(*args, **kwargs): pass
    def update_graph(*args, **kwargs): pass

# Cell
# if IN_NOTEBOOK: master_bar, progress_bar = NBMasterBar, NBProgressBar
# else:           master_bar, progress_bar = ConsoleMasterBar, ConsoleProgressBar
master_bar, progress_bar = NBMasterBar, NBProgressBar
# Cell
#nbdev_comment _all_ = ['master_bar', 'progress_bar']

# Cell
def force_console_behavior():
    "Return the console progress bars"
    return ConsoleMasterBar, ConsoleProgressBar

# Cell
def workaround_empty_console_output():
    "Change console output behaviour to correctly show progress in consoles not recognizing \r at the end of line"
    ConsoleProgressBar.end = ''