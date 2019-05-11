# **README**


Per executar el projecte S'ha d'introduir la seguent comanda: python3.7 ./MainChat.py
El projecte en divideix en 4 parts:

Main: es el projecte principal el qual executa els threads del servidor i el client per tal de poder crear-ne tants com és vulguin.

Servidor: encarregat de crear una connexió de fins a 10 clients i de tancar totes les connexions amb els clients una vegada es tanca l'aplicació.
també disposa d'un thread que espera entrades del terminal per a llistar els clients connectats i aturar el servidor

Client: es connecta amb el servidor al port i host donats.

Commons: disposa d'un parell de funcions les quals són usades per totes les classes anteriors