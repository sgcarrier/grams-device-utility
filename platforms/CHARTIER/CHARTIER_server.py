from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib


class CHARTIERHandler(BaseHTTPRequestHandler):

    board = None
    def do_GET(self):
        if self.board:
            parsed_path = urllib.parse.urlsplit(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)




if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8080), CHARTIERHandler)
    print('Starting server at http://127.0.0.1:5000')
    server.serve_forever()