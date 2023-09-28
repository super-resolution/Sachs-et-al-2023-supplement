import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns

#RIMPSD
def plot_rim_psd():
    data = {"5043":[.47, .34],"5044_1":[.77,.46],"5044":[.47,.35],"5046":[.61,.50],"5047":[.35,.31],"5050":[.58,.35],"5051":[.79, .67], }
    dat = pd.DataFrame(data).T
    dat["difference"] = dat[0] - dat[1]
    dat=dat.rename(columns={0:"original data",1:"randomized"})
    ax = sns.boxplot(data=pd.melt(dat), orient="v",x="variable", y="value", boxprops={"facecolor": (.0, .0, .0, .1)},
        medianprops={"color": "black"}, )
    for key,value in data.items():
        plt.plot([0,1], value, linestyle='dotted',  marker="o", markersize=6)

    ax.set_xlabel('condition', fontsize=16)
    ax.set_ylabel('PCC', fontsize=16)

    ax.tick_params(axis='both', labelsize=16)
    ax.set_yticks(np.arange(0,.8,0.2))
    plt.savefig(r"D:\Daten\Stefan\RIM_PSD\results.svg")
    plt.show()

#MUNCGLUA
def plot_munc_glua():
    data = {"4595": [.57, .44], "4721": [.39, .42], "4723": [.59, .50], "4726_1": [.74, .56], "4726": [.55, .40],
            "4727_1": [.74, .44], "4727": [.62, .64], }
    dat = pd.DataFrame(data).T
    dat["difference"] = dat[0] - dat[1]
    dat = dat.rename(columns={0: "original data", 1: "randomized"})
    ax = sns.boxplot(data=pd.melt(dat), orient="v", x="variable", y="value", boxprops={"facecolor": (.0, .0, .0, .1)},
                     medianprops={"color": "black"})
    for key, value in data.items():
        plt.plot([0, 1], value, linestyle='dotted', marker="o", markersize=6)

    ax.set_xlabel('condition', fontsize=16)
    ax.set_ylabel('PCC', fontsize=16)

    ax.tick_params(axis='both', labelsize=16)

    ax.set_yticks(np.arange(0,.74,0.2))
    plt.savefig(r"D:\Daten\Stefan\munc\results.svg")
    plt.show()

if __name__ == '__main__':
    matplotlib.rcParams['font.sans-serif'] = "Arial"
    plot_rim_psd()