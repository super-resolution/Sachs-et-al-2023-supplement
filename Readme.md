# Automated Simple Elastix
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8390729.svg)](https://doi.org/10.5281/zenodo.8390729)
%%todo add image here 
This package wraps around Simple Elastix [cite] and is intended for the alignment of biological data. The two main applications that are currently covered are.


## Set Up
Clone the github repository:

    git clone https://github.com/super-resolution/Sachs-et-al-2023-supplement

Cd into the project folder to `wheels/{your python version}` and run either:

    pip install SimpleITK-2.0.0rc2.dev910+ga138e-cp36-cp36m-win_amd64.whl

or

    python setup.py install

## Creating Distortion Maps for Expansion Microscopy Data
[Is explained in detail here.](https://towardsdatascience.com/using-simpleelastix-to-compare-pre-and-post-expansion-microscopy-images-660eaf992482)

## Detecting Nanocolumns in Pre- and Post-Synaptic proteins
The algorithm's overall notion is explained in detail in [ref to paper]. The synapse-covering ROI is initially identified. A bounding box and the major axis orientation are calculated for this ROI. Then, in order to align the pre- and post-synapse, we compute an Affine transform. Here, we turn off scaling and give the translation settings more weight. We calculated the Pearson correlation coefficient to see whether the data was suitably aligned. The presence of nanocolumns is already indicated by a high correlation. We compute the dot product of the shift vector and synapse orientation to verify the presence of nanocolumns. A result that is close to zero signifies that the postsynaptic protein is moved perpendicular to the synapses orientation to align with its presynaptic counterpart.



### Configuration
For evaluating synaptic proteins we provide a configuration file and a batch processing option:
The processing pipeline is initialized with the processing tool hydra (2). The corresponding configuration (.yaml) files contain the following parameters. 
- Directory: 
 - `condition`: Acquisition conditions of the file
 - `culture`: Culture of the file
 - `root_dir`: path to the root directory of the file
 - `save_name`: save name of the result file (defaults to filename + processing operation)
- Params:
 - `channels`: channels to compare
 - `z_project`: indicates whether to perform an average intensity projection on the first - dimension
- Transform:
 -	`type`: type of transformation which should be performed (can be affine, b-spline, similarity)
 - `parameter_file`: path to the parameter file for the given transformation

### Identifying pre and postsynaptic structures
Images are transformed into a binary format by the Otsu thresholding processing. To further separate related regions, we employ the `sk_image` [4] label algorithm. These areas are arranged in descending order by size. We calculate the orientation, major_axis, minor_axis, and bounding_box of the first element, i.e. the largest connected structure. We attempt to connect the three largest signal clusters and retest these qualities in cases when the largest region is smaller than 300 px or has a major_axis/minor_axis ratio of less than 2. The synaptic connection is discarded if the region still the mentioned conditions. We do, however, record a plot of the regions so that we may manually confirm the choice. If the synaptic connection is successful, we save the associated properties in a `properties.txt` file that pandas (5) may access. 

### Choice of parameter files
Because the `AffineDTITransform` has the ability to weight the degrees of freedom of the transform, we used it for our parameter file. We anticipate the signal of the two channels to shift in a direction perpendicular to the major axis of the pre or postsynaptic structure in order to determine nanocolumns. Thus, the translation parameters, for instance, have the lowest value (1) and therefore the highest degree of adjustability. The transform attempts to maximize translation, rotation, and shear in that sequence. Scaling is penalized in a way that eliminates it from the range of potential degrees of freedom.
**Note:** transform rotates starting from the geometrical picture center. All other utilized settings are fully described in the elastix documentation and may be found in the relevant file in our [repository](static/affine_noscaling_parameters.txt).

In order to display the differences between non-aligned and aligned images with a vector map, we apply the estimated transform to build a distortion map [6]. Data.txt, a file holding the file name, the Pearson correlation index, and the employed picture channels, is saved along with an overlay of the aligned images and the distortion map.


## References
1. Marstal, Kasper, Floris Berendsen, Marius Staring, und Stefan Klein. „SimpleElastix: A User-Friendly, Multi-lingual Library for Medical Image Registration“. In 2016 IEEE Conference on Computer Vision and Pattern Recognition Workshops (CVPRW), 574–82, 2016. https://doi.org/10.1109/CVPRW.2016.78.
2. Yadan, Omry. „Hydra - A framework for elegantly configuring complex applications“, 2019. https://github.com/facebookresearch/hydra.

3. Klein, Stefan, Marius Staring, Keelin Murphy, Max A. Viergever, und Josien P. W. Pluim. „elastix: A Toolbox for Intensity-Based Medical Image Registration“. IEEE Transactions on Medical Imaging 29, Nr. 1 (Januar 2010): 196–205. https://doi.org/10.1109/TMI.2009.2035616.

4. Van der Walt, Stefan, Johannes L Schönberger, Juan Nunez-Iglesias, François Boulogne, Joshua D Warner, Neil Yager, Emmanuelle Gouillart, und Tony Yu. „scikit-image: image processing in Python“. PeerJ 2 (2014): e453.

5. team, The pandas development. „pandas-dev/pandas: Pandas“. Zenodo, Februar 2020. https://doi.org/10.5281/zenodo.3509134.

6. Trinks, Nora, Sebastian Reinhard, Matthias Drobny, Linda Heilig, Jürgen Löffler, Markus Sauer, und Ulrich Terpitz. „Subdiffraction-Resolution Fluorescence Imaging of Immunological Synapse Formation between NK Cells and A. Fumigatus by Expansion Microscopy“. Communications Biology 4, Nr. 1 (4. Oktober 2021): 1–12. https://doi.org/10.1038/s42003-021-02669-y.