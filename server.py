import socket
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

HOST = "127.0.0.1"
PORT = 65431

p = 8371433218848358145038188834376952780015970046874950635276595345380605659774957836526221018721547441806561287602735774125878237978059976407232379361297183
q = 11466377869587829648871708469119992174705652479796097233499813683057983019116298140412758762054846456284362676185136356912754651085919371755263313171141577
n = p * q
phi = (p - 1) * (q - 1)
e = 65537
d = pow(e, -1, phi)
k = 128
cipher = PKCS1_v1_5.new(RSA.construct((n, e, d)))
sentinel = b"\x00" * k


def _valid_padding_v1_5(cipher, k, c, sentinel):
    return cipher.decrypt(c.to_bytes(k, byteorder="big"), sentinel) != sentinel


def _start_server_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print(f"Listening on {HOST}:{PORT}")
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"[OK] Connection from {addr} established")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("[OK] Received: ", data.decode())

                response = f"{e},{n}"
                conn.sendall(response.encode())
                print("[OK] RSA parameters sent")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print(f"\nListening on {HOST}:{PORT}")
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"[OK] Connection from {addr} established")
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                m = cipher.decrypt(data, sentinel)
                print(f"Decrypted message: \"{m.decode()}\"")


def _start_server_attacker():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, 9999))
    server.listen()
    print(f"\nListening on {HOST}:9999")
    while True:
        client_socket, addr = server.accept()
        print(f"[OK] Connection from {addr} established")

        ciphertext = int.from_bytes(client_socket.recv(256), byteorder='big')
        padding_valid = _valid_padding_v1_5(cipher, k, ciphertext, sentinel)
        client_socket.send(b'1' if padding_valid else b'0')
        client_socket.close()


def main():
    option = input("Choose: \n(0) - Start Server Client\n(1) - Start Server Attacker\n")

    if option == '0':
        _start_server_client()
    elif option == '1':
        _start_server_attacker()
    else:
        return


if __name__ == "__main__":
    main()
