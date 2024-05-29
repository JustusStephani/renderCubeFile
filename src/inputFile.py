"""
Implements the Class "InputFile"

Author: Justus Stephani
"""

import json

import numpy as np

import logging
import logging.config

import sys
import os

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logging.conf'))
loggerErr = logging.getLogger('stderr')
loggerOut = logging.getLogger('stdout')
loggerDebug = logging.getLogger('debug')

class InputFile():
    '''
    Class to handle reading and validating input files for rendering cube files.
    '''
    
    defaultValues = {
        'filterIterations': 1,
        'isosurfaceValue': 0.001,
        'deleteOBJFile': True,
        'pathToOBJFile': '/tmp/tmp.obj',
        "focalLenght": 25,
        "cameraLocation": "-y",
        "imagePath" : "./cubeFileRender.png"
    }

    def __init__(self,) -> None:
        '''
        Initialize the InputFile class.
        '''
        pass
    
    def readInputFile(self, pathToInputFile: str) -> dict:
        '''
        Read and validate the input file.

        params:
            pathToInputFile (str): Path to the input file.

        return:
            data (dict): Data from the input file.
        '''
        data = self._getDataFromInputFile(pathToInputFile)
        self._validateData(data)
        loggerOut.info(f'Finished with reading input file {pathToInputFile}')

        return data


    def _getDataFromInputFile(self, pathToInputFile:str) -> dict:
        '''
        Retrieve data from the input file.

        params:
            pathToInputFile (str): Path to the input file.

        return:
            data (dict): Data from the input file.
        '''
        data = {}
        try:
            with open(pathToInputFile, 'r') as f:
                try:
                    inputFileData = json.load(f)
                except ValueError:
                    loggerErr.exception(f'InputFile: {pathToInputFile} is not valid JSON.')
                    raise ValueError(f'InputFile: {pathToInputFile} is not valid JSON.')

                inputKeys = inputFileData.keys()
                for key in self.defaultValues.keys():
                    if key not in inputKeys:
                        pass
                    else:
                        data[key] = inputFileData[key]
        except IOError:
            loggerErr.exception(f'InputFile: {pathToInputFile} could not be open.')
            raise IOError(f'InputFile: {pathToInputFile} could not be open.')

        return data


    def _validateData(self, data:dict) -> None:
        '''
        Validate the input data.

        params:
            data (dict): Data to be validated.

        return:
            None
        '''
        dataKeys = data.keys()

        for key in self.defaultValues.keys():
            if key not in dataKeys:
                data[key] = self.defaultValues[key]

            elif key == 'filterIterations':
                if type(data[key]) != int:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be an integer.')
                    raise ValueError
                if data[key] < 0:
                    loggerErr.exception(f'Filter iterations must be greater than 0.')
                    raise ValueError

            elif key == 'isosurfaceValue':
                if type(data[key]) != float:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be a float.')
                    raise ValueError
                
            elif key == 'deleteOBJFile':
                if type(data[key]) != bool:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be a bool.')
                    raise ValueError

            elif key == 'pathToOBJFile':
                if type(data[key]) != str:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be a str.')
                    raise ValueError
                self._validatePath(data[key])

            elif key == 'focalLenght':
                if type(data[key]) != int:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be an integer.')
                    raise ValueError
                if data[key] < 0:
                    loggerErr.exception(f'Focal length must be greater than 0.')
                    raise ValueError
                
            elif key == 'cameraLocation':
                if type(data[key]) != str:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be a str.')
                    raise ValueError
                elif data[key] not in {'-x', '+x', '-y', '+y', '-z', '+z'}:
                    loggerErr.exception(f'Camera location must be one of these: "-x", "+x", "-y", "+y", "-z", "+z"')
                    raise ValueError
                
            elif key == 'imagePath':
                if type(data[key]) != str:
                    loggerErr.exception(f'Wrong type of value for keyword: {key}. Must be a str.')
                    raise ValueError
                self._validatePath(data[key])

            
    def _validatePath(self, path: str):
        '''
        Validate if the given path exists.

        params:
            path (str): Path to be validated.

        return:
            None
        '''
        if not os.path.exists(path):
            if not os.path.exists(os.path.dirname(path)):
                loggerErr.error(f'Path {path} does not exist! Is the path correct?')
                raise OSError
        
                