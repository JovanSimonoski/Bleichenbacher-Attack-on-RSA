import socket
import bleichenbacher_attack

HOST = "127.0.0.1"
PORT = 65431

k = 128
sentinel = b"\x00" * k


def padding_oracle(ciphertext):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 9999))
    s.send(ciphertext)
    response = s.recv(1)
    s.close()
    return response == b'1'


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')


# Modify padding_oracle to convert integer to bytes
def padding_oracle_int(ciphertext_int):
    ciphertext_bytes = int_to_bytes(ciphertext_int)
    return padding_oracle(ciphertext_bytes)


def _exchange_key():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("[OK] Successfully connected to server")
        s.sendall(b"Hello")
        data = s.recv(1024)
        print("[OK] RSA parameters received")
        return data.decode()


def _start_attacker():
    data = _exchange_key()
    values = data.split(',')
    e = int(values[0])
    n = int(values[1])

    print(f"\ne = {e}")
    print(f"n = {n}")

    c = int(input("\n\nInsert cipher: "))

    m_ = bleichenbacher_attack.attack(padding_oracle_int, n, e, c)

    print("\nAttack completed.")
    print("\nRecovered message (integer):", m_)

    decrypted_bytes = m_.to_bytes((m_.bit_length() + 7) // 8, byteorder='big')

    padding_end_index = decrypted_bytes.find(b'\x00', 2)
    if padding_end_index != -1:
        print('\n' + decrypted_bytes[padding_end_index + 1:])


if __name__ == "__main__":
    _start_attacker()
