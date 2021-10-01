#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <sys/time.h>
#include <time.h>
#include <string.h>

#define LOCATIONBUFSIZE 32
#define WRITEBUFSIZE 512
#define READBUFSIZE 2048
#define NULLREDIRECT "index.html"
#define HOSTNAME "localhost"
#define FILENAME "REDIRECT"
#define REPEAT 20


FILE* file;
unsigned int port;
fd_set read_set;
struct timeval tv;

//a = b - c
int timeval_subtract(struct timeval *a, struct timeval *b, struct timeval *c)
{
	if (b->tv_sec < c->tv_sec || (b->tv_sec == c->tv_sec && b->tv_usec < c->tv_usec))
	{
		fprintf(stderr, "wrong order of arguments for timeval_subtract\n");
		a->tv_sec = 0; //HACK!
		a->tv_usec = 0; //HACK!
		return -1; //wrong argument order
	}

	a->tv_sec = b->tv_sec - c->tv_sec;
	a->tv_usec = b->tv_usec - c->tv_usec;
	if (b->tv_usec < c->tv_usec)
	{
		a->tv_sec -= 1;
		a->tv_usec *= -1;
	}

	return 0;
}

//generates defunct children
int redirector(int fd, char* src) {
	char buffer[WRITEBUFSIZE];
	char oldTimestampStr[LOCATIONBUFSIZE];
	char locationPrefix[] = "index";
	char locationSuffix[] = ".html";
	char newLocation[LOCATIONBUFSIZE];
	struct timeval currentTime, oldTime, diffTime;
	size_t length;
	char* pos;
	unsigned int current;

	FD_ZERO(&read_set);
	FD_SET(fd, &read_set);
	tv.tv_sec = 99920;
	tv.tv_usec = 0;

	//fprintf(stderr, "Redirector start...\n");

	current = 0;
	while (current < REPEAT + 1) {
		//fprintf(stderr, "Servicing victim request %d\n", current);

		//read to see if we got an old timestamp
		if ((select(fd + 1, &read_set, NULL, NULL, &tv) > 0) &&
				((length = read(fd, buffer, sizeof(buffer) - 1)) > 0 )) {

			//fprintf(stderr, "Received:\n%s\n", buffer);
			/* pos = strpbrk(buffer, "\n");
			   if (pos > 0) {
			 *pos = '\0'; //terminate at line break
			 } else {
			 fprintf(stderr, "CHILD: no line breaks in buffer. huh?\n");
			 return 2;
			 }*/

			if (gettimeofday(&currentTime, NULL) != 0) {
				fprintf(stderr, "ERROR: cannot gettimeofday\n");
				currentTime.tv_sec = 0;
				currentTime.tv_usec = 0;
			}

			pos = strstr(buffer, locationSuffix);
			if (pos > 0) {
				*pos = '\0'; //terminate at line break
				//fprintf(stderr, "new buffer:\n%s\n", buffer);
				char substring[] = "/index";
				pos = strstr(buffer, substring);
				//fprintf(stderr, "%s\n", pos);
				if (pos <= 0) {
					fprintf(stderr, "something is desparately wrong!\n");
					//return -2;
					continue;
				}
				sprintf(oldTimestampStr, pos+strlen(substring),sizeof(oldTimestampStr));
				//fprintf(stderr, "Old timestamp:%s\n", oldTimestampStr);
				pos = strchr(oldTimestampStr, '-');
				if (pos > 0)
				{
					*pos = '\0';
					//fprintf(stderr, "old timestamp: %s\n", oldTimestampStr);
					oldTime.tv_sec = atoi(oldTimestampStr);
					oldTime.tv_usec = atoi(pos+1); //BAD THING!
					//fprintf(stderr, "Old time: %d.%d\n", oldTime.tv_sec, oldTime.tv_usec);
					//timeval_subtract(&diffTime, &currentTime, &oldTime);
					fprintf(file, "%s\t%ld.%06ld\t%ld.%06ld\n", src, oldTime.tv_sec, oldTime.tv_usec, currentTime.tv_sec, currentTime.tv_usec);
				} else {
					fprintf(stderr, "CHILD: no dashes in buffer. Initial request?\n");
					fprintf(file, "start @ %ld.%06ld\n\n", currentTime.tv_sec, currentTime.tv_usec);
				}
			} else {
				fprintf(stderr, "CHILD: no periods in buffer. Initial request?\n");
				fprintf(file, "start @ %ld.%06ld\n", currentTime.tv_sec, currentTime.tv_usec);
			}
			fflush(file);

			//compose new redirect with current time
			sprintf(newLocation, "%s%ld-%06ld%s", locationPrefix, currentTime.tv_sec, currentTime.tv_usec, locationSuffix);
			//sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\n\r\n<html>boooooo!</html>\r\n\r\n", newLocation);
			sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\nContent-Length: 0\r\n\r\n", newLocation);
			write(fd,buffer,strlen(buffer));

			//fflush((FILE*)fd);
			//fprintf(stderr, "Sent:%s\n\n", buffer);
			#ifdef LINUX
				sleep(1);       /* to allow socket to drain */
			#endif
			current++;
		}
	}

	//fprintf(stderr, "Child finished!\n");
	return 0;
}

