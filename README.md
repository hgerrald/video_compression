# video_compression
Quick summary of what each file / directory is:

- base_images: contains the uncompressed image data set
- include: a directory with all the Libpressio headers
- palmetto: contains the scripts used to submit each job on Palmetto as well as a script to turn an image data set into a video
- results: the hybrid images I created based off the segmentation and compression technique mentioned in my paper
- createData.py - Don't need this, I was trying to use the libcompress.cpp file to call Python and compress images using a mix of the two files. The horizontal_compress.py is what I used to create the 3 region compressoin
- create_result_images.sh: call this script to call the horizontal_compress.py on every image
- horizontal_compress.py: segments the image into 3 seperate regions and applies the SZ compressor in Libpressio to each one. The PSNR to compress each section by can be changed at lines 66, 70, and 74, respectively.
- lib_compress.cpp: don't need this. This was my initial attempt to use Libpressio in C++ instead of Python


To run an image set through Palmetto you must configure an Anaconda environment with Tensorflow and Jupyterhub. I have the environment I used saved on Google Drive, but the folder is to big to upload to GitHub. It is called tf_gpu and is why I activate tf_gpu in my pbs scripts.

After everything is configured, you can create a pbs script similar to some of my own and submit it using qsub. You must go and change the config.json file to run the correct image set before submitting this job.

The conda environment should be saved in /home/[username]/.conda/envs/
