"""
Implements the Class "RenderCubeFile"

Author: Justus Stephani
"""

import os
import sys

import logging
import logging.config

import bpy
import chemcoord as cc

import numpy as np
import numpy.typing as npt
from math import radians, pi
import mathutils

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

CONVERSION_BOHR_TO_ANG = 0.529177

atomSizes = {'H' : 0.4,
            'He': 0.45,
            'Li': 0.50,
            'Be': 0.55,
            'B': 0.60,
            'C': 0.65,
            'N': 0.70,
            'O': 0.75,
            'F': 0.80,
            'Ne': 0.90,
            'Na': 0.95,
            'Mg' : 1.00,
            'Al': 1.05,
            'Si': 1.10,
            'P' : 1.15,
            'S' : 1.20,
            'Cl' : 1.25,
            'default': 0.7,
            }

atomColors = {'bond': (0.0, 0.00, 0.00, 1), 
            'default': (1.0, 1.0, 1.0, 1),
            'H' : (1.0, 1.0, 1.0, 1),
            'He': (0.0, .0, 1.0, 1),
            'Li': (0.9, 0.9, 0.9, 1),
            'Be': (1.0, 1.0, 1.0, 1),
            'B': (1.0, 1.0, 1.0, 1),
            'C': (0.13, 0.13, 0.13, 1),
            'N': (1.0, 1.0, 1.0, 1),
            'O': (1.0, 0.0, 0.0, 1),
            'F': (0.85, 0.4, 0.0, 1),
            'Ne': (1.0, 1.0, 1.0, 1),
            'Na': (1.0, 1.0, 1.0, 1),
            'Mg' : (1.0, 1.0, 1.0, 1),
            'Al': (1.0, 1.0, 1.0, 1),
            'Si': (1.0, 1.0, 1.0, 1),
            'P' : (1.0, 0.7, 0.4, 1),
            'S' : (1.0, 1.0, 1.0, 1),
            'Cl' : (1.0, 1.0, 1.0, 1),
            }