main(int argc, char **argv) {
	int true_val = 1; //for setting socket options
	int send_size = 1024; //for setting send buffer size
	int real_send_size = 0;
	int send_timeout = 10; //for setting the socket send timeout
	int i, pid, listenfd, socketfd;
	size_t length;
	char *str;
	static struct sockaddr_in cli_addr;
	static struct sockaddr_in serv_addr;
	char buffer[READBUFSIZE] = {0};
	unsigned int served;
#ifndef FILENAME
	struct timeval currentTime; //for filename
	char filename[32] = {0};
#endif

	if(argc !=  2) {
		printf("usage: %s <port>\n\n", argv[0]);
		return 0;
	}

	//signal(SIGCLD, SIG_IGN); /* ignore child death */
	//signal(SIGHUP, SIG_IGN); /* ignore terminal hangups */

	/* setup the network socket */
	if((listenfd = socket(AF_INET, SOCK_STREAM,0)) <0)
	{ 
		fprintf(stderr, "Unable to listen on socket\n");
		return 1;
	}

	if (setsockopt(listenfd, SOL_TCP, TCP_NODELAY, &true_val, sizeof(int)) == -1) {
		fprintf(stderr, "Unable to set socket options\n");
		return 1;
	}

	int ssize = 0;
	socklen_t size = sizeof(int);
	if (getsockopt(listenfd, SOL_SOCKET, SO_SNDBUF, (char *)&ssize, &size) < 0)
	{
		fprintf(stderr, "Unable to get send buffer size of socket\n");
		return 1;
	}
	fprintf(stderr, "Size of send buffer is: %d \n", ssize);
	if (ssize < WRITEBUFSIZE) {
		fprintf(stderr, "WRITEBUFSIZE too large (%d versus allowed max %d)\n", WRITEBUFSIZE, ssize);
		return 1;
	}

	port = atoi(argv[1]);

	if(port < 1 || port >65536) {
		fprintf(stderr, "Invalid port\n");
		return 1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	serv_addr.sin_port = htons(port);

	if(bind(listenfd, (struct sockaddr *)&serv_addr,sizeof(serv_addr)) <0) {
		fprintf(stderr, "Unable to bind\n");
		return 1;
	}

	if( listen(listenfd,64) <0) {
		fprintf(stderr, "Failed to listen\n");
		return 1;
	}

#ifndef FILENAME
	if (gettimeofday(&currentTime, NULL) != 0) {
		fprintf(stderr, "ERROR (fatal): cannot gettimeofday\n");
		return 3;
	}

	//compose file name with current time
	sprintf(filename, "%d-%d.log", currentTime.tv_sec, currentTime.tv_usec);

	if ((file = fopen(filename, "a")) > 0) {
		fprintf(stderr, "File %s opened\n", filename);
	}
	else {
		fprintf(stderr, "fopen(%s, \"a\") failed: %d\n", filename, file);
		return 3;
	}
#else
	if ((file = fopen(FILENAME, "a")) > 0) {
		fprintf(stderr, "File %s opened\n", FILENAME);
	}
	else {
		fprintf(stderr, "fopen(%s, \"a\") failed: %d\n", FILENAME, file);
		return 3;
	}
#endif

	//fprintf(file, "----------------------------------\nStarted listening on port %d\nOld Timestamp (received),\tNew Timestamp (current)\n", port);
	//fflush(file);

	fprintf(stderr, "Ready\n");

	//FIXME: does not work for more than one client
	served = 0;
	while (1) {
		length = sizeof(cli_addr);

		if((socketfd = accept(listenfd, (struct sockaddr *) &cli_addr, &length)) < 0) {
			fprintf(stderr, "Unable to accept new connections\n");
			return 1;
		}

		served++;
		fprintf(stderr, "Serving victim connection %d\n", served);
		if((pid = fork()) < 0) {
			fprintf(stderr, "Fork failed\n");
			return 2;
		} else {
			if(pid == 0) {  /* child */
				close(listenfd);
				redirector(socketfd, (char*) inet_ntoa(cli_addr.sin_addr));
				close(socketfd);
				exit(0);
			} else {        /* parent */
				close(socketfd);
				//waitpid(pid);
				//close(listenfd);
				continue;
			}
		}
	}
}
