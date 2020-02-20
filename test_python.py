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



### MAIN ###
image = "imgs/image"+str(sys.argv[1])+".jpg"
im = Image.open(image,'r')
pix_vals = im.load()
width,height = im.size

height_2 = height // 2;
dataArray = createFloatArray(0, height_2, 0, width, pix_vals)

## Configure the compressor ###
library = pressio.instance()
compressor = pressio.get_compressor(library, b"sz")
sz_options = pressio.compressor_get_options(compressor)
metric_ids = pressio.vector_string([b'time',b'size'])
metrics = pressio.new_metrics(library, metric_ids)
pressio.options_set_integer(sz_options, b"sz:error_bound_mode", sz.PSNR)
pressio.options_set_double(sz_options, b"sz:psnr_err_bound", 20)
pressio.compressor_check_options(compressor, sz_options)
pressio.compressor_set_options(compressor, sz_options)
pressio.compressor_set_metrics(compressor, metrics)


input_data = pressio.io_data_from_numpy(dataArray)
compressed_data = pressio.data_new_empty(pressio.byte_dtype, pressio.vector_uint64_t())
dims = pressio.vector_uint64_t([height_2,width,3])
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


### Compress the bottom of the image
dataArray_bottom = createFloatArray(height_2, height, 0, width, pix_vals)
input_data_bottom = pressio.io_data_from_numpy(dataArray_bottom)
compressed_data_bottom = pressio.data_new_empty(pressio.byte_dtype, pressio.vector_uint64_t())
dims_bottom = pressio.vector_uint64_t([height - height_2 ,width,3])
decompressed_data_bottom = pressio.data_new_empty(pressio.double_dtype, dims_bottom)
pressio.compressor_compress(compressor, input_data_bottom, compressed_data_bottom)
pressio.compressor_decompress(compressor, compressed_data_bottom, decompressed_data_bottom)

## Write out the image
result = pressio.io_data_to_numpy(decompressed_data)
#result_list = np.ndarray.tolist(result)
result_2 = pressio.io_data_to_numpy(decompressed_data_bottom)
final = np.vstack((result, result_2))
newImage = Image.fromarray((final).astype(np.uint8),'RGB')
newImage.save("output" + "0" + ".jpeg","JPEG")
