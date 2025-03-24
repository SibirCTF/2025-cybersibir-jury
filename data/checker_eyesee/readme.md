# EyeSee Checker

## HowTo

```
usage: EyeSee Checker [-h] host {put,check} flag_id flag

positional arguments:
  host
  {put,check}
  flag_id
  flag

options:
  -h, --help   show this help message and exit
```

examples:

```bash
./checker.py 127.0.0.1 put "somekekeke" "6a331fd2-133a-4713-9587-12652d34666d12"
```

```bash
./checker.py 127.0.0.1 check "somekekeke" "6a331fd2-133a-4713-9587-12652d34666d12"
```

## Dev

### Generate gRPC code

Run from `EyeSee` dir

```bash
python -m grpc_tools.protoc -Iprotocols --python_out=checker/proto --pyi_out=checker/proto --grpc_python_out=checker/proto protocols/service.proto
```
