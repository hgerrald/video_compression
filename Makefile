lib_compress: lib_compress.cpp
	  g++ lib_compress.cpp -g -o lib_compress -I/usr/include/python2.7 -llibpressio -lpython2.7 -O0 -ggdb3 -ljpeg

run:
		./lib_compress
