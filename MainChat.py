from threading import Thread
from Commons import *

import TCPClient
import TCPSercer


class Main:
    #FSDFGSDFGggfn

    def __init__(self):
        self.servidors = {}

        # Llibreria visual organitzada en forma de taula
        self.fines = Tk()
        self.fines.title("Toni's Chat")

        # boto del servidor
        self.server_button = Button(self.fines, text="Nou Servidor", command=self.newServidor, width=20)
        self.server_button.grid(column=0, row=0, padx=5, pady=10)

        # boto del client
        client_button = Button(self.fines, text="Nou Clien", command=self.newClient, width=20)
        client_button.grid(column=1, row=0, padx=5, pady=10)

        # Configuracio
        self.fines.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.fines.grid_columnconfigure(0, weight=1)
        self. fines.grid_rowconfigure(0, weight=1)

        # Espera a la finalització del entorn visual
        self.fines.mainloop()
        print("----- Main Tancat")

    def newServidor(self, event=None):
        serv = toastGetHostPort()
        server = TCPSercer.Servidor(serv)
        self.servidors[serv[1]] = server
        Thread(target=server.inici).start()

    def newClient(self, event=None):
        Thread(target=TCPClient.Client().inici()).start()

    def on_closing(self, event=None):
        for server in self.servidors:
            self.servidors[server].stopServer()
        self.fines.destroy()

Main()