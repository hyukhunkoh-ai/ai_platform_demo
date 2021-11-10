######### thread.start, queue - put, task_done, join
# 쓰레드를 사용하기 위해서는 threading 모듈을 import해야 한다.
# queue를 사용하기 위해서 queue를 import해야 한다.
# time 모듈은 Thread 상에서 처리를 잠시 멈추게 하는 기능이 있다.
import queue
import threading

# work로 Queue를 생성헀다.
# Queue란 Fifo의 구조의 자료형으로 put으로 넣은 데이터 순서대로 get을 통해 데이터가 나오는 구조체이다.
work = queue.Queue();


# generator함수에서 queue에 1부터 10까지 데이터를 넣었다.
def generator(start, end):
    for i in range(start, end, 1):
        work.put(i);


# 출력은 queue가 빌때까지 루프를 통해서 데이터를 취득한다.
def display():
    while work.empty() is False:
        data = work.get();
        print("data is " + str(data));
        # 1초 단위로 루프를 멈춘다.
        time.sleep(1);
        work.task_done();


# 두개의 쓰레드에 두개이 처리를 넣었다.
# 쓰레드에서 함수를 호출할 때 파라미터는 args로 넣을 수 있다.
threading.Thread(target=generator, args=(1, 10)).start();
threading.Thread(target=display).start();
work.join();


###### 결과값의 중복을 원한다면 lock 쓰기 단 deadlock 조심
import threading, time;

data = 0;
# 쓰레드의 Lock를 가져온다.
lock = threading.Lock();


def generator(start, end):
    global data;
    for i in range(start, end, 1):
        # lock이 설정된 이상 다음 이 lock를 호출할 때 쓰레드는 대기를 한다.
        lock.acquire();
        buf = data;
        time.sleep(0.01);
        # data 값을 1씩 증가
        data = buf + 1;
        # 사용이 끝나면 lock 해제한다.
        lock.release();


# generator함수를 두개의 쓰레드로 실행했다.
t1 = threading.Thread(target=generator, args=(1, 10));
t2 = threading.Thread(target=generator, args=(1, 10));
# 쓰레드 시작
t1.start();
t2.start();
# 쓰레드가 종료할 때까지 대기
t1.join();
t2.join();

print(data);
