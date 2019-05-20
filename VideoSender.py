import socket
import _thread

import VideoConnector


class VideoSender(object):
    def __init__(self, connections):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((connections[0], connections[1]))
        self.server_socket.listen(10)

        self.opened_cameras = {}

    def inici(self):
        while 1:
            try:
                client_socket, address = self.server_socket.accept()
                print("Conencted to - ", address, "\n")
                cam_url = client_socket.recv(1024)
                # if camera url does not exsists in oppened camera, open new connection,
                # or else just append client params and pass to Connection thread
                if cam_url not in self.opened_cameras:
                    client = VideoConnector.Connection([client_socket, cam_url])
                    self.opened_cameras[cam_url] = client
                    _thread.start_new_thread(client.capture, (self.opened_cameras,))

                else:
                    self.opened_cameras[cam_url].addConnection(client_socket)

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.server_socket.close()

                exit(0)

    def signal_handler(self, signal=None, frame=None):
        exit(0)
