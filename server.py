from tornado import websocket, web, ioloop

import os, uuid, json, base64_converter, logging


class Client:
    def __init__(self, uuid, current_equation):
        self.buffer = []  # this is going to be a list of lists
        self.uuid = uuid
        self.current_equation = current_equation
        self.data = None
        print("New client with uuid: ", uuid)

    # msg is a map
    def to_buffer(self, msg):
        if 'traceid' in msg:
            traceid = msg['traceid']
            print("Traceid: ", traceid)
            if len(self.buffer) - 1 < traceid:
                self.buffer.append([])
            if 'x1' in msg and 'y1' in msg:  # Make sure to only add pairs of coordinates.
                self.buffer[traceid].append(int(msg['x1']))
                self.buffer[traceid].append(int(msg['y1']))
            if 'x2' in msg and 'y2' in msg:
                self.buffer[traceid].append(int(msg['x2']))
                self.buffer[traceid].append(int(msg['y2']))
        else:
            print("Found no traceid.")

    # now the buffers are filled, with each trace as a list.
    def to_inkml(self):
        pass


def find_client(uuid):
    # Can return None
    return clients.get(uuid)


def find_client_with_request_data(data):
    for k, client in clients.items():
        if client.data == data:
            return client

    return None


clients = dict()


class WebSocket(websocket.WebSocketHandler):
    def open(self):
        print('Client connected to websocket!')

    def on_message(self, message):
        parsed_message = json.loads(message)
        print("on_message: ", parsed_message)

        # Find client
        client = find_client(parsed_message['uuid'])

        # Remove uuid from json
        parsed_message.pop('uuid', None)

        # Add data to buffer
        # if 'status' in parsed_message and 'traceid' in parsed_message:
        #    if parsed_message['status'] == 'End':
        #        client.buffer.append(message)  # this should make the buffer of a client a list og lists.
        #        print(client.buffer)

        # this passes data in inkml format to to_buffer method.
        # param is parsed json
        if client:
            if 'status' in parsed_message:
                if parsed_message['status'] == 201:  # http created = 201
                    # pass to inkml creation
                    print("InkML config.")
                    pass
            # elif 'status' in parsed_message:
            else:
                client.to_buffer(parsed_message)



                # Set client data if not set
        if not client.data:
            client.data = self

    def on_close(self):
        print('Client disconnected with: ', self)

        # Find client
        # client = find_client_with_request_data(self) # this can be none

        # Delete client buffer
        # if client is not None:
        #   if client.buffer is not None:
        #        del client.buffer

        # Remove client from set
        # del clients[client.uuid] #TODO handle possible keyerror


class rest_handler(web.RequestHandler):
    def get(self, *args):
        # Create client object and add to set
        id = uuid.uuid4()
        equation = '2 + 2 = 4'

        client = Client(uuid=str(id), current_equation=equation)
        clients[str(id)] = client

        # Get an equation from db

        # Create json
        data = {
            'equation': equation,
            'uuid': str(id)
        }

        # Send equation and uuid to client
        self.write(json.dumps(data))

    def post(self):
        # Extract UUID
        id = self.get_body_argument("uuid")

        # Find client in set
        client = find_client(id)

        # Extract image and save image
        base64_converter.convertToImg(self.get_body_argument("b64_str"), client.current_equation)

        # Send client buffer to db

        # Reset buffer

        # Get an equation from db
        equation = '4 - 1 = 3'
        client.current_equation = equation

        # Send equation to client
        data = {
            'equation': equation
        }

        self.write(json.dumps(data))


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("./client/index.html")


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', WebSocket),
    (r'/api', rest_handler),
    (r'/client/(.*)', web.StaticFileHandler, {'path': './client/'})
])

if __name__ == '__main__':
    app.listen(8080)
    ioloop.IOLoop.instance().start()
