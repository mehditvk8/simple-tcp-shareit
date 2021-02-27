import socket
import datetime
import json
import os
import hashlib


class Log:
    def __init__(self, log_file_name="report.log"):
        self.__log_file_name = log_file_name

    def print_log(self, msg):
        log_file = open(self.__log_file_name, "a+")
        time = str(datetime.datetime.now())
        log_file.write(time + ": " + msg + "\n")
        log_file.close()

    def set_file_name(self, name):
        self.__log_file_name = name

    def get_file_name(self):
        return self.__log_file_name


class Config:

    def __init__(self, config_file=None):
        if config_file is None:
            self.__config_file = "config.json"

        else:
            try:
                self.__config_file = config_file
                self.__ip = self.load("ip")

            except KeyError:
                print("can not reading configs")
                exit(1)

    def load(self, name):
        try:
            cnf_file = open(self.__config_file, "r")
            cntnt = json.load(cnf_file)
            cnf_file.close()
            return cntnt[name]
        except Exception:
            print("can not load config file")
            exit(1)

    def get__config_file(self):
        return self.__config_file

    def set__config_file(self, name):
        self.__config_file = name

    def set_item(self, key, value):

        cnf_file = open(self.__config_file, "r")
        inf_dict = json.load(cnf_file)
        cnf_file.close()

        inf_dict[key] = value

        cnf_file = open(self.__config_file, "w")
        json.dump(inf_dict, cnf_file)
        cnf_file.close()


log = Log()
config = Config()


def hashf(filename):
    hasher = hashlib.md5()

    with open(filename, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)

    return hasher.hexdigest()


def hasht(content):
    hash_object = hashlib.md5(content)
    return hash_object.hexdigest()


class FTServer:
    def __init__(self):
        self.__ip = config.load("ip")
        self.__port = config.load("port")
        self.__file_name = config.load("filename")
        self.__dl_dir = config.load("dldir")

    def run(self):
        ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ser.bind((self.__ip, 0))
        self.binded_port = ser.getsockname()[1]
        self.address = self.__ip + ":" + str(self.binded_port)
        config.set_item("port", self.binded_port)
        print("server is run at ", self.address)
        log.print_log("server is run at " + self.address)
        ser.listen(5)

        return ser

    def recvf(self, client):
        file_inf = client.recv(4096).decode()
        filename = file_inf.split("/")[0]

        if filename:
            sent_fsize = file_inf.split("/")[1]
            sent_fhash = file_inf.split("/")[2]
            config.set_item("filename", filename)
            print("downloading " + filename + " with size " + sent_fsize + " from " + self.address)
            log.print_log("downloading " + filename + "with size " + sent_fsize + " Byte from " + self.address)
            try:
                recv_file = open(self.__dl_dir + "/" + filename, "wb+")
            except FileNotFoundError:
                log.print_log("can not find download destination directory.")
                exit(1)

            while True:
                err_time = 0
                recv_content = client.recv(4096)

                if not recv_content:
                    break

                client.send(hasht(recv_content).encode())
                stat = client.recv(2).decode()

                while stat == "er":
                    log.print_log("There is an error.")
                    recv_content = client.recv(4096)
                    client.send(hasht(recv_content).encode())
                    stat = client.recv(2).decode()
                    err_time += 1

                    if err_time == 5:
                        print("There is problem in downloading file.")
                        client.close()
                        break

                if err_time == 5:
                    break

                recv_file.write(recv_content)

            recv_file.close()
            recv_fsize = os.path.getsize(self.__dl_dir + "/" + filename)
            recv_fhash = hashf(self.__dl_dir + "/" + filename)

            if int(sent_fsize) == recv_fsize and recv_fhash == sent_fhash:
                print("file downloaded completely")
                log.print_log("file downloaded completely")

            else:
                log.print_log("there is an error in downloading file")
                print("there is an error in downloading file")
                print(recv_fhash, recv_fsize, sent_fhash, sent_fsize)

    def main(self):

        server = self.run()

        while True:
            print("waiting for clients...\n")
            conn, cli_addr = server.accept()
            client_addr = cli_addr[0] + ":" + str(cli_addr[1])
            print(client_addr + " connected to the server")
            log.print_log(client_addr + " connected to the server")
            self.recvf(client=conn)
            log.print_log("client left")
            print("client left")


if __name__ == "__main__":
    ft_server = FTServer()
    ft_server.main()
