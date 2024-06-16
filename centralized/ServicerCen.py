import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

import grpc, time
import store_pb2
import store_pb2_grpc
from data_store import data_store
from concurrent import futures

class KeyValueStoreServicer(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, port):
        self.delay = 0
        self.nodes_ports = []
        self.masterNode = (port == 32770)
        
        if not self.masterNode:
            # If the node is not the master (registers it with the master (using his port))
            with grpc.insecure_channel(f'localhost:32770') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                success = stub.registerNode(store_pb2.RegisterNodeRequest(port=port))

        with grpc.insecure_channel(f'localhost:50051') as channel:
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            # Gets all key-value stored
            values = stub.GetValues(store_pb2.Empty())

            for value in values.values:
                print(f'Received Key: {value.key} --> Value: {value.value}')
                data_store.doCommit(value.key, value.value)

    # If node (self) is master registers the new node otherwise returns false
    def registerNode(self, request, context):
        if self.masterNode:
            self.nodes_ports.append(request.port)
            print(f"Node (port:{request.port}) registered with master")
            return store_pb2.RegisterNodeResponse(success=True)
        else:
            return store_pb2.RegisterNodeResponse(success=False)

    # Saves the value into the specified key
    def put(self, request, context):
        time.sleep(self.delay)
        # If node is not master ends
        if not self.masterNode:
            return store_pb2.PutResponse(success=False)

        # If node is master tries to store key-value
        success = data_store.put(request.key, request.value)
        response = store_pb2.PutResponse(success=success)

        # For every port checks if it can commit, if it can it commits - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for port in self.nodes_ports:
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                status = stub.canCommit(store_pb2.Empty())
                if status.success:
                    stub.doCommit(store_pb2.DoCommitRequest(key=request.key, value=request.value))
                else:
                    print(f"Node {port} can't commit atm")

        # Stores data into the centralised file
        with grpc.insecure_channel(f'localhost:50051') as channel:
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            stub.Store(store_pb2.StoreRequest(key=request.key, value=request.value))
        return response


    def doCommit(self, request, context):
        data_store.doCommit(request.key, request.value)
        return store_pb2.Empty()

    def canCommit(self, empty, context):
        return store_pb2.CanCommitResponse(success=True)

    # Gets the value from the specified key
    def get (self, request, context):
        value, found = data_store.get(request.key)
        response = store_pb2.GetResponse(value=value, found=found)
        print (f'Get: {request.key} --> {response.found}, value: {response.value}')
        time.sleep(self.delay)
        return response

    # The receiver node suppresses any delays, if it has previously received a slow down request
    def restore (self, empty, context):
        time.sleep(self.delay)
        self.delay = 0
        return store_pb2.RestoreResponse(success=True)

    # The receiver node adds a secs seconds delay to all its gRPC responses.
    # We will use this call in eval.py to simulate defective nodes and network partitions
    def slowDown(self, request, context):
        try:
            self.delay = request.seconds
            print("SlowDown: " + str(self.delay) + " seconds")
        except (AttributeError, TypeError) as e:
            self.delay = 0
            return store_pb2.SlowDownResponse(success=False)

        time.sleep(self.delay)
        return store_pb2.SlowDownResponse(success=True)