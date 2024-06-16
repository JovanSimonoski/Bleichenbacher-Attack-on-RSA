import socket
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

HOST = "127.0.0.1"
PORT = 65431


def _exchange_key():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("[OK] Successfully connected to server")
        s.sendall(b"Hello")
        data = s.recv(1024)
        print("[OK] RSA parameters received")
        return data.decode()


def _send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("\n[OK] Successfully connected to server")
        s.sendall(message)
        print("[OK] Successfully sent message to server")


def _start_client():
    data = _exchange_key()
    values = data.split(',')
    e = int(values[0])
    n = int(values[1])

    print(f"\ne = {e}")
    print(f"n = {n}")

    cipher = PKCS1_v1_5.new(RSA.construct((n, e)))

    original_message = "SECRET: DwHGh3gEIUa12d3DssNaU32JDN2O"
    print(f"\nOriginal message: \"{original_message}\"")

    cipher_text = cipher.encrypt(original_message.encode())
    c = int.from_bytes(cipher_text, byteorder='big')

    print(f"c = {c}")

    _send_message(cipher_text)


if __name__ == "__main__":
    _start_client()
