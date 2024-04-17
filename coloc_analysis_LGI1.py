import os

import hydra
from hydra.utils import get_original_cwd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tifffile.tifffile import TiffFile

from src.image_operations import ImageStuff


#write configuration yaml with batch
@hydra.main(config_path="configurations/", config_name="LGI1")
def main(cfg):
    #todo: load images
    save_dir = os.path.join(cfg.directory.root_dir, cfg.directory.save_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if cfg.directory.save_name == "auto":
        save_name = cfg.directory.file_name
    else:
        save_name = cfg.directory.save_name
    #save_path = os.path.join(save_dir,save_name)
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    if not os.path.exists("results"):
        os.mkdir("results")
    # read image
    with TiffFile(os.path.join(cfg.directory.root_dir, cfg.directory.file_name)+".tif") as tif:
        fixed = tif.asarray()



    if cfg.params.z_project:
        if fixed.shape[1]>4:
            raise ValueError(f"not 2 channel{cfg.directory.file_name}")
        fixed = np.sum(fixed, 0)
    #transpose image color on last channel?
    fixed = np.transpose(fixed, (1, 2, 0))
    ch1,ch2 = cfg.params.channels

    #if cfg.params.mixup:
    np.random.seed(0)
    ch_ax = {0:ch1,1:ch2}
    im1  =fixed[:, :, ch1]
    im2 = fixed[:, :, ch2]

    fig, axs = plt.subplots(1, 3)
    axs[0].imshow(im1)
    axs[1].imshow(im2)
    axs[2].imshow(im1 * im2, cmap="hot")
    plt.savefig("tmp.svg")
    plt.clf()
    #render overlay of 2 channels and save with pearson
    image_op = ImageStuff()
    #todo:edit colors
    image_op.show_overlay(im1, im2, scale=1,px_size=cfg.params.px_size,
                          save_path=os.path.join("results" , save_name) + f"{cfg.params.mixup}_mixup_aligned",ch=[ch1,ch2])

    #write file to save values
    pearson = np.corrcoef(im1.flatten(), im2.flatten())

    d = {"name":cfg.directory.file_name, "pearson":pearson[0][1], "ch1":[ch1], "ch2":[ch2]}
    df = pd.DataFrame(d, index=[0])
    df.to_csv('data.txt', sep='\t')


if __name__ == '__main__':
    main()
