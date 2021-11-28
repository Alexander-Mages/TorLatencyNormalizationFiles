#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <sys/time.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <errno.h>
#include <semaphore.h>

#define LOCATIONBUFSIZE 32
#define WRITEBUFSIZE 512
//#define READBUFSIZE 2048
#define READBUFSIZE 512
#define NULLREDIRECT "index.html"
#define HOSTNAME "localhost"
#define FILENAME "REDIRECT"
#define REPEAT 20
#define THREADS 2
#define OUTSTANDING_WRITES 5

struct arg_t {
	//pthread_mutex_t mutex; //protection for this structure
	int socketfd;
	char* src;
	//sem_t *sem;
};

FILE* file;
unsigned int port;
const char locationPrefix[] = "index";
const char locationSuffix[] = ".html";

//generates defunct children
//void *socketReader(int socketfd, char* src) {
void *socketReader(void* ptr) {
	char buffer[READBUFSIZE];
	char oldTimestampStr[LOCATIONBUFSIZE];
	struct timeval currentTime, oldTime;
	size_t length;
	char* pos;
	unsigned int current;
	fd_set read_set;
	struct timeval tv;

	fprintf(stderr, "Reader start...\n");

	int socketfd = ((struct arg_t*) ptr)->socketfd;
	char* src = ((struct arg_t*) ptr)->src;
	//sem_t *sem = ((struct arg_t*) ptr)->sem;

	//cleanup
	//XXX: make sure other thread has copied args first!!!
	/* sem_destroy(sem);
	free(sem);
	free(src);
	free(arg); */

	FD_ZERO(&read_set);
	FD_SET(socketfd, &read_set);
	//tv.tv_sec = 99920;
	tv.tv_sec = 60; //pulled some unreasonable timeout value out of my ass
	tv.tv_usec = 0;

	current = 0;
//	while (current < REPEAT + 1) {
	while (1) {
		//read to see if we got an old timestamp
		if ((select(socketfd + 1, &read_set, NULL, NULL, &tv) > 0) &&
				((length = read(socketfd, buffer, sizeof(buffer) - 1)) > 0 )) {

			fprintf(stderr, "Reader servicing victim request %d\n", current);

			//sem_post(sem);

			//fprintf(stderr, "Received:\n%s\n", buffer);

			if (gettimeofday(&currentTime, NULL) != 0) {
				fprintf(stderr, "ERROR: cannot gettimeofday\n");
				currentTime.tv_sec = 0;
				currentTime.tv_usec = 0;
			}

			pos = strstr(buffer, locationSuffix);
			if (pos > 0) {
				*pos = '\0'; //terminate at line break
				//fprintf(stderr, "new buffer:\n%s\n", buffer);
			}
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
				fprintf(stderr, "Reader: no dashes in buffer. Initial request?\n");
				fprintf(stderr, "%s\n", buffer);
				fprintf(stderr, "%s\n", oldTimestampStr);
				fprintf(file, "start @ %ld.%06ld\n", currentTime.tv_sec, currentTime.tv_usec);
				fprintf(file, "%s\n", buffer);
			}
			fflush(file);

			current++;
		} else {
			perror("Read failed, bailing");
			close(socketfd);
			return;
		}
	}

	close(socketfd);
	fprintf(stderr, "Reader finished!\n");
}

//void *socketWriter(int socketfd, char* src) {
void *socketWriter(void* ptr) {
	char buffer[WRITEBUFSIZE];
	char oldTimestampStr[LOCATIONBUFSIZE];
	char newLocation[LOCATIONBUFSIZE];
	struct timeval currentTime;
	size_t length;
	fd_set write_set;
	struct timeval tv;
	char* pos;
	unsigned int current;

	fprintf(stderr, "Writer start...\n");

	int socketfd = ((struct arg_t*) ptr)->socketfd;
	//sem_t *sem = ((struct arg_t*) ptr)->sem;
	//sem_t *lock = ((struct arg_t*) ptr)->lock;

	FD_ZERO(&write_set);
	FD_SET(socketfd, &write_set);
	//tv.tv_sec = 99920;
	tv.tv_sec = 60; //pulled some unreasonable timeout value out of my ass
	tv.tv_usec = 0;

	current = 0;
	while (current < REPEAT + 1) {
		//sem_wait(sem); //sem_timewait()?

		fprintf(stderr, "Writer servicing victim request %d\n", current);

		if (gettimeofday(&currentTime, NULL) != 0) {
			fprintf(stderr, "ERROR: cannot gettimeofday\n");
			currentTime.tv_sec = 0;
			currentTime.tv_usec = 0;
		}

		//compose new redirect with current time
		sprintf(newLocation, "%s%ld-%06ld%s", locationPrefix, currentTime.tv_sec, currentTime.tv_usec, locationSuffix);
		//sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\n\r\n<html>boooooo!</html>\r\n\r\n", newLocation);
		sprintf(buffer,"HTTP/1.1 301\r\nContent-Type: text/html\r\nLocation: %s\r\nContent-Length: 0\r\n\r\n", newLocation);
		length = strlen(buffer);

		if ((select(socketfd + 1, NULL, &write_set, NULL, &tv) > 0) &&
				(write(socketfd,buffer,strlen(buffer)) >= length)) {
			//fflush((FILE*)fd);
			//fprintf(stderr, "Sent:%s\n\n", buffer);
			//#ifdef LINUX
			usleep(500000);//sleep 0.5 seconds
			//#endif
			current++;
		}  else {
			//for when the reader closes the connection after 20 reads
			perror("Write failed, bailing");
			close(socketfd);
			return;
		}
	}

	fprintf(stderr, "Writer finished!\n");
}

