"""
Implements the Class "CubeFile"

Author: Justus Stephani
"""

import os

import numpy as np
import numpy.typing as npt

from skimage import measure
import open3d

import logging
import logging.config

from typing import Self, TextIO, Tuple

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logging.conf")
)
loggerErr = logging.getLogger("stderr")
loggerOut = logging.getLogger("stdout")
loggerDebug = logging.getLogger("debug")


class CubeFile:
    """Class Cube File
    Implemented as a context manager.
    - Read a gaussian cube files.
    """

    elementNumToString = {
        0: "udf",
        1: "H",
        2: "He",
        3: "Li",
        4: "Be",
        5: "B",
        6: "C",
        7: "N",
        8: "O",
        9: "F",
        10: "Ne",
        11: "Na",
        12: "Mg",
        13: "Al",
        14: "Si",
        15: "P",
        16: "S",
        17: "Cl",
        18: "Ar",
        19: "K",
        20: "Ca",
        21: "Sc",
        22: "Ti",
        23: "V",
        24: "Cr",
        25: "Mn",
        26: "Fe",
        27: "Co",
        28: "Ni",
        29: "Cu",
        30: "Zn",
        31: "Ga",
        32: "Ge",
        33: "As",
        34: "Se",
        35: "Br",
        36: "Kr",
        37: "Rb",
        38: "Sr",
        39: "Y",
        40: "Zr",
        41: "Nb",
        42: "Mo",
        43: "Tc",
        44: "Ru",
        45: "Rh",
        46: "Pd",
        47: "Ag",
        48: "Cd",
        49: "In",
        50: "Sn",
        51: "Sb",
        52: "Te",
        53: "I",
        54: "Xe",
        55: "Cs",
        56: "Ba",
        57: "La",
        58: "Ce",
        59: "Pr",
        60: "Nd",
        61: "Pm",
        62: "Sm",
        63: "Eu",
        64: "Gd",
        65: "Tb",
        66: "Dy",
        67: "Ho",
        68: "Er",
        69: "Tm",
        70: "Yb",
        71: "Lu",
        72: "Hf",
        73: "Ta",
        74: "W",
        75: "Re",
        76: "Os",
        77: "Ir",
        78: "Pt",
        79: "Au",
        80: "Hg",
        81: "Tl",
        82: "Pb",
        83: "Bi",
        84: "Po",
        85: "At",
        86: "Rn",
        87: "Fr",
        88: "Ra",
        89: "Ac",
        90: "Th",
        91: "Pa",
        92: "U",
        93: "Np",
        94: "Pu",
        95: "Am",
        96: "Cm",
    }

    def __init__(self, cubeFilePath: str) -> None:
        """Cube File init"""
        self.cubeFilePath = cubeFilePath

    def __enter__(self) -> Self:
        """Cube File context manager enter"""
        try:
            self.cubeFile = open(self.cubeFilePath, "r")
            self._readCubeFile(self.cubeFile)
            self.cubeFile.close
        except IOError as e:
            loggerErr.exception(f"CubeFile: {self.cubeFilePath} could not be read.")
        loggerOut.info(f"Finished reading cube file {self.cubeFilePath}")

        return self

    def __exit__(self, type, value, traceback):
        """Cube File context manager exit"""
        del self

    def _readCubeFile(self, f: TextIO) -> None:
        """readCubeFile
        Read the Cube File, store information about the system located in the header of the cube file in np.arrays
        and store the data of the cube file in an np.array

        The following class attributes are created:
        - numberOfAtoms
        - numberOfVoxelsX, numberOfVoxelsY, numberOfVoxelsZ
        - voxelVectorX, voxelVectorY, voxelVectorZ
        - nameOfAtoms
        - chargeOfAtoms
        - coordinatesOfAtoms
        - simulationBoxSize
        - data

        params:
                None
        returns:
                None
        """

        # Line 1 and two are comments and are ignored
        f.readline()
        f.readline()

        # Read the file header
        self.numberOfAtoms, self.origin = self._readHeaderLineShort(f)
        self.numberOfVoxelsX, self.voxelVectorX = self._readHeaderLineShort(f)
        self.numberOfVoxelsY, self.voxelVectorY = self._readHeaderLineShort(f)
        self.numberOfVoxelsZ, self.voxelVectorZ = self._readHeaderLineShort(f)

        self.nameOfAtoms = np.empty((self.numberOfAtoms), str)
        self.chargeOfAtoms = np.empty((self.numberOfAtoms), int)
        self.coordinatesOfAtoms = np.empty((self.numberOfAtoms, 3), float)
        for i in range(self.numberOfAtoms):
            element, charge, coordinates = self._readHeaderLineLong(f)
            self.nameOfAtoms[i] = self.elementNumToString[element]
            self.chargeOfAtoms[i] = charge
            self.coordinatesOfAtoms[i] = np.array([coordinates])

        # Determine the units of the cube file from file header
        if (
            self.numberOfVoxelsX < 0
            or self.numberOfVoxelsX < 0
            or self.numberOfVoxelsX < 0
        ):
            self.unit = "Angstrom"
            self.numberOfVoxelsX = abs(self.numberOfVoxelsX)
            self.numberOfVoxelsY = abs(self.numberOfVoxelsY)
            self.numberOfVoxelsZ = abs(self.numberOfVoxelsZ)
        else:
            self.unit = "Bohr"

        # Determine voxel size from file header
        self.voxelSizeX = self.voxelVectorX[0]
        self.voxelSizeY = self.voxelVectorY[1]
        self.voxelSizeZ = self.voxelVectorZ[2]

        # Determine simulation box size from file header
        self.simulationBoxSize = np.array(
            [
                (self.numberOfVoxelsX - 1) * self.voxelSizeX,
                (self.numberOfVoxelsY - 1) * self.voxelSizeY,
                (self.numberOfVoxelsZ - 1) * self.voxelSizeZ,
            ]
        )

        # read the data of the cube file
        self.data = np.zeros(
            (self.numberOfVoxelsX * self.numberOfVoxelsY * self.numberOfVoxelsZ)
        )
        idx = 0
        for line in f:
            for value in line.split():

                # This happens when the value is smaller than E99. For E100 is not enogh space and the E is ommit (e. g. 0.806033-100)
                if "E" not in value:
                    value = 0

                try:
                    self.data[idx] = float(value)
                except ValueError:
                    loggerErr.exception("Failed to convert string to float")

                idx += 1

        self.data = np.reshape(
            self.data,
            (self.numberOfVoxelsX, self.numberOfVoxelsY, self.numberOfVoxelsZ),
        )

    def _readHeaderLineShort(self, file: TextIO) -> Tuple[int, np.ndarray]:
        """Read a single line of the header of the cube file and return the leading int and
            the float values that follow it.
            Short means it has only one leading int and three float values
        params:
                file (instance of the file)
        return:
                leadingInt, listOfFloats ((int, np.array([])))
        """
        lineSplit = file.readline().split()

        leadingInt = int(lineSplit[0])
        listOfFloats = np.array(list(map(float, lineSplit[1:])))

        return leadingInt, listOfFloats

    def _readHeaderLineLong(self, file: TextIO) -> Tuple[int, float, np.ndarray]:
        """Read a single line of the header of the cube file and return the leading int, float value
            the  rest of float values that follow it as a list.
            Long means it has only one leading int and four float values
        params:
                file (instance of the file)
        return:
                leadingInt, firstFloat, listOfFloats ((int, float, np.array([])))
        """
        leadingInt, listOfFloats = self._readHeaderLineShort(file)
        return leadingInt, listOfFloats[0], listOfFloats[1:]
    

    def createMesh(self, isosurfaceValue:float=0.0001, filterIterations:int=1) -> open3d.geometry.TriangleMesh:
        ''' Creat a mesh from the cube file data by calculating an isosurface (vertecies, faces) using the marching
            cubes algorithm and make a tringle mesh from that.
        params: 
                isosurfaceValue (float) = 0.0001: parameter for the marchingCubeAlgo to determine the iosurface level
                filterIterations (int) = 1: How oftern to filter (smooth) the resulting mesh in open3D
        return: 
                mesh (open3d.geometry.TriangleMesh()): The isosurface of the cube file as a open3d triangleMesh
        '''
        verts, faces = self._calculateIsosurfaces(isosurfaceValue)
        mesh = self._createMeshFromVerticesAndFaces(verts, faces, filterIterations)

        return mesh


    def _calculateIsosurfaces(self, isosurfaceValue:float=0.0001) -> Tuple[np.ndarray, np.ndarray]:
        ''' Calculating an isosurface (vertecies, faces) using the marching
            cubes algorithm and translate the vertecies to the origin of the cube file data.
        params: 
                isosurfaceValue (float) = 0.0001: parameter for the marchingCubeAlgo to determine the iosurface level
        return: 
                verts, faces ((np.array([]), np.array([]))): The isosurface of the cube file in the form of (vertecies, faces)
        '''
        try:
            verts, faces, _, _ = measure.marching_cubes(self.data,
                                                        spacing=(self.voxelSizeX, 
                                                                self.voxelSizeY, 
                                                                self.voxelSizeZ),
                                                        level=isosurfaceValue)
        except:
            loggerErr.exception(f'Could not calculate verts, faces from cube file')
            return [], []

        verts = self._translateVerteciesToCenterOfSimulationBox(verts)

        return verts, faces

    def _translateVerteciesToCenterOfSimulationBox(self, verts: npt.ArrayLike) -> np.ndarray:
        ''' Translate the vertecies to the origin of the cube file data.
        params: 
                verts (np.array([])): Vertecies of the isosurface
        return: 
                verts (np.array([])): Vertecies of the isosurface
        '''
        verts[:, 0] = verts[:, 0] - abs(self.origin[0])
        verts[:, 1] = verts[:, 1] - abs(self.origin[1])
        verts[:, 2] = verts[:, 2] - abs(self.origin[2])

        return verts


    def _createMeshFromVerticesAndFaces(self,
                                        verts: npt.ArrayLike,
                                        faces: npt.ArrayLike,
                                        filterIterations: int) -> open3d.geometry.TriangleMesh:
        ''' create a trinangle mesh from vertices and faces
        params: 
                verts (np.array([])): Vertecies of the isosurface
                faces (np.array([])): Faces of the isosurface
                ilterIterations (int): How often to "smooth" the mesh
        return: 
                mesh (open3d.geometry.TriangleMesh()): The isosurface of the cube file as a open3d triangleMesh
        '''
        try:
            mesh = open3d.geometry.TriangleMesh()
            mesh.vertices = open3d.utility.Vector3dVector(verts)
            mesh.triangles = open3d.utility.Vector3iVector(faces)
            mesh.filter_smooth_simple(number_of_iterations=filterIterations)
        except:
            loggerErr.exception(f'Could not create mesh from vers and faces')

        return mesh


    def exportCubeFileIsosurfaceToFile(self,
                                       pathToOutputFile: str,
                                       mesh: open3d.geometry.TriangleMesh) -> None:
        ''' export the cube file Isosurface to a file.
            File support for .ply and .obj
        params: 
                pathToOutputFile (str): path to the output file
                mesh (open3d.geometry.TriangleMesh()): The isosurface of the cube file as a open3d triangleMesh
        return: 
                None
        '''
        try:
            open3d.io.write_triangle_mesh(pathToOutputFile, mesh, write_ascii=True)
        except:
            loggerErr.exception(f'Could not write mesh to file: {pathToOutputFile}')
