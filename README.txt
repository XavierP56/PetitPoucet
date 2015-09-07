Install python-bottle:
    sudo apt-get install python-bottle
Install bower:
	sudo apt-get install nodejs
	sudo apt-get install npm
	sudo npm install -g bower
	
Instrument your software:
	gcc -finstrument-functions -g -c -o main.o main.c
	
Compile the trace library:
	gcc -c -o trace.o trace.c
	
Link your software with the trace library:
	gcc main.o trace.o -o main

Or you can do:
	gcc -fPIC -shared trace.c -o trace.so
	gcc -finstrument-functions  -g -o main main.c
	LD_PRELOAD=/home/xavier/Traceur/trace.so ./main

Currently, the python server has no parameters.
Edit server.py and change this line to point to your executable:
    cmd = 'addr2line -p -f -e /home/xavier/Traceur/main ' + addr
    
Start the python server:
python server.py

Launch the IDE through a Browser:
http://localhost:8080/demo/petitpoucet.html
Record a trace
Launch your main executable
Stop trace
Analyze the trace

Limitation:
- Executable location hardcoded in server.py
- No support of shared libs.
