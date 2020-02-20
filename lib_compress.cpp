#include <Python.h>
#include <stdio.h>
#include <sz.h>
#include <libpressio.h>
#include <posix.h>
#include <dirent.h>
#include <stdlib.h>
#include <unistd.h>
#include <jpeglib.h>

int find_num_imgs(DIR* dirp, struct dirent *entry);
void SetupPython();

int loadJpg(const char* Name)
{
  unsigned char a, r, g, b;
  int width, height;
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;

  FILE * infile;        /* source file */
  JSAMPARRAY pJpegBuffer;       /* Output row buffer */
  int row_stride;       /* physical row width in output buffer */
  if ((infile = fopen(Name, "rb")) == NULL) {
    fprintf(stderr, "can't open %s\n", Name);
    return 0;
  }
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_decompress(&cinfo);
  jpeg_stdio_src(&cinfo, infile);
  (void) jpeg_read_header(&cinfo, TRUE);
  (void) jpeg_start_decompress(&cinfo);
  width = cinfo.output_width;
  height = cinfo.output_height;

  unsigned char * pDummy = new unsigned char [width*height*4];
  unsigned char * pTest = pDummy;
  if (!pDummy) {
    printf("NO MEM FOR JPEG CONVERT!\n");
    return 0;
  }
  row_stride = width * cinfo.output_components;
  pJpegBuffer = (*cinfo.mem->alloc_sarray)
    ((j_common_ptr) &cinfo, JPOOL_IMAGE, row_stride, 1);

  while (cinfo.output_scanline < cinfo.output_height) {
    (void) jpeg_read_scanlines(&cinfo, pJpegBuffer, 1);
    for (int x = 0; x < width; x++) {
      a = 0; // alpha value is not supported on jpg
      r = pJpegBuffer[0][cinfo.output_components * x];
      if (cinfo.output_components > 2) {
        g = pJpegBuffer[0][cinfo.output_components * x + 1];
        b = pJpegBuffer[0][cinfo.output_components * x + 2];
      } else {
        g = r;
        b = r;
      }
      *(pDummy++) = b;
      *(pDummy++) = g;
      *(pDummy++) = r;
      *(pDummy++) = a;
    }
  }
  fclose(infile);
  (void) jpeg_finish_decompress(&cinfo);
  jpeg_destroy_decompress(&cinfo);

  // BMap = (int*)pTest;
  // Height = height;
  // Width = width;
  // Depth = 32;

  FILE* outfile = fopen("out.jpg", "wb");
  //fwrite(cinfo, sizeof(struct jpeg_decompress_struct), 1, outfile);
}

/******************************************************************************
 * Sets up and calls the Python function to print the pixel data to a file so
 * we can read the data into C
 */
void grap_pixels_python()
{
  // Call Python function to convert to float array
    char *image_to_call = (char*)calloc(100, sizeof(char));
    strcpy(image_to_call, "0");
    PyObject* myModuleString = PyString_FromString((char*)"createData");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"createFloatArray");
    PyObject* args = PyTuple_Pack(1,PyString_FromString(image_to_call));
    PyObject* myResult = PyObject_CallObject(myFunction, args);
    double result = PyFloat_AsDouble(myResult);
   // printf("%lf\n", result);
}


/******************************************************************************
 * Find the width and height, extract start of frame marker(FFCO) of width and
 * height and get the position
 */
void find_height_width(int file_length, unsigned char *img_data, size_t *iHeight,
   size_t *iWidth)
{
    int i, j, xyPos;

    for (i = 0; i < file_length; i++)
    {
        if((img_data[i]==0xFF) && (img_data[i+1]==0xC0) )
        {
            xyPos=i;
            break;
        }
    }

   xyPos += 5;
   *iHeight = img_data[xyPos]<<8|img_data[xyPos+1];
   *iWidth = img_data[xyPos+2]<<8|img_data[xyPos+3];
}


/******************************************************************************
 * MAIN
 */
