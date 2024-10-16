""" Main file to run the server and load the data into memory """

import sys
from http.server import HTTPServer
import time
import json

import memdb
import server as srv
import movies as mvs


if __name__ == "__main__":
    movies = sys.argv[1]
    past_screenings = sys.argv[2]

    # initialize the memdb
    mem = memdb.MemDB()
    start = time.time()
    mem.load_movies(movies)
    mem.load_past_screenings(past_screenings)
    print(
        "Finished loading movies and past screenings, time took:",
        round(time.time() - start, 2),
        "seconds",
    )
    if len(sys.argv) > 3:
        rules = sys.argv[3]
        f = open(rules, "r")
        queries = json.load(f)
        for q in queries:
            if len(q) != 2:
                raise mvs.InvalidRule
            query = mvs.Query(q[1])
            print(q[0], mem.query(query))

    # run the server to handle queries
    PORT = 8081
    if len(sys.argv) > 4:
        PORT = int(sys.argv[4])
    server = HTTPServer(
        ("0.0.0.0", PORT),
        lambda *args, **kwargs: srv.Server(*args, mem=mem, **kwargs),
    )
    try:
        print("Server is running on port", PORT)
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
