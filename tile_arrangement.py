import czifile
import matplotlib.pyplot as plt

im = czifile.imread(r"D:\Daten\Stefan\LatticeSIM\Image 1 - 7 8 9 expandiert_SIM².czi")
im2 = czifile.imread(r"D:\Daten\Stefan\LatticeSIM\Image 11 - 7 8 9 unexpandiert 63x WO_SIM².czi")

import napari
from qtpy.QtCore import QTimer

with napari.gui_qt() as app:
    viewer = napari.Viewer()
    new_layer = viewer.add_image(im.squeeze())
    new_layer2 = viewer.add_image(im2.squeeze())
