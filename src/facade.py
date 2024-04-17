import os
from collections import namedtuple

import SimpleITK as sitk
import numpy as np


class TransformElastix():
    """
        Interface to Elastix alginment tool
        Expected Expansion: initial scaling factor
        Spacing: Spacing of arrows in quiver plot
        Path to tranformation parameter files
        Quiver class
    """
    EXPECTED_EXPANSION = 3.5
    SPACING = 20
    INITIAL_SIMILARITY_PF = "static/similarity_parameters.txt"
    INITIAL_SPLINE_PF = "static/b_spline_parameters.txt"
    INITIAL_AFFINE_PF = "static/affine_parameters.txt"
    QUIVER = namedtuple("Quiver", "XY YX XY_final YX_final cm")
    def __init__(self, wd:str=None):
        """
        load transformation files and set up temp and output directories
        :param wd: Set working directory for Elastix
        """
        if not wd:
            self.wd = os.getcwd()
        else:
            self.wd = wd
        self._fixed_i = None
        self._move_i = None
        self.BTP = None
        self.STP = None
        self.ATP = None
        self._similarityParameterMap = sitk.ReadParameterFile(os.path.join(self.wd, self.INITIAL_SIMILARITY_PF))
        self._bSplineParameterMap = sitk.ReadParameterFile(os.path.join(self.wd,self.INITIAL_SPLINE_PF))
        self._affineParameterMap = sitk.ReadParameterFile(os.path.join(self.wd,self.INITIAL_AFFINE_PF))

        self.process = sitk.ElastixImageFilter()
        self.process.SetOutputDirectory("tmp")
        self.t_process = sitk.TransformixImageFilter()
        self.t_process.SetOutputDirectory("tmp")


    def similarity_transform(self):
        """
        Perform similarity transform on current fixed and moving image
        """
        if not self._fixed_i or not self._move_i:
            raise ValueError("Set fixed and moving image before transform")
        self.process.SetFixedImage(self._fixed_i)
        self.process.SetMovingImage(self._move_i)
        self.process.SetParameterMap(self._similarityParameterMap)
        self.process.Execute()
        self.STP = self.process.GetTransformParameterMap(0)
        sitk.WriteParameterFile(self.STP, "tmp/similarity.txt")


    def affine_transform(self,i:int=0):
        """
        Perform affine transformation on current fixed and moving image
        :param i: supports iterative alignment by providing a parameter i
        """
        if not self._fixed_i or not self._move_i:
            raise ValueError("Set fixed and moving image before transform")
        self.process.SetFixedImage(self._fixed_i)
        self.process.SetMovingImage(self._move_i)
        self.process.SetParameterMap(self._affineParameterMap)
        self.process.LogToConsoleOn()
        self.process.Execute()
        self.ATP = self.process.GetTransformParameterMap(0)
        sitk.WriteParameterFile(self.ATP, f"tmp/affine{i}.txt")

    def apply_affine_transform(self, i:int, resize:float=1., fixed:np.ndarray=None):
        """
        Apply the ith affine transform from the tmp folder
        :param i: ith iteration to use
        :param resize: resize factor
        :param fixed: fixed image
        """
        self.ATP = sitk.ReadParameterFile(f"tmp/affine{i}.txt")
        if np.any(fixed):
            self.ATP["Size"] = [str(fixed.shape[1]), str(fixed.shape[0])]
        self.ATP["CenterOfRotationPoint"] = [str(float(self.ATP["CenterOfRotationPoint"][0])* resize),str(float(self.ATP["CenterOfRotationPoint"][1])* resize)]
        if resize >1.:
            self.ATP['TransformParameters']= [self.ATP['TransformParameters'][0],
                                              self.ATP['TransformParameters'][1],
                                              self.ATP['TransformParameters'][2],
                                              self.ATP['TransformParameters'][3],
                                              str(float(self.ATP['TransformParameters'][4])* resize),
                                              str(float(self.ATP['TransformParameters'][5])* resize)]

        self.t_process.SetTransformParameterMap(self.ATP)
        self.t_process.SetMovingImage(self._move_i)
        self.t_process.Execute()

    def apply_similarity_transform(self, resize:float=1., fixed:np.ndarray=None):
        """
        Apply similarity transform
        :param resize: scaling factor
        :param fixed: fixed image
        get image as t_result_image
        """
        self.STP = sitk.ReadParameterFile( f"tmp/similarity.txt")
        if np.any(fixed):
            self.STP["Size"] = [str(fixed.shape[1]), str(fixed.shape[0])]
        self.STP["CenterOfRotationPoint"] = [str(self.moving_image.shape[1]/2),str(str(self.moving_image.shape[0]/2))]
        if resize >1.:
            self.STP['TransformParameters']= [self.STP['TransformParameters'][0],
                                              self.STP['TransformParameters'][1],
                                              str(float(self.STP['TransformParameters'][2])* resize),
                                              str(float(self.STP['TransformParameters'][3])* resize)]
            #todo: change STP translation
        self.t_process.SetTransformParameterMap(self.STP)
        self.t_process.SetMovingImage(self._move_i)
        self.t_process.Execute()


    def b_spline_tranform(self):
        """
        Perform b-spline transformation on current fixed and moving image
        """
        if not self._fixed_i or not self._move_i:
            raise ValueError("Set fixed and moving image before transform")
        self.process.SetFixedImage(self._fixed_i)
        self.process.SetMovingImage(self._move_i)
        self.process.SetParameterMap(self._bSplineParameterMap)
        self.process.Execute()

        self.BTP = self.process.GetTransformParameterMap(0)
        sitk.WriteParameterFile(self.BTP, os.path.join(self.wd, "tmp/b_spline.txt"))

    def apply_b_spline_transform(self, image):
        """
        Apply tmp bspline transform on image
        :param image: input image
        get image as t_result_image
        """
        if not self.BTP:
            self.BTP = sitk.ReadParameterFile(os.path.join(self.wd, "tmp/b_spline.txt"))
        self.t_process.SetTransformParameterMap(self.BTP)
        self.t_process.SetMovingImage(sitk.GetImageFromArray(image))
        self.t_process.Execute()

    def get_distortion_map(self, typ="bspline")->namedtuple:
        """
        Compute distortion map from the currently save transformation in tmp
        :param typ: type of transform to load
        :return: Quiver object with vector maps
        """
        if typ=="bspline":
            if not self.BTP:
                self.BTP = sitk.ReadParameterFile(os.path.join(self.wd, "tmp/b_spline.txt"))
            self.t_process.SetTransformParameterMap(self.BTP)
        if typ=="similarity":
            if not self.STP:
                self.STP = sitk.ReadParameterFile(os.path.join(self.wd, "tmp/similarity.txt"))
            self.t_process.SetTransformParameterMap(self.STP)
        if typ=="affine":
            if not self.ATP:
                self.ATP = sitk.ReadParameterFile(os.path.join(self.wd, "tmp/affine0.txt"))
            self.ATP["CenterOfRotationPoint"] = [str(self.moving_image.shape[1] / 2),
                                                 str(str(self.moving_image.shape[0] / 2))]
            self.t_process.SetTransformParameterMap(self.ATP)

        X = np.arange(0, self.fixed_image.shape[1])
        Y = np.arange(0, self.fixed_image.shape[0])
        XY, YX = np.meshgrid(X, Y)
        self.t_process.SetMovingImage(sitk.GetImageFromArray(XY))
        self.t_process.Execute()
        XY_new = self.t_result_image

        self.t_process.SetMovingImage(sitk.GetImageFromArray(YX))
        self.t_process.Execute()
        YX_new = self.t_result_image

        XY_final = XY - XY_new
        YX_final = YX - YX_new
        XY_final[np.where(XY_new == 0)] = 0
        YX_final[np.where(YX_new == 0)] = 0
        XY = XY[::self.SPACING, ::self.SPACING]
        YX = YX[::self.SPACING, ::self.SPACING]
        XY_final = XY_final[::self.SPACING, ::self.SPACING]
        YX_final = YX_final[::self.SPACING, ::self.SPACING]

        XY_new = XY_new[::self.SPACING, ::self.SPACING]
        YX_new = YX_new[::self.SPACING, ::self.SPACING]

        values = np.abs(XY_final) + np.abs(YX_final)

        return self.QUIVER(XY, YX, XY_final, YX_final, values)


    def get_transform_parameters(self)->np.ndarray:
        """
        Get Similarity transformparameters as np array
        :return:
        """
        #if self.STP["Transform"] == "SimilarityTransform":
        print(self.STP["Transform"][0])
        c_y = self.fixed_image.shape[0] / 2
        c_x = self.fixed_image.shape[1] / 2
        if self.STP["Transform"][0] == "SimilarityTransform":

            scale = float(self.STP['TransformParameters'][0])
            rot = float(self.STP['TransformParameters'][1])


            t_x = float(self.STP['TransformParameters'][2])
            t_y = float(self.STP['TransformParameters'][3])

            matrix = np.array([[scale*np.cos(rot),scale*-np.sin(rot),0],
                             [scale *np.sin(rot), scale*np.cos(rot), 0],
                            [0.,0.,1]])

        elif self.STP["Transform"][0] == "AffineTransform":
            matrix = np.array([[float(self.STP['TransformParameters'][0]),float(self.STP['TransformParameters'][1]),0],
                             [float(self.STP['TransformParameters'][2]), float(self.STP['TransformParameters'][3]), 0],
                            [0.,0.,1]])
            t_x = float(self.STP['TransformParameters'][4])
            t_y = float(self.STP['TransformParameters'][5])


        test = np.matmul(matrix, np.array([c_x,c_y,1]))
        center_offset = np.array([c_x+ t_x, c_y+t_y,0])-test
        matrix[0,2] = center_offset[0]
        matrix[1,2] = center_offset[1]


        return matrix.flatten()[0:8]
        #elif self.STP["Transform"] == "AffineTransform":
        #    return np.array([])


    def transform_3d(self,moving_images, fixed_images):
        """
        Not tested yet...
        """
        vectorOfMoving_Images = sitk.VectorOfImage()
        for image in moving_images:
            vectorOfMoving_Images.push_back(sitk.GetImageFromArray(image))
        moving_image = sitk.JoinSeries(vectorOfMoving_Images)

        vectorOfFixed_Images = sitk.VectorOfImage()
        for image in fixed_images:
            vectorOfFixed_Images.push_back(sitk.GetImageFromArray(image))
        fixed_image = sitk.JoinSeries(vectorOfFixed_Images)


        # Register
        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.SetFixedImage(fixed_image)
        elastixImageFilter.SetMovingImage(moving_image)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap('groupwise'))
        elastixImageFilter.Execute()
        elastixImageFilter.GetTransformParameterMap(0)
        sitk.WriteParameterFile(self.BTP, "../tmp/b_spline.txt")


    @property
    def fixed_image(self)->np.ndarray:
        return sitk.GetArrayFromImage(self._fixed_i)

    @fixed_image.setter
    def fixed_image(self, value:[str,np.ndarray]):
        if isinstance(value, str):
            self._fixed_i = sitk.ReadImage(value)
        else:
            self._fixed_i = sitk.GetImageFromArray(value)

    @property
    def moving_image(self)->np.ndarray:
        return sitk.GetArrayFromImage(self._move_i)

    @moving_image.setter
    def moving_image(self, value:[str,np.ndarray]):
        if isinstance(value, str):
            self._move_i = sitk.ReadImage(value)
        else:
            self._move_i = sitk.GetImageFromArray(value)

    @property
    def result_image(self)->np.ndarray:
        return sitk.GetArrayFromImage(self.process.GetResultImage())

    @property
    def t_result_image(self)->np.ndarray:
        return sitk.GetArrayFromImage(self.t_process.GetResultImage())


    @property
    def affineParameterMap(self):
        return self._affineParameterMap

    @affineParameterMap.setter
    def affineParameterMap(self,file:str):
        self._affineParameterMap = sitk.ReadParameterFile(os.path.join(self.wd, file))

    @property
    def similarityParameterMap(self):
        return self._similarityParameterMap

    @similarityParameterMap.setter
    def similarityParameterMap(self, file:str):
        self._similarityParameterMap = sitk.ReadParameterFile(os.path.join(self.wd, file))

    @property
    def bSplineParameterMap(self):
        return self._bSplineParameterMap

    @bSplineParameterMap.setter
    def bSplineParameterMap(self, file:str):
        self._bSplineParameterMap = sitk.ReadParameterFile(os.path.join(self.wd, file))