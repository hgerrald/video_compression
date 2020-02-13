#!/usr/bin/env python3

import sys
#kind of ugly hack to load the path to the library without installing it
#the path gets passed from the CMakeLists.txt file
pressio_path = sys.argv[1]
sys.path.insert(0, pressio_path)

import numpy as np
np.random.seed(0)

import pressio
import pressio_sz as sz

# gets a reference to a new instance of libpressio; initializes the library if necessary
# returns a pointer to a library instance
library = pressio.instance()

# param[in] library the pointer to the library
# param[in] compressor_id the compressor to use
# returns non-owning pointer to the requested instantiated pressio compressor; it may return the same pointer on multiple calls
compressor = pressio.get_compressor(library, b"sz")

# returns a pressio options struct that represents the current options of the compressor
# param[in] compressor which compressor to get options for
sz_options = pressio.compressor_get_options(compressor)

# puts the string in param[] into the result
metrics_ids = pressio.vector_string([b'time',b'size'])

# creates a possibly composite metrics structure
# param[in] library the pointer to the library
# param[in] metrics a list of c-strings containing the list of metrics requested
# param[in] num_metrics the number of metrics requested
# returns a new pressio_metrics structure
metrics = pressio.new_metrics(library, metrics_ids)

pressio.options_set_integer(sz_options, b"sz:error_bound_mode", sz.ABS);

# void pressio_options_set_double (struct \fBpressio_options\fP * options, const char * key, double value)"
# Sets an particular key in an options structure with the given key to a value
# \fIoptions\fP the options structure to modify
# \fIkey\fP the key to change
# \fIvalue\fP the value to change to 
pressio.options_set_double(sz_options, b"sz:abs_err_bound", 0.5);

# Validates that only defined options have been set.  This can be useful for programmer errors.
# This function should NOT be used with any option structure which contains options for multiple compressors.
# Other checks MAY be preformed implementing compressors.
# param[in] compressor which compressor to validate the options struct against
# param[in] options which options set to check against.  It should ONLY contain options returned by pressio_compressor_get_options
# returns 0 if successful, 1 if there is an error.  On error, an error message is set in pressio_compressor_error_msg.
# see pressio_compressor_error_msg to get the error message
pressio.compressor_check_options(compressor, sz_options)

# sets the options for the pressio_compressor.  Compressors MAY choose to ignore
# some subset of options passed in if there valid but conflicting settings
# (i.e. two settings that adjust the same underlying configuration).
# Compressors SHOULD return an error value if configuration
# failed due to a missing required setting or an invalid one. Users MAY
# call pressio_compressor_error_msg() to get more information about the warnings or errors
# Compressors MUST ignore any and all options set that they do not support.
# param[in] compressor which compressor to get options for
# param[in] options the options to set
# returns 0 if successful, positive values on errors, negative values on warnings
# see pressio_compressor_error_msg
pressio.compressor_set_options(compressor, sz_options)

# param[in] compressor the compressor to set metrics plugin for
# param[in] the configured libpressio_metrics plugin to use
pressio.compressor_set_metrics(compressor, metrics)

# creates an array of specified shape and fills it with random values.
# d0, d1, ..., dn : [int, optional] Dimension of the returned array we require,
# If no argument is given a single Python float is returned.
data = np.random.rand(300, 300, 300)

# Convers 'data' to data that can be read by libpressio
input_data = pressio.io_data_from_numpy(data)

compressed_data = pressio.data_new_empty(pressio.byte_dtype, pressio.vector_uint64_t())

dims = pressio.vector_uint64_t([300,300,300])
decompressed_data = pressio.data_new_empty(pressio.double_dtype, dims)

pressio.compressor_compress(compressor, input_data, compressed_data)

pressio.compressor_decompress(compressor, compressed_data, decompressed_data)

metric_results = pressio.compressor_get_metrics_results(compressor)
compression_ratio = pressio.new_double()
pressio.options_get_double(metric_results, b"size:compression_ratio", compression_ratio)
print("compression ratio", pressio.double_value(compression_ratio))

result = pressio.io_data_to_numpy(decompressed_data)
