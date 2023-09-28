import tensorflow as tf
import tensorflow_addons as tfa
from tifffile import TiffFile
import numpy as np
import matplotlib.pyplot as plt

optimizer = tf.keras.optimizers.Adam(1e-4)
path = r"D:\Daten\Matt\volume_r10_c488.tif"
path2= r"D:\Daten\Matt\average_template_10.tif"

with TiffFile(path) as tif:
    moving_image = tif.asarray()[500]

with TiffFile(path2) as tif:
    fixed_image = tif.asarray()[500]

def loss( fixed, moving):
    return tf.image.ssim(tf.cast(fixed, tf.float64), moving, max_val=1.0)


class SimilarityTransform(tf.keras.layers.Layer):
    def __init__(self,*args, **kwargs,):
        super(SimilarityTransform, self).__init__(*args, **kwargs,dtype='float32')
        self.translation = tf.Variable([0.,0.])
        self.rotation = tf.Variable(0.)
        self.scaling = tf.Variable([1300,1300])

    def __call__(self, input):
        #x = tf.image.resize(input, self.scaling)
        x = tfa.image.rotate(input, self.rotation)
        x = tfa.image.translate(x, self.translation)
        return x




class Network(tf.keras.Model):
    def __init__(self):
        super(Network, self).__init__()
        self.alignment_layer = SimilarityTransform()

    def __call__(self, inputs):
        return self.alignment_layer(inputs)

network = Network()


#@tf.function
def train_step(fixed, moving, h, w):
    with tf.GradientTape() as tape:
        aligned = network(moving)
        mse = tf.keras.losses.MeanSquaredError()
        c = aligned[:,0:h,0:w]
        los = mse(fixed[:,0:500,0:500], c[:,0:500,0:500])#todo, undo
    gradients = tape.gradient(los, network.trainable_variables)
    optimizer.apply_gradients(zip(tf.cast(gradients, tf.float32), network.trainable_variables))
    return loss

if __name__ == '__main__':
    for i in range(1000):
        fixed_image_t = tf.convert_to_tensor(fixed_image[np.newaxis,:,:,np.newaxis]/fixed_image.max())
        moving_image_t = tf.convert_to_tensor(moving_image[np.newaxis,:,:,np.newaxis]/moving_image.max())
        print(loss(fixed_image_t[:,0:500,0:500], moving_image_t[:,0:500,0:500]))
        train_step(fixed_image_t, moving_image_t, fixed_image.shape[0], fixed_image.shape[1])