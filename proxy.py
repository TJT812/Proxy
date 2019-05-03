import os
import sys
import threading
import socket
import codecs
import gzip


BACKLOG = 5
MAX_DATA_RECV = 999999
DEBUG = True
BLOCKED = []
HTTP_PORT = 80


def main():
    if (len(sys.argv)<2):
        print ("No port given, using :8080")
        port = 8080
    else:
        port = int(sys.argv[1])

    host = ''

    print ("Proxy Server Running on ", host,":", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(BACKLOG)
    while 1:
        conn, client_addr = s.accept()
        threading.Thread(target=proxy_thread, args=(conn, client_addr)).start()
    s.close()

    print (type + ' ' + request)

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)

    first_line = request.decode('utf-8').split('\n')[0]
    #print(first_line + '-')
    blocked_message = b"<html><body><h1>Forbidden</h1></body></html>"
    if first_line  != '':
        url = first_line.split(' ')[1]
        #print(first_line)
        #print(url)
        for i in range(0, len(BLOCKED)):
            if BLOCKED[i] in url:
                conn.send(blocked_message)
                print("Blacklisted " + first_line)
                conn.close()
                sys.exit(1)

        print("Request " + first_line)

        http_pos = url.find("://")
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(":")


        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos == -1) or (webserver_pos < port_pos):
            port = HTTP_PORT
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos-port_pos - 1])
            webserver = temp[:port_pos]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((webserver, port))
        sock.sendall(request)

        while 1:
            data = sock.recv(MAX_DATA_RECV)
            #print(data)
            #data_decompressed = gzip.decompress(data)
            if(data):
                line = data.decode('utf-8', errors='ignore').split('\n')[0]

            #line = data[:12]

            #file = open('temp.txt', 'wb')
            #file.write(data)
            #file.close()
            #with codecs.open('temp.txt', 'r', encoding='utf-8', errors='ignore') as fdata:
            #     print(fdata)
            #line = fdata.encoding('utf-8').split('\n')[0]
            
            if (line != 0) and ('HTTP' in line):
                print("From " + webserver + " " + line)


            if (len(data) > 0):
                try:
                    conn.send(data)
                except ConnectionAbortedError:
                    break
            else:
                break
        sock.close()
        conn.close()

if __name__ == '__main__':
    main()
