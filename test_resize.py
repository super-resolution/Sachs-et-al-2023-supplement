from tifffile import TiffFile, TiffWriter
import numpy as np
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
  tf.config.experimental.set_memory_growth(gpu, True)



path = r"D:\Daten\Matt\dcr_2_pred_small.tif"

with TiffFile(path) as tif:
    image = tif.asarray()


def tf_batch_transform(image):
    processed = []
    batch = 10
    s = image.shape[0]//batch
    if image.shape[0]%batch !=0:
        s+=1
    for i in range(s):
        tf_preprocessed = tf.constant(image[batch*i:batch*(i+1), :, :, np.newaxis])
        processed.append(tf.image.resize(tf_preprocessed,tf.constant([int(image.shape[1]*0.4),int(image.shape[2]*0.4)])))

    return np.concatenate(processed,axis=0)


img = tf_batch_transform(image)


with TiffWriter('temp_signal.tif') as tif:
    tif.save(img, photometric='minisblack')