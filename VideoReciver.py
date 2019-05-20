#!/usr/bin/python
import socket
import cv2
import numpy
import sys

class VideoReciver(object):
    def __init__(sel):
        pass

    def inici(self, connections):
        self.host = connections[0]
        self.port = connections[1]
        self.cam_url = connections[2]  # 'webcam'# 'http://www.html5videoplayer.net/videos/toystory.mp4'
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((self.host, self.port))
        self.name = connections[2]

        self.run = True

        self.client_socket.send(str.encode(self.cam_url))

        while self.run:
            self.rcv()
        cv2.destroyAllWindows()

    def rcv(self):
        data = b''
        while self.run:
            try:
                r = self.client_socket.recv(90456)
                if len(r) == 0:
                    exit(0)
                a = r.find(b'END!')
                if a != -1:
                    data += r[:a]
                    break
                data += r
            except Exception as e:
                self.run = False
                continue
        try:
            nparr = numpy.fromstring(data, numpy.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if type(frame) is type(None):
                pass
            else:
                try:
                    cv2.imshow(self.name,frame)
                    if cv2.waitKey(10) == ord('q'):
                        self.client_socket.close()
                        sys.exit()
                except:
                    self.run=False
                    self.client_socket.close()
        except Exception as e:
            self.run = False
            print(e)

    def stopVideo(self):
        self.run = False
