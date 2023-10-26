from http.server import ThreadingHTTPServer
from server import Handler
from server.utils import set_bd_keys
from threading import Thread
import yaml
import zhipuai

config = {}
with open("config.yml", "r") as f:
    config = yaml.load(f, yaml.Loader)
zhipuai.api_key = config["zhipuai"]["key"]
set_bd_keys(dict(config["baidu"]))
port = config["port"]

server = ThreadingHTTPServer(('localhost', port), Handler)

server_thread = Thread(target=server.serve_forever)
server_thread.start()
print(f'Server started on port {port}')
input()
server.shutdown()
print('Server closed')
