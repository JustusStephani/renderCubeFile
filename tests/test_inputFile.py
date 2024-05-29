import os
import pytest


from src.inputFile import InputFile


PATH_TO_MOCK_INPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "testData/mockInputFile.json"
)

PATH_TO_NON_VALID_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "testData/nonValid.json"
)

NOT_VALID_PATH = 'null'

validTestData={
  "filterIterations": 2,
  "isosurfaceValue": 0.001,
  "deleteOBJFile": True,
  "pathToOBJFile": "/tmp/tmp.obj",
  "focalLenght": 140,
  "cameraLocation": "-z",
  "imagePath" : "./cubeFileRender.png"
}
nonValidTestData={
  "filterIterations": False,
  "isosurfaceValue": 0.001,
  "deleteOBJFile": True,
  "pathToOBJFile": "/tmp/tmp.obj",
  "focalLenght": 140,
  "cameraLocation": "-z",
  "imagePath" : "./cubeFileRender.png"
}


@pytest.fixture
def inputFileInstance():
    return InputFile()

def test_readInputFile(inputFileInstance):
    # valid file
    data = inputFileInstance.readInputFile(PATH_TO_MOCK_INPUT_FILE)
    assert data == validTestData

    # non valid path
    with pytest.raises(IOError) as context:
        inputFileInstance.readInputFile(NOT_VALID_PATH)

    # non valid json
    with pytest.raises(ValueError) as context:
        inputFileInstance.readInputFile(PATH_TO_NON_VALID_JSON)

def test_validateData(inputFileInstance):
    # valid 
    inputFileInstance._validateData(validTestData)

    # non valid
    with pytest.raises(ValueError) as context:
        inputFileInstance._validateData(nonValidTestData)


def test_validatePath(inputFileInstance):
    # valid
    inputFileInstance._validatePath(PATH_TO_MOCK_INPUT_FILE)

    # non valid
    with pytest.raises(OSError) as context:
        inputFileInstance._validatePath(NOT_VALID_PATH)

    
    
    
