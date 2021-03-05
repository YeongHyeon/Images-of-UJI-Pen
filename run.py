import os, glob, shutil
import numpy as np
import matplotlib.pyplot as plt

def sorted_list(path):

    tmplist = glob.glob(path)
    tmplist.sort()

    return tmplist

def make_dir(path, refresh=False):

    try: os.mkdir(path)
    except:
        if(refresh):
            shutil.rmtree(path)
            os.mkdir(path)

def parsing_pen(list_pen):

    coord_x, coord_y = [], []
    for idx_p, pen in enumerate(list_pen):
        if('PEN_DOWN' in pen or 'PEN_UP' in pen): continue

        tmp_coord = pen.replace('\n', '').split(' ')
        while(True):
            try: tmp_coord.remove('')
            except: break

        x, y = int(tmp_coord[0]), -int(tmp_coord[1])
        coord_x.append(x)
        coord_y.append(y)

    coord_x, coord_y = np.asarray(coord_x), np.asarray(coord_y)
    return coord_x, coord_y

def main(savepath='images'):

    make_dir(path=savepath, refresh=True)

    list_set = sorted_list(os.path.join('dataset', 'UJIpenchars*'))

    for path_set in list_set:

        subpath = path_set.split('/')[-1]
        make_dir(path=os.path.join(savepath, subpath))

        fpen = open(path_set, 'r')
        contents = fpen.readlines()
        fpen.close()

        list_start, list_end = [], []
        idx_end = 0
        for idx_c, content in enumerate(contents):
            if('.SEGMENT CHARACTER' in content):
                if(len(list_start) > 1):
                    list_end.append(list_start[-1]-2)
                list_start.append(idx_c)

            if('.DT 100' in content):
                idx_end = idx_c
        list_end.append(list_start[-1]-2)
        list_end.append(idx_end)

        for idx, _ in enumerate(list_start):
            idx_s, idx_e = list_start[idx], list_end[idx]
            label = contents[idx_s+1].split('[')[-1].replace(']\n', '')

            contents_tmp = contents[idx_s:idx_e]
            idx_down = -1
            list_coord_x, list_coord_y = [], []
            for idx_c, content in enumerate(contents_tmp):
                if(idx_down == -1 and '.PEN_DOWN' in content):
                    idx_down = idx_c

                if(idx_down != -1 and '.PEN_UP' in content):
                    coord_x, coord_y = parsing_pen(contents_tmp[idx_down:idx_c])
                    list_coord_x.append(coord_x)
                    list_coord_y.append(coord_y)
                    idx_down = -1

            x_min, x_max, y_min, y_max = 1e+10, -1e+10, 1e+10, -1e+10
            for idx_c, _ in enumerate(list_coord_x):
                x_min = min(list_coord_x[idx_c].min(), x_min)
                x_max = max(list_coord_x[idx_c].max(), x_max)
                y_min = min(list_coord_y[idx_c].min(), y_min)
                y_max = max(list_coord_y[idx_c].max(), y_max)

            for idx_c, _ in enumerate(list_coord_x):
                list_coord_x[idx_c] = (list_coord_x[idx_c] - x_min) / (x_max - x_min)
                list_coord_y[idx_c] = (list_coord_y[idx_c] - y_min) / (y_max - y_min)

            plt.figure(figsize=(5, 3))
            for idx_c, _ in enumerate(list_coord_x):
                plt.title(label)
                plt.plot(list_coord_x[idx_c], list_coord_y[idx_c], label='pen %d' %(idx_c+1))
            plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
            plt.tight_layout()
            plt.savefig(os.path.join(savepath, subpath, '%06d-%s.png' %(idx, label)))
            plt.close()

if __name__ == '__main__':

    main(savepath='images')