main(int argc, char **argv) {
	int true_val = 1; //for setting socket options
	int i, pid1, pid2, listenfd, socketfd;
	size_t length;
	static struct sockaddr_in cli_addr;
	static struct sockaddr_in serv_addr;
	unsigned int served;
#ifndef FILENAME
	struct timeval currentTime; //for filename
	char filename[32] = {0};
#endif
	pthread_t *reader, *writer;

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

	fprintf(stderr, "Binding to %d...", port);
	while (bind(listenfd, (struct sockaddr *)&serv_addr,sizeof(serv_addr)) <0) {
		//fprintf(stderr, "Unable to bind\n");
		//return 1;
		sleep(5);
		fprintf(stderr, ".");
	}
	fprintf(stderr, "success!\n");

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

	signal(SIGPIPE, SIG_IGN); /* ignore sigpipe - is this safe?? */

	fprintf(stderr, "Ready\n");

	reader = writer = NULL;
	length = sizeof(cli_addr);
	served = 0;
	while (1) {

		if((socketfd = accept(listenfd, (struct sockaddr *) &cli_addr, &length)) < 0) {
			fprintf(stderr, "Unable to accept new connection\n");
			return 1;
		}

		//if we accept a new connection, no outstanding threads should exist!
		/* if (writer) {
			pthread_kill(*writer, SIGKILL);
			free(writer);
		}
		if (reader) {
			pthread_kill(*reader, SIGKILL);
			free(reader);
		} */

		served++;
		fprintf(stderr, "Serving victim connection %d\n", served);

		//initialize our semaphore
		/*sem_t *sem = calloc(1, sizeof(sem_t));
		if (sem_init(sem, 0, OUTSTANDING_WRITES)) {
			fprintf(stderr, "Could not initialize semaphore.\n");
			exit(2);
		} //OUTSTANDING_WRITES is how many pipelines writes are allowed

		sem_t *lock = calloc(1, sizeof(sem_t));
		if (sem_init(lock, 0, THREADS)) {
			fprintf(stderr, "Could not initialize semaphore.\n");
			exit(3);
		}*/

		struct arg_t *arg = calloc(1, sizeof(struct arg_t));
		arg->src = (char*) inet_ntoa(cli_addr.sin_addr);
		arg->socketfd = socketfd;
		//arg->sem = sem;
		//arg->lock = lock;

		reader = calloc(1, sizeof(pthread_t));
		writer = calloc(1, sizeof(pthread_t));
		pid1 = pthread_create(reader, NULL, socketReader, (void*) arg);
		pid2 = pthread_create(writer, NULL, socketWriter, (void*) arg);

		//leaks threads, along with all their args, semaphores, pids, etc.

		/*
		if((pid1 = fork()) < 0) {
			fprintf(stderr, "Fork failed\n");
			exit(1);
		} else if(pid1 == 0) {		// 1st child
			close(listenfd);
			socketReader(socketfd, (char*) inet_ntoa(cli_addr.sin_addr));
			close(socketfd);
			return 0;
		} else {					// intermediate parent
			if((pid2 = fork()) < 0) {
				fprintf(stderr, "Fork failed\n");
				exit(2);
			} else if(pid1 == 0) {  // 2nd child
				close(listenfd);
				socketWriter(socketfd, (char*) inet_ntoa(cli_addr.sin_addr));
				close(socketfd);
				return 0;
			}
			else {					// final parent
				close(socketfd);
				continue;
			}
		} */
	}
	fprintf(stderr, "HUH?");
}
