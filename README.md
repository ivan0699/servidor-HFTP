Informe de Laboratorio n° 2: Un servidor concurrente para HFTP
======

Alumnos:
----
* Beckford, Mauricio Mermán
* Bettinotti, Ivan Matias
* Menendez, Hilario Iñigo
_____

# Introducción

Este trabajo tiene como objetivo implementar un programa servidor de archivos en
Python3 que sea mínimamente robusto a la hora de manejar unos pocos comandos. El
mismo es una versión simplificada de ftp que llamaremos HFTP.

# Implementación

Para lograr nuestro objetivo, trabajamos a partir de un esqueleto otorgado por
la cátedra y el elaborado en el proyecto anterior, en el cual debíamos modificar
los módulos 'server.py' y 'connection.py' para realizar la conexión y las tareas
de recibir, procesar y enviar respuestas al cliente. Esta implementación
consiste en una clase Server que se encarga de crear las conexiones mediante
hilos, lo que permite que hayan múltiples usuarios conectados al servidor
simultáneamente. Otra clase es la Connection, en ella se maneja los comandos que
llegan desde el cliente (La clase Client se encontraba implementada con
anterioridad), es este método es donde se optó por manejar la mayoría de las
validaciones de los comando. Ademas, en Connection, se encuentran implemetados
los comandos (quit, get_file_listing, get_metadata y get_slice) que se requerían

La principal complicación fue darse cuenta de los posibles errores, pero los
test que se nos fueron buena guía para resolver esto.
