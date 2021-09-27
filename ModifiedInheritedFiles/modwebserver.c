#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/time.h>
#include <time.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/select.h>

#define BUFSIZE 327

//TODO this is really simple - read timestamp, print it out, and send another one - need to probably parallelize this. Not sure how though - thread, or fork a new process? How about writing to a file?

static FILE **file = NULL;
fd_set read_set;
struct timeval tv;
	
void setLogFile(FILE **f) {
	file = f;
}

void web2(int fd, int sleepTime, int totalCount) {
	FD_ZERO(&read_set);
	FD_SET(fd, &read_set);
	tv.tv_sec = 99920;
	tv.tv_usec = 0;
	fprintf(stderr, "Started!\n");
	static char buffer2[BUFSIZE+1];
	int count = 0;
	int bufsize;
	
	if ( (bufsize = read(fd, buffer2, sizeof(buffer2) - 1)) > 0 ) {
		fprintf(stderr, "bufsize is %d\n", bufsize);
		static FILE *f;
		if (buffer2[0] == 'A') {
			f = fopen("ATTACK", "w+");
		} else if (buffer2[0] == 'V') {
			fprintf(stderr, "First letter is a V\n");
			f = fopen("VICTIM", "w+");
			fprintf(stderr, "opened Victim file\n");
		} else {
			fprintf(stderr, "wrong buffer type?\n");
			fprintf(stderr, "%s\n", buffer2);
		}
		setLogFile(&f);
		fprintf(stderr, "File opened\n");
		fprintf(*file, "%s\n", buffer2);
		fprintf(stderr, "Written to file\n");
		fflush(*file);
		fprintf(stderr, "Flushed file\n");
	} else {
		fprintf(stderr, "read returns 0\n");
	}
	//memset(buffer2, 0, strlen(buffer2));
	
	fprintf(stderr, "Ready to roll\n");
	while (count < totalCount) {
		fprintf(stderr, "Count is %d\n", count);
	    static char buffer[BUFSIZE+1]; /* static so zero filled */
        int j, file_fd, buflen, len;
	    long i, ret;
        char * fstr;
	    buffer[0]=0;

        	//(void)sprintf(buffer,"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n");
	        //(void)write(fd,buffer,strlen(buffer));
		
		//time_t currentTime = time(NULL);
		struct timeval currentTime;
	        if (gettimeofday(&currentTime, NULL) != 0) {
			fprintf(stderr, "ERROR cannot get gettimeofday\n");
		}
		//int currentTimeMicro = currentTime.tv_usec;
		(void)sprintf(buffer,"                                                                  ::%ld.%ld", currentTime.tv_sec, currentTime.tv_usec);
		//(void)fprintf(*file,"%ld.%ld::%ld.%ld\n", currentTime.tv_sec, currentTime.tv_usec, currentTime.tv_sec, currentTime.tv_usec);
		//fflush(*file);
		fprintf(stderr, "%s\n", buffer);
		//TODO get first request from client and print
		//TODO get subsequent replies from client and print
		//fprintf(stdout, "%s\n", buffer2);
		//fprintf(stderr, "Wrote currentTime %d\n", currentTimeMicro);
		(void) write(fd, buffer, strlen(buffer));

		memset(buffer2, 0, strlen(buffer2));
		
		if (select(fd + 1, &read_set, NULL, NULL, &tv) > 0) {
			if ( (bufsize = read(fd, buffer2, sizeof(buffer2) - 1)) > 0) {
			if (gettimeofday(&currentTime, NULL) != 0) {
			fprintf(stderr, "ERROR cannot get gettimeofday\n");
		}
				fprintf(*file, "%ld.%ld::%s\n", currentTime.tv_sec, currentTime.tv_usec, buffer2);
				fflush(*file);
			}
		}
		/*if (sleepTime > 10) {
			usleep(sleepTime);
		} else {
			sleep(sleepTime);
		}*/
		count++;
		//fprintf(stderr, "%d\n", count);
		memset(buffer, 0, strlen(buffer));
	}
	fprintf(stderr, "END!\n");
	fclose(*file);
#ifdef LINUX
        sleep(1);       /* to allow socket to drain */
#endif
	(void)close(fd); 
        exit(1);
}

main(int argc, char **argv) {
	int true_val = 1; //for setting socket options
	int send_size = 1024; //for setting send buffer size
	int real_send_size = 0;
	int send_timeout = 10; //for setting the socket send timeout
        int i, port, pid, listenfd, socketfd;
        size_t length;
        char *str;
        static struct sockaddr_in cli_addr;
        static struct sockaddr_in serv_addr;

        if( argc < 4  || argc > 4 || !strcmp(argv[1], "-?") ) {
                (void)printf("usage failed: ./server <port> <sleep time in microsec/sec> <number of timestamps>\n\n");
                exit(0);
        }

        (void)signal(SIGCLD, SIG_IGN); /* ignore child death */
        (void)signal(SIGHUP, SIG_IGN); /* ignore terminal hangups */

        /* setup the network socket */
        if((listenfd = socket(AF_INET, SOCK_STREAM,0)) <0)
		fprintf(stderr, "Unable to listen on socket\n");

	if (setsockopt(listenfd, SOL_TCP, TCP_NODELAY, &true_val, sizeof(int)) == -1) {
		fprintf(stderr, "Unable to set socket options\n");
	}

	/*int err;
	if ( (err = setsockopt(listenfd, SOL_SOCKET, SO_SNDBUF, (char *)&send_size, sizeof(int) )) < 0) {
		fprintf(stderr, "Unable to set buffer size of socket\n");
	}*/
	//fprintf(stderr, "Value from setsockopt SNDBUF is %d\n", err);

	int ssize = 0;
	socklen_t size = sizeof(int);
	if (getsockopt(listenfd, SOL_SOCKET, SO_SNDBUF, (char *)&ssize, &size) < 0) {
		fprintf(stderr, "Unable to get send buffer size of socket\n");
	}
	fprintf(stderr, "Size of send buffer is: %d \n", ssize);

/*	if (setsockopt(listenfd, SOL_SOCKET, SO_SNDTIMEO, &send_timeout, sizeof(int)) == -1) {
		fprintf(stderr, "Unable to set send timeout of socket\n");
	}*/

        port = atoi(argv[1]);
	int sleep = atoi(argv[2]);
	int count = atoi(argv[3]);
	
        if(port < 0 || port >60000)
		fprintf(stderr, "Invalid port\n");

        serv_addr.sin_family = AF_INET;
        serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
        serv_addr.sin_port = htons(port);

        if(bind(listenfd, (struct sockaddr *)&serv_addr,sizeof(serv_addr)) <0)
		fprintf(stderr, "Unable to bind\n");

        if( listen(listenfd,64) <0)
		fprintf(stderr, "Failed\n");

	fprintf(stderr, "Ready\n");
	while (1) {
                length = sizeof(cli_addr);

                if((socketfd = accept(listenfd, (struct sockaddr *) &cli_addr, &length)) < 0)
			fprintf(stderr, "Unable to accept new connections\n");

                if((pid = fork()) < 0) {
			fprintf(stderr, "Fork failed\n");
                } else {
                        if(pid == 0) {  /* child */
                                (void)close(listenfd);
                                web2(socketfd, sleep, count);
				int ssize = 0;
				socklen_t size = sizeof(int);
				if (getsockopt(listenfd, SOL_SOCKET, SO_SNDBUF, (char *)&ssize, &size) < 0) {
					fprintf(stderr, "Unable to get send buffer size of socket\n");
				}
				fprintf(stderr, "Size of send buffer is: %d \n", ssize);
                        } else {        /* parent */
                                (void)close(socketfd);
                        }
                }
        }
}
