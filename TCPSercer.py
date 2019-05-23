from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import VideoSender


class Servidor():

    # Funció utilitzada per inicialitzar la classe serves des del MainChat.
    # S'encarrega d'inicialitzar les variables globals
    def __init__(self, param):
        self.ADDR = param
        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.clients = {}#Diccionari amb els sokets dels clients i els seus noms
        self.canals = {}#Diccionari de canals amb els clients que formen part d'ell
        self.listCanals = []#llista de canals diaponibes
        self.addresses = {}#llista de addreces de cada servidor
        self.SERVER.bind(self.ADDR)
        print('Nou Servidor: '+self.SERVER.__str__())

        self.isVideo = False
        self.isTerminal = True#variable que ens indica si el terminal ha des segir esperant

    # S'encarrega de llençar el servidor des del MainChat amb el seu propi thread.
    # Inicialitza dos nou threads. Un per esperar noves connexions dels clients i un altre per esperar
    # comasdes del terminal, un com acaben aquests dos treads significa que el servidor esta tancat.
    def inici(self):
        self.SERVER.listen(10)
        # executam un thread per esperar la connexió d'algun client.
        ACCEPT_THREAD = Thread(target=self.accept_incoming_connections)
        ACCEPT_THREAD.start()
        # Executam un thread per esperar les comandes a traves del terminal.
        TERMINAL_THREAD = Thread(target=self.getTerminal)
        TERMINAL_THREAD.start()

        print("s- Esperant noves connexions...")
        #Esperam que els dos threads acabin
        ACCEPT_THREAD.join()
        TERMINAL_THREAD.join()
        print("------- Class Servidor finalitzada ----------")

    # Espera la connexio de un client i una vegada connectat inicialitza un nou thread encarregat d'administrar el
    # soket del client i escoltar totos els missatges que aquest envia
    def accept_incoming_connections(self):
        while True:
            try:  # guardam cada una de les connexions es un array per poder accedir a elles en cualsevol momment
                client, client_address = self.SERVER.accept()
                print("s- %s:%s sha connectat." % client_address)
                self.addresses[client] = client_address #guardam l'adreça del client amb el seu socket
                Thread(target=self.handle_client, args=(client,)).start()
            except OSError:
                break
        print("s: Espera de nou clients tancat")

    # Thread que escolta a un unic client, La seva funcionalitat es basa en demanar el nom al client i si aquest nom no
    # existeix el guarda amb el seu soket i es queda en u bucle fin que rep el misatge 'quit'.
    # La comunicació es basa en misatges que al principi porten un tag el qual indica el que esta demanant el client,
    # per exemple si el client vol crear un nou canal el tag sera '_NOU_CANAL_' i al nom del canal a continuació
    def handle_client(self, client):
        name = "quit"
        try:
            self.enviar(client, "s-info:~:Introdueix el teu nom per començar!")

            name = client.recv(1024).decode("utf8")
            # Si en nom ja existeix en demana un altre fins que en trobi un que no existeix
            while list(dict.fromkeys(list(self.clients.values()))).__contains__(name):
                self.enviar(client, 's-info:~:Aquest no ja esta escollit, intenten un altre')
                name = client.recv(1024).decode("utf8")
            if name != 'quit':
                self.enviar(client, 's-info:~:Bones %s!, si vols sortir del char escriu {quit} o tanca la finestra.\n'
                                    'Per enviar un missatge privat a algun usuari, nomes has de introduir el seu nom,'
                                    ' segit d\'una fletxa \'->\' i el missatge que desitgis enviar' % name)

                # Si ja existeixen canals extres s'envia una llista amb els canals extres
                if len(self.listCanals) >= 1:
                    shit = ''
                    for canal in self.listCanals:
                        shit += canal + ','
                    self.enviar(client, 'set_canal:~:' + shit)

                # S'envia un misatge a totos els clients informant que s'ha unit una nova persona
                self.broadcast("%s s'ha unit al chat!" % name)
                self.clients[client] = name # safegeix el nou client al diccionari amb el seu soket relacionat amb el seu nom
                self.canals[client] = 'general' # s'afegeix el client al canal inicial

                while True:
                    # esperam els missatges del client fins que es desconnecti
                    try:
                        msg = client.recv(1024).decode("utf-8")#decodificam el missatge rebut
                        if len(msg) == 0:#Si el missatge es buit significa que el client s'ha desconnectat i tancam la connexió
                            break
                        tag = msg.split(':~:')#semaram el misatge per el indicador
                        if len(tag) >= 2:
                            if tag[0] == '_NEW_CANAL_':#Cream un nou canal i enviam al nom a tots els clients
                                print("s nou Canal creat: %s" % tag[1])
                                self.listCanals.append(tag[1])
                                self.broadcast(tag[1], "new_canal:~:")
                            elif tag[0] == '_SET_CANAL_':#Cambiam el client al canal especificat
                                self.sendCanal("En %s s'ha cambiat al canal %s." % (name, tag[1]), self.canals[client])
                                self.canals[client] = tag[1]
                                self.sendCanal("En %s s'ha unit al canal." % name, tag[1])
                            elif tag[0] == '_SET_VIDEO_':#Inicializam la clase per a fer streaming de video i informam a tots el clients del canal
                                if not self.isVideo:
                                    self.isVideo = True
                                    self.getSenderVideo()
                                self.sendCanal(tag[1], self.canals[client], 'video:~:')

                        else:
                            tag = msg.split('->')#Separam el misatge per el indicador de misatge directe
                            if len(tag) >= 2:#Enviam un misatge a una persona en concret
                                print("s M-Directe: %s -> %s: %s" % (name, tag[0], tag[1]))
                                self.sendClient(tag[1], tag[0], name + "direct:~: ")
                            else:#enviam el missatge als clients que estan al mateix canal que el client emisor
                                print("s canal: %s - %s: " % (self.canals[client], name), msg)
                                self.sendCanal(msg, self.canals[client], name + ":~: ")
                    except OSError:
                        break
        except OSError:
            print("s- %s desconnectat." % name)

        self.tancaClient(client)#tancam la connexió amb el client
        self.broadcast(name + " ha abandonat el chat.")#informam a tots que el client s'ha desconnectat

    # Envia un missatge a tots el usuaris connectats al servidor
    def broadcast(self, msg, prefix="s-info:~:"):
        # funcio per enviar un missatge a totos els clients
        try:
            for soket_client in self.clients:
                self.enviar(soket_client, prefix + msg)
        except Exception:
            print("s- Multi Client desconnectats.")

    # Envia un missatge a tots els usuaris que estan dintre de un canal
    def sendCanal(self, msg, canal='general', prefix="s-info:~:"):
        # funcio per enviar un missatge a totos els clients d'un canal determinat
        try:
            for soket_client in self.clients:
                if self.canals[soket_client] == canal:
                    self.enviar(soket_client, prefix + msg)
        except Exception:
            print("s- Multi send canal.")

    # Envia un missatge directe a un unic client a partir del seu nom
    def sendClient(self, msg, client, prefix="s-info:~:"):
        try:
            soket_client = [key for (key, value) in self.clients.items() if value == client]
            self.enviar(soket_client.__getitem__(0), prefix + msg)
        except Exception:
            print("s- send client.")

    # Funció generalitzada que envi un missatge a un client
    def enviar(self, client, msg):#Envia un misatge cosidicat a un determinat client
        try:
            client.send(msg.encode("utf-8"))
        except Exception:
            pass# print("s e- Client ja tancat")

    # Tanca la connexió i elimina el usuari desconectat de les llistes
    def tancaClient(self, client):#Tanca un determinat client i l'elimina de totes les llistes
        client.close()
        print("s: Client %s tancat" % self.clients[client])
        del self.clients[client]
        del self.canals[client]
        del self.addresses[client]

    # Funcio per a tancar totes les connexions acceptades i tancar el servidor
    def stopServer(self):
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
            if text == "canalsclients":
                self.getListClientsCanals()
            if text == "canals":
                self.getListCanals()
            if text == "stop":
                self.stopServer()
        print("--- S: Terminal tancada ---")

    # Imprimeix una llista de totos els clients
    def getListClients(self):
        for client in self.clients:
            print("%s: %s" %(self.clients[client], self.addresses[client]))

    # Imprimeix una llista amb els clients que hi ha dintre de cada canal
    def getListClientsCanals(self):
        for canal in list(dict.fromkeys(list(self.canals.values()))):
            print("\n--- Clients del canal %s --- " % canal)
            for client in [self.clients[key] for (key, value) in self.canals.items() if value == canal]:
                print("-%s" % client)

    # Imprimeix una llista de tots els canals
    def getListCanals(self):
        print("--- LLISTA DE CANALS ---")
        print("general")
        for canal in self.listCanals:
            print(canal)

    # ------------------ Striming de Viceo -----------------
    # Inicialitza un nou thread per a poder realitzar un streaming
    def getSenderVideo(self):
        sender = VideoSender.VideoSender([self.ADDR[0], 5050])
        Thread(target=sender.inici).start()