class RenderCubeFile():
    '''
    '''
    def __init__(self, pathToCubeFile, pathToInputFile:str='') -> None:
        '''
        Initialize the RenderCubeFile class with paths to cube and input files.
        
        params:
            pathToCubeFile (str): Path to the cube file.
            pathToInputFile (str): Path to the input file. Default is an empty string.

        return: 
            None
        '''
        inputData = self._getInputData(pathToInputFile)
        self.imagePath = inputData['imagePath']

        self._createScene(inputData['cameraLocation'], inputData['focalLenght'])

        with CubeFile(pathToCubeFile) as c:
            mesh = c.createMesh(inputData['isosurfaceValue'], inputData['filterIterations'])
            c.exportCubeFileIsosurfaceToFile(inputData['pathToOBJFile'], mesh)

            self._drawOBJStructure(inputData['pathToOBJFile'])

            if inputData['deleteOBJFile']:
                os.remove(inputData['pathToOBJFile'])

            self._drawAtomsAndBonds(c.coordinatesOfAtoms, c.nameOfAtoms, c.unit)


    def _getInputData(self, pathToInputFile) -> dict:
        '''
        Retrieve input data from the specified input file or default values.
        
        params:
            pathToInputFile (str): Path to the input file.
        
        return:
            dict: Input data as a dictionary.
        '''
        inputFile = InputFile()
        if pathToInputFile != '':
            inputData =  inputFile.readInputFile(pathToInputFile)
        else:
            inputData = inputFile.defaultValues

        return inputData
    
     
    def _createScene(self, cameraLocation, focalLenght) -> None:
        '''
        Create the Blender scene with specified camera location and focal length.
        
        params:
            cameraLocation (str): Camera location in the scene.
            focalLenght (float): Focal length of the camera.
        return: 
            None
        '''
        self._cleanUpDefaultBlenderScene()

        self._setBackground()
        self._createLight(cameraLocation)
        self._createCamera(cameraLocation, focalLenght)


    def _cleanUpDefaultBlenderScene(self) -> None:
        '''
        Clean up the default Blender scene by removing default objects.
        params:
            None
        return:
            None
        '''
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
        '''
        Set the background color of the Blender scene.
        params:
            None
        return:
            None
        '''
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = BACKGROUND_COLOR
                

    def _createLight(self, cameraLocation: str) -> None:
        '''
        Create a light source in the Blender scene based on camera location.
        
        params:
            cameraLocation (str): Camera location in the scene.
        return:
            None
        '''
        lightData = bpy.data.lights.new('sun', 'SUN')
        lightData.energy = 5.0
        lightData.angle = 180.0 
        light = bpy.data.objects.new(name="New Light", object_data=lightData)

        bpy.context.view_layer.active_layer_collection.collection.objects.link(light)

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
        '''
        Create and position a camera in the Blender scene.
        
        params:
            cameraLocation (str): Camera location in the scene.
            focalLenght (float): Focal length of the camera.
        return:
            None
        '''
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        cam.data.lens = focalLenght
       
        bpy.context.scene.camera = cam
        
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

        bpy.context.scene.camera.location = cameraLocationCoordinates
        bpy.context.scene.camera.rotation_euler = ([radians(a) for a in cameraLocationRotationAngles])
            

    def renderScene(self, imagePath: str) -> None:
        bpy.context.scene.render.filepath = imagePath
        bpy.ops.render.render(write_still = True)  


    def _drawOBJStructure(self, pathToOBJFile: str) -> None:
        '''
        Import and draw the OBJ structure in the Blender scene.
        
        params:
            pathToOBJFile (str): Path to the OBJ file.
        return:
            None
        '''

        def _createTransperentOBJShader() -> bpy.data.materials:
            '''
            Import and draw the OBJ structure in the Blender scene.
            
            params:
                None
            return:
                mat: (bpy.data.materials) The material the electron denisty is rendered from
            '''

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


    def _drawAtomsAndBonds(self, atomCoordinates: npt.ArrayLike, atomNames: npt.ArrayLike, unit: str) -> None:
        '''
        Use the names and coordinates of the nuclei from the cube file to draw the atoms. Calcualte the bonds
        using the library chemcoord and draw them as sticks.
        
        params:
            atomCoordinates: (npt.ArrayLike) The coordinates of the atoms
            atomNames: (npt.ArrayLike) The names of the atoms
        return:
            None
        '''

        def _drawAtoms(atomCoordinates: npt.ArrayLike, atomNames: npt.ArrayLike) -> None:
            '''
            Use the names and coordinates of the nuclei from the cube file to draw the atoms
            
            params:
                atomCoordinates: (npt.ArrayLike) The coordinates of the atoms
                atomNames: (npt.ArrayLike) The names of the atoms
            return:
                None
            '''
            for element, position in zip(atomNames, atomCoordinates):
                try:
                    radius=atomSizes[element]
                except:
                    radius=atomSizes["default"]
                    #TODO: GIve a warning here
                bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=position)
                obj = bpy.context.active_object

                try:
                    mat = bpy.data.materials[element]
                except:
                    mat = bpy.data.materials["default"]
                    #TODO: GIve a warning here
                obj.data.materials.append(mat)
                bpy.ops.object.shade_smooth() 
                
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                bpy.ops.transform.rotate(value=-pi / 2, orient_axis='X')

        def _calculateBonds(atomCoordinates: npt.ArrayLike, atomNames: npt.ArrayLike, unit: str) -> set:
            '''
            Calcualte the bonds using the library chemcoord.
            
            params:
                atomCoordinates: (npt.ArrayLike) The coordinates of the atoms
                atomNames: (npt.ArrayLike) The names of the atoms
                unit: (str) The unit the cube file is writen in (default is bohr)
            return:
                Bonds: (set)
            '''
            if unit == 'Bohr':
                atomCoordinates = atomCoordinates * CONVERSION_BOHR_TO_ANG

            # make cc molecule and get bonds dict
            molecule = cc.Cartesian(atoms=atomNames, coords=atomCoordinates)
            bondsDict = molecule.get_bonds()

            # get every bond in a set (atom1OfTheBond, atom2OfTheBond)
            bonds = set()
            for i in range(0, len(bondsDict)):
                for j in bondsDict[i]:
                    bondInList = False
                    if len(bonds) == 0:
                        pass
                    else:
                        for listedBond in bonds:
                            if listedBond[0] == i and listedBond[1] == j or listedBond[0] == j and listedBond[1] == i:
                                bondInList = True
                            
                    if bondInList == False:
                        bonds.add((i, j))

            return bonds
        

        def _drawBonds(bonds: set, atomCoordinates: npt.ArrayLike) -> None:
            '''
            Draw the bonds as cylinders
            
            params:
                bonds: (set) The bonds between the atoms
                atomCoordinates: (npt.ArrayLike) The coordinates of the atoms
            return:
                None
            '''
            def _distance(a, b):
                return np.sqrt(np.dot(a - b, a - b))
        
            def _normalizeVec(vec):
                return np.array(vec) / np.sqrt(np.dot(vec, vec))
            
            for atom1, atom2 in bonds:
                pos1 = atomCoordinates[atom1]
                pos2 = atomCoordinates[atom2]
                
                difference = pos2 - pos1
                center = (pos2 + pos1) / 2.0
                magnitude = _distance(pos1, pos2)
                bondDirection = _normalizeVec(difference)

                vertical = np.array((0.0, 0.0, 1.0))
                rotationAxis = np.cross(bondDirection, vertical)
                angle = -np.arccos(np.dot(bondDirection, vertical))
                
                bpy.ops.mesh.primitive_cylinder_add(radius=0.1, 
                                                    depth=magnitude, 
                                                    location=center,
                                                    )
                                                    
                obj = bpy.context.active_object
                obj.data.materials.append(bpy.data.materials['bond'])
                bpy.ops.object.shade_smooth()
                
                obj.rotation_mode = 'QUATERNION'
                quat = mathutils.Quaternion(rotationAxis, angle)
                obj.rotation_quaternion = quat
                
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                bpy.ops.transform.rotate(value=-pi / 2, orient_axis='X')

        # make materials for atoms
        for key in atomColors.keys():
            bpy.data.materials.new(name=key)
            bpy.data.materials[key].diffuse_color = atomColors[key]
            bpy.data.materials[key].specular_intensity = 1.0
            bpy.data.materials[key].roughness = 1.0

        # for each atom render a sphere
        _drawAtoms(atomCoordinates, atomNames)

        # for each bond render a cylinder
        if len (atomNames) >= 3:
            bonds = _calculateBonds(atomCoordinates, atomNames, unit)
            _drawBonds(bonds, atomCoordinates)


if __name__ == "__main__":
    pass

