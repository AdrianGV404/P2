import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))

import grpc, time, store_pb2, store_pb2_grpc
from concurrent import futures
from ServicerDes import KeyValueStoreServicer


def serve(port_main,port_discover):
    # Starts the server with an instance of KeyValueStoreServicer as gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(port_main, port_discover, 1), server)
    server.add_insecure_port(f'[::]:{port_main}')
    server.start()
    time.sleep(5)
    
    print("DEBUG - PORT_A: " + str(port_main) + " PORT_B: " + str(port_discover))
    # Creates an insecure channel to port_discover and creates a stub to interact with the server through port_discover
    with grpc.insecure_channel(f'localhost:{port_discover}') as channel:
        node_stub = store_pb2_grpc.KeyValueStoreStub(channel)
        # Tries to discover other nodes through port_discover (insecure channel)
        new_ports = node_stub.discover(store_pb2.DiscRequest(port=port_discover))

        if new_ports:
            # If a port is discovered it gets added to port_main with addPortts
            with grpc.insecure_channel(f'localhost:{port_main}') as my_channel:
                stub = store_pb2_grpc.KeyValueStoreStub(my_channel)
                stub.addPorts(store_pb2.portRequest(ports=new_ports))
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(1)
    port_main = int(sys.argv[1])
    port_discover = int(sys.argv[2])
    print("port_main: " + sys.argv[1] + " port_discover: " + sys.argv[2])
    serve(port_main,port_discover)
