import socket
import threading
import time

def send_message(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(message.encode('gbk'))

def send_message_every_second(ip, port, message):
    while True:
        send_message(ip, port, message)
        time.sleep(2)

ip1 = "172.17.0.2"
ip2 = "172.17.0.3"
port = 8000

thread1 = threading.Thread(target=send_message_every_second, args=(ip1, port, "(Client1) message from client 1"))
thread2 = threading.Thread(target=send_message_every_second, args=(ip2, port, "(Client1) message from client 1"))

thread1.start()
thread2.start()

thread1.join()
thread2.join()