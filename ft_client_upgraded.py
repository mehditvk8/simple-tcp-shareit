import socket
import json
import os
import hashlib


class Config:

    def __init__(self, config_file=None):
        if config_file is None:
            self.__config_file = "config.json"

        else:
            try:
                self.__config_file = config_file
                self.__ip = self.load("ip")
                self.__port = self.load("port")
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
            print("cant load config file")
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


class FTClient:

    def __init__(self):
        mode = input("Is your server on another system? [y/n]")

        while mode not in ("y", "n"):
            mode = input("Incorrect input. Is your server on another system? [y/n]")

        if mode == "n":
            config = Config()
            self.__ip = config.load("ip")
            self.__port = config.load("port")
        elif mode == "y":
            self.__ip = str(input("enter server ip: "))
            self.__port = int(input("enter server port: "))

    @staticmethod
    def hashf(filename):
        hasher = hashlib.md5()

        with open(filename, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)

        return hasher.hexdigest()

    @staticmethod
    def hasht(content):
        hash_object = hashlib.md5(content)
        return hash_object.hexdigest()

    def connect(self):

        try:

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.__ip, self.__port))
            print("connected to", self.__ip, ":", self.__port)

        except ConnectionRefusedError:

            print("can not connect to server")
            exit(1)

    def sendf(self):

        fpath = input("Enter your file full path: ")

        try:
            fname = fpath.split("/")[-1]
            send_file = open(fpath, "rb")
            fsize = os.path.getsize(fpath)
            finf = fname + "/" + str(fsize) + "/" + self.hashf(fpath)
            self.sock.send(finf.encode())

        except FileNotFoundError:
            print("there isnt such file")
            exit(1)

        try:
            i = 0
            while True:
                i += 1
                err_time = 0
                send_cntnt = send_file.read(4096)
                comp_hasht = self.hasht(send_cntnt)
                self.sock.sendall(send_cntnt)

                if not send_cntnt:
                    break

                recvd_hasht = self.sock.recv(4096).decode()

                while recvd_hasht != comp_hasht:

                    self.sock.send("er".encode())
                    err_time += 1
                    self.sock.sendall(send_cntnt)
                    recvd_hasht = self.sock.recv(4096).decode()

                    if not recvd_hasht:
                        print("server down")
                        break

                    if err_time == 5:
                        print("There is problem in downloading file.")
                        self.sock.close()
                        break

                if err_time == 5:
                    break

                self.sock.send("ok".encode())

        except (BrokenPipeError, ConnectionRefusedError):
            print("server down")
            send_file.close()

            if err_time != 5:
                print("uploading is end")

    def main(self):
        self.connect()
        self.sendf()
        self.sock.close()


if __name__ == "__main__":
    ft_client = FTClient()
    ft_client.main()
