#include <stdio.h>
#include <stdlib.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <string.h>

int sockfd;
struct sockaddr_in server;

void
__attribute__ ((constructor))
trace_begin (void)
{
	sockfd = socket(AF_INET , SOCK_STREAM , 0);
	server.sin_addr.s_addr = inet_addr("127.0.0.1");
	server.sin_family = AF_INET;
	server.sin_port = htons( 1111 );
    //Connect to remote server
    if (connect(sockfd , (struct sockaddr *)&server , sizeof(server)) < 0)
    {
		fprintf(stderr,"CAN NOT CONNECT\n");
		exit(0);
    }
}
 
void
__attribute__ ((destructor))
trace_end (void)
{
	close(sockfd);
}
 
void
__cyg_profile_func_enter (void *func,  void *caller)
{
	char buff[256];
 if(sockfd != -1) {
	 pid_t tid;
	 tid = syscall(SYS_gettid);
	 sprintf(buff, "#e %p %p 0x%x\n", func, caller, tid );
	 send(sockfd, &buff, strlen(buff)+1,0);
 }
}
 
void
__cyg_profile_func_exit (void *func, void *caller)
{
	char buff[256];
 if(sockfd != -1) {
	 pid_t tid;
	 tid = syscall(SYS_gettid);
	 sprintf(buff, "#x %p %p 0x%x\n", func, caller, tid );
	 send(sockfd, &buff, strlen(buff)+1,0);
 }
}
