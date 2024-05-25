"""
Implements the Class "RenderCubeFile"

Author: Justus Stephani
"""

import os
import sys

import logging
import logging.config

import bpy

from math import radians

from src.cubeFile import CubeFile
from src.inputFile import InputFile
from src.argumentParser import ArgumentParserForBlender

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf")
)
loggerErr = logging.getLogger("stderr")
loggerOut = logging.getLogger("stdout")
loggerDebug = logging.getLogger("debug")

BACKGROUND_COLOR = (1, 1, 1, 1)

class RenderCubeFile():

    def __init__(self, pathToCubeFile, pathToInputFile:str='') -> None:
        inputData = self._getInputData(pathToInputFile)
        self.imagePath = inputData['imagePath']

        self._createScene(inputData['cameraLocation'], inputData['focalLenght'])

        with CubeFile(pathToCubeFile) as c:
            mesh = c.createMesh(inputData['isosurfaceValue'], inputData['filterIterations'])
            c.exportCubeFileIsosurfaceToFile(inputData['pathToOBJFile'], mesh)

            self._drawOBJStructure(inputData['pathToOBJFile'])

            if inputData['deleteOBJFile']:
                os.remove(inputData['pathToOBJFile'])


    def _getInputData(self, pathToInputFile) -> dict:
        inputFile = InputFile()
        if pathToInputFile != '':
            inputData =  inputFile.readInputFile(pathToInputFile)
        else:
            inputData = inputFile.defaultValues

        return inputData
    
     
    def _createScene(self, cameraLocation, focalLenght):
        self._cleanUpDefaultBlenderScene()
        
        self.context = bpy.context
        self.scene = self.context.scene
        self.viewLayer = bpy.context.view_layer

        self._setBackground()
        self._createLight(cameraLocation)
        self._createCamera(cameraLocation, focalLenght)


    def _cleanUpDefaultBlenderScene(self) -> None:
        objs = bpy.data.objects
        objs.remove(objs["Cube"], do_unlink=True)
        objs.remove(objs["Camera"], do_unlink=True)
        objs.remove(objs["Light"], do_unlink=True)
        
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)

        for texture in bpy.data.textures:
            if not texture.users:
                bpy.data.textures.remove(texture)
    

    def _setBackground(self, ) -> None:
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = BACKGROUND_COLOR
                

    def _createLight(self, cameraLocation: str) -> None:
        lightData = bpy.data.lights.new('sun', 'SUN')
        lightData.energy = 5.0
        lightData.angle = 180.0 
        light = bpy.data.objects.new(name="New Light", object_data=lightData)

        self.viewLayer.active_layer_collection.collection.objects.link(light)

        if cameraLocation == '-x':
            lightLocationCoordinates = (-80.0, 0, 80.0)
            lightLocationRotationAngles = (0.0, 0.0, 0.0)
        elif cameraLocation == '+x':
            lightLocationCoordinates = (80.0, 0, 80.0)
            lightLocationRotationAngles = (0.0, 0.0, 0.0)
        elif cameraLocation == '-y':
            lightLocationCoordinates = (0.0, -80.0, 80.0)
            lightLocationRotationAngles = (0.0, 0.0, 0.0)
        elif cameraLocation == '+y':
            lightLocationCoordinates = (0.0, 80.0, 80.0)
            lightLocationRotationAngles = (0.0, 0.0, 0.0)
        elif cameraLocation == '-z':
            lightLocationCoordinates = (0.0, 80.0, -80.0)
            lightLocationRotationAngles = (-90.0, 0.0, 0.0) 
        elif cameraLocation == '+z':
            lightLocationCoordinates = (0.0, 80.0, 80.0)
            lightLocationRotationAngles = (-90.0, 0.0, 0.0) 

        light.location = lightLocationCoordinates
        light.rotation_euler = ([radians(a) for a in lightLocationRotationAngles])              
                

    def _createCamera(self, cameraLocation: str, focalLenght: float) -> None:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        cam.data.lens = focalLenght
       
        self.scene.camera = cam
        
        if cameraLocation == '-x':
            cameraLocationCoordinates = (-70.0, 0.0, 0.0)
            cameraLocationRotationAngles = (90.0, 0.0, -90.0)
        elif cameraLocation == '+x':
            cameraLocationCoordinates = (70.0, 0.0, 0.0)
            cameraLocationRotationAngles = (270.0, 180.0, -90.0)
        elif cameraLocation == '-y':
            cameraLocationCoordinates = (0.0, -70.0, 0.0)
            cameraLocationRotationAngles = (90.0, 00.0, 0.0)
        elif cameraLocation == '+y':
            cameraLocationCoordinates = (0.0, 70.0, 0.0)
            cameraLocationRotationAngles = (-90.0, 180.0, 0.0)
        elif cameraLocation == '-z':
            cameraLocationCoordinates = (0.0, 0.0, -70.0)
            cameraLocationRotationAngles = (0.0, 180.0, 0.0)
        elif cameraLocation == '+z':
            cameraLocationCoordinates = (0.0, 0.0, 70.0)
            cameraLocationRotationAngles = (0.0, 0.0, 0.0)

        self.scene.camera.location = cameraLocationCoordinates
        self.scene.camera.rotation_euler = ([radians(a) for a in cameraLocationRotationAngles])
            

    def renderScene(self, imagePath: str) -> None:
        bpy.context.scene.render.filepath = imagePath
        bpy.ops.render.render(write_still = True)  


    def _drawOBJStructure(self, pathToOBJFile: str) -> None:
        def _createTransperentOBJShader():
            mat = bpy.data.materials.new('Transperent')
            
            mat.use_nodes=True

            nodes = mat.node_tree.nodes
            nodes.clear()
            
            links = mat.node_tree.links

            node_output = nodes.new(type='ShaderNodeOutputMaterial')
            node_output.location = 700,0
            
            node_pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            node_pbsdf.location = 0,0
            node_pbsdf.inputs['Base Color'].default_value = (0.0, 0.0, 1.0, 1.0)
            node_pbsdf.inputs['Alpha'].default_value = 0.8
            node_pbsdf.inputs['Roughness'].default_value = 1
            
            node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
            node_transparent.location = 300,-200
            
            node_mix = nodes.new(type='ShaderNodeMixShader')
            node_mix.location = 500,0
            
            link = links.new(node_pbsdf.outputs['BSDF'], node_mix.inputs[1])
            link = links.new(node_transparent.outputs['BSDF'], node_mix.inputs[2])
            link = links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])

            mat.blend_method = 'BLEND'
            mat.shadow_method = 'OPAQUE'
            mat.use_screen_refraction = False

            bpy.context.scene.eevee.use_ssr = True
            bpy.context.scene.eevee.use_ssr_refraction = True
            
            return mat
        
        bpy.ops.wm.obj_import(filepath=pathToOBJFile)

        obj = bpy.context.selected_objects[0] 
        mat = _createTransperentOBJShader()
    
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)      
    


if __name__ == "__main__":
    pass

