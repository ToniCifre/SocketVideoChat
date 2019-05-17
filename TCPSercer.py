from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from Commons import *
import VideoSender


class Servidor():

    def __init__(self, param):
        print(param)
        self.ADDR = param
        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.clients = {}
        self.canals = {}
        self.addresses = {}
        self.SERVER.bind(self.ADDR)

        self.isTerminal = True

    def inici(self):
        self.SERVER.listen(10)
        # executam un thread per esperar la connecció s'algun client
        ACCEPT_THREAD = Thread(target=self.accept_incoming_connections)
        ACCEPT_THREAD.start()

        TERMINAL_THREAD = Thread(target=self.getTerminal)
        TERMINAL_THREAD.start()

        print("s- Esperant noves connexions...")

        ACCEPT_THREAD.join()
        TERMINAL_THREAD.join()
        print("------- Class Servidor finalitzada ----------")

    def accept_incoming_connections(self):
        # Funcio que espera a que un client es connecti i executa un thread per escoltar els missages
        # de cada un dels clients
        while True:
            try:  # guardam cada una de les connexions es un array per poder accedir a elles en cualsevol momment
                client, client_address = self.SERVER.accept()
                print("s- %s:%s sha connectat." % client_address)
                self.addresses[client] = client_address
                Thread(target=self.handle_client, args=(client,)).start()
            except OSError:
                break
        print("s: Espera de nou clients tancat")

    def handle_client(self, client):
        # Funcio que escolta a un unic client, Primes demana el nom i el guarda en un array ce clients amb el seu nom
        name = "quit"
        try:
            self.enviar(client, "s-info:~:Introdueix el teu nom per començar!")
            name = client.recv(1024).decode("utf8")
            if name != 'quit':
                self.enviar(client,
                            's-info:~:Bones %s!, si vols sortir del char escriu {quit} o talca la finestra.' % name)
                self.broadcast("%s s'ha unit al chat!" % name)
                self.clients[client] = name
                self.canals[client] = 'general'
                while True:
                    try:
                        msg = client.recv(1024).decode("utf-8")
                        print(msg)
                        if len(msg) == 0:
                            break
                        tag = msg.split(':~:')
                        if len(tag) >= 2:
                            if tag[0] == '_NEW_CANAL_':
                                print("new Canal: %s" % tag[1])
                                self.broadcast(tag[1], "new_canal:~:")
                            elif tag[0] == '_SET_CANAL_':
                                self.sendCanal("En %s s'ha cambiat al canal %s." % (name, tag[1]), self.canals[client])
                                self.canals[client] = tag[1]
                                self.sendCanal("En %s s'ha unit al canal." % name, tag[1])
                            elif tag[0] == '_SET_VIDEO_':
                                self.getSenderVideo()
                                self.sendCanal(tag[1], self.canals[client], 'video:~:')

                        else:
                            tag = msg.split('->')
                            if len(tag) >= 2:
                                print("s M-Directe: %s -> %s: %s" % (name, tag[0], tag[1]))
                                self.sendClient(tag[1], tag[0], name + "direct:~: ")
                            else:
                                print("s canal: %s - %s: " % (self.canals[client], name), msg)
                                self.sendCanal(msg, self.canals[client], name + ":~: ")
                    except OSError:
                        break
        except OSError:
            print("s- %s desconnectat." % name)

        self.tancaClient(client)
        self.broadcast(name + " ha abandonat el chat.")

    def broadcast(self, msg, prefix="s-info:~:"):
        # funcio per enviar un missatge a totos els clients
        try:
            for soket_client in self.clients:
                self.enviar(soket_client, prefix + msg)
        except Exception:
            print("s- Multi Client desconnectats.")

    def sendCanal(self, msg, canal='general', prefix="s-info:~:"):
        # funcio per enviar un missatge a totos els clients
        try:
            for soket_client in self.clients:
                if self.canals[soket_client] == canal:
                    self.enviar(soket_client, prefix + msg)
        except Exception:
            print("s- Multi send canal.")

    def sendClient(self, msg, client, prefix="s-info:~:"):
        # funcio per enviar un missatge a totos els clients
        try:
            soket_client = [key for (key, value) in self.clients.items() if value == client]
            self.enviar(soket_client.__getitem__(0), prefix + msg)
        except Exception:
            print("s- send client.")

    def enviar(self, client, msg):
        try:
            client.send(msg.encode("utf-8"))
        except Exception:
            print("s e- Client ja tancat")

    def tancaClient(self, client):
        client.close()
        print("s: Client %s tancat" % self.clients[client])
        del self.clients[client]
        del self.addresses[client]

    def stopServer(self):
        # funcio per a tancar totes les connexions acceptades i tancar el servidor
        self.isTerminal = False
        for client in self.clients.copy():
            self.enviar(client, "quit:~:quit")
        self.SERVER.close()

    # Terminal Response Server
    def getTerminal(self):
        while self.isTerminal:
            text = input("")
            if text == "clients":
                self.getListClients()
            if text == "canals":
                self.getListClientsCanals()
            if text == "stop":
                self.stopServer()
        print("--- S: Terminal tancada ---")

    def getListClients(self):
        for client in self.clients:
            print(self.clients[client])

    def getListClientsCanals(self):
        for canal in list(dict.fromkeys(list(self.canals.values()))):
            print("\n--- Clients del canal %s --- " % canal)
            for client in [self.clients[key] for (key, value) in self.canals.items() if value == canal]:
                print("-%s" % client)

    # ------------------ Striming de Viceo -----------------
    def getSenderVideo(self):
        sender = VideoSender.VideoSender([self.ADDR[0], 5050])
        Thread(target=sender.inici).start()