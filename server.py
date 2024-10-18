
import http.server
import json
import sys
from http.server import HTTPServer

import movies as mvs

# simple server to handle queries
class Server(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, mem=None, path_to_data="data/", **kwargs):
        self.mem = mem
        self.path_to_data = path_to_data
        super().__init__(*args, **kwargs)

    def write_response(self, error_code, mes):
        self.send_response(error_code)
        self.end_headers()
        self.wfile.write(mes.encode("utf-8"))

    def do_GET(self) -> None:
        self.write_response(404, "404 Not Found")

    def do_POST(self):
        if self.path != "/query":
            self.write_response(404, "404 Not Found")
            return
        try:
            data = json.loads(self.rfile.read(
                int(self.headers["Content-Length"])))
            # check if data is string or list
            queries = []
            try:
                filename = data["filename"]
                queries = json.load(open(self.path_to_data + filename))
            except Exception as _:
                queries = data
            res = []
            for q in queries:
                if len(q) != 2:
                    raise mvs.InvalidRule
                query = mvs.Query(q[1])
                valid_weeks = self.mem.query(query)
                res.append((q[0], valid_weeks))
            self.write_response(200, json.dumps(res))
        except Exception as e:
            if e == mvs.InvalidRule:
                self.write_response(400, "400 Bad Request")
                return
            print("Received uknown error:", e)
            self.write_response(500, "500 Internal Server Error")

def init(mem):
    # run the server to handle queries
    port = 8081
    if len(sys.argv) > 4:
        port = int(sys.argv[4])
    server = HTTPServer(
        ("127.0.0.1", port),
        lambda *args, **kwargs: Server(*args, mem=mem, **kwargs),
    )
    try:
        print("Server is running on port", port)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server received keyboard interrupt")
        server.shutdown()
        server.server_close()
        sys.exit(0)
    except Exception as e:
        print("Server stopped due to exception:", e)
        server.shutdown()
        server.server_close()
        sys.exit(0)
