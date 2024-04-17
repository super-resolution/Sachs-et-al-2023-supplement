import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
from skimage import io
import os

class ImageStuff():
    ORANGE = (0.9, .4, .11, 0.15)
    BLACK = (0., 0., 0., 1.)
    #ORANGE = (1,1,1,1)
    CYAN = (.0, 1.0, 1.0, 1.0)
    BLUE = (0,0,1.0,1.0)
    YELLOW = (0,1.0,1.0,1.0)
    GREY = (0.2,0.2,.2,1.0)
    GREEN = (.0, 246/255, .0)
    MAGENTA = (242/255, .0, 242/255)
    channel_colors = {0:MAGENTA, 1:ORANGE, 2:GREEN}
    def resize_image(self, path, scale):
        image = io.imread(path)
        output_dimension = (int(image.shape[0] * scale), int(image.shape[1] * scale))
        image = resize(image, output_dimension, preserve_range=True)
        io.imsave("tmp/resized.tif", image.astype("uint16"))
        return image

    def image_to_rgba_color(self, image, color, multiplier=1.):
        res_rgba = np.zeros((image.shape[0], image.shape[1], 4))
        res_rgba[:, :, 0] = (image / image.max()) * color[0]
        res_rgba[:, :, 1] = (image / image.max()) * color[1]
        res_rgba[:, :, 2] = (image / image.max()) * color[2]
        res_rgba[:, :, 3] =  image/ image.max()
        res_rgba = np.clip(multiplier * res_rgba, 0, 1.0)
        return res_rgba

    def show_overlay(self, im1, im2, scale=1, TP=None, vec_map=None, save_path=None, px_size=None, ch=None):
        if not ch:
            im_rgba = self.image_to_rgba_color(im1, self.MAGENTA, multiplier=4)
            res_rgba = self.image_to_rgba_color(im2, self.GREEN , multiplier=4)
        if ch:
            im_rgba = self.image_to_rgba_color(im1, self.channel_colors[ch[0]], multiplier=3)
            res_rgba = self.image_to_rgba_color(im2, self.channel_colors[ch[1]], multiplier=2.5)
        composit = res_rgba+ im_rgba
        ax = plt.gca()
        #ax.set_facecolor((0.0, 0.0, 1.0))
        #add scalebar with approx 500 nm
        if px_size:
            plt.text(1-int(0.5/float(px_size)+5)/composit.shape[1], 8/composit.shape[0], '0.5 μm', c="white", ha='left', va='bottom', transform=ax.transAxes)
            composit[-7:-5,-int(0.5/float(px_size)+5):-5] = [1,1,1,1]

        plt.imshow(np.zeros_like(im1)*255,cmap="hot")
        plt.imshow(composit)
        #plt.imshow(im_rgba)
        plt.axis('off')
        pearson = np.corrcoef(im1.flatten(), im2.flatten())

        if TP:
            plt.title(f"Expansion = {scale*float(TP['TransformParameters'][0]):.2f}\n Pearson = {pearson[0][1]:.2f}", fontsize=25)
        else:
            plt.title(f"Pearson = {pearson[0][1]:.2f}", fontsize=25)

        if vec_map:
            plt.quiver(vec_map.XY, vec_map.YX, vec_map.XY_final, -vec_map.YX_final,
                       color="red", scale_units='xy',scale=1)
        if save_path:
            plt.savefig(save_path+".png", bbox_inches="tight")
            plt.savefig(save_path+".svg", bbox_inches="tight")
            plt.cla()
        else:
            plt.show()
