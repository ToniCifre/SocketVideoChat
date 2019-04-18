from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from Commons import *


class Servidor():

    def __init__(self, param):
        print(param)
        self.ADDR = param
        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.clients = {}
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
            self.enviar(client, "s-info:~: Introdueix el teu nom per començar!")
            name = client.recv(1024).decode("utf8")
            if name != 'quit':
                self.enviar(client,
                            's-info:~: Bones %s!, si vols sortir del char escriu {quit} o talca la finestra.' % name)
                self.broadcast("%s s'ha unit al chat!" % name)
                self.clients[client] = name
                while True:
                    try:
                        msg = client.recv(1024).decode("utf-8")
                        if len(msg) == 0:
                            break
                        print("s %s- " % name, msg)
                        self.broadcast(msg, name + ":~: ")
                    except OSError:
                        break
        except OSError:
            print("s- %s desconnectat." % name)

        self.tancaClient(client)
        self.broadcast(name + " ha abandonat el chat.")

    def broadcast(self, msg, prefix="s-info:~: "):
        # funcio per enviar un missatge a totos els clients
        try:
            for sock in self.clients:
                self.enviar(sock, prefix + msg)
        except Exception:
            print("s- Multi Client desconnectats.")

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
            if text == "stop":
                self.stopServer()
        print("--- S: Terminal tancada ---")


    def getListClients(self):
         for client in self.clients:
             print(self.clients[client])
