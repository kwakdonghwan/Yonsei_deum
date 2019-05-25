#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define port 8888
#define SIZE 768

int sockfd, newsockfd, portno;
socklen_t clilen;
short buffer[SIZE];

struct sockaddr_in serv_addr, cli_addr;
int n;



void error(const char *msg)
{
    perror(msg);
    exit(0);
}

void send_socket_data() {
    bzero(buffer,256);
    n = read(newsockfd,buffer,255);
    if (n < 0) error("ERROR reading from socket");

    for(int i=0; i < SIZE; i++) {
        buffer[i] = 300;
    }
    n = write(newsockfd, buffer, SIZE*2);
}

void init_socket_server() {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        error("ERROR opening socket");
    bzero((char *) &serv_addr, sizeof(serv_addr));
    portno = port;


    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno);
    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) error("ERROR on binding");

    listen(sockfd,5);
    clilen = sizeof(cli_addr);
    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
    if (newsockfd < 0) error("ERROR on accept");

}


int main()
{

    init_socket_server();
    while(1) {

        send_socket_data();

    }

    close(newsockfd);
    close(sockfd);

}