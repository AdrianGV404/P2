import os, sys
import time, grpc

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

import store_pb2, store_pb2_grpc
from data_store import data_store
from concurrent import futures

class KeyValueStoreServicer(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, port_main, port_discover, weight):
        self.delay = 0
        self.nodes_ports = [port_main, port_discover]
        if port_main==32770:
            self.weight=1
        if port_main==32771:
            self.weight=2
        if port_main==32772:
            self.weight=1
        #self.weight = port_discover
        self.READ_QUORUM = 2
        self.WRITE_QUORUM = 3

        self._initialize_db_channel()
        self._load_initial_values()
        print(f"INIT - port_main: {port_main} port_discover: {port_discover}")

    # Sets an insecure channel with the "database server"
    def _initialize_db_channel(self):
        self.db_channel = grpc.insecure_channel('localhost:50051')
        self.db_stub = store_pb2_grpc.KeyValueStoreStub(self.db_channel)

    # Loads the initial values from the databse
    def _load_initial_values(self):
        values = self.db_stub.GetValues(store_pb2.Empty())
        for value in values.values:
            print(f"Recieved: {value.key} --> {value.value}")
            data_store.doCommit(value.key, value.value)

    def put(self, request, context):
        print("------------------PUT------------------")
        print("------------------PUT------------------")
        print("------------------PUT------------------")
        time.sleep(self.delay)
        # Checks if he can write (askVote is OK)
        success = self._perform_write_quorum(request)

        # If it gets stored succesfully, tells other nodes about it (so they store it too)
        if success:
            put_response = data_store.put(request.key, request.value)
            if put_response:
                self._propagate_commit(request)

            self._propagate_to_db(request)

        return store_pb2.PutResponse(success=success)

    def _perform_write_quorum(self, request):
        quorum = self.weight

        # For every port asks for a vote (if 3 or more vote for it returns true)
        for port in self.nodes_ports:
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                response_quorum = stub.askVote(store_pb2.AskRequest(key=request.key))
                quorum += response_quorum.weight

        return quorum >= self.WRITE_QUORUM

    # Propagates the commit to other nodes
    def _propagate_commit(self, request):
        for port in self.nodes_ports:
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                stub.doCommit(store_pb2.DoCommitRequest(key=request.key, value=request.value))

    # Propagates the stored value to the "database"
    def _propagate_to_db(self, request):
        value = store_pb2.StoreRequest(key=request.key, value=request.value)
        with grpc.insecure_channel(f'localhost:50051') as channel:
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            stub.Store(value)

    # Gets the data_store value
    def get(self, request, context):
        value, found = data_store.get(request.key)
        response = store_pb2.GetResponse(value=value, found=found)

        quorum = 0
        for port in self.nodes_ports:
            # Asks other nodes about read
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                response_quorum = stub.askVote(store_pb2.AskRequest(key=request.key))
                if response_quorum.value == value:
                    quorum += response_quorum.weight

        response.found = quorum >= self.READ_QUORUM
        time.sleep(self.delay)
        return response

    def slowDown(self, request, context):
        try:
            self.delay = request.seconds
        except (AttributeError, TypeError):
            self.delay = 0
            return store_pb2.SlowDownResponse(success=False)

        return store_pb2.SlowDownResponse(success=True)

    def restore(self, empty, context):
        self.delay = 0
        return store_pb2.RestoreResponse(success=True)

    def askVote(self, request, context):
        value = data_store.askVote(request.key)
        return store_pb2.AskResponse(weight=self.weight, value=value)

    def doCommit(self, request, context):
        data_store.doCommit(request.key, request.value)
        return store_pb2.Empty()

    def discover(self, request, context):
        print("------------------DISCOVER------------------")
        print("------------------DISCOVER------------------")
        print("------------------DISCOVER------------------")
        ports = ','.join(map(str, self.nodes_ports))
        return store_pb2.DiscResponse(ports=ports)

    def addPorts(self, request, context):
        node_ports = request.ports.split(",")
        for item in node_ports:
            if item != "":
                try:
                    port = int(item)
                    if port not in self.nodes_ports:
                        self.nodes_ports.append(port)
                except ValueError:
                    print(f"Skip: {item}")

        return store_pb2.Empty()

    def Store(self, request, context):
        return store_pb2.Empty()

    def GetValue(self, request, context):
        return store_pb2.StoreRequest(key=request.key, value="dummy_value")

    def GetValues(self, request, context):
        return store_pb2.List(values=[])

    def registerNode(self, request, context):
        return store_pb2.RegisterNodeResponse(success=True)

    def canCommit(self, request, context):
        return store_pb2.CanCommitResponse(success=True)