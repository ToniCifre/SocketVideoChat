from threading import Thread
from Commons import *

import TCPClient
import TCPSercer


class Main:

    def __init__(self):
        #Guarda tots els servidors que s'executen
        self.servidors = {}

        # Llibreria visual organitzada en forma de taula
        self.fines = Tk()
        self.fines.title("Toni's Chat")

        # boto del servidor
        self.server_button = Button(self.fines, text="Nou Servidor", command=self.newServidor, width=20)
        self.server_button.grid(column=0, row=0, padx=5, pady=10)

        # boto del client
        client_button = Button(self.fines, text="Nou Client", command=self.newClient, width=20)
        client_button.grid(column=1, row=0, padx=5, pady=10)

        # Configuracio de la finestra visual
        self.fines.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.fines.grid_columnconfigure(0, weight=1)
        self. fines.grid_rowconfigure(0, weight=1)

        # Espera a la finalització del entorn visual
        self.fines.mainloop()
        print("----- Main Tancat")

    #Inicialitza un nou thread servidor
    def newServidor(self, event=None):
        serv = toastGetHostPort()
        server = TCPSercer.Servidor(serv)
        self.servidors[serv[1]] = server
        Thread(target=server.inici).start()

    #Inicialitza un nou thread client
    def newClient(self, event=None):
        Thread(target=TCPClient.Client()).start()

    #tanca tots els servidors
    def on_closing(self, event=None):
        for server in self.servidors:
            self.servidors[server].stopServer()
        self.fines.destroy()

Main()