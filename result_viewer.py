import matplotlib.pyplot as plt
import os
from PIL import Image
import numpy as np
from matplotlib.widgets import Button
import pandas as pd

def result_viewer(path, file):
    p = os.path.join(path,file)
    data_path = os.path.join(p, os.listdir(p)[0])
    quality = ["Good"]
    fig,axs = plt.subplots(2,2)
    axs[0][0].imshow(np.array(Image.open(os.path.join(data_path, "region_props.png"))))
    #axs[1][0].imshow(np.array(Image.open(os.path.join(data_path, "tmp.svg"))))
    axs[1][0].imshow(np.array(Image.open(os.path.join(data_path,f"results/{file}False_mixup_distortion.png"))))
    axs[1][1].imshow(np.array(Image.open(os.path.join(data_path,f"results/{file}False_mixup_aligned.png"))))
    for i in range(4):
        fig.axes[i].get_xaxis().set_visible(False)
        fig.axes[i].get_yaxis().set_visible(False)
    fig.suptitle(file, fontsize=16)
    axgood = fig.add_axes([0.1, 0.05, 0.1, 0.075])
    axrev = fig.add_axes([0.4, 0.05, 0.1, 0.075])
    axkill = fig.add_axes([0.7, 0.05, 0.1, 0.075])
    def quality_good(ev):
        quality[0] = "Good"
        plt.close()
    def quality_rev(ev):
        quality[0] = "Review"
        plt.close()
    def quality_out(ev):
        quality[0] = "Out"
        plt.close()
    bgood = Button(axgood, 'Good')
    bgood.on_clicked(quality_good)
    brev = Button(axrev, 'Review')
    brev.on_clicked(quality_rev)
    bkill = Button(axkill, 'Out')
    bkill.on_clicked(quality_out)
    plt.show()

    data = {"file_name":file, "quality":quality[0]}
    return data


if __name__ == '__main__':
    HB = "230824_Homer1_ATTO643_Bassoon_CF568_CaV21_AF488_pansCF405"
    RP = "230824_PSD95_CF568_RIM12_AF488_VGlut1_ATTO643_panExM _CF405"
    GM = "230825_GluA1_ATTO643_LGI1_CF568_Munc13_AF488_PanExM"



    base_path = fr"outputs"
    data = []
    for k in range(1, 5):
        directory = os.path.join(base_path, rf"Culture {k}")
        if os.path.exists(directory):
            files = os.listdir(directory)
            f = []
            argument = ""
            for i in range(len(files)):
                p = os.path.join(directory, files[i])
                if os.path.exists(os.path.join(p,os.listdir(p)[0],"data.txt")):
                    d = result_viewer(directory, files[i])
                    d["Culture"] = f"Culture {k}"
                    data.append(pd.DataFrame(d,index=[0]) )
    df = pd.concat(data)
    df.to_csv(os.path.join(base_path, "data.txt"))