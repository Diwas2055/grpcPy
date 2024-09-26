# GRPC With Python 

## What is GRPC?

- gRPC is a high performance, open-source universal RPC framework initially developed by Google. It is based on HTTP/2, Protocol Buffers and other Google technologies. It is a language agnostic, high-performance Remote Procedure Call (RPC) framework.

## Why gRPC?

- gRPC is a modern, open source, high-performance remote procedure call (RPC) framework that can run anywhere. It enables client and server applications to communicate transparently, and makes it easier to build connected systems.

## How gRPC works?

- gRPC uses Protocol Buffers as the Interface Definition Language (IDL) for describing both the service interface and the structure of the payload messages. It is a language-agnostic, platform-neutral, extensible way of serializing structured data for use in communications protocols, data storage, and more.

- gRPC uses HTTP/2 for transport, allowing it to benefit from features such as multiplexing, flow control, header compression, and connection reuse. This makes gRPC ideal for use in microservices applications.

- gRPC also supports authentication and authorization, with support for OAuth, JWT, and more.

## How to install gRPC?

- To install gRPC, you need to install the gRPC tools and the gRPC Python package. You can install the gRPC tools using pip:

```bash
pip install grpcio-tools
```

- You can install the gRPC Python package using pip as well:

```bash

pip install grpcio
```

## How to create a gRPC service?

- To create a gRPC service, you need to define the service interface using Protocol Buffers. You can define the service interface in a .proto file, and then use the gRPC tools to generate the client and server code in the language of your choice.

- Here is an example of a simple gRPC service interface defined in a .proto file:

```proto

syntax = "proto3";

package helloworld;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```
## Generating gRPC Files
- You can then use the gRPC tools to generate the client and server code in Python:
- Run the following commands to generate the gRPC files:

```bash
python -m grpc_tools.protoc -I. --python_out=./pb --pyi_out=./pb --grpc_python_out=./pb helloworld.proto
```
- saving them in the `pb` folder
- This will generate the client and server code in Python, which you can then use to implement the gRPC service.

> This generates several Python files from the .proto file. Here’s a breakdown:
> 
> - **python -m grpc_tools.protoc** runs the protobuf compiler, which will generate Python code from the protobuf code.
> - **-I.** to tell the compiler to look in the current directory or  **-I ../protobufs** tells the compiler where to find files that your protobuf code imports. You don’t actually use the import feature, but the `-I` flag is required nonetheless or **-Ipb=./protobufs** this generating gRPC interfaces with custom package path for now `pb`.
> - **--python_out=. --grpc_python_out=.** tells the compiler where to output the Python files. As you’ll see shortly, it will generate two files, and you could put each in a separate directory with these options if you wanted to. or you can use the `--python_out=./pb --grpc_python_out=./pb` to save them in the `pb` folder [Generating gRPC interfaces with custom package path]( https://grpc.io/docs/languages/python/basics/#generating-grpc-interfaces-with-custom-package-path).
> - **--pyi_out=./pb** tells the compiler where to output the Python stub files. This is optional, but it’s a good idea to generate these files so that your IDE can provide better autocompletion and type checking. or you can use the `--pyi_out=./pb` to save them in the `pb` folder
> - `helloworld.proto` is the file you want to compile or **./protobufs/helloworld.proto** if you have the file in a different directory.`protobufs` is the directory where you keep your .proto files.
> - The compiler will generate two files: `helloworld_pb2.py` and `helloworld_pb2_grpc.py`. The first file contains the Python classes that represent your protocol buffer data, and the second contains the classes that represent your gRPC service.

## How to run a gRPC service?

- To run a gRPC service, you need to implement the service interface in the server code, and then start the gRPC server. You can use the gRPC Python package to create the server and start it on a specific port.

- Here is an example of a simple gRPC server implementation in Python:

```python

import grpc
from concurrent import futures
import time

import helloworld_pb2

class Greeter(helloworld_pb2.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':

    serve()
```

- You can then run the gRPC server using the following command:

```bash

python server.py
```

- This will start the gRPC server on port 50051, and it will be ready to accept requests from clients.

## How to create a gRPC client?

- To create a gRPC client, you need to use the client code generated by the gRPC tools. You can use the client code to make requests to the gRPC server and receive responses.

- Here is an example of a simple gRPC client implementation in Python:

```python

import grpc

import helloworld_pb2

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = helloworld_pb2.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)

if __name__ == '__main__':

    run()
```

- You can then run the gRPC client using the following command:

```bash

python client.py
```

- This will make a request to the gRPC server running on localhost:50051, and print the response received from the server.




## AsyncIO and gRPC in Python

- AsyncIO support in the official gRPC package was lacking for a long time, but has recently been added. It’s still experimental and under active development, but if you really want to try AsyncIO in your microservices, then it could be a good option. You can check out the [gRPC AsyncIO documentation](https://grpc.github.io/grpc/python/grpc_asyncio.html) for more details.

- There’s also a third-party package called `grpclib` that implements AsyncIO support for gRPC and has been around longer.


## References

- [gRPC](https://grpc.io/)
- [gRPC Python](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [gRPC AsyncIO](https://grpc.github.io/grpc/python/grpc_asyncio.html)
- [grpclib](https://grpclib.readthedocs.io/en/latest/)
- [Python Microservices With gRPC](https://realpython.com/python-microservices-grpc/#why-microservices)
- [Generating gRPC interfaces with custom package path]( https://grpc.io/docs/languages/python/basics/#generating-grpc-interfaces-with-custom-package-path)


## Generating gRPC Files

```bash
python -m grpc_tools.protoc -Ipb=./protobuf --python_out=. --grpc_python_out=.  ./protobuf/users.proto 
```