from tkinter import *
from tkinter import ttk

# mostra el misatge enviat amb un toast de forma visual
def mostrarToast(titol, msg):
    popup = Tk()
    popup.title(titol)
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10, padx=10)
    b1 = ttk.Button(popup, text="Okey", command=popup.destroy)
    b1.pack(side="bottom", fill="x", pady=10, padx=10)


host = "toni"
port = 0


def enviaHostPort(finestra, h, p):
    global host
    global port
    host = h.get()
    try:
        x = int(p.get())
        port = x
        if port < 1000:
            mostrarToast("ERROR", "El port ha de tenir 4 digits")
        else:
            finestra.quit()
            finestra.destroy()
    except:
        mostrarToast("ERROR", "El port ha de ser un enter")

def toastGetHostPort():
    arrel = Tk()
    arrel.resizable(width=False, height=False)
    arrel.title("Init Servidor")

    # HOST
    Label(arrel, text="Host: ").grid(column=1, row=1, columnspan=3, sticky=E)
    host_entry = Entry(arrel, width=35)
    host_entry.grid(column=4, row=1, pady=10, padx=5, sticky=(W, E))

    # PORT
    Label(arrel, text="Port: ").grid(column=1, row=3, columnspan=3, sticky=E)
    port_entry = Entry(arrel, width=35)
    port_entry.grid(column=4, row=3, pady=10, padx=5, sticky=(W, E))

    # Botón
    Button(arrel, text="Iniciar", command=lambda: enviaHostPort(arrel, host_entry, port_entry))\
        .grid(column=1, row=5,columnspan=8,sticky=(W, E))

    host_entry.insert(END, 'localhost')
    port_entry.insert(END, '1613')

    arrel.mainloop()
    global host
    global port
    return host, port


def enviaCanal(finestra, c):
    global canal
    canal = c.get()
    if len(canal) > 0:
        finestra.quit()
        finestra.destroy()
    else:
        mostrarToast("ERROR", "El canal no pot estar buit")


def toastNewCanal() -> StringVar:
    arrel = Tk()
    arrel.resizable(width=False, height=False)
    arrel.title("NOU CANAL")

    # CANAL
    Label(arrel, text="Nou canal: ").grid(column=1, row=1, columnspan=3, sticky=E)
    host_entry = Entry(arrel, width=35)
    host_entry.grid(column=4, row=1, pady=10, padx=5, sticky=(W, E))

    # Botón
    Button(arrel, text="Crear", command=lambda: enviaCanal(arrel, host_entry))\
        .grid(column=1, row=5,columnspan=8,sticky=(W, E))

    arrel.mainloop()
    global canal
    return canal

def enviaVideo(finestra, c):
    global canal
    canal = c.get()
    if len(canal) > 0:
        finestra.quit()
        finestra.destroy()
    else:
        mostrarToast("ERROR", "El Url no pot estar buit")


def toastNewVideo() -> StringVar:
    arrel = Tk()
    arrel.resizable(width=False, height=False)
    arrel.title("iniciar video")

    # misatge
    Label(arrel, text="videos disponibles: toni.mp4\nTambe es pot introduir una url\nPer a veure la webcam del server"
                      " introdueix webcam").grid(column=1, row=0, columnspan=3, sticky=E)
    # video
    Label(arrel, text="URL: ").grid(column=1, row=1, columnspan=3, sticky=E)
    video_entry = Entry(arrel, width=35)
    video_entry.grid(column=1, row=1, pady=10, padx=5, sticky=(W, E))

    # Botón
    Button(arrel, text="Inicar", command=lambda: enviaVideo(arrel, video_entry))\
        .grid(column=1, row=5,columnspan=8,sticky=(W, E))

    arrel.mainloop()
    global canal
    return canal