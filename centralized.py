import subprocess
import time


data_storage_script = 'data/dataStorage.py'
node_script = 'centralized/cen_node.py'
master_port=32770
s1_port=32771
s2_port=32772

process_list = []

# Starts the specified scripts, with an optional port argument if provided
def start_process(script_path, params=None):
    if params:
        process = subprocess.Popen(['python3', script_path, str(params)])
    else:
        process = subprocess.Popen(['python3', script_path])
    process_list.append(process)
    time.sleep(2) # Gives time for the process to initialize
    return process

try:
    # Starts the grpc server (key-value) and the master and it's slaves
    storage_process = start_process(data_storage_script)
    master_process = start_process(node_script,master_port)
    slave1_process = start_process(node_script,s1_port)
    slave2_process = start_process(node_script,s2_port)

    for process in process_list:
        process.wait()
except KeyboardInterrupt:
    print("KeyboardInterrupt - Stopping all processes...")
    for process in process_list:
        process.terminate()
        process.wait()
    print("All processes have been stopped")
