#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <sys/time.h>
#include <time.h>
#include <string.h>
#include <unistd.h>

#define LOCATIONBUFSIZE 32
#define WRITEBUFSIZE 512
#define READBUFSIZE 2048
#define NULLREDIRECT "index.html"
#define HOSTNAME "localhost"


FILE* file;
unsigned int port;

//a = b - c
int timeval_subtract(struct timeval *a, struct timeval *b, struct timeval *c)
{
	int comparison;

	if (b->tv_sec < c->tv_sec || (b->tv_sec == c->tv_sec && b->tv_usec < c->tv_usec))
	{
		fprintf(stderr, "wrong order of arguments for timeval_subtract\n");
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

int redirector(int fd) {
	char buffer[WRITEBUFSIZE];
	char oldTimestampStr[LOCATIONBUFSIZE];
	char locationPrefix[] = "index";
	char locationSuffix[] = ".html";
	char newLocation[LOCATIONBUFSIZE];
	struct timeval currentTime, oldTime, diffTime;
	size_t length;
	unsigned char* pos;

	if (gettimeofday(&currentTime, NULL) != 0) {
		fprintf(stderr, "ERROR: cannot gettimeofday\n");
	}

	//read to see if we got an old timestamp
	if ( (length = read(fd, buffer, sizeof(buffer) - 1)) > 0 ) {
		//fprintf(stderr, "bufsize is %d\n", length);
		//fprintf(file, "%s\n", buffer);
		//fprintf(stderr, "Written to file\n");
		//fflush(file);
		//fprintf(stderr, "Flushed file\n");
	} else {
		fprintf(stderr, "read returns %d\n", length);
		return 2;
	}

	/*fprintf(stderr, "buffer:\n%s\n", buffer);
	pos = strpbrk(buffer, "\n");
	if (pos > 0) {
		*pos = '\0'; //terminate at line break
	} else {
		fprintf(stderr, "CHILD: no line breaks in buffer. huh?\n");
		exit(2);
	}*/
	pos = strstr(buffer, locationSuffix);
	if (pos > 0) {
		*pos = '\0'; //terminate at line break
		//fprintf(stderr, "new buffer:\n%s\n", buffer);
		char substring[] = "GET /index"; // "GET /" + locationPrefix; 
		pos = strstr(buffer, substring);
		//assume it is found...
		sprintf(oldTimestampStr, pos+strlen(substring), sizeof(oldTimestampStr));
		pos = strchr(oldTimestampStr, '-');
		if (pos > 0)
		{
			*pos = '\0';
			//fprintf(stderr, "old timestamp: %s\n", oldTimestampStr);
			oldTime.tv_sec = atoi(oldTimestampStr);
			oldTime.tv_usec = atoi(pos+1); //BAD THING!
			//fprintf(stderr, "Old time: %d.%d\n", oldTime.tv_sec, oldTime.tv_usec);
			timeval_subtract(&diffTime, &currentTime, &oldTime);
			fprintf(file, "%d.%d,%d.%d,%d.%d\n", oldTime.tv_sec, oldTime.tv_usec, currentTime.tv_sec, currentTime.tv_usec, diffTime.tv_sec, diffTime.tv_usec);
		}
		else {
			fprintf(stderr, "CHILD: no periods in buffer. Initial request?\n");
			fprintf(file, "start @ %d.%d\n", currentTime.tv_sec, currentTime.tv_usec);
		}
	} else {
		fprintf(stderr, "CHILD: no periods in buffer. Initial request?\n");
		fprintf(file, "start @ %d.%d\n", currentTime.tv_sec, currentTime.tv_usec);
	}
	fflush(file);

	//compose new redirect with current time
	sprintf(newLocation, "%s%d-%d%s", locationPrefix, currentTime.tv_sec, currentTime.tv_usec, locationSuffix);

	//fprintf(stderr, "Started!\n");
	//fprintf(stderr, "Ready to roll\n");
	//fprintf(stderr, "Location is %s\n", location);
	/* sprintf(buffer,"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
		write(fd,buffer,strlen(buffer));
		sprintf(buffer,"<html>boooooo!</html>\r\n\r\n");
		write(fd,buffer,strlen(buffer));*/
	//sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\n\r\n", (location == NULL)? NULLREDIRECT : location);
	sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\n\r\n", newLocation);
	write(fd,buffer,strlen(buffer));
	//fprintf(stderr, "%s\n", buffer);
	//fprintf(stderr, buffer);
	sprintf(buffer,"<html>boooooo!</html>\r\n\r\n");
	write(fd,buffer,strlen(buffer));
	//fprintf(stderr, buffer);
	fflush((FILE*)fd);
#ifdef LINUX
	sleep(1);       /* to allow socket to drain */
#endif
	//fprintf(stderr, "Finished!\n");
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
	struct timeval currentTime; //for filename
	char filename[32] = {0};

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

	fprintf(file, "----------------------------------\nStarted listening on port %d\nOld Timestamp (received),New Timestamp (current)\n", port);
	fflush(file);

	fprintf(stderr, "Ready\n");

	//FIXME: does not work for more than one client
	served = 0;
	while (1) {
		length = sizeof(cli_addr);

		if((socketfd = accept(listenfd, (struct sockaddr *) &cli_addr, &length)) < 0) {
			fprintf(stderr, "Unable to accept new connections\n");
			return 1;
		}





		if((pid = fork()) < 0) {
			fprintf(stderr, "Fork failed\n");
			return 2;
		} else {
			if(pid == 0) {  /* child */
				close(listenfd);
				redirector(socketfd);
				//redirector(socketfd, NULL);
				close(socketfd);
				return 0;
			} else {        /* parent */
				close(socketfd);
				//waitpid(pid);
				//close(listenfd);
				//exit(0);
			}
		}
		served++;

        	//This reminds me why I haven't learned C yet
	      	//struct sockaddr_in* pV4Addr = (struct sockaddr_in*)&cli_addr;
                //struct in_addr ipAddr = pV4Addr->sin_addr;
                //char str[INET_ADDRSTRLEN];
                //inet_ntop( AF_INET, &ipAddr, str, INET_ADDRSTRLEN );
		fprintf(stderr, "Served %d victim connections - ", served);
		//I tried
		printf("%s\n", inet_ntoa(cli_addr.sin_addr)); 
	}
}
