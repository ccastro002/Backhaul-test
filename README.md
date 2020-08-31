# Backhaul-test

This backhauled test currently only works for one node. It will be expanded to support multiple nodes in order 
to test backhauled pli data in the future.

### Prerequisites
- Python 3.7 and pip
- pipenv: make sure to activate environment`source name/bin/activate `
- protoc (`brew install protobuf` or [via binary](https://github.com/protocolbuffers/protobuf/releases))
- add an empty folder named `gen/`

## Set up 
1. Install submodule
   `git submodule update --recursive --init`
2. Install pip requirements `pip install -r requirements.txt`
3. To generate the protobufs, run
   `protoc --proto_path=./goTenna-Pro-Payloads/buffers --python_out=./gen ./goTenna-Pro-Payloads/buffers/*.proto`
   
4. Inside the `gen/` folder add a python filed named `__init__.py`

5. Add the following code to that file
```
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
```
 
6. Make sure to update `credentials.py` by editing the desired attributes
**NOTE** Never commit any credentials 
  
7. To run file: `python main.py`
