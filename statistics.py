import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from scikit_posthocs import posthoc_ttest,posthoc_mannwhitney
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
    n=3
    #todo: use this plot for statistic
    for c in set(data["condition"]):
        print(c, data[data["condition"]==c]["pearson"].median(),data[data["condition"]==c]["pearson"].mean(),data[data["condition"]==c]["pearson"].std(), len(data[data["condition"]==c]["pearson"]))
    data["translation"].mean(), data["translation"].std()
    ax = sns.boxplot(data=data, orient="v",x="condition", y="pearson", palette=c_palette,
        medianprops={"color": "black"})
    sns.swarmplot(data=data, orient="v",x="condition", y="pearson", c="black")
    # for key,value in data.items():
    #     plt.plot([0,1], value, linestyle='dotted',  marker="o", markersize=6)

    for i in range(n):
        for j in range(n-1 - i):
            j += i + 1
            p_value = significance.iloc[i, j]
            plot_significance( i,  j, p_value, height=0.2+(j - i)*0.1)


    ax.set_xlabel('condition', fontsize=16)
    ax.set_ylabel('PCC', fontsize=16)

    ax.tick_params(axis='both', labelsize=16)
    #ax.set_yticks(np.arange(0,.8,0.2))
    plt.savefig(r"D:\Daten\Stefan\RIM_PSD\results.svg")
    plt.show()


def plot_distances(data):
    for i,c in enumerate(set(data["condition"])):
        ax = sns.histplot(data=data[data["condition"]==c], x="translation",  color=c_palette[c], binwidth=100, binrange=(0,1100), alpha=1)
        ax.set_xlabel('distance [nm]', fontsize=16)
        ax.set_ylabel('count', fontsize=16)

        ax.tick_params(axis='both', labelsize=16)
        ax.set_xlim(0)
        plt.title(c, fontsize=24, fontweight="bold")
        plt.savefig(fr"D:\Daten\Stefan\RIM_PSD\hist{i}.svg")
        plt.show()

if __name__ == '__main__':
    HOMER_BASSOON = "230824_Homer1_ATTO643_Bassoon_CF568_CaV21_AF488_pansCF405"
    RIM_PSD = "230824_PSD95_CF568_RIM12_AF488_VGlut1_ATTO643_panExM _CF405"
    GLUA_MUNC = "230825_GluA1_ATTO643_LGI1_CF568_Munc13_AF488_PanExM"
    #todo: dataframes for all three conditions
    conditions = [HOMER_BASSOON, RIM_PSD, GLUA_MUNC]
    c_names = ["Homer1-Bassoon", "PSD95-RIM 1/2", "GluA1-Munc 13-1"]
    c_palette = {"Homer1-Bassoon":"#ffe74c", "PSD95-RIM 1/2":"#ff5964", "GluA1-Munc 13-1":"#38618c"}

    df = []

    for i,c in enumerate(conditions):
        base = rf"D:\Daten\Stefan\Revision\Frotiers Review\{c}\outputs"
        #base = "outputs"
        scores = pd.read_csv(os.path.join(base,"scores.txt"))
        scores = scores.set_index("file_name")
        files = os.listdir(base)
        n = 0
        for folder in files:
            if folder.split(".")[-1] == "txt":
                continue
            culture = folder
            dir = os.path.join(base,folder)
            files = os.listdir(dir)
            for file in files:

                suffix = ["worst","3D"]
                post = "best"
                for s in suffix:
                    if s in file:
                        post = s

                if post == "worst":
                    continue
                condition = "ch_[0, 1]_mix_False" if c != GLUA_MUNC else "ch_[0, 2]_mix_False"
                path = os.path.join(dir,file,condition)
                if not os.path.exists(os.path.join(path, "data.txt")):
                    continue
                #todo: read filename as primary key
                score = scores[scores.index == file]
                if score["quality"][0].lower() == "out" or score["quality"][0].lower() == "review":
                    continue
                data = pd.read_csv(os.path.join(path, "data.txt"),sep="\t")
                #todo: also read transform
                transform_parameters = pd.read_csv(os.path.join(path, "tmp/affine0.txt"),sep="\t").iloc[-2].values[0]
                regionprops = pd.read_csv(os.path.join(path, "properties.txt"),sep="\t")
                transform_parameters = transform_parameters.replace(")","").split(" ")
                parameters = []
                for value in transform_parameters:
                    try:
                        parameters.append(float(value))
                    except ValueError:
                        print(f"{value} is not a float")
                data["rotation"] = abs(parameters[0]/(2*np.pi)*360)
                data["translation"] = np.sqrt(parameters[-1]**2+parameters[-2]**2)*41.1769
                data["culture"] = culture
                data["condition"] = c_names[i]
                data["subculture"] = post
                orientation = regionprops["orientation"][0]
                ab = math.sqrt(parameters[-1]**2+parameters[-2]**2)*math.sqrt(math.cos(orientation)**2+math.sin(orientation)**2)
                dot = math.acos((math.cos(orientation)*parameters[-1]+math.sin(orientation)*parameters[-2])/ab)/(2*np.pi)*360
                data["orientation"] = dot
                p = data["pearson"]
                #if np.sqrt(parameters[-1]**2+parameters[-2]**2)<5 or p[0]<0.4:
                #    continue
                df.append(data)

                if dot <60:
                    print(file)
                n+=1

                #if equal pearson throw
                # condition2 = "ch_[0, 1]_mix_True"
                # path = os.path.join(dir,file,condition2)
                # data = pd.read_csv(os.path.join(path, "data.txt"),sep="\t")
                # transform_parameters = pd.read_csv(os.path.join(path, "tmp/affine0.txt"),sep="\t").iloc[-2].values[0]
                # transform_parameters = transform_parameters.replace(")","").split(" ")
                # parameters = []
                # for value in transform_parameters:
                #     try:
                #         parameters.append(float(value))
                #     except ValueError:
                #         pass
                #         #print(f"{value} is not a float")
                # data["rotation"] = abs(parameters[0]/(2*np.pi)*360)
                # data["translation"] = np.sqrt(parameters[-1]**2+parameters[-2]**2)
                # data["culture"] = culture
                # data["condition"] = condition2
                # data["subculture"] = post
                # df.append(data)
                # condition3 = "difference"
                # data3 = data.copy()
                # data3["condition"] = condition3
                # data3["pearson"] = p-data["pearson"]
                # df.append(data3)
                # if data3["rotation"][0]>20:
                #     print(culture, file)
                # if p[0] == data["pearson"][0]:
                #     raise ValueError(f"pearsons shouldnt be equal {file}")
        print(n)
    df = pd.concat(df)
    for c in c_names:
        data = df.loc[df["condition"]==c]["pearson"].to_numpy()
        print(c, shapiro(data))
    significance = posthoc_ttest(df, "pearson", "condition")
    print(significance)
    print(df["translation"].mean(),df["translation"].std())
    #df.hist(column="translation", by="condition")
    plot_rim_psd(df, c_palette, significance)#df.boxplot(column="pearson", by="condition")
    plot_distances(df)
    # plt.savefig("tmp.svg")
    # plt.show()
