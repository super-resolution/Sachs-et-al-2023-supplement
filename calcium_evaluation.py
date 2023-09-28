import os

import hydra
from hydra.utils import get_original_cwd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tifffile.tifffile import TiffFile

from src.facade import TransformElastix
from src.image_operations import ImageStuff
from src.region_utils import get_region_props_sum_ch


@hydra.main(config_path="configurations/", config_name="calcium_eval")
def main(cfg):
    save_dir = os.path.join(cfg.directory.root_dir, cfg.directory.save_dir)
    # if not os.path.exists(save_dir):
    #     os.mkdir(save_dir)
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
    # res = []
    # for image in fixed:
    #     res.append(np.corrcoef(image[2].flatten(), image[1].flatten())[0][1])
    # plt.plot(res)
    # plt.show()
    #transpose image color on last channel?
    fixed = np.transpose(fixed, (1, 2, 0))
    ch1,ch2 = cfg.params.channels

    np.random.seed(0)
    ch_ax = {0:ch1,1:ch2}
    #get_region_props_sum_ch(fixed[:, :, ],ch_ax, mixup=False)
    # define parameter file in config
    transform = TransformElastix(ocwd)
    # if cfg.transform.parameter_file:
    #     transform.affineParameterMap = cfg.transform.parameter_file
    # else:
    #     print("no_parameter_file_found")
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
    axs[2].imshow(a * b/(a**2+b**2), cmap="hot")
    plt.savefig("tmp.svg")
    plt.clf()
    #plt.show()

    # create a save name that includes the mixup
    image_op = ImageStuff()

    image_op.show_overlay(transform.fixed_image, affine_image, scale=1,
                          save_path=os.path.join("results" , save_name) + f"{False}_mixup_aligned")
    image_op.show_overlay(transform.fixed_image, transform.moving_image,
                          scale=1, vec_map=transform.get_distortion_map(typ="affine"),
                          save_path=os.path.join("results" , save_name) + f"{False}_mixup_distortion")

    pearson = np.corrcoef(transform.fixed_image.flatten(), affine_image.flatten())
    #write file to save values

    d = {"name":cfg.directory.file_name, "pearson":pearson[0][1], "ch1":[ch1], "ch2":[ch2]}
    df = pd.DataFrame(d, index=[0])
    df.to_csv('data.txt', sep='\t')


if __name__ == '__main__':
    main()