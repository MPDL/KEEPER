# Standard library imports...
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import re
import socket
from threading import Thread

# Third-party imports...
import requests


class MockServerRequestHandler(BaseHTTPRequestHandler):
    USERS_PATTERN = re.compile(r'/certifyData') 

    def do_POST(self):
        if re.search(self.USERS_PATTERN, self.path):
            self.send_response(requests.codes.ok)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            # Add response content.
            response_content = json.dumps({"msg":"Transaction succeeded","txReceipt":{"transactionHash":"0x3d302773bbebd1a9d44ff96784fae2082df483ecf50a695e70cddc9d54da5e57"}})
            self.wfile.write(response_content.encode('utf-8'))


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(('localhost', port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()

