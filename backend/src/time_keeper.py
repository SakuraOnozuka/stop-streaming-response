import signal
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from time import sleep


class TimeKeeperThread(Thread):
    def __init__(self):
        super(TimeKeeperThread, self).__init__()
        self.exit_flag: bool = True
        self.N: int = 5
        self.sleep_t: int = 3

    def run(self) -> None:
        while self.exit_flag:
            sleep(self.sleep_t)
            time = datetime.now()
            print("time_record_1")
            with open('./sample/test_thread.txt', 'w') as f:
                f.write("time_recorded_thread_1: ")
                f.write(str(time))
                f.write("\n")
                f.write(str(self.exit_flag))
                f.write("\n")

            for i in range(self.N - 1):
                sleep(self.sleep_t)
                print(f"time_record_{i + 2}")
                time = datetime.now()
                with open('./sample/test_thread.txt', 'a') as f:
                    f.write(f"time_recorded_thread_{i + 2}: ")
                    f.write(str(time))
                    f.write("\n")
                    f.write(str(self.exit_flag))
                    f.write("\n")

    def terminate(self):
        self.exit_flag = False


class TimeKeeperProcess(Process):
    def __init__(self):
        super(TimeKeeperProcess, self).__init__()
        self.exit_flag: bool = True
        self.N: int = 5
        self.sleep_t: int = 3

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self.terminate_time_keeping)  # ハンドラを設定
        signal.signal(signal.SIGINT, self.terminate_time_keeping)  # ハンドラを設定
        while self.exit_flag:
            sleep(self.sleep_t)
            time = datetime.now()
            print("time_record_1")
            with open('./sample/test_process.txt', 'w') as f:
                f.write("time_recorded_process_1: ")
                f.write(str(time))
                f.write("\n")
                f.write(str(self.exit_flag))
                f.write("\n")

            for i in range(self.N - 1):
                sleep(self.sleep_t)
                print(f"time_record_{i + 2}")
                time = datetime.now()
                with open('./sample/test_process.txt', 'a') as f:
                    f.write(f"time_recorded_process_{i + 2}: ")
                    f.write(str(time))
                    f.write("\n")
                    f.write(str(self.exit_flag))
                    f.write("\n")

    def terminate_time_keeping(self, __, _):
        self.exit_flag = False
