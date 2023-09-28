import os

import hydra
from hydra.utils import get_original_cwd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tifffile.tifffile import TiffFile

from src.facade import TransformElastix
from src.image_operations import ImageStuff
from src.region_utils import get_region_props_automated


@hydra.main(config_path="configurations/", config_name="distance_maps")
def main(cfg):
    #todo: glua munc and rim psd
    save_dir = os.path.join(cfg.directory.root_dir, cfg.directory.save_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if cfg.directory.save_name == "auto":
        save_name = cfg.directory.file_name
    else:
        save_name = cfg.directory.save_name
    #save_path = os.path.join(save_dir,save_name)
    ocwd = get_original_cwd()
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
        #todo: get angles here
    get_region_props_automated(fixed[:, :, ],ch_ax)
    # define parameter file in config
    transform = TransformElastix(ocwd)
    if cfg.transform.parameter_file:
        transform.affineParameterMap = cfg.transform.parameter_file
    else:
        print("no_parameter_file_found")
    # run similarity transform
    transform.fixed_image = fixed[:, :, ch1]
    # run spline transform
    transform.moving_image = fixed[:, :, ch2]
    transform.affine_transform(0)
    affine_image = transform.result_image
    #todo: set center rotation point?
    #plot transform results
    a = transform.fixed_image / transform.fixed_image.max()
    b = affine_image / affine_image.max()
    fig, axs = plt.subplots(1, 3)
    axs[0].imshow(a)
    axs[1].imshow(b)
    axs[2].imshow(a * b, cmap="hot")
    plt.savefig("tmp.svg")
    plt.clf()
    #plt.show()

    # create a save name that includes the mixup
    image_op = ImageStuff()

    image_op.show_overlay(transform.fixed_image, affine_image, scale=1,px_size=cfg.params.px_size,
                          save_path=os.path.join("results" , save_name) + f"{cfg.params.mixup}_mixup_aligned")
    image_op.show_overlay(transform.fixed_image, transform.moving_image,
                          scale=1, vec_map=transform.get_distortion_map(typ="affine"), px_size=cfg.params.px_size,
                          save_path=os.path.join("results" , save_name) + f"{cfg.params.mixup}_mixup_distortion")

    pearson = np.corrcoef(transform.fixed_image.flatten(), affine_image.flatten())
    #write file to save values

    d = {"name":cfg.directory.file_name, "pearson":pearson[0][1], "ch1":[ch1], "ch2":[ch2]}
    df = pd.DataFrame(d, index=[0])
    df.to_csv('data.txt', sep='\t')


if __name__ == '__main__':
    main()