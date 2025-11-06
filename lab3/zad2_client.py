from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from multiprocessing import Pool

import socket
import pickle


def sobel_filter(image):
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)
    Ky = np.array([[-1, -2, -1],
                   [0, 0, 0],
                   [1, 2, 1]], dtype=np.float32)

    Gx = cv2.filter2D(image, cv2.CV_32F, Kx)
    Gy = cv2.filter2D(image, cv2.CV_32F, Ky)

    magnitude = cv2.magnitude(Gx, Gy)

    result = cv2.convertScaleAbs(magnitude)
    return result


def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')
    data = b''
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet
    return pickle.loads(data)


def send_all(sock, data):
    data = pickle.dumps(data)
    sock.sendall(len(data).to_bytes(4, byteorder='big'))
    sock.sendall(data)


def client_main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 2040))

    fragment = receive_all(client_socket)
    processed_fragment = sobel_filter(fragment)
    send_all(client_socket, processed_fragment)

    client_socket.close()
    print("Fragment przetworzony i wysłany z powrotem do serwera")


client_main()
