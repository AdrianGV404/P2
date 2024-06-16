# Distributed storage systems and the CAP theorem

```
Project/
│
├── proto/
│   ├── store.proto
│   ├── store_pb2.py
│   └── store_pb2_grpc.py
│
├── data/
│   ├── data.json
│   ├── data_store.py
│   └── dataStorage.py
│
├── centralized/
│   ├── cen_node.py
│   └── ServicerCen.py
│
├── decentralized/
│   ├── dec_node.py
│   └── ServicerDes.py
│
├── centralized_config.yaml
├── decentralized_config.yaml
├── requirements.txt
├── centralized.py
├── decentralized.py
├── eval/
│   ├── test_centralized_system.py
│   └── test_decentralized_system.py
│   ├── decentralized_config.yaml
│   ├── centralized_config.yaml
│
└── README.md

```


## Directory Structure Explanation

- **proto/**: Contiene archivos de Protocol Buffers utilizados para definir los servicios y mensajes gRPC. Los archivos Python generados (`store_pb2.py` y `store_pb2_grpc.py`) basados en `store.proto` deben almacenarse aquí.

- **data/**: Contiene los archivos relacionados con el almacenamiento de datos.
  - **data.json**: Archivo JSON que almacena los datos.
  - **data_store.py**: Implementación de la lógica de almacenamiento en memoria.
  - **dataStorage.py**: Controla la carga y almacenamiento de datos en el archivo JSON y define el servicio gRPC relacionado.

- **centralized/**: Contiene los archivos específicos para la implementación centralizada.
  - **cen_node.py**: Implementa la lógica para los nodos centralizados.
  - **ServicerCen.py**: Define el servicio `KeyValueStoreServicer` para la configuración centralizada.

- **decentralized/**: Contiene los archivos específicos para la implementación descentralizada.
  - **dec_node.py**: Implementa la lógica para los nodos descentralizados.
  - **ServicerDes.py**: Define el servicio `KeyValueStoreServicer` para la configuración descentralizada.

- **centralized_config.yaml y decentralized_config.yaml**: Archivos YAML que contienen configuraciones para los sistemas centralizados y descentralizados.

  - **Formato Centralizado**:
    ```yaml
    master:
      ip: <IP>
      port: <Port>

    slaves:
      - id: <slave_1_ID>
        ip: <slave_1_IP>
        port: <slave_1_Port>
      - id: <slave_2_ID>
        ip: <slave_2_IP>
        port: <slave_2_Port>
      ...
    ```

  - **Formato Descentralizado**:
    ```yaml
    nodes:
      - id: <node_1_ID>
        ip: <node_1_IP>
        port: <node_1_Port>
      - id: <node_2_ID>
        ip: <node_2_IP>
        port: <node_2_Port>
      ...
    ```

## Pasos para la Ejecución

1. **Instalar Dependencias**:
   Asegúrate de tener instaladas las dependencias necesarias para ejecutar el proyecto. Puedes instalar las dependencias con:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generar Archivos gRPC:**:
  Si los archivos store_pb2.py y store_pb2_grpc.py no están generados, puedes generarlos utilizando el compilador de Protocol Buffers:
   ```bash
   python3 -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/store.proto

3. **Ejecutar la Implementación Centralizada:**:
   Inicia el sistema centralizado ejecutando el script centralized.py:
   ```bash
   python3 centralized.py
   ```
4. **Ejecutar Pruebas Centralizado:**:
   Inicia el sistema centralizado ejecutando el script centralized.py:
   ```bash
   python3 eval/test_centralized_system.py
   ```
5. **Ejecutar la Implementación Descentralizada:**:
   Inicia el sistema descentralizado ejecutando el script decentralized.py:
   ```bash
   python3 decentralized.py
   ```
6. **Ejecutar Pruebas Descentralizado:**:
   Inicia el sistema descentralizado ejecutando el script decentralized.py:
   ```bash
   python3 eval/test_decentralized_system.py
   ```