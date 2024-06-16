import subprocess
import time
import os

data_storage_script = os.path.join('data', 'dataStorage.py')
node_script = os.path.join('decentralized', 'dec_node.py')

processes = []

def start_process(script_path, port1=None, port2=None):
    if port1 is not None and port2 is not None:
        process = subprocess.Popen(['python3', script_path, str(port1), str(port2)])
    else:
        process = subprocess.Popen(['python3', script_path])
    processes.append(process)
    time.sleep(2)
    return process

try:
    storage_process = start_process(data_storage_script)
    slave0_process = start_process(node_script, 32770, 32771)
    slave1_process = start_process(node_script, 32771, 32772)
    slave2_process = start_process(node_script, 32772, 32770)

    for process in processes:
        process.wait()
except KeyboardInterrupt:
    print("KeyboardInterrupt - Stopping all processes...")
    for process in processes:
        process.terminate()
        process.wait()
    print("All processes have been stopped")
