from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
from platforms.CHARTIER.CHARTIER import CHARTIER

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

            cmd(*query['args'])

    # def do_GET(self):
    #     if self.board:
    #         parsed_path = urllib.parse.urlsplit(self.path)
    #         query = urllib.parse.parse_qs(parsed_path.query)
    #         print(query)
    #
    #         paths = (self.path).split('/')
    #         cmd = self.board
    #         for path in paths:
    #             cmd = getattr(cmd, path)
    #
    #         cmd(*query['args'])




if __name__ == '__main__':
    from http.server import HTTPServer
    handler = CHARTIERHandler
    handler.board = CHARTIER()
    server = HTTPServer(('localhost', 5000), handler)
    print('Starting server at http://localhost:5000')
    server.serve_forever()