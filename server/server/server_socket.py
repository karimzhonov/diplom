import socket
import pickle
from threading import Thread

PASSWORD = '9009'


def check_password(conn: socket.socket):
    try:
        conn.send(b'Password: ')
        answer = conn.recv(4096).decode()
        if answer == PASSWORD:
            conn.send('1'.encode())
            return True
        else:
            conn.send('0'.encode())
            return False
    except ConnectionResetError:
        return False


def client_accept(conn, addr):
    print('Client: ', addr)
    _flag = check_password(conn)
    print('Client: ', addr, ', Password is ', _flag)
    while _flag:
        try:
            answer = conn.recv(4096)
            face_enc = pickle.loads(answer)
            if face_enc:

                conn.send(b'1')
            else:
                conn.send(b'0')

        except ConnectionResetError:
            break
    else:
        print('Password error')
    conn.close()


def main():
    HOST = 'localhost'
    PORT = 5555
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    while True:
        connection, address = s.accept()
        Thread(target=client_accept, args=(connection, address)).start()


if __name__ == '__main__':
    main()
    
