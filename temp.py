from PIL import Image
import glob
import sys
import numpy as np

def createFloatArray(height_start, height_end, width_start, width_end, pix_vals):
    numRows = height_end - height_start
    numCols = width_end - width_start
    intArray = np.zeros((numRows, numCols, 3),dtype = np.int32)
    for y in range(numRows):
        for x in range(numCols):
            intArray[y][x][0] = pix_vals[x,y][0]
            intArray[y][x][1] = pix_vals[x,y][1]
            intArray[y][x][2] = pix_vals[x,y][2]

    floatArray = intArray.astype(float)
    return floatArray




image = "imgs/image"+str(sys.argv[1])+".jpg"
im = Image.open(image,'r')
pix_vals = im.load()
width,height = im.size
height_2 = height // 2;
dataArray = createFloatArray(height_2, height_2+1, 0, width-1, pix_vals)
dataArray = createFloatArray(height_2, height-1, 0, width-1, pix_vals)
