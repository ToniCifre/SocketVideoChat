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
        self.isVideo = False
        self.inici()

    def inici(self):
        #Crida a la funció per a connectarse al soket desitjat
        conec = self.connect()

        #inicialitza la llibreria visual
        self.initTk()

        #Si sha pogut connectar al soket escollit s'obrira un nou thread en espera als misatges del servidor.
        if conec:
            Thread(target=self.handleMissatge).start()
        else:#Si no s'ha pogut connectar es mostrara un missatge en vermell a la finestra visual
            self.error_mesage("no sha pogut connectar al servidor")
        #S'inicialitza la classe per a poder fer streaming de video
        self.reciver = VideoReciver.VideoReciver()

        #Esoeram a que la finestra visual es tanqui
        self.finestra.mainloop()
        print("------- Class Client finalitzada ----------")

    def initTk(self):
        #Inicialització de la finestra visual

        tkinter.NoDefaultRoot()
        self.finestra = Tk()
        self.finestra.title("Chat")

        #drop down amb la llista de canals.
        self.canal = StringVar(self.finestra)
        self.canal.set("general")
        self.canals = ["general"]
        self.drop_down = OptionMenu(self.finestra, self.canal, *self.canals)
        self.drop_down.grid(column=0, row=0, padx=5, pady=10, columnspan=1,  sticky=EW)
        #Boto per a cambiar de canal
        cambia_canal_button = Button(self.finestra, text="Canvia Canal", command=self.setCanal, width=20)
        cambia_canal_button.grid(column=1, row=0, padx=5, pady=10)
        #Boto Per a crear un nou canal
        nou_canal_button = Button(self.finestra, text="Nou Canal", command=self.nouCanal, width=20)
        nou_canal_button.grid(column=2, row=0, padx=5, pady=10)
        #Boto per a crear un nou video

        set_video_button = Button(self.finestra, text="Iniciar Video", command=self.buttonNewVideo, width=20)
        set_video_button.grid(column=3, row=0, padx=5, pady=10)

        # Scrollable box on es mostraras els missatges
        self.msg_list = scrolledtext.ScrolledText(self.finestra, state='disabled')
        self.msg_list.grid(column=0, row=1, columnspan=4, padx=5, pady=5, sticky=NSEW)

        # Field on s'escriuran els missatges que volgem enviar
        self.entry_field = Entry(self.finestra)
        self.entry_field.bind("<Return>", self.envia)  # funció que es realitzara si apretam la lletra enter
        self.entry_field.grid(column=0, row=2, columnspan=3, sticky=EW, padx=5, pady=10)

        # Boto per enviar el missatge
        envia_button = Button(self.finestra, text="envia", command=self.envia, width=20)
        envia_button.grid(column=3, row=2, padx=5, pady=10)

        # funcio que es fera si es tanca la finestra del client
        self.finestra.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.finestra.grid_columnconfigure(0, weight=1)
        self.finestra.grid_rowconfigure(0, weight=1)

    def connect(self):
        try:  # intentam connectar amb el servidor
            self.ADDR = toastGetHostPort()#Finestra visual per a poder escollir el host i el port
            self.client_socket = socket(AF_INET, SOCK_STREAM)#Creació del soket de client
            self.client_socket.connect(self.ADDR)#Connecció amb el soket del servidor

        except Exception:#si no troba la direccio a la qual ens volem connectar torna false
            print("C: No sha pogut connectar amb el servidor")
            return FALSE
        return TRUE

    def handleMissatge(self):
        #Thread que es dedica a escoltar al servidor i decodificar la informació que li arriba des del servidor.
        try:
            while self.get_missatge():
                pass
            self.tancarconnexio()#Funció que tanca la conexio amb el servidor

        except Exception:
            print("C: ++ Error handleMissatge")

        print("C: Exit handleMissatge")

    def get_missatge(self):
        msg = self.client_socket.recv(1024).decode("utf8")#espera un missatge del servidor i decodifica
        if len(msg) == 0:#si el misatge esta buit significa que la connexió sha perdut i es tanca el soket
            return False

        #Es cambia l'estat del misagList per a poder introduit el nou misatge rebut
        self.msg_list.configure(state='normal')

        tag = msg.split(':~:')#es separa el missatge i depenen del tag inicial s'escolleix l'acció a realitzar
        if tag[0] == "s-info":#mostra un misatge en informatiu negre rebut per el servidor
            self.msg_list.insert(END, tag[1] + "\n")
        elif tag[0] == "new_canal":#es crea un nou canal i s'introdueix al dropdown
            self.canals.append(tag[1])
            menu = self.drop_down["menu"]
            menu.delete(0, "end")
            for string in self.canals:
                menu.add_command(label=string,
                                 command=lambda value=string: self.canal.set(value) and self.setCanal)
            self.msg_list.insert(END, "S'ha creat un nou canal." + "\n")
        elif tag[0] == "quit":#es tanca la conexio amb el servidor
            return False
        elif tag[0] == "set_canal":#Sinicialitza la llista de canals que disposa el servidor
            canals = tag[1].split(',')
            for canal in canals:
                if canal != '':
                    self.canals.append(canal)
            menu = self.drop_down["menu"]
            menu.delete(0, "end")
            for string in self.canals:
                menu.add_command(label=string,
                                 command=lambda value=string: self.canal.set(value) and self.setCanal)
        elif tag[0][-6:] == "direct":#S'introdueix el tag del emisor en blau per indicar que es un misatge privat
            print(tag[0][:-6])
            self.msg_list.insert(END, tag[0][:-6] + ':', tag[0])
            self.msg_list.insert(END, tag[1] + "\n")
            self.msg_list.tag_config(tag[0], foreground='blue')
        elif tag[0] == "video":#S'inicialitza una nova connexió on e mostrara un video
            self.getSenderVideo(tag[1])
        else:#Es rep un misatge normal i corrent
            self.msg_list.insert(END, tag[0] + ':', tag[0])
            self.msg_list.insert(END, tag[1] + "\n")
            self.msg_list.tag_config(tag[0], foreground='green')

        self.msg_list.configure(state='disabled')# es desactica l'edició del msg-List
        return True

    def envia(self, event=None):
        try:  # Funció per enviar un missatge al servidor
            msg = self.entry_field.get()
            self.entry_field.delete(0, END)
            if msg == "quit":#si el misatge es quit es tanca la connexió amb el servidor
                self.tancarconnexio()
            else:#sino es codifica i s'envia
                self.client_socket.send(msg.encode("utf-8"))
        except OSError:
            print("C: ++ Error Envia")

    def nouCanal(self):#S'envia el nom del nou canal al servidor
        msg = "_NEW_CANAL_:~:%s" % toastNewCanal()
        self.client_socket.send(msg.encode("utf-8"))

    def setCanal(self):#S'envia el canal escollit al servidor per a poder formar part d'ell
        msg = "_SET_CANAL_:~:%s" % self.canal.get()
        self.client_socket.send(msg.encode("utf-8"))

    def error_mesage(self, msg):
        try:  # funcio per mostrar algun missatge d'error vermell per el Box
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

    def tancarconnexio(self):#tanca la connexio mab el soket del servidor
        self.error_mesage("S'ha tancat la connexió amb el servidor")
        self.client_socket.close()
        print("C: Soket Client tancat")

    def exit(self):#tanca la finestra visual
        # self.finestra.quit()
        self.finestra.destroy()

    # ------------------ Striming de Viceo -----------------
    def getSenderVideo(self, video):#inicialitza un nou thread amb el seu pertinent soket el qual es connectara amb
        # el servidor por a poder veure un video en straming
        self.isVideo = True
        Thread(target=self.reciver.inici([self.ADDR[0], 5050, video])).start()

    def buttonNewVideo(self):
        #si no hi ha cap video s'en creara un de nou i sino es tancara
        if self.isVideo:
            self.isVideo = False
            self.reciver.stopVideo()
        else:
            self.isVideo = True
            msg = '_SET_VIDEO_:~:' + toastNewVideo()
            self.client_socket.send(msg.encode("utf-8"))
