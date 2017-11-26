import asyncio
import sys
import websockets
import json
import time
from ctypes import windll, Structure, c_long, byref


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    if windll.user32.GetKeyState(0x01) not in [0, 1]:
        lclick = True
    else:
        lclick = False
    if windll.user32.GetKeyState(0x02) not in [0, 1]:
        rclick = True
    else:
        rclick = False
    if windll.user32.GetKeyState(0x4d) not in [0, 1]:
        return None
    else:
        return (pt.x,pt.y,lclick,rclick)


def mouse_handler(old_data):
    while True:
        pos1 = queryMousePosition()
        if pos1 is None:
            return None, (False, False)
        time.sleep(0.25)
        pos2 = queryMousePosition()
        if pos2 is None:
            return None, (False, False)

        if pos1 == pos2 and old_data == (pos2[2], pos2[3]):
            continue
        else:
            out_dic = {'type': "mouse",
                       'button': "b0"}
            if pos2[2]:
                out_dic['button'] = "b1"
            elif pos2[3]:
                out_dic['button'] = "b2"
            out_dic['x'] = pos2[0] - pos1[0]
            out_dic['y'] = pos2[1] - pos1[1]
            return json.dumps(out_dic), (pos2[2], pos2[3])


def keyboard_handler():
    mouse_enable = False
    print("Enter mode of controlling = string, symbol, mouse")
    mode = input("Mode? ")
    if mode == 'string':
        input_string = input("String? ")
        out_dic = {'type': "keyboard_string",
                   'string': input_string}
        return json.dumps(out_dic), mouse_enable

    elif mode == 'symbol':
        print("Symbols: return, space, esc, right, left, down, up, delete, backspace, meta")
        input_symbol = input("Symbol? ")
        out_dic = {'type': "keyboard_symbol",
                   'button': input_symbol}
        return json.dumps(out_dic), mouse_enable

    elif mode == 'mouse':
        print("Enabling mouse mode")
        mouse_enable = True
        return None, mouse_enable
    else:
        return None, mouse_enable

mouse_enable = False
previous_mouse = (False, False)


def input_handler():
    global mouse_enable
    global previous_mouse
    while True:
        if mouse_enable:
            data, previous_mouse = mouse_handler(previous_mouse)
            if data is None:
                mouse_enable = False
                continue
        else:
            data, mouse_enable = keyboard_handler()
            if data is None and mouse_enable is True:
                continue
        # last check before sending to server
        if data is None:
            break
        print(data)
        return data

@asyncio.coroutine
def connection_handler(argv):
    if len(argv) > 0:
        websocket = yield from websockets.connect(argv[0])
    else:
        print("Please specify server address")
        sys.exit(2)

    try:
        dic = {'client': "sw_client"}
        yield from websocket.send(json.dumps(dic))
        print(dic)
        greeting = yield from websocket.recv()
        print("{}".format(greeting))
        data = input_handler()
        while data is not None:
            yield from websocket.send(data)
            data = input_handler()
        yield from websocket.close()
    except websockets.ConnectionClosed:
        sys.exit(2)


if '__main__' == __name__:
    asyncio.get_event_loop().run_until_complete(connection_handler(sys.argv[1:]))
