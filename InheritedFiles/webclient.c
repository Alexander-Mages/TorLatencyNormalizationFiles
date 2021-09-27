#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <time.h>
#include <sys/select.h>

#define PROTOCOL "tcp"
#define SERVICE "http"
#define GET "GET / HTTP/1.0\n\n"

#define BUFSIZE 512
fd_set read_set;
struct timeval tv;

int main(int argc, char *argv[]) {
  int sockid;
  int bufsize;
  char host[50];
  static char buffer[BUFSIZE];
  struct sockaddr_in socketaddr;
  struct hostent *hostaddr;
  struct servent *servaddr;
  struct protoent *protocol;

  strcpy(host, argv[1]);

  /* Resolve the host name */
  if (!(hostaddr = gethostbyname(host))) {
    fprintf(stderr, "Error resolving host.");
    exit(1);
  }

  /* clear and initialize socketaddr */
  memset(&socketaddr, 0, sizeof(socketaddr));
  socketaddr.sin_family = AF_INET;

  /* setup the servent struct using getservbyname */
  //servaddr = getservbyname(SERVICE, PROTOCOL);
  //socketaddr.sin_port = servaddr->s_port;
  socketaddr.sin_port = htons(atoi(argv[2]));

  memcpy(&socketaddr.sin_addr, hostaddr->h_addr, hostaddr->h_length);

  /* protocol must be a number when used with socket()
     since we are using tcp protocol->p_proto will be 0 */
  protocol = getprotobyname("tcp");

  sockid = socket(AF_INET, SOCK_STREAM, protocol->p_proto);
  //sockid = socket(AF_INET, SOCK_STREAM, "tcp");
  if (sockid < 0) {
    fprintf(stderr, "Error creating socket.");
    exit(1);
  }

  int true_val = 1;
  if (setsockopt(sockid, SOL_TCP, TCP_NODELAY, &true_val, sizeof(int)) == -1) {
    fprintf(stderr, "Unable to set socket options\n");
  }
	
  /* everything is setup, now we connect */
  if(connect(sockid, (struct sockaddr *) &socketaddr, sizeof(socketaddr)) == -1) {
    fprintf(stderr, "Error connecting.");
    exit(1);
  }

  FD_ZERO(&read_set);
  FD_SET(sockid, &read_set);
  tv.tv_sec = 99920;
  tv.tv_usec = 0;

  /* send our get request for http */
  /*if (send(sockid, GET, strlen(GET), 0) == -1) {
    fprintf(stderr, "Error sending data.");
    exit(1);
  }*/
  if (send(sockid, "VICTIM\0", 7, 0) == -1) {
	  fprintf(stderr, "Error sending data\n");
  }
  fprintf(stderr, "Sent header\n");

  /* read the socket until its clear then exit */

  static char buffer2[BUFSIZE];
  
  if (select(sockid + 1, &read_set, NULL, NULL, &tv) > 0) {
    fprintf(stderr, "Got something after header\n");
  while ( (bufsize = read(sockid, buffer, sizeof(buffer) - 1))) {
    //write(1, buffer, bufsize);
    fprintf(stderr, "%s\n", buffer);
    /*struct timeval currentTime;
    if (gettimeofday(&currentTime, NULL) != 0) {
      fprintf(stderr, "ERROR cannot get gettimeofday\n");
    }*/
    //(void)sprintf(buffer2,"%s   ::   CLIENT--%ld.%ld", buffer, currentTime.tv_sec, currentTime.tv_usec);
    //fprintf(stderr, "%s\n", buffer2);
    (void)write(sockid, buffer, strlen(buffer));
    //(void) write(sockid, buffer2, strlen(buffer2));
    //send(sockid, buffer, bufsize, 0);
    memset(buffer, 0, strlen(buffer));
    //memset(buffer2, 0, strlen(buffer2));
  }
  }

  close(sockid);
}
