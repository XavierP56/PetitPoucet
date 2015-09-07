#!/usr/bin/env python
# -*- coding: utf-8 -*

import socket
from threading import Thread
import os, sys
import bottle
from bottle import route, run, request, abort, static_file
from copy import deepcopy
from operator import itemgetter

app = bottle.Bottle()
@app.route('/demo/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./Files/')
    
execution = []
result = []
filter_this = ['check_in_range', 'find_by_addr_in_unit']
record_status = 0
files = []

def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)
    
@memoize
def addr2funcline(addr):
    global files
    cmd = 'addr2line -p -f -e /home/xavier/PetitPoucet/main ' + addr
    p = os.popen(cmd)
    sloc_line = p.readline()
    sloc = sloc_line.split() 
    try:
        from_func = sloc[0]
        infos = sloc[2].split(':')
        from_src = infos[0]
        from_line = int(infos[1])
        e = { 'src': from_src, 'filtered' : False }
        if not e in files:
            files.append(e)
    except:
        from_func = '???'
        from_src =  ''
        from_line = 0
    p.close()
    return (from_func, from_src, from_line)
    
class ClientThread(Thread):

    def __init__(self, ip, port, clientsocket):

        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self): 
        global execution
        global filter_this
        global record_status
        
        print("Connection de %s %s" % (self.ip, self.port, ))
        line = ''
        while True:
            if not record_status:
                line = ''
                r = self.clientsocket.recv(1)
                continue
            while line == '':
                r = self.clientsocket.recv(1)
                if r == '#':
                   r = self.clientsocket.recv(1)
                   line += r
            r = self.clientsocket.recv(1)
            if r != '\n':
                line += r
            else:
                res = line.split()
                execution.append(line)
                # print line
                line = ''
            
class SocketThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        # Create the socket
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind(("",1111))
        # Listen to client
        while True:
            tcpsock.listen(1)
            print( "En écoute...")
            (clientsocket, (ip, port)) = tcpsock.accept()
            print "Creating thread"
            newthread = ClientThread(ip, port, clientsocket)
            newthread.start()
        

# Start the socket thread.
socketthread = SocketThread()
socketthread.start()

print 'Bottle is started too...'

def find_caller(idx, func_number, tof, fromf, tid):
    global result
    
    # Retrieve the func number.
    endidx = idx
    if (idx == 0):
        return
    idx -= 1
    while (idx != 0):
        if result[idx]['from_func'] == fromf and result[idx]['to_func'] == tof and result[idx]['tid'] == tid:
            result[idx]['endnum'] = func_number
            result[idx]['endidx'] = endidx
            break
        idx -=1
    return

def checkIfKnow(src):
    global files
    
    if src == '':
        return False
        
    e = { 'src': src, 'filtered' : True }
    if e in files:
        return True
    else:
        return False
     
@app.route('/trace/refresh', method='GET')
def refresh():
    global execution
    global result
    global files
    
    result = []
    idx = 0
    func_number = 0
    
    # First pass. Only look at entered functions.
    for line in execution:
        #print '------------------'
        #print line
        res = line.split()
        # res[1] func, res[2] caller
        filterIt = False
        (to_func, to_src, to_line) = addr2funcline(res[1])
        filterIt |= checkIfKnow(to_src)
        (from_func, from_src, from_line) = addr2funcline(res[2])
        filterIt |= checkIfKnow(from_src)
        tid = res[3]                
         
        if (filterIt):
            #print 'FILTERED'
            if (res[0] == 'e'):
                func_number += 1
            continue
        else:
            # Entry new function.
            if (res[0] == 'e'):
                #print 'TO:' + to_func + ' src ' + to_src + ':' + str(from_line)
                #print '   FROM:' + from_func + ' src ' + from_src + ':' + str(from_line)
                v = { 'idx':idx, 'fnum': func_number, 'from_func' : from_func, 'from_src': from_src, 'from_line': from_line, 'to_func': to_func, 'to_src': to_src, 'to_line': to_line, 'endnum': '?', 'endidx': '?', 'tid': tid }
                idx += 1
                func_number += 1
                result.append(v)
            elif (res[0] == 'x'):
                # We are leaving to_func, caller from_func
                find_caller(idx, func_number, to_func, from_func, tid);

    # Filter the list of files
    files = sorted(files, key=itemgetter('src')) 
    return { 'result' : result, 'files': files }
    
@app.route('/trace/getFile', method='POST')
def getFile():
    curFile = request.json['fPath']
    # Read file in python
    f = open (curFile, 'r')
    content = f.read()
    f.close()
    return { 'src' : content }
    
@app.route('/trace/getStatus', method='GET')
def getStatus():
    global record_status
    return { 'res': record_status};

@app.route('/trace/setStatus/<status:int>', method='GET')
def setStatus(status):
    global record_status
    global execution
    global files
    record_status = status
    if (record_status == 1):
        execution = []
        files = []
    return { 'res': record_status};
     
@app.route('/trace/filterFiles', method='POST')
def filterFiles():
    global files
    files = request.json['filefilter']
    return refresh()
    
#Start the bottle thread
bottle.run(app, port=8080, host='0.0.0.0')



