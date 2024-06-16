import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))

import grpc, time, store_pb2, store_pb2_grpc
from concurrent import futures
from ServicerCen import KeyValueStoreServicer

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(port), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)
    port = int(sys.argv[1])
    print("PORT: " + str(port))
    serve(port)
