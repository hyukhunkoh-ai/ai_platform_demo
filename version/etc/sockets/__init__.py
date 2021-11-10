# -*- coding: utf-8 -*-
import socket
#소켓 생성할 때 socket.AF_INET와 socket.SOCK_STREAM를 사용했는데 socket.AF_INET는 IP4인터넷을 사용한다는 뜻이고 데이터를 바이너리(byte 스트림)식으로 사용한다는 뜻입니다.


class HHsocket():

    def __init__(self, args=None):
        self.args = args

    #server
    def listen(self, ip, port, listen_num=5):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, int(port))

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(server_address)
        except Exception as e:
            print("binding error: ", e)
            return None

        sock.listen(listen_num)

        return sock
    

    #client
    def connect(self, ip, port):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (ip, int(port))

        try:
            sock.connect(addr)
        except Exception as e:
            print("failed to connect")
            return None

        return sock
    #전송
    def send(self, conn, dat):

        # 데이터 utf-8 인코딩
        dat = dat.encode('utf-8')

        # 길이 정보 4바이트 송신
        length = len(dat)
        ret = conn.sendall(length.to_bytes(4, byteorder='little'))
        if ret is not None:
            return False

        # 페이로드 데이터 송신
        ret = conn.sendall(dat)
        if ret is not None:
            return False

        return True

    # 메시지 수신시 길이 만큼 받는 함수(recv - 보조격)
    def recvall(self, conn, n):
        # Helper function to recv n bytes or return None if EOF is hit
        dat = bytearray()
        while len(dat) < n:
            packet = conn.recv(n - len(dat))
            if not packet:
                return None
            dat.extend(packet)
        return dat

    # 메시지 수신
    def recv(self, conn):

        # 길이 정보 4바이트 수신
        length_bytes = conn.recv(4)
        if len(length_bytes) == 0:
            return False, None
        length = int.from_bytes(length_bytes, byteorder='little')

        # 페이로드 데이터 수신
        dat = self.recvall(conn, length).decode('utf-8')
        if len(dat) == 0:
            return False, None

        return True, dat

    def close(self, conn):
        conn.close()