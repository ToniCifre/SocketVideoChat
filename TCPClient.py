import tkinter

from tkinter import scrolledtext
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from Commons import *

import VideoReciver

class Client:

    def __init__(self):
        # inicialitzacio del client, es crea la finestra del client i s'executa el thread per escoltar els missatges
        # que envia el servidor

        self.inici()

    def inici(self):
        conec = self.connect()

        self.initTk()

        if conec:
            Thread(target=self.handleMissatge).start()
        else:
            self.error_mesage("no sha pogut connectar al servidor")

        self.finestra.mainloop()
        print("------- Class Client finalitzada ----------")

    def initTk(self):
        tkinter.NoDefaultRoot()
        self.finestra = Tk()
        self.finestra.title("Chat")

        self.canal = StringVar(self.finestra)
        self.canal.set("general")
        self.canals = ["general"]
        self.drop_down = OptionMenu(self.finestra, self.canal, *self.canals)
        self.drop_down.grid(column=0, row=0, padx=5, pady=10, columnspan=1,  sticky=EW)
        cambia_canal_button = Button(self.finestra, text="Canvia Canal", command=self.setCanal, width=20)
        cambia_canal_button.grid(column=1, row=0, padx=5, pady=10)
        nou_canal_button = Button(self.finestra, text="Nou Canal", command=self.nouCanal, width=20)
        nou_canal_button.grid(column=2, row=0, padx=5, pady=10)

        # Scrollable box on es mostraras els missatges
        self.msg_list = scrolledtext.ScrolledText(self.finestra, state='disabled')
        self.msg_list.grid(column=0, row=1, columnspan=3, padx=5, pady=5, sticky=NSEW)

        # Field on s'escriuran els missatges que volgem enviar
        self.entry_field = Entry(self.finestra)
        self.entry_field.bind("<Return>", self.envia)  # funció que es realitzara si apretam la lletra enter
        self.entry_field.grid(column=0, row=2, columnspan=2, sticky=EW, padx=5, pady=10)

        # Boto per enviar el missatge
        envia_button = Button(self.finestra, text="envia", command=self.envia, width=20)
        envia_button.grid(column=2, row=2, padx=5, pady=10)

        # funcio que es fera si es tanca la finestra del client
        self.finestra.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.finestra.grid_columnconfigure(0, weight=1)
        self.finestra.grid_rowconfigure(0, weight=1)

    def connect(self):
        try:  # intentam connectar amb el servidor
            self.ADDR = toastGetHostPort()
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)

        except Exception:
            print("C: No sha pogut connectar amb el servidor")
            return FALSE
        return TRUE

    def handleMissatge(self):
        try:
            while self.get_missatge():
                pass
            self.tancarconnexio()

        except Exception:
            print("C: ++ Error handleMissatge")

        print("C: Exit handleMissatge")

    def get_missatge(self):
        msg = self.client_socket.recv(1024).decode("utf8")
        if len(msg) == 0:
            return False

        self.msg_list.configure(state='normal')

        tag = msg.split(':~:')
        if tag[0] == "s-info":
            self.msg_list.insert(END, tag[1] + "\n")
        elif tag[0] == "new_canal":
            self.canals.append(tag[1])
            menu = self.drop_down["menu"]
            menu.delete(0, "end")
            for string in self.canals:
                menu.add_command(label=string,
                                 command=lambda value=string: self.canal.set(value) and self.setCanal)
            self.msg_list.insert(END, "S'ha creat un nou canal." + "\n")
        elif tag[0] == "quit":
            return False
        elif tag[0][-6:] == "direct":
            print(tag[0][:-6])
            self.msg_list.insert(END, tag[0][:-6] + ':', tag[0])
            self.msg_list.insert(END, tag[1] + "\n")
            self.msg_list.tag_config(tag[0], foreground='blue')
        elif tag[0] == "video":
            self.getSenderVideo(tag[0])
        else:
            self.msg_list.insert(END, tag[0] + ':', tag[0])
            self.msg_list.insert(END, tag[1] + "\n")
            self.msg_list.tag_config(tag[0], foreground='green')

        self.msg_list.configure(state='disabled')
        return True

    def envia(self, event=None):
        try:  # Funció per enviar un missatge al servidor
            msg = self.entry_field.get()
            self.entry_field.delete(0, END)
            if msg == "quit":
                self.tancarconnexio()
            else:
                self.client_socket.send(msg.encode("utf-8"))
        except OSError:
            print("C: ++ Error Envia")

    def nouCanal(self):
        msg = "_NEW_CANAL_:~:%s" % toastNewCanal()
        self.client_socket.send(msg.encode("utf-8"))

    def setCanal(self):
        msg = "_SET_CANAL_:~:%s" % self.canal.get()
        self.client_socket.send(msg.encode("utf-8"))

    def error_mesage(self, msg):
        try:  # fincio per mostrar algun missatge d'error vermell per el Box
            self.msg_list.configure(state='normal')
            self.msg_list.insert(END, msg, "error")
            self.msg_list.tag_config("error", foreground='red')
            self.msg_list.configure(state='disabled')
        except Exception:
            print("C: ++Error erro_mesage")

    def on_closing(self, event=None):
        # si apretam el boto per tancar la finestra informam al servidor i es tanca la finestra
        self.tancarconnexio()
        self.exit()

    def tancarconnexio(self):
        self.error_mesage("S'ha tancat la connexió amb el servidor")
        self.client_socket.close()
        print("C: Soket Client tancat")

    def exit(self):
        # self.finestra.quit()
        self.finestra.destroy()

    # ------------------ Striming de Viceo -----------------
    def getSenderVideo(self, video):
        reciver = VideoReciver.VideoReciver([self.ADDR[0], 5050, 'toni.mp4'])
        Thread(target=reciver.inici).start()
