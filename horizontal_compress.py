from PIL import Image
import glob
import sys
import numpy as np
import pressio
import pressio_sz as sz

def createFloatArray(height_start, height_end, width_start, width_end, pix_vals):
    numRows = height_end - height_start
    numCols = width_end - width_start
    intArray = np.zeros((numRows, numCols, 3),dtype = np.int32)
    for y in range(numRows):
        for x in range(numCols):
            intArray[y][x][0] = pix_vals[x+width_start,y+height_start][0]
            intArray[y][x][1] = pix_vals[x+width_start,y+height_start][1]
            intArray[y][x][2] = pix_vals[x+width_start,y+height_start][2]

    floatArray = intArray.astype(float)
    return floatArray


def performCompression(compress_rate, dataArray, height_start, height_end, width_start, width_end):
    height = height_end-height_start
    width = width_end - width_start

    library = pressio.instance()
    compressor = pressio.get_compressor(library, b"sz")
    sz_options = pressio.compressor_get_options(compressor)
    metric_ids = pressio.vector_string([b'time',b'size'])
    metrics = pressio.new_metrics(library, metric_ids)
    pressio.options_set_integer(sz_options, b"sz:error_bound_mode", sz.PSNR)
    pressio.options_set_double(sz_options, b"sz:psnr_err_bound", compress_rate)
    pressio.compressor_check_options(compressor, sz_options)
    pressio.compressor_set_options(compressor, sz_options)
    pressio.compressor_set_metrics(compressor, metrics)

    input_data = pressio.io_data_from_numpy(dataArray)
    compressed_data = pressio.data_new_empty(pressio.byte_dtype, pressio.vector_uint64_t())
    dims = pressio.vector_uint64_t([height,width,3])
    decompressed_data = pressio.data_new_empty(pressio.double_dtype, dims)

    #compress/decompress data with selected compressor
    pressio.compressor_compress(compressor, input_data, compressed_data)
    pressio.compressor_decompress(compressor, compressed_data, decompressed_data)

    #get metric results for compression
    metric_results = pressio.compressor_get_metrics_results(compressor)
    compression_ratio = pressio.new_double()
    pressio.options_get_double(metric_results, b"size:compression_ratio", compression_ratio)
    print("compression ratio", pressio.double_value(compression_ratio))

    return decompressed_data



### MAIN ###
image = "base_images/image"+str(sys.argv[1])+".jpg"
im = Image.open(image,'r')
pix_vals = im.load()
width,height = im.size
height_2 = height // 5
height_3 = height_2 * 2

# Compress the top of the image
dArray_top = createFloatArray(0, height_2, 0, width, pix_vals)
dc1 = performCompression(3, dArray_top, 0, height_2, 0, width)

# Compress the second layer
dArray_middle = createFloatArray(height_2, height_3 ,0, width, pix_vals)
dc2 = performCompression(30, dArray_middle, height_2, height_3, 0, width)

# Compress the bottom of the image
dArray_bottom = createFloatArray(height_3, height, 0, width, pix_vals)
dc3 = performCompression(50, dArray_bottom, height_3, height, 0, width)


## Write out the image
result = pressio.io_data_to_numpy(dc1)
result_mid = pressio.io_data_to_numpy(dc2)
result_2 = pressio.io_data_to_numpy(dc3)
final = np.vstack((result, result_mid, result_2))
newImage = Image.fromarray((final).astype(np.uint8),'RGB')
newImage.save("results/image" + str(sys.argv[1]) + ".jpg","JPEG")
