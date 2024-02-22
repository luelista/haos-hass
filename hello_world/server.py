from http.server import HTTPServer, SimpleHTTPRequestHandler

from ptouch import PTouch
#import config
import io
import logging
import argparse
import json
logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serial-port', required=True)
parser.add_argument('-l', '--tcp-port', type=int, default=8000)
args = parser.parse_args()

class MyRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server, directory='./ui/')

    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            if self.path == "/print":
                response = self.do_print(post_body)
            elif self.path == "/status":
                response = self.do_status(post_body)
            else:
                raise Exception("Not found")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        except Exception as ex:
            logging.exception("POST request failed")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"success":False,"message":str(ex)}), "utf-8"))


    def do_print(self, file_bytes):
        pt = PTouch(args.serial_port)
        text_stream = io.StringIO(file_bytes.decode('ascii'))
        pt.readBufferPBM(text_stream)

        #if not pt.showBufferTk():
        #    return

        pt.printBuffer()
        pt.print(True)
        return { "success": True }

    def do_status(self, file_bytes):
        pt = PTouch(args.serial_port)
        return { "success": True, "statusText": pt.initStatus, "dotswidth": pt.dotswidth }



handler = MyRequestHandler
httpd = HTTPServer(('0.0.0.0', args.tcp_port), handler)
logging.info("Listening on http://0.0.0.0:%d"%(args.tcp_port,))
logging.info("Expecting printer at %s"%(args.serial_port,))
httpd.serve_forever()

