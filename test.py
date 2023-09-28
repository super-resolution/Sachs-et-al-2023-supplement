import numpy as np
from src.facade import TransformElastix
from src.image_operations import ImageStuff

def create_chessboard(shape=256):
    image = np.zeros((shape,shape))
    for i in range(shape):
        if i%10 == 0:
            image[i:i+1,:] = 255
            image[:,i:i+1] = 255
    return image

root = r"D:\Daten\Nora\Pre-post\data\test"+"\\"
path1 = r"1_1_POST.tif"

if __name__ == '__main__':
    chess = create_chessboard()
    t = TransformElastix()
    t.fixed_image = chess

    s = ImageStuff()
    t.apply_b_spline_transform(chess)#no error this is inverse transform therefore also display inverse vec maps...
    chess_d = t.t_result_image

    v = t.get_distortion_map()
    s.show_overlay(chess,chess_d[:1000,:1000], vec_map=v, save_path="image")
    #apply random bspline tranform and register back...
