import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from scikit_posthocs import posthoc_ttest
import math
from scipy.stats import shapiro

def plot_significance(x1, x2, p, height=0, start=1.1):
    if 5.00e-02 < p <= 1.00e+00:
        significance = "ns"
    elif 1.00e-02 < p <= 5.00e-02:
        significance = "*"
    elif 1.00e-03 < p <= 1.00e-02:
        significance = "**"
    elif 1.00e-04 < p <= 1.00e-03:
        significance = "***"
    elif p <= 1.00e-04:
        significance = "****"
    y, h, col = start, height, 'k'
    plt.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c='k', alpha=1)
    if height <0:
        plt.text((x1 + x2) * .5, y + h, significance, ha='center', va='top', color=col)
    else:
        plt.text((x1 + x2) * .5, y + h, significance, ha='center', va='bottom', color=col)

def plot_rim_psd(data, c_palette, significance):
    n = 2
    for c in set(data["condition"]):
        print(c, data[data["condition"]==c]["pearson"].median(),data[data["condition"]==c]["pearson"].mean(),data[data["condition"]==c]["pearson"].std(), len(data[data["condition"]==c]["pearson"]))
    ax = sns.boxplot(data=data, orient="v",x="condition", y="pearson", palette=c_palette,
        medianprops={"color": "black"})
    sns.swarmplot(data=data, orient="v",x="condition", y="pearson", c="black")
    # for key,value in data.items():
    #     plt.plot([0,1], value, linestyle='dotted',  marker="o", markersize=6)

    ax.set_xlabel('condition', fontsize=16)
    ax.set_ylabel('PCC', fontsize=16)

    ax.tick_params(axis='both', labelsize=16)
    for i in range(n):
        for j in range(n-1 - i):
            j += i + 1
            p_value = significance.iloc[i, j]
            plot_significance( i,  j, p_value, height=0.2+(j - i)*0.1)
    #ax.set_yticks(np.arange(0,.8,0.2))
    plt.savefig(r"D:\Daten\Stefan\RIM_PSD\LGI1.svg")
    plt.show()

if __name__ == '__main__':
    LGI1 = "LGI1"
    #todo: dataframes for all three conditions
    conditions = [LGI1]
    c_palette = {"GluA1 - LGI1":"#ffe74c", "LGI1 - Munc 13-1":"#ff5964"}
    df = []
    base = rf"D:\Daten\Stefan\Revision\Frotiers Review\{LGI1}\outputs_LGI1"
    #base = "outputs"

    files = os.listdir(base)
    n = 0
    for folder in files:
        if folder.split(".")[-1] == "txt" or folder.split(".")[-1] == "svg" :
            continue
        culture = folder
        dir = os.path.join(base,folder)
        files = os.listdir(dir)
        for file in files:

            for condition,name in zip(["ch_[0, 1]_mix_False", "ch_[1, 2]_mix_False"],["GluA1 - LGI1", "LGI1 - Munc 13-1"]):
                path = os.path.join(dir,file,condition)
                if not os.path.exists(os.path.join(path, "data.txt")):
                    continue
                data = pd.read_csv(os.path.join(path, "data.txt"),sep="\t")
                parameters = []

                data["culture"] = culture
                data["condition"] = name
                p = data["pearson"]
                #if np.sqrt(parameters[-1]**2+parameters[-2]**2)<5 or p[0]<0.4:
                #    continue
                df.append(data)


                n+=1
        print(n)
    df = pd.concat(df)
    for c in c_palette.keys():
        data = df.loc[df["condition"]==c]["pearson"].to_numpy()
        print(c, shapiro(data))
    significance = posthoc_ttest(df, "pearson", "condition")
    print(significance)

    #df.hist(column="translation", by="condition")
    plot_rim_psd(df, c_palette, significance)#df.boxplot(column="pearson", by="condition")
