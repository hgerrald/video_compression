# video_compression
Quick summary of what each file / directory is:

- base_images: contains the uncompressed image data set
- include: a directory with all the Libpressio headers
- palmetto: contains the scripts used to submit each job on Palmetto as well as a script to turn an image data set into a video
- results: the hybrid images I created based off the segmentation and compression technique mentioned in my paper
- createData.py - Don't need this, I was trying to use the libcompress.cpp file to call Python and compress images using a mix of the two files. The horizontal_compress.py is what I used to create the 3 region compressoin
- create_result_images.sh: call this script to call the horizontal_compress.py on every image
