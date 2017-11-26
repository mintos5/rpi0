import sys
import getopt
import asyncio
import websockets
import json


class Application:

    def __init__(self):
        self.keyboard_name = '/dev/hidg0'
        self.mouse_name = '/dev/hidg1'
        self.keyboard_file = None
        self.mouse_file = None

    keyboard_string, keyboard_symbol, mouse = range(3)

    hid_shift = 0x02

    hid_basic = {
        "a": 0x04,
        "b": 0x05,
        "c": 0x06,
        "d": 0x07,
        "e": 0x08,
        "f": 0x09,
        "g": 0x0a,
        "h": 0x0b,
        "i": 0x0c,
        "j": 0x0d,
        "k": 0x0e,
        "l": 0x0f,
        "m": 0x10,
        "n": 0x11,
        "o": 0x12,
        "p": 0x13,
        "q": 0x14,
        "r": 0x15,
        "s": 0x16,
        "t": 0x17,
        "u": 0x18,
        "v": 0x19,
        "w": 0x1a,
        "x": 0x1b,
        "y": 0x1c,
        "z": 0x1d,
        "1": 0x1e,
        "2": 0x1f,
        "3": 0x20,
        "4": 0x21,
        "5": 0x22,
        "6": 0x23,
        "7": 0x24,
        "8": 0x25,
        "9": 0x26,
        "0": 0x27,
        " ": 0x2c,
        "\n": 0x28
    }

    hid_special = {
        "return": 0x28,
        "space": 0x2c,
        "esc": 0x29,
        "right": 0x4f,
        "left": 0x50,
        "down": 0x51,
        "up": 0x52,
        "delete": 0x4c,
        "backspace": 0x2a,
        "meta": 0xe3
    }

    hid_mouse_buttons = {
        "b0": 0x00,
        "b1": 0x01,
        "b2": 0x02,
        "b3": 0x03
    }

    def mouse_handler(self, *args):
        # calculate count and remainder
        x_positive = False
        if args[1] > 0:
            x_positive = True
        x_count = abs(args[1]) // 0x7f
        x = abs(args[1]) % 0x7f

        y_positive = False
        if args[2] > 0:
            y_positive = True
        y_count = abs(args[2]) // 0x7f
        y = abs(args[2]) % 0x7f

        # loop x_count and y_count
        while x_count > 0 or y_count > 0:
            report = [0x00, 0x00, 0x00, 0x00]
            if x_count > 0:
                if x_positive:
                    report[1] = 0x7f
                else:
                    report[1] = 0x81
            if y_count > 0:
                if y_positive:
                    report[2] = 0x7f
                else:
                    report[2] = 0x81
            print(report)
            self.mouse_file.write(bytes(report))
            x_count -= 1
            y_count -= 1
        report = [0x00, 0x00, 0x00, 0x00]
        if x_positive:
            report[1] = x
        else:
            if x > 0:
                report[1] = 0x100 - x
        if y_positive:
            report[2] = y
        else:
            if y > 0:
                report[2] = 0x100 - y
        report[0] = self.hid_mouse_buttons[args[0]]
        print(report)
        self.mouse_file.write(bytes(report))

    def keyboard_handler(self, mode, arg):
        report = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        if mode == self.keyboard_string:
            for c in arg:
                if c.isupper():
                    report[0] = self.hid_shift
                report[2] = self.hid_basic[c.lower()]
                print(report)
                self.keyboard_file.write(bytes(report))
                self.keyboard_file.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
                # reset the shift key
                report[0] = 0x00
        if mode == self.keyboard_symbol:
            if arg in self.hid_special:
                report[2] = self.hid_special[arg]
            print(report)
            self.keyboard_file.write(bytes(report))
            self.keyboard_file.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')

    def parse_json(self, json_message):
        python_message = json.loads(str(json_message))
        if python_message['type'] == "keyboard_string":
            if 'string' in python_message:
                self.keyboard_handler(self.keyboard_string, python_message['string'])

        if python_message['type'] == "keyboard_symbol":
            if 'button' in python_message:
                self.keyboard_handler(self.keyboard_symbol, python_message['button'])

        if python_message['type'] == "mouse":
            if 'x' in python_message and 'y' in python_message and 'button' in python_message:
                self.mouse_handler(python_message['button'], python_message['x'], python_message['y'])

    def interactive_mode(self, arg):
        self.keyboard_file = open(self.keyboard_name, "bw", 0)
        self.mouse_file = open(self.mouse_name, "bw", 0)
        # self.mouse_handler(self.mouse_movement, -300, -130)
        # self.mouse_handler(self.mouse_button, "b1")
        # print("")
        # self.keyboard_handler(self.keyboard_string, "Hello Python")
        # print("")
        # self.keyboard_handler(self.keyboard_string, "esc")
        if isinstance(arg, str):
            print(arg)
            self.keyboard_handler(self.keyboard_string, arg)

    @asyncio.coroutine
    def connection_handler(self, address):
        try:
            websocket = yield from websockets.connect(address)
        except:
            print("Connection error")
            return
        try:
            dic = {'client': 'hw_client'}
            yield from websocket.send(json.dumps(dic))
            greeting = yield from websocket.recv()
            print("{}".format(greeting))
            while True:
                msg = yield from websocket.recv()
                print(msg)
                self.parse_json(msg)

        except websockets.ConnectionClosed:
            print("ConnectionClosed")

        finally:
            yield from websocket.close()

    def client_mode(self, arg):
        self.keyboard_file = open(self.keyboard_name, "bw", 0)
        self.mouse_file = open(self.mouse_name, "bw", 0)
        asyncio.get_event_loop().run_until_complete(self.connection_handler(arg))

    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv, "i:a:", ["address="])
        except getopt.GetoptError:
            print("wrong arguments")
            print("use -i with word for interactive mode or -a for setting ip address of server")
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-i':
                print("Interactive mode")
                self.interactive_mode(arg)
                self.keyboard_file.close()
                self.mouse_file.close()
                sys.exit(0)
            if opt == '-a':
                print("Client mode")
                print("Address: " + arg)
                self.client_mode(arg)
                self.keyboard_file.close()
                self.mouse_file.close()
                sys.exit(0)
        print("No arguments, starting interactive mode")
        self.interactive_mode("Hello world from rpi0")
        self.keyboard_file.close()
        self.mouse_file.close()
        sys.exit(0)


if '__main__' == __name__:
    app = Application()
    app.main(sys.argv[1:])
