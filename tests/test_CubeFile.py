import pytest

import pprint
import sys

pprint.pprint(sys.path)

import os

import numpy as np

from cubeFile import CubeFile

PATH_TO_MOCK_CUBE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "testData/mock.cube"
)


class Test_CubeFile:

    def test_readCubeFile(self):
        with CubeFile(PATH_TO_MOCK_CUBE_FILE) as c:
            assert c.numberOfAtoms == 3, "incorrect numberOfAtoms"
            assert np.array_equal(
                c.origin, [-4.500000, -4.500000, -4.500000]
            ), "incorrect origin"
            assert c.numberOfVoxelsX == 31, "incorrect numberOfVoxelsX"
            assert c.numberOfVoxelsY == 31, "incorrect numberOfVoxelsY"
            assert c.numberOfVoxelsZ == 31, "incorrect numberOfVoxelsZ"
            assert np.array_equal(
                c.voxelVectorX, [0.3, 0.0, 0.0]
            ), "incorrect voxelVectorX"
            assert np.array_equal(
                c.voxelVectorY, [0.0, 0.3, 0.0]
            ), "incorrect voxelVectorY"
            assert np.array_equal(
                c.voxelVectorZ, [0.0, 0.0, 0.3]
            ), "incorrect voxelVectorZ"
            assert np.array_equal(
                c.nameOfAtoms,
                [
                    "O",
                    "H",
                    "H",
                ],
            ), "incorrect atomNames"
            assert np.array_equal(
                c.chargeOfAtoms,
                [
                    0.0,
                    0.0,
                    0.0,
                ],
            ), "incorrect chargeOfAtoms"
            assert np.array_equal(
                c.coordinatesOfAtoms,
                [
                    [0.739512, 0.000000, 0.000000],
                    [-0.369757, 0.000000, 1.472097],
                    [-0.369757, 0.000000, -1.472097],
                ],
            ), "incorrect coordinatesOfAtoms"
            assert c.unit == "Bohr", "incorrect unit"
            assert c.voxelSizeX == 0.3, "incorrect voxelSizeX"
            assert c.voxelSizeY == 0.3, "incorrect voxelSizeY"
            assert c.voxelSizeZ == 0.3, "incorrect voxelSizeZ"
            assert np.array_equal(
                c.simulationBoxSize, [9.0, 9.0, 9.0]
            ), "incorrect simulationBoxSize"
            assert np.array_equal(c.data.shape, (31, 31, 31)), "incorrect data.shape"
            assert c.data[12, 14, 2] == 0.000139717, "incorrect data value [12, 14, 2]"
