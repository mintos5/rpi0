import sys
import getopt
import asyncio
import signal
import websockets
import json

hw_client_list = []
ok_response = {'server': 'ok'}


@asyncio.coroutine
def handler(websocket, path):
    global hw_client_list
    try:
        msg = yield from websocket.recv()
        reg_data = json.loads(str(msg))
        if 'client' in reg_data:
            # HW CLIENT
            if reg_data['client'] == 'hw_client':
                print("Added HW client")
                if len(hw_client_list) == 0:
                    yield from websocket.send(json.dumps(ok_response))
                    hw_client_list.append(websocket)
                    # wait for commands
                    while True:
                        msg = yield from websocket.recv()
                        print(msg)
                else:
                    print("Only one hw_client allowed at once")
                    return
            # SW CLIENT
            elif reg_data['client'] == 'sw_client':
                print("Added SW client")
                yield from websocket.send(json.dumps(ok_response))
                while True:
                    msg = yield from websocket.recv()
                    if len(hw_client_list) == 0:
                        print("Sorry, no HW client")
                        return
                    else:
                        # send to hw_client
                        yield from hw_client_list[0].send(msg)
            # BAD JSON
            else:
                print("Wrong json message")
                print(msg)
                return
        else:
            print("Wrong json message")
            print(msg)
            return
    except websockets.ConnectionClosed:
        hw_client_socket = None
        print("ConnectionClosed")
        return


if __name__ == "__main__":
    # default server values
    server_address = "0.0.0.0"
    server_port = 5432
    # load paramaters from arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:")
    except getopt.GetoptError:
        print("wrong arguments")
        print("use -a for setting ip address of server and -p for server port")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-a':
            server_address = arg
        if opt == '-p':
            server_port = int(arg)
    # Get the event loop
    loop = asyncio.get_event_loop()

    # Create the server.
    start_server = websockets.serve(handler, server_address, server_port)
    server = loop.run_until_complete(start_server)

    # Run the server until SIGTERM.
    stop = asyncio.Future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.run_until_complete(stop)

    # Shut down the server.
    server.close()
    loop.run_until_complete(server.wait_closed())
