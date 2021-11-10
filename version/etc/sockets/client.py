# 소켓을 사용하기 위해서는 socket을 import해야 한다.
import socket
import time
# 로컬은 127.0.0.1의 ip로 접속한다.
HOST = '127.0.0.1'
# port는 위 서버에서 설정한 9999로 접속을 한다.
PORT = 1010
# 소켓을 만든다.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect함수로 접속을 한다.
client_socket.connect((HOST, PORT))
# 10번의 루프로 send receive를 한다.
for i in range(1,10):

# 메시지는 hello로 보낸다.
    msg = 'hello'
    # 메시지를 바이너리(byte)형식으로 변환한다.
    data = msg.encode()
    # 메시지 길이를 구한다.
    length = len(data)
    # server로 리틀 엔디언 형식으로 데이터 길이를 전송한다.
    client_socket.sendall(length.to_bytes(4, byteorder="little"))
    print(i)
    time.sleep(5)
    # 데이터를 전송한다.
    client_socket.sendall(data)
    # server로 부터 전송받을 데이터 길이를 받는다.
    data = client_socket.recv(4)
    # 데이터 길이는 리틀 엔디언 형식으로 int를 변환한다.
    length = int.from_bytes(data, "little")
    # 데이터 길이를 받는다.
    data = client_socket.recv(length)
    # 데이터를 수신한다.
    msg = data.decode()
    # 데이터를 출력한다.
    print('Received from : ', msg)
    # 언제 socket 클로즈 할 지 정하기
    # client_socket.close()
