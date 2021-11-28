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

#define BUFSIZE 512

//TODO this is really simple - read timestamp, print it out, and send another one - need to probably parallelize this. Not sure how though - thread, or fork a new process? How about writing to a file?

static FILE **file = NULL;
fd_set read_set;
struct timeval tv;
	
void setLogFile(FILE **f) {
	file = f;
}

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

int web2(int fd, int sleepTime, int totalCount, char* src) {
	FD_ZERO(&read_set);
	FD_SET(fd, &read_set);
	tv.tv_sec = 99920;
	tv.tv_usec = 0;
	fprintf(stderr, "Started!\n");
	static char buffer2[BUFSIZE+1];
	int count = 0;
	int bufsize;
	struct timeval currentTime, oldTime, diffTime;
	
	if ( (bufsize = read(fd, buffer2, sizeof(buffer2) - 1)) > 0 ) {
		fprintf(stderr, "bufsize is %d\n", bufsize);
		static FILE *f;
		if (buffer2[0] == 'A') {
			f = fopen("ATTACK", "a");
		} else if (buffer2[0] == 'V') {
			fprintf(stderr, "First letter is a V\n");
			f = fopen("VICTIM", "a");
			fprintf(stderr, "opened Victim file\n");
		} else {
			fprintf(stderr, "wrong buffer type?\n");
			fprintf(stderr, "%s @ %ld.%ld\n", buffer2, currentTime.tv_sec, currentTime.tv_usec);
		}
		setLogFile(&f);
		fprintf(stderr, "File opened\n");
		if (gettimeofday(&currentTime, NULL) != 0) {
			fprintf(stderr, "ERROR cannot get gettimeofday\n");
			currentTime.tv_sec = 0;
			currentTime.tv_usec = 0;
		}
		fprintf(*file, "%s\n\n", buffer2);
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

		if (gettimeofday(&currentTime, NULL) != 0) {
			fprintf(stderr, "ERROR cannot get gettimeofday\n");
			currentTime.tv_sec = 0;
			currentTime.tv_usec = 0;
		}
		//int currentTimeMicro = currentTime.tv_usec;
		(void)sprintf(buffer,"                                                                  %ld.%06ld", currentTime.tv_sec, currentTime.tv_usec);
		//(void)fprintf(*file,"%ld.%ld::%ld.%ld\n", currentTime.tv_sec, currentTime.tv_usec, currentTime.tv_sec, currentTime.tv_usec);
		//fflush(*file);
		//fprintf(stderr, "%s\n", buffer);
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
					currentTime.tv_sec = 0;
					currentTime.tv_usec = 0;
				}
				//UGH. You do not check return values. BAD!!
				char* pos = strrchr(buffer2, ' '); //clear whitespace
				char* pos2 = strrchr(buffer2, '.');
				*pos2 = '\0';
				//fprintf(stderr, "old timestamp: %s\n", oldTimestampStr);
				oldTime.tv_sec = atoi(pos);
				oldTime.tv_usec = atoi(pos2+1); //BAD THING!
				//fprintf(*file, "%s,\t%s,\t%ld.%ld,\n", src, pos, currentTime.tv_sec, currentTime.tv_usec);
				//timeval_subtract(&diffTime, &currentTime, &oldTime);
				fprintf(*file, "%s\t%ld.%06ld\t%ld.%06ld\n", src, oldTime.tv_sec, oldTime.tv_usec, currentTime.tv_sec, currentTime.tv_usec);
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
	close(fd); 
    exit(0);
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

        //(void)signal(SIGCLD, SIG_IGN); /* ignore child death */
        //(void)signal(SIGHUP, SIG_IGN); /* ignore terminal hangups */

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
                                web2(socketfd, sleep, count, (char*) inet_ntoa(cli_addr.sin_addr));
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