int main(void)
{
  FILE* fpt, *out, *data;
  DIR *dirp;
  struct dirent *entry;
  char *img_name = (char*)malloc(100 * sizeof(char));
  unsigned char *img_data;
  int file_length, i, x, y;
  size_t iHeight, iWidth;
  double compression_ratio = 0;
  double ***data_array;

  SetupPython();

  find_num_imgs(dirp, entry);
  sprintf(img_name, "imgs/image%d.jpg", 0);
  fpt = fopen(img_name, "rb");
  if(!fpt)
  {
    printf("Error: could not open %s\n", img_name);
    exit(0);
  }

  // Get the file length
  fseek(fpt, 0, SEEK_END);
  file_length = ftell(fpt);
  fseek(fpt, 0, SEEK_SET);

 // Read the image data
  img_data = (unsigned char*)calloc(file_length+1, sizeof(unsigned char));
  read(fileno(fpt), img_data, file_length+1);
  fclose(fpt);

  find_height_width(file_length, img_data, &iHeight, &iWidth);

  // Call the Python function to write the image data to a file
  grap_pixels_python();

  // Read the results from the file into a 3D array
  data = fopen("image_data.txt", "rb");
  data_array = (double***)calloc(iHeight, sizeof(double**));
  for (y = 0; y < iHeight; y++)
  {
    data_array[y] = (double**)calloc(iWidth, sizeof(double*));
    for (x = 0; x < iWidth; x++)
    {
      data_array[y][x] = (double*)calloc(3, sizeof(double*));
      fscanf(data, "%lf", &data_array[y][x][0]);
      fscanf(data, "%lf", &data_array[y][x][1]);
      fscanf(data, "%lf", &data_array[y][x][2]);
    }
  }
  fclose(data);


// Apply libpressio
  struct pressio* library = pressio_instance();
  struct pressio_compressor* compressor = pressio_get_compressor(library, "sz");

// Configure metrics
  const char* metrics[] = { "size" };
  struct pressio_metrics* metrics_plugin = pressio_new_metrics(library, metrics, 1);
  pressio_compressor_set_metrics(compressor, metrics_plugin);

// Configure the compressor
  struct pressio_options* sz_options = pressio_compressor_get_options(compressor);
  pressio_options_set_integer(sz_options, "sz:error_bound_mode", ABS);
  pressio_options_set_double(sz_options, "sz:abs_err_bound", 0.5);
  if (pressio_compressor_check_options(compressor, sz_options))
  {
    printf("%s\n", pressio_compressor_error_msg(compressor));
    exit(pressio_compressor_error_code(compressor));
  }
  if (pressio_compressor_set_options(compressor, sz_options))
  {
     printf("%s\n", pressio_compressor_error_msg(compressor));
     exit(pressio_compressor_error_code(compressor));
   }


  size_t dims[] = {iHeight, iWidth, 3};
  struct pressio_data* input_data = pressio_data_new_move(pressio_double_dtype, data_array, 3, dims, pressio_data_libc_free_fn, NULL);
  struct pressio_data* compressed_data = pressio_data_new_empty(pressio_byte_dtype, 0, NULL);
  struct pressio_data* decompressed_data = pressio_data_new_empty(pressio_double_dtype, 3, dims);

// Compress the data
  if (pressio_compressor_compress(compressor, input_data, compressed_data))
  {
    printf("%s\n", pressio_compressor_error_msg(compressor));
    exit(pressio_compressor_error_code(compressor));
  }

  // Decompress the data
   if (pressio_compressor_decompress(compressor, compressed_data, decompressed_data))
   {
     printf("%s\n", pressio_compressor_error_msg(compressor));
     exit(pressio_compressor_error_code(compressor));
   }

  // Get the compression ratio
  struct pressio_options* metric_results = pressio_compressor_get_metrics_results(compressor);
  if (pressio_options_get_double(metric_results, "size:compression_ratio", &compression_ratio))
  {
   printf("failed to get compression ratio\n");
   exit(1);
  }
 printf("compression ratio: %lf\n", compression_ratio);

 // Write the image data
  sprintf(img_name, "results/image%d.jpg", 0);
  out = fopen(img_name, "wb");
  data = fopen("image_data.txt", "wb");
  for (y = 0; y < iHeight; y++)
  {
    for (x = 0; x < iWidth; x++)
    {
      fprintf(data, "%lf\n", data_array[y][x][0]);
      fprintf(data, "%lf\n", data_array[y][x][1]);
      fprintf(data, "%lf\n", data_array[y][x][2]);
    }
  }
  fclose(data);

// //  call_python_write_image();
   pressio_io_data_path_write(input_data, "results/result0.jpg");



  fclose(out);


  return 0;
}


/******************************************************************************
 * Find the number of images in the img directory
 */
int find_num_imgs(DIR* dirp, struct dirent *entry)
{
   int file_count = 0;

   dirp = opendir("./imgs");
   while (entry = readdir(dirp))
   {
     if (entry->d_type == DT_REG)
       file_count++;
   }
   closedir(dirp);
   return file_count;
}


/******************************************************************************
 * Sets up compatibility with Python functions
 */
void SetupPython(){

  Py_Initialize();
  PyEval_InitThreads();
  PyEval_ReleaseLock();
  PyObject *sysmodule = PyImport_ImportModule("sys");
  PyObject *syspath = PyObject_GetAttrString(sysmodule, "path");
  PyList_Append(syspath, PyString_FromString("."));
  Py_DECREF(syspath);
  Py_DECREF(sysmodule);

}
