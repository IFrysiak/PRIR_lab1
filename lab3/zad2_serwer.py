from PIL import Image
import socket
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pickle


def server_main(img_path, n_clients):
    image = Image.open(img_path).convert("L")
    img_np = np.array(image)
    fragments = np.array_split(img_np, n_clients)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to '0.0.0.0' to listen on all available interfaces
    server_socket.bind(('0.0.0.0', 2040))
    server_socket.listen(n_clients)

    print("Serwer nasłuchuje...")

    processed_fragments = []

    for i in range(n_clients):
        client_socket, client_address = server_socket.accept()
        print(f"Połączono z klientem {i + 1}: {client_address}")

        send_all(client_socket, fragments[i])
        processed_fragment = receive_all(client_socket)
        processed_fragments.append(processed_fragment)

        client_socket.close()

    # Assuming result_image should be a PIL Image to save
    # result_image = Image.fromarray(np.vstack(processed_fragments))
    # result_image.save("processed_image.png")
    print("Obraz przetworzony zapisany jako processed_image.png")

    # Correcting the imshow call to display the combined image
    plt.imshow(np.vstack(processed_fragments), cmap='gray')
    # plt.axis('off')
    plt.show()


def send_all(sock, data):
    data = pickle.dumps(data)
    data_length = len(data)

    sock.sendall(data_length.to_bytes(4, byteorder='big'))

    sock.sendall(data)


def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')

    data = b''
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet

    return pickle.loads(data)


img_path = "bird.jpg"
server_main(img_path, 4)
