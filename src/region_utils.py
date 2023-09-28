import math
import sys
from tifffile.tifffile import imwrite
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
import pandas as pd

# customn CMAP
values = np.array(
    [(0, 0, 0), (0, 117, 220), (153, 63, 0), (76, 0, 92), (0, 92, 49), (43, 206, 72), (255, 204, 153), (128, 128, 128),
     (148, 255, 181), (143, 124, 0), (157, 204, 0), (194, 0, 136), (0, 51, 128), (255, 164, 5), (255, 168, 187),
     (66, 102, 0), (255, 0, 16), (94, 241, 242), (0, 153, 143), (224, 255, 102), (116, 10, 255), (153, 0, 0),
     (255, 255, 128), (255, 255, 0), (255, 80, 5)])
CMAP2 = matplotlib.colors.ListedColormap([v / 255 for v in values] * 2)


def get_region_props_automated(images,ch_ax, connected_axes=0):
    # matplotlib subplots with regions
    # callback slider for threshold
    # callback to select region props with mouse event
    # show both regions in a third image with angle and distance?

    # both images in subpllots
    labeled_images = np.zeros_like(images)
    sliders = []
    for i in range(1):
        # expect color as last channel
        otsu = threshold_otsu(images[:, :, ch_ax[i]])
        bin = images[:, :, ch_ax[i]] > otsu
        current = label(bin)
        labeled_images[:, :, ch_ax[i]] = current
        size_dict = {}
        for j in range(1,current.max()+1):
            size_dict[j] = len(np.where(current.flatten()==j)[0])
        size_dict = sorted(size_dict.items(), key=lambda item: item[1],reverse=True)
        properties = regionprops(current)
        props = properties[size_dict[0][0]-1]
        cop = np.zeros_like(current)
        if size_dict[0][1]<200 or props.axis_major_length/props.axis_minor_length<2:
            indices = np.where(np.logical_or(np.logical_or(current==size_dict[0][0], current==size_dict[1][0]), current==size_dict[2][0]))
            cop[indices] = 1
            props = regionprops(cop)[0]
            if len(indices[0]) < 200 or props.axis_major_length/props.axis_minor_length<2:
                #discard this synapse
                y0, x0 = props.centroid
                orientation = props.orientation
                x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
                y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
                x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
                y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length
                x3 = x0 + math.sin(orientation) * 0.5 * props.major_axis_length
                y3 = y0 + math.cos(orientation) * 0.5 * props.major_axis_length
                plt.imshow(current)
                plt.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
                plt.plot((x3, x2), (y3, y2), '-r', linewidth=2.5)
                plt.plot(x0, y0, '.g', markersize=15)
                plt.savefig("region_props.png")
                plt.clf()
                imwrite("property_image.tif", props.image, )
                sys.exit(())
        y0, x0 = props.centroid
        orientation = props.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
        y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
        x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
        y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length
        x3 = x0 + math.sin(orientation) * 0.5 * props.major_axis_length
        y3 = y0 + math.cos(orientation) * 0.5 * props.major_axis_length
        plt.imshow(current)
        plt.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
        plt.plot((x3, x2), (y3, y2), '-r', linewidth=2.5)
        plt.plot(x0, y0, '.g', markersize=15)
        plt.savefig("region_props.png")
        plt.clf()
        imwrite("property_image.tif", props.image, )
        d = {"major_axis_length": props.axis_minor_length, "minor_axis_length": props.axis_major_length, "orientation": props.orientation}
        df = pd.DataFrame(d, index=[0])
        df.to_csv('properties.txt', sep='\t')



