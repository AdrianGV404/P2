import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))

import grpc, json
import store_pb2
import store_pb2_grpc
from concurrent import futures

FILE = 'data.json'

# This class controls the load/store of data in a JSON
class dataControlJson:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data_store = self.load()
        self.keys_set = set(self.data_store.keys())

# Loads data from JSON
    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as s:
                values = json.load(s)
                print("Data loaded from JSON")
                return values
        else:
           print("Nothing to load")
           return {}

# Saves data in JSON
    def save(self):
        with open(self.file_path, 'w') as s:
            json.dump(self.data_store, s)
            print ("Data stored in JSON")

class dataStorage(store_pb2_grpc.KeyValueStoreServicer, dataControlJson):
    def __init__(self, file_path):
        dataControlJson.__init__(self, file_path)

    # Stores a value with it's key
    def Store(self, request, context):
        self.keys_set.add(request.key)
        self.data_store[request.key] = request.value
        self.save()
        return store_pb2.Empty()

    # Gets a value with a given key
    def GetValue(self, request, context):
        # Value = empty if it doesn't exist
        value = self.data_store.get(request.key, "")
        return store_pb2.StoreRequest(key=request.key, value=value)

    # Gets all the values with their keys
    def GetValues(self, request, context):
        values = [store_pb2.StoreRequest(key=k, value=v) for k, v in self.data_store.items()]
        return store_pb2.List(values=values)


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(dataStorage(FILE), server) 
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
