from PIL import Image
import sys
import numpy as np
import pressio
import pressio_sz as sz
import glob
import re

#python library to rival matlab functionality - numpy

# Print various statistics of the float array
def stats(float_array,width,height):
    print('max value in array',np.max(float_array))
    print('min value in array',np.min(float_array))
    print('pixels in array',np.size(float_array)/3)
    print('total RGB values in array',np.size(float_array))
    print(float_array.shape)
    print('width: ',width,' height: ',height, ' pixels: ',width*height)


# Initialize a 3D in array
def createIntArray(pix_vals,width,height):
    intArray = np.zeros((height,width,3),dtype = np.int32)
    for y in range(height):
        for x in range(width):
            intArray[y][x][0] = pix_vals[x,y][0]
            intArray[y][x][1] = pix_vals[x,y][1]
            intArray[y][x][2] = pix_vals[x,y][2]

    return intArray


# Print the RGB values in the data set
def print2DArray(array,width,height):
    for y in range(width):
        for x in range(height):
            print(array[y][x][:], end = ''),
        print('\n')

    return


# Creates a float array from an int array
def createFloatArray(intArray,width,height):
    floatArray = intArray.astype(float)
    return floatArray


###### START OF MAIN ######
Dataset = glob.glob("imgs/*") # Grab all of the images in the designated folder
Divisor = len(Dataset)
Sum = 0


for imgs in Dataset:

#open image get path from array
    im = Image.open(imgs,'r')
    OutputID = re.findall("(\d+)", imgs)

#load images
    pix_vals = im.load()
    width,height = im.size

#Create Datasets From Image For extrapolation
    intArray = []
    intArray = createIntArray(pix_vals,width,height)
    floatArray = createFloatArray(intArray,width,height)


    library = pressio.instance()
    compressor = pressio.get_compressor(library, b"sz")
    sz_options = pressio.compressor_get_options(compressor)
    metric_ids = pressio.vector_string([b'time',b'size'])
    metrics = pressio.new_metrics(library, metric_ids)

    pressio.options_set_integer(sz_options, b"sz:error_bound_mode", sz.PSNR)
    pressio.options_set_double(sz_options, b"sz:psnr_err_bound", float(sys.argv[1]))

    pressio.compressor_check_options(compressor, sz_options)
    pressio.compressor_set_options(compressor, sz_options)
    pressio.compressor_set_metrics(compressor, metrics)

    input_data = pressio.io_data_from_numpy(floatArray)

    compressed_data = pressio.data_new_empty(pressio.byte_dtype, pressio.vector_uint64_t())

    dims = pressio.vector_uint64_t([height,width,3])

    decompressed_data = pressio.data_new_empty(pressio.double_dtype, dims)

#compress data with selected compressor
    pressio.compressor_compress(compressor, input_data, compressed_data)
#decompress data with selected compressor
    pressio.compressor_decompress(compressor, compressed_data, decompressed_data)
#get metric results for compression
    metric_results = pressio.compressor_get_metrics_results(compressor)
    compression_ratio = pressio.new_double()
    pressio.options_get_double(metric_results, b"size:compression_ratio", compression_ratio)
    print("compression ratio", pressio.double_value(compression_ratio))


#Grab relevant compression metrics
    compression_ratio = pressio.new_double()
    compressed_size = pressio.new_uint32()
    uncompressed_size = pressio.new_uint32()
    decompressed_size = pressio.new_uint32()
    pressio.options_get_double(metric_results, b"size:compression_ratio", compression_ratio)
    pressio.options_get_uinteger(metric_results, b"size:compressed_size", compressed_size)
    pressio.options_get_uinteger(metric_results, b"size:uncompressed_size", uncompressed_size)
    pressio.options_get_uinteger(metric_results, b"size:decompressed_size", decompressed_size)
#
#
#     #print(OutputID,"      ","%.2f" % pressio.double_value(compression_ratio), "           ",pressio.uint32_value(compressed_size), "       ",pressio.uint32_value(uncompressed_size))
#
#
    result = pressio.io_data_to_numpy(decompressed_data)
#
#     Sum += pressio.double_value(compression_ratio)
#
#     IdString = ""
#
#     for id in OutputID:
#             IdString += id
#
    newImage = Image.fromarray((result).astype(np.uint8),'RGB')
    newImage.save("output" + "0" + ".jpeg","JPEG")
#
#
# average = Sum/Divisor
# print(average, "    ", float(sys.argv[1]))
