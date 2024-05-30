### Render Cube File
This is a Python script to render [Gaussian cube files](https://gaussian.com/cubegen/) using the free, open-source 3D creation suite [Blender](https://www.blender.org/).

A Gaussian cube file type described discrete volumetric data as well as atom positions.  The file consists of a header which includes the atom information and the size of the volumetric data, which is followed by the volumetric data, one scalar per voxel element.  It is a common output of multiple quantum chemistry programs. The cube files in this repository have been created via a time-dependent density functional theory calculation using [Octopus Code](https://www.octopus-code.org/). 

The script works by providing a path to a cube file and an .json input file:

    {
      "filterIterations": 0,
      "isosurfaceValue": 0.001,
      "deleteOBJFile": true,
      "pathToOBJFile": "/tmp/tmp.obj",
      "focalLenght": 70,
      "cameraLocation": "-x",
      "imagePath" : "README_files/cubeFileRender.png"
    }

There are multiple ways to run this script, which are described below.

#### Run via python:

Install a virtual environment with python3.11 via:

    make install



```python
from renderCubeFile import RenderCubeFile

r = RenderCubeFile(pathToCubeFile='README_files/test.cube',pathToInputFile='README_files/testInputFile.json')
r.renderScene()
```

    Jupyter environment detected. Enabling Open3D WebVisualizer.
    [Open3D INFO] WebRTC GUI backend enabled.
    [Open3D INFO] WebRTCWindowSystem: HTTP handshake server disabled.


    2024-05-30 13:28:12,053 - INFO - Finished with reading input file README_files/testInputFile.json


    2024-05-30 13:28:12,069 - INFO - Finished reading cube file README_files/test.cube


    OBJ import of 'tmp.obj' took 1.61 ms
    Fra:1 Mem:44.37M (Peak 45.43M) | Time:00:00.15 | Syncing New Light
    Fra:1 Mem:44.37M (Peak 45.43M) | Time:00:00.15 | Syncing Camera
    Fra:1 Mem:44.38M (Peak 45.43M) | Time:00:00.15 | Syncing tmp
    Fra:1 Mem:44.93M (Peak 45.43M) | Time:00:00.17 | Syncing Sphere
    Fra:1 Mem:45.06M (Peak 45.43M) | Time:00:00.18 | Syncing Sphere.001
    Fra:1 Mem:45.16M (Peak 45.43M) | Time:00:00.19 | Syncing Sphere.002
    Fra:1 Mem:45.25M (Peak 45.43M) | Time:00:00.19 | Syncing Cylinder
    Fra:1 Mem:45.27M (Peak 45.43M) | Time:00:00.19 | Syncing Cylinder.001
    Fra:1 Mem:45.27M (Peak 45.43M) | Time:00:00.19 | Rendering 1 / 65 samples
    Fra:1 Mem:44.82M (Peak 45.43M) | Time:00:00.24 | Rendering 26 / 64 samples
    Fra:1 Mem:44.82M (Peak 45.43M) | Time:00:00.24 | Rendering 51 / 64 samples
    Fra:1 Mem:44.82M (Peak 45.43M) | Time:00:00.25 | Rendering 64 / 64 samples


    Saved: 'README_files/cubeFileRender.png'
    Time: 00:01.75 (Saving: 00:00.38)
    


![alt text](README_files/cubeFileRender.png)

If you have multiple cube files from a real-time time-dependent density functional theory calculation, you can make an simple animation form multiple cube files:


```python
from renderCubeFile import RenderCubeFile
from os import walk, path
# get all cube files from the tddft simulation
pathToCubeFiles = []
for (root, _, filenames) in walk('README_files/collision/'):
    for filename in filenames:
        if filename.split('.')[1] == 'cube':
            pathToCubeFiles.append(path.join(root, filename))
pathToCubeFiles.sort()

# render the cube files to pngs
for cubeFile in pathToCubeFiles:
    print (cubeFile)
    r = RenderCubeFile(cubeFile, 'README_files/testInputFile.json')
    r.renderScene(f'{cubeFile.split(".")[0]}.png')
```
    

Render the .png files to a animation:


```python
from os import walk, path
import contextlib
from PIL import Image

# get all pngs files
pngs = []
for (root, _, filenames) in walk('README_files/collision/'):
    for filename in filenames:
        if filename.split('.')[1] == 'png':
            pngs.append(path.join(root, filename))
pngs.sort()

# Render the pngs to an animation
with contextlib.ExitStack() as stack:
    imgs = (stack.enter_context(Image.open(f)) for f in pngs)
    img = next(imgs)
    img.save(fp='README_files/collision.gif', format='GIF', append_images=imgs,
             save_all=True, duration=8, loop=0)


```

![alt text](README_files/collision.gif)

#### Run via Blender:

You can also run the script via the command line using a blender installation downloaded [here](https://www.blender.org/download/).
This way, the internal Python installation Blender ships with is used, and the required modules are installed there.

    <pathToBlenderExe> --background --python renderCubeFile.py  -- --cubeFile <pathToCubeFile> --inputFile <pathToInputFile>
