from src.image_operations import ImageStuff
from src.facade import TransformElastix
import os
import numpy as np
from tifffile.tifffile import TiffFile
import matplotlib.pyplot as plt

EXPECTED_EXPASION = 7.5
root = r"D:\Daten\Janna\PrePost"+"\\"
path1 = r"C1-MAX_Janna_postExp_5x5_stack_60xW002 - Stitched - DenoisedMIP_crop2.tif"#post
path2 = r"C2-MAX_Janna_Neurone_preExp_stack_60x_0002MIP_crop2.tif"#pre
save_dir = root + r"\results"+"\\"
save_name = path2.split(".")[0]

ALIGNMENT_RESIZE = 8
px_size = 0.1150890/0.1035718

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
    plt.imshow(resized)
    plt.show()
    #resized -= resized.min()
    transform.fixed_image = resized
    with TiffFile(root+path1) as tif:
        moving = tif.asarray()
    #     moving = gaussian_filter(moving, sigma=20)
    #     moving -= moving.min()
    moving = image_op.resize_image(root+path1, 1/(ALIGNMENT_RESIZE))
    moving2 = image_op.resize_image(root+path1, 1/(1))
    #resized = resized.max()-resized
    #resized =gaussian_filter(resized, sigma=2)
    #moving[np.where(moving<500)] = 0
    plt.imshow(moving)
    plt.show()
    transform.moving_image = moving.astype(np.float32)
    #run similarity transform
    transform.similarity_transform()
    #todo: comment stuff
    transform.moving_image = moving2
    transform.apply_similarity_transform(resize=ALIGNMENT_RESIZE, fixed=resized2)
    similarity_image = transform.t_result_image
    image_op.show_overlay(resized2, similarity_image, scale=EXPECTED_EXPASION*px_size, )
    TP = transform.STP
    image_op.show_overlay(resized2, similarity_image, scale=EXPECTED_EXPASION*px_size, TP=TP, save_path=save_dir+save_name+"similarity")
    #print(np.corrcoef(transform.fixed_image.flatten(),similarity_image.flatten()))
    #run spline transform
    transform.moving_image = transform.result_image
    transform.affine_transform(0)

    # todo: apply affine transform
    transform.moving_image = similarity_image
    transform.apply_affine_transform(0, resize=ALIGNMENT_RESIZE, fixed=resized2)
    affine_image = transform.t_result_image
    image_op.show_overlay(resized2, affine_image, scale=EXPECTED_EXPASION*px_size, save_path=save_dir+save_name+"affine")
    transform.fixed_image = resized2
    image_op.show_overlay(resized2, similarity_image,
                          scale=EXPECTED_EXPASION*px_size, vec_map=transform.get_distortion_map(typ="affine"), TP=TP, save_path=save_dir+save_name+"distortion")
