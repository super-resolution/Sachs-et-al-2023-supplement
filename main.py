from src.image_operations import ImageStuff
from src.facade import TransformElastix
import os
import numpy as np
from tifffile.tifffile import TiffFile
import matplotlib.pyplot as plt

#todo: move -> source

EXPECTED_EXPASION = 4
root = r"D:\Daten\Janna\2024PrePostAlignment\Trex"+"\\"
path1 = r"POST_TREx.tif"#post
path2 = r"PRE_TREx.tif"#pre
save_dir = root + r"\results"+"\\"
save_name = path2.split(".")[0]

ALIGNMENT_RESIZE = 1
#px_size = 0.1150890/0.1035718

if __name__ == '__main__':
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    image_op = ImageStuff()
    transform = TransformElastix()
    #can be removed if resizing to post
    # with TiffFile(root+path2) as tif:
    #     fixed = tif.asarray()
    #fixed = image_op.resize_image(root+path2, 1/(10))
    #fixed = fixed.max()-fixed
    resized = image_op.resize_image(root+path2, EXPECTED_EXPASION/ALIGNMENT_RESIZE)
    resized2 = image_op.resize_image(root+path2, EXPECTED_EXPASION)
    #resized[np.where(resized<1000)] = 0
    resized -= resized.min()
    #resized = np.clip(resized, 0, resized.max()/5)
    plt.imshow(resized)
    plt.show()
    #
    transform.fixed_image = resized
    # with TiffFile(root+path1) as tif:
    #     moving = tif.asarray()

    #     moving = gaussian_filter(moving, sigma=20)
    #     moving -= moving.min()
    moving = image_op.resize_image(root+path1, 1/(ALIGNMENT_RESIZE))
    moving -= moving.min()
    #moving = np.clip(moving, 0, moving.max()/5)
    moving2 = image_op.resize_image(root+path1, 1/(1))
    #resized = resized.max()-resized
    #resized =gaussian_filter(resized, sigma=2)
    #moving[np.where(moving<500)] = 0
    fig,axs = plt.subplots(2)
    axs[0].imshow(moving)
    axs[1].imshow(resized)
    plt.show()
    transform.moving_image = moving.astype(np.float32)
    #run similarity transform
    transform.similarity_transform()
    #todo: comment stuff
    # transform.moving_image = moving
    # transform.apply_similarity_transform(resize=ALIGNMENT_RESIZE, fixed=resized)
    # similarity_image = transform.t_result_image
    # image_op.show_overlay(resized, similarity_image, scale=EXPECTED_EXPASION, )
    # TP = transform.STP
    # image_op.show_overlay(resized2, similarity_image, scale=EXPECTED_EXPASION, TP=TP, save_path=save_dir+save_name+"similarity")
    similarity_image = transform.result_image
    TP = transform.STP
    #print(np.corrcoef(transform.fixed_image.flatten(),similarity_image.flatten()))
    #run spline transform
    #transform.moving_image = transform.result_image
    #transform.affine_transform(0)
    image_op.show_overlay(resized, similarity_image, scale=EXPECTED_EXPASION, save_path=save_dir+save_name+"similarity")
    transform.fixed_image = resized
    transform.moving_image = similarity_image
    transform.b_spline_tranform()
    spline_image = transform.result_image
    image_op.show_overlay(resized, spline_image, scale=EXPECTED_EXPASION, save_path=save_dir+save_name+"spline")
    transform.fixed_image = resized
    image_op.show_overlay(resized, similarity_image,
                          scale=EXPECTED_EXPASION, vec_map=transform.get_distortion_map(), TP=TP, save_path=save_dir+save_name+"distortion")
