from PIL import Image
import glob
import sys
import numpy as np

def createFloatArray(image_num):
    fpt = open("image_data.txt", "wb")
    image = "imgs/image"+str(image_num)+".jpg"
    im = Image.open(image,'r')
    pix_vals = im.load()
    width,height = im.size

    #Create Datasets From Image For extrapolation
    intArray = []
    intArray = np.zeros((height,width,3),dtype = np.int32)
    for y in range(height):
        for x in range(width):
            intArray[y][x][0] = pix_vals[x,y][0]
            intArray[y][x][1] = pix_vals[x,y][1]
            intArray[y][x][2] = pix_vals[x,y][2]


    floatArray = intArray.astype(float)

    # Print the float values
    for y in range(height):
        for x in range(width):
            fpt.write("%f\n" % floatArray[y][x][0])
            fpt.write("%f\n" % floatArray[y][x][1])
            fpt.write("%f\n" % floatArray[y][x][2])

    fpt.close()
    return floatArray


def writeImage(height, width):
    result = pressio.io_data_to_numpy(decompressed_data)
    newImage = Image.fromarray((result).astype(np.uint8),'RGB')
    newImage.save("output" + IdString + ".jpeg","JPEG")
