from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
from platforms.CHARTIER.CHARTIER import CHARTIER
import json
class CHARTIERHandler(BaseHTTPRequestHandler):

    board = None
    def do_POST(self):
        if self.board:
            parsed_path = urllib.parse.urlsplit(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            print(query)

            paths = (self.path).split('?')[0]
            paths = paths.split('/')
            cmd = self.board
            paths = filter(None, paths)
            for path in paths:
                cmd = getattr(cmd, path)

            args = query['args']
            for i in range(len(args)):
                args[i] = self.autoconvert(args[i])

            r = cmd(*args)

        if (r == -1):
            self.send_response(400)
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()

    def do_GET(self):
        if self.board:
            parsed_path = urllib.parse.urlsplit(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            print(query)

            paths = (self.path).split('?')[0]
            paths = paths.split('/')
            cmd = self.board
            paths = filter(None, paths)
            for path in paths:
                cmd = getattr(cmd, path)

            args = query['args']
            for i in range(len(args)):
                args[i] = self.autoconvert(args[i])

            r = cmd(*args)

            if (r == -1):
                self.send_response(400)
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                json_str = json.dumps({'returnValue': str(r)})
                self.wfile.write(json_str.encode(encoding='utf_8'))

    def boolify(self, s):
        if s == 'True':
            return True
        if s == 'False':
            return False
        raise ValueError("Not a bool")

    def autoconvert(self, s):
        for fn in (self.boolify, int, float, str):
            try:
                return fn(s)
            except ValueError:
                pass
        return s


if __name__ == '__main__':
    from http.server import HTTPServer
    handler = CHARTIERHandler
    handler.board = CHARTIER()
    server = HTTPServer(('localhost', 5000), handler)
    print('Starting server at http://localhost:5000')
    server.serve_forever()