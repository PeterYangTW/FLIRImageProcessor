# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 02:05:34 2022

@author: Peter
"""
from FlirImageProcessor import FLIRImage

import subprocess
import json
import numpy
import os
from io import BytesIO
from PIL import Image, ImageEnhance
from matplotlib import cm

class flir_image(FLIRImage):
    def __init__(self,ImageName):
       #設定顯示及儲存用的ColorMap
       self.colormap = cm.gray
       #
       self.ImageName = ImageName
       self.ExifToolPath = "exiftool"
       self.PrintAllExifMetaData = False
       self.FlirObject = self.GetFlirFileData()
       self.MinTemp=numpy.amin(self.FlirObject['ThermalData'])
       self.MaxTemp=numpy.amax(self.FlirObject['ThermalData'])
       self.ThermalMin = self.MinTemp
       self.ThermalMax = self.MaxTemp
       self.ThresholdTemperature = 20.0
        
       NormalWidth=self.FlirObject['MetaData']['EmbeddedImageWidth']
       NormalHeight=self.FlirObject['MetaData']['EmbeddedImageHeight']
        
    def GetFlirFileData(self):
       FlirDataDict=dict()

       #First Get all the Exif Meta Data from the image, binaries are not part of this.
       FlirDataDict['MetaData'] = self.__GetMetaData()

       if self.PrintAllExifMetaData:
           for key,value in FlirDataDict['MetaData'].items():
             print(key.__str__()+" : "+value.__str__())

       #Now get the raw thermal camera data and convert the raw data to temperatures using the camera's calibration values from the ExifData.
       PlanckR1=FlirDataDict['MetaData']["PlanckR1"]
       PlanckR2=FlirDataDict['MetaData']["PlanckR2"]
       PlanckB=FlirDataDict['MetaData']["PlanckB"]
       PlanckF=FlirDataDict['MetaData']["PlanckF"]
       PlanckO=FlirDataDict['MetaData']["PlanckO"]
       Emissivity=FlirDataDict['MetaData']['Emissivity']
       RAT=float(FlirDataDict['MetaData']['ReflectedApparentTemperature'].split(" ")[0])
       ExifByteOrder=FlirDataDict['MetaData']['ExifByteOrder']
       FlirDataDict['ThermalData'] = self.__GetThermalData(PlanckR1, PlanckR2, PlanckB, PlanckF, PlanckO, Emissivity, RAT, ExifByteOrder)

       #Finally get the Normal image data
       FlirDataDict['PictureData'] = self.__GetPictureData()
       
       return (FlirDataDict)
   
    def __GetMetaData(self):
       JsonMetaData = super().GetMetaData()
       #print('get_meta : '+self.ImageName)
       return (JsonMetaData)
    
    def __GetThermalData(self, PlanckR1, PlanckR2, PlanckB, PlanckF, PlanckO, Emissivity, RAT, ExifByteOrder="Little-endian (Intel, II)"):
       TemperatureData = super().GetThermalData(PlanckR1, PlanckR2, PlanckB, PlanckF, PlanckO, Emissivity, RAT, ExifByteOrder)
       return (TemperatureData)
    
    def __GetPictureData(self):
       ImageData = super().GetPictureData()
       return (ImageData)
   
    def __RescaleImageColorMap(self, ImageArray):
       NormalizedImage = super().RescaleImageColorMap(ImageArray)
       return(NormalizedImage)
   
    def SaveThermalImage(self, ImageData, Name):
       Name = Name.split('/')[-1]
       image_path = "./thermal"
       
       if not(os.path.exists(image_path)):
           os.mkdir(image_path)
    
       MyImage = Image.fromarray(self.colormap(ImageData, bytes=True))
       # convert to jpeg and enhance
       MyImage = MyImage.convert("RGB")
       MyImage = ImageEnhance.Sharpness(MyImage).enhance(3)
       MyImage.save(f"{image_path}/{Name}.jpeg", quality=100)
       #super().SaveThermalImage(ImageData, Name)
       
    def SaveImage(self, ImageData, Name):
       Name = Name.split('/')[-1]
       image_path = "./RGB"
       
       if not(os.path.exists(image_path)):
           os.mkdir(image_path)
       
       MyImage = Image.fromarray(ImageData)
       MyImage.save(f"{image_path}/{Name}.jpeg", quality=100)          
       #MyImage.save(Name, "jpeg", quality=100)
   
    def save_ImageIR(self):
       ThermalImageArr = numpy.array(Image.fromarray(self.FlirObject['ThermalData']))
       ThermalImageToSave = self.RescaleImageColorMap(ThermalImageArr)
       self.SaveThermalImage(ThermalImageToSave, self.ImageName.split('.')[1]+"_Thermal.jpg")
    
    def save_ImageRGB(self):
       NewRGBImage = numpy.array(Image.fromarray(self.FlirObject['PictureData']))
       self.SaveImage(NewRGBImage, self.ImageName.split('.')[1]+"_RGB.jpg")
       
##############################################################################################################
# Main Application
##############################################################################################################
if __name__ == '__main__':
    
    # 指定要列出所有檔案的目錄
    source_path = "./inputs"

    # 取得所有檔案與子目錄名稱
    source_list = os.listdir(source_path)
    #print(source_list)
    
    for f in source_list:
        fpath = source_path + '/' +f
        print(fpath)
        FlirImage = flir_image(fpath)
        FlirImage.save_ImageIR()
        FlirImage.save_ImageRGB()
    
    
    
