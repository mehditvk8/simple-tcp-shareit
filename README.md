# simple-tcp-shareit
It is a simple file transfer program with tcp protocol using python 3 socket.
In this program, client can connect to server and send file from client system to server.
also it has the good features that check if the file transfered correctly or not.

## manual
For use it after download and unzip the files,open `config.json` file in server system. then copy the full path of the directory you want to download your file over there.then set it to value of the **dldir** in config file.then  run `server.py` in server system.
after that run the `client.py` in client system. after run client program you see an input message that you should select if your client and server system are same or not.
if your client and server system are diffrent enter **y** for yes. then enter the ip and port of your system and start use the program.you can read port from server program.


**Note**: you can access each system **ip** with [this manual](https://www.dnsstuff.com/scan-network-for-device-ip-address)

### install reqired packages
on this program I use socket,threading and json packages if you dont have them you can install them using pip:

**windows**
```bash
pip install socket
```

**linux**
```bash
pip3 install socket
```

## help

**thank you if report me bugs and help me develop it.**