def get_region_props(images,ch_ax, mixup=False):
    # matplotlib subplots with regions
    # callback slider for threshold
    # callback to select region props with mouse event
    # show both regions in a third image with angle and distance?

    # both images in subpllots
    fig, axs = plt.subplots(1, 3)
    labeled_images = np.zeros_like(images)
    sliders = []
    for i in range(2):
        # expect color as last channel
        ax_x = plt.axes([0.25, 0.15 * i, 0.65, 0.03])
        otsu = threshold_otsu(images[:, :, ch_ax[i]])
        bin = images[:, :, ch_ax[i]] > otsu
        labeled_images[:, :, ch_ax[i]] = label(bin)
        axs[i].imshow(labeled_images[:, :, ch_ax[i]], cmap=CMAP2)
        sliders.append(Slider(ax_x, 'x', 0.0, images[:, :, ch_ax[i]].max(), valinit=otsu, valstep=1))
    placeholder = np.zeros_like(bin).astype(np.uint8)
    axs[2].imshow(placeholder)
    properties = []

    # propterties = regionprops(lab)
    # for props in propterties:
    #     y0, x0 = props.centroid
    #     orientation = props.orientation
    #     x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
    #     y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
    #     x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
    #     y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length
    #     x3 = x0 + math.sin(orientation) * 0.5 * props.major_axis_length
    #     y3 = y0 + math.cos(orientation) * 0.5 * props.major_axis_length
    #
    #
    #     ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
    #     ax.plot((x3, x2), (y3, y2), '-r', linewidth=2.5)
    #     ax.plot(x0, y0, '.g', markersize=15)

    # minr, minc, maxr, maxc = props.bbox
    # bx = (minc, maxc, maxc, minc, minc)
    # by = (minr, minr, maxr, maxr, minr)
    # ax.plot(bx, by, '-b', linewidth=2.5)

    # ax.axis((0, 600, 600, 0))
    def onclick(event):
        if event.button == 1:  # left mouse
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

            for i, ax in enumerate(axs):
                if ax == event.inaxes:
                    current_axs = i
                    num = labeled_images[int(event.ydata), int(event.xdata), ch_ax[current_axs]]
                    indices = np.where(labeled_images[:, :, ch_ax[current_axs]] == num)
                    if mixup:
                        images[:, :, ch_ax[current_axs]] = mix_up_pixels(images[:, :, ch_ax[current_axs]], indices)
                    new = np.zeros_like(placeholder).astype(np.uint8)
                    new[indices] = 1
                    properties.extend(regionprops(new))
                    for props in properties:
                        y0, x0 = props.centroid
                        orientation = props.orientation
                        x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
                        y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
                        x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
                        y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length
                        x3 = x0 + math.sin(orientation) * 0.5 * props.major_axis_length
                        y3 = y0 + math.cos(orientation) * 0.5 * props.major_axis_length

                        axs[2].plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
                        axs[2].plot((x3, x2), (y3, y2), '-r', linewidth=2.5)
                        axs[2].plot(x0, y0, '.g', markersize=15)
                    if len(properties) == 2:
                        print(
                            f"alpha is {(properties[0].orientation - properties[1].orientation) * 360 / (2 * math.pi)}")

                    placeholder[indices] = current_axs + 2
                    axs[2].imshow(placeholder.astype(np.uint8), cmap=CMAP2)
                    fig.canvas.draw_idle()
                    plt.pause(0.1)
            # query_points[0,1,0,0] = float(event.xdata) / 512 * 2 - 1
            # query_points[0, 1, 0, 1] =float(event.ydata) / 512 * 2 - 1
        if event.button == 3:  # right mouse
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))
            plt.savefig("tmp2.svg")

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    def create_update(num):
        def update(val):
            bin = images[:, :, ch_ax[num]] > val
            labeled_images[:, :, ch_ax[num]] = label(bin)
            axs[num].imshow(labeled_images[:, :, ch_ax[num]], cmap=CMAP2)
            plt.pause(0.1)

        return update

    sliders[0].on_changed(create_update(0))
    sliders[1].on_changed(create_update(1))

    plt.show()

def mix_up_pixels(image, indices):
    values = image[indices]
    np.random.shuffle(values)
    image[indices] = values
    return image