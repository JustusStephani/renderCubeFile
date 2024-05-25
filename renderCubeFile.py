"""
Implements the Class "RenderCubeFile"

Author: Justus Stephani
"""

import os
import sys

import logging
import logging.config

from src.cubeFile import CubeFile
from src.inputFile import InputFile
from src.argumentParser import ArgumentParserForBlender

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf")
)
loggerErr = logging.getLogger("stderr")
loggerOut = logging.getLogger("stdout")
loggerDebug = logging.getLogger("debug")


class RenderCubeFile():

    def __init__(self, pathToCubeFile, pathToInputFile:str='') -> None:
        inputData = self._getInputData(pathToInputFile)

        with CubeFile(pathToCubeFile) as c:
            mesh = c.createMesh(inputData['isosurfaceValue'], inputData['filterIterations'])
            c.exportCubeFileIsosurfaceToFile(inputData['pathToOBJFile'], mesh)


    def _getInputData(self, pathToInputFile) -> dict:
        inputFile = InputFile()
        if pathToInputFile != '':
            inputData =  inputFile.readInputFile(pathToInputFile)
        else:
            inputData = inputFile.defaultValues

        return inputData


if __name__ == "__main__":
    pass

