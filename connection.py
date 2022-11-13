# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
import os
import base64

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        # FALTA: Inicializar atributos de Connection
        self.my_socket = socket
        self.directory = directory
        self.buffer = ''
        self.connected = True
        self.bufferout = ''

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        acept_commands = ["quit", "get_slice", "get_file_listing", "get_metadata"]
        while self.connected:
            data = self.my_socket.recv(4096).decode("ascii")
            ctrl_c = data.split(' ')[0]
            print(ctrl_c)

            if ctrl_c == '\xff\xf4\xff\xfd\x06':
                self.bufferout = "anda"
                self.send()
            else:
                self.buffer += data
                index = self.buffer.find('\n')
                if index != -1:
                    if self.buffer[index -1] != '\r':
                        self.bufferout = "%s %s" %\
                                            (BAD_EOL,\
                                            error_messages[BAD_EOL]) + EOL
                        self.send()

                if EOL in self.buffer:
                    command = self.buffer.split(EOL, 1)[0]
                    self.buffer = self.buffer.split(EOL, 1)[1]
                    command = command.split(' ')
                    command = [x for x in command if x != '']
                    command = [x for x in command if x != '\t']
                    command = [x.strip('\t') for x in command]

                    if command[0] == 'quit':
                        if len(command) == 1:
                            self.quit()
                        else:
                            self.bufferout = "%s %s" %\
                                                (INVALID_ARGUMENTS,\
                                                error_messages[INVALID_ARGUMENTS]) + EOL
                            self.send()
                    elif command[0] == 'get_file_listing':
                        if len(command) == 1:
                            if( os.path.isdir(DEFAULT_DIR)):
                                self.get_file_listing()
                            else:
                                os.mkdir(DEFAULT_DIR)
                                self.get_file_listing()
                        else:
                            self.bufferout = "%s %s" % INVALID_ARGUMENTS,error_messages[INVALID_ARGUMENTS] + EOL
                            self.send()
                    elif command[0] == 'get_metadata':
                        length = len(command)
                        if length < 2 or length > 2:
                            self.bufferout = "%s %s" %\
                                                (INVALID_ARGUMENTS,\
                                                error_messages[INVALID_ARGUMENTS]) + EOL
                            self.send()
                        elif length == 2 and os.path.isfile(self.directory + '/' + command[1]):
                            size_file = len(command[1])
                            if size_file > 15:
                                self.bufferout = "%s %s" % (INVALID_ARGUMENTS,\
                                                error_messages[INVALID_ARGUMENTS]) + EOL
                                self.send()
                            else:
                                self.get_metadata(command[1])
                        else:
                            self.bufferout = "%s %s" % (FILE_NOT_FOUND,\
                                                error_messages[FILE_NOT_FOUND]) + EOL
                            self.send()
                    elif command[0] == 'get_slice':
                        length = len(command)
                        if(os.path.isfile(self.directory + '/' + command[1]) != True):
                            self.bufferout = "%s %s" % (FILE_NOT_FOUND,\
                                                        error_messages[FILE_NOT_FOUND]) + EOL
                            self.send()

                        elif length == 4:
                            size_file = len(command[1])
                            if size_file > 15:
                                self.bufferout = "%s %s" % (INVALID_ARGUMENTS,\
                                                error_messages[INVALID_ARGUMENTS]) + EOL
                                self.send()
                            else:
                                try:
                                    print(len(command))
                                    print(command[1])
                                    print(int(command[2]))
                                    print(int(command[3]))
                                    self.get_slice(command[1], int(command[2]),\
                                                   int(command[3]))
                                except:
                                    self.bufferout = "%s %s" % (INVALID_ARGUMENTS,\
                                                                error_messages[INVALID_ARGUMENTS]) + EOL
                                    self.send()
                        else:
                            self.bufferout = "%s %s" % (INVALID_ARGUMENTS,\
                                                error_messages[INVALID_ARGUMENTS]) + EOL
                            self.send()
                    elif any(command[0] in s for s in acept_commands):
                        self.bufferout = "%s %s" % (INVALID_ARGUMENTS,\
                                                    error_messages[INVALID_ARGUMENTS]) + EOL
                        self.send()
                    else:
                        self.bufferout = "%s %s %s" %\
                                            (INVALID_COMMAND,\
                                            error_messages[INVALID_COMMAND], EOL) + EOL
                        self.send()
    def send(self):
        #self.my_socket.settimeout(timeout)
        #self.bufferout += EOL
        while self.bufferout:
            bytes_sent = self.my_socket.send(self.bufferout.encode("ascii"))
            assert bytes_sent > 0
            self.bufferout = self.bufferout[bytes_sent:]
    def quit(self):
        """
        Este comando no recibe argumentos y busca terminar laconexión. El
        servidor responde con un resultado exitoso (0 OK) y luego
        cierra la conexión.
        """
        self.connected = False
        self.bufferout = "%s %s %s" % (CODE_OK, error_messages[CODE_OK], EOL)
        self.send()
        self.my_socket.close()

    def get_file_listing(self):
        """
        Este comando busca listar los archivos en ekl servidor y enviarlos al cliente
        """
        self.bufferout = "%s %s %s" % (CODE_OK,error_messages[CODE_OK], EOL)
        self.send()
        try:
            self.bufferout = '\r\n'.join(os.listdir(self.directory)) + "\r\n" + EOL
            self.send()
        except:
            self.bufferout = "%s %s %s" % (FILE_NOT_FOUND,error_messages[FILE_NOT_FOUND], EOL)
            self.send()


    def get_metadata(self, filename):
        """
        Este comando recibe un argumento FILENAME especificando un
        nombre de archivo del cual se pretende averiguar el tamaño . El
        2
        servidor responde con una cadena indicando su valor en bytes.
        """
        self.bufferout = "%s %s %s" % (CODE_OK,error_messages[CODE_OK], EOL)
        self.send()
        try:
            self.bufferout = "%d" % os.stat(self.directory + '/' + filename).st_size + EOL
            self.send()
        except:
            self.bufferout = "%s %s %s" % (FILE_NOT_FOUND,error_messages[FILE_NOT_FOUND], EOL)
            self.send()

    def get_slice(self, file, offset, size):
        """
        Este comando recibe en el argumento FILENAME el nombre dearchivo del
        que se pretende obtener un slice o parte. La parte seespecifica con un
        OFFSET (byte de inicio) y un SIZE (tamaño de laparte esperada, en
        bytes), ambos no negativos. El servidor3responde con el fragmento de
        archivo pedido codificado enbase64 y un \r\n.
        """
        toread = open(os.path.join(self.directory,file), "rb")
        toread.seek(offset)
        res = toread.read(size)
        toread.close()
        self.bufferout = "%s %s %s" % (CODE_OK,error_messages[CODE_OK], EOL)
        self.send()
        self.bufferout = "%s %s" % (base64.b64encode(res).decode("ascii"), EOL)
        self.send()

        """
        try:
            file_content = open(self.directory + '/' + file).readline().encode()
            self.my_socket.send(file_content[offset:size])
            self.bufferout = "%s %s %s" % (CODE_OK,error_messages[CODE_OK], EOL)
            self.send()
        except:
            self.bufferout = "%s %s %s" % (FILE_NOT_FOUND,error_messages[FILE_NOT_FOUND], EOL)
            self.send()
        """
