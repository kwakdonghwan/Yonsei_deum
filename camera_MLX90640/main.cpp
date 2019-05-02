#define _GLIBCXX_USE_CXX11_ABI 0

#include <dirent.h>
#include <sys/types.h>

#include "math.h"
#include "defines.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <signal.h>
#include <bcm2835.h>
#include <errno.h>
#include <string.h>
#include <sys/wait.h>
#include <fstream>
#include <iterator>
#include <vector>
#include <sstream>
#include <iostream>
#include <time.h>
#include <cstdlib>
#include <ctype.h>


// socket
#include <cstdio>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#define SIZE 768


int sockfd, newsockfd, portno, n;
short buffer[SIZE];
struct sockaddr_in serv_addr, cli_addr;
socklen_t clilen;
bool socket_flag = true;

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void init_socket(int port) {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if(sockfd < 0) {
        error("Error opening Socket.");
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));
    portno = port;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno); // host to network shot?

    if(bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0)
        error("Binding Failed");

}

void listen_to_socket() {
    listen(sockfd, 5);
    printf("Listening...\n");
    clilen = sizeof(cli_addr);

    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
    socket_flag = true;

    if(newsockfd < 0)
        error("Error on Accept");
}


extern void Prepaire_coeff();
extern void Reset_New_Data_In_Ram2();
extern void GET_A_KEY();
extern void Get_Image_Median(int);
extern void Get_cyclops_val_init();
extern void Get_Image_Median_Chess(int de_inter);

extern char     SENSOR_ID[];
extern short    IMA[NROWS][NCOLS];
//double          NORMALIZED[NROWS][NCOLS];
extern int      i,j,k;
extern unsigned char       ir_data[NROWS*NCOLS*2+2];   // toke a few bytes more to be sure!

// for file parameter read

char            refesh_rate = '0';


char            mlxFifo[] = "/var/run/mlx90640.sock";

// int             num, fd, sleepinsec;

int num,fd;
double sleepinsec;

pid_t           pid;


// *************
// * FUNCTIONS *
// *************

// ----------------------------------------------------------------------------
/**
 * Represents a single Pixel in the image. A Pixel has red, green, and blue
 * components that are mixed to form a color. Each of these values can range
 * from 0 to 255
**/
typedef double array2d[NROWS][NCOLS];

array2d* NormaliseValue()  //this funtion for percentage mode
{
  double returnValues[NROWS][NCOLS];

  for (i=0; i<NROWS; i++) {
      for (j=0; j<NCOLS; j++) {
        returnValues[i][j] = (double)(IMA[i][j] - MINTEMP) / (double)(MAXTEMP - MINTEMP);
      }
  }

  return &returnValues;
}


tm operator+ ( tm uct, int span_in_minutes )
{
    uct.tm_min += span_in_minutes ;
    const auto t = mktime(std::addressof(uct) ) ;

    return *localtime(std::addressof(t) ) ;
}

tm operator+ ( int span_in_minutes, tm uct ) { return uct + span_in_minutes ; }
tm operator- ( tm uct, int span_in_minutes ) {  return uct + -span_in_minutes ; }





void display_Ima()
{

  int    fd, sleeper;


  NORMALIZED = NormaliseValue();

    int buffer_index = 0;
    for (i=0; i<NROWS; i++) {
        //pc.printf("D%2d:",i);
        for (j=0; j<NCOLS; j++) {

            buffer[buffer_index++] = IMA[i][j];

    }

  n = write(newsockfd, buffer, SIZE*2);
  if(n < 0) socket_flag = false;




  printf("\n\r");
  sleeper = 1000000*sleepinsec;
  if(sleeper > 1500000)
    sleeper-=1500000;
  usleep(sleeper);

} // end display_Ima


// ++++++++++++++++++++++++
// main  application loop
// ++++++++++++++++++++++++


void find_objects()
{


    // get cyclops values to start for averaging them
    Get_cyclops_val_init();

    Reset_New_Data_In_Ram2();

#ifdef CHESS_PAT
    // get the thermal image without de-interlace techniques
    Get_Image_Median_Chess(0);
    printf("chess P\n\r");
#else
    Get_Image_Median(1);       // collect an full image using the odd and even frames wait for both odd and even image
    printf("None chess P\n\r");
#endif

    (void) display_Ima();

    printf("REady to start\n\r");//GET_A_KEY();

    Reset_New_Data_In_Ram2();

    while (1){

#ifdef CHESS_PAT
                Get_Image_Median_Chess(1);
#else
                Get_Image_Median(0);
#endif
               if(!socket_flag) break;
               (void) display_Ima();  //send socket file is in hear

                //GET_A_KEY();
    } // end while

}  // end find objects


// *****************
// * END FUNCTIONS *
// *****************

// ================
// = main routine =
// ================
const char *defaults[] = { "5"};
int main(int argc =3, const char* argv[] =defaults)
{
    int port;
    if (argc < 3)
    {
        std::cerr << "Usage: " << argv[0] << " Sleep in secounds," <<  argv[1] << "Port number" <<std::endl;
        return 1;
    }
    else
    {
      std::istringstream ss(argv[1]);

      if (!(ss >> sleepinsec)){
          std::cerr << "Invalid number " << argv[1] << '\n';
          std::cerr << "Usage: " << argv[0] << " Sleep in secounds <-THIS MEANS NUMBERS ONLY !" << std::endl;
          return 1;
        }

    }

    /////////////////////////////////////////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/////////////////////
    // sleepinsec to double
    sleepinsec = atoi(argv[1]);
    ////////////////////////////////////////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/////////////////////////


    int x,y;
    if (!bcm2835_init())
    {
      printf("ERROR: CANNOT INIT bcm2835 \n\r");
      return 0;
    }
    bcm2835_i2c_begin();

    bcm2835_i2c_set_baudrate(400000);

    Prepaire_coeff();  // get and prepare all eeprom calibration coeff's
    printf("Note: due to the slow To screen print of each pixel\n\r");
    printf("Image sync is lost, fix speed in your application!\n\r");


    port = atoi(argv[2]);
    //printf("enter port: ");
    //scanf("%d", &port);
    init_socket(port);


    while(1) {

        listen_to_socket();
        find_objects();
        close(newsockfd);
    }
    bcm2835_i2c_end();

}
