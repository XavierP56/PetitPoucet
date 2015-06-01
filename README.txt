gcc -finstrument-functions -g -c -o main.o main.c
gcc -c -o trace.o trace.c
gcc main.o trace.o -o main

gcc -fPIC -shared trace.c -o trace.so
gcc -finstrument-functions  -g -o main main.c
LD_PRELOAD=/home/xavier/Traceur/trace.so ./main
