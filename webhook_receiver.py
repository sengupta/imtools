"""
This is a sample, barebones Instamojo webhook receiver.

For more information, visit:
    http://support.instamojo.com/support/solutions/folders/228045
"""
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse

PORT = 8000
FILENAME = '/tmp/webhook_data.txt'

class MojoHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['content-length'])
        querystring = self.rfile.read(content_length)
        data = urlparse.parse_qs(querystring)
        with open(FILENAME, 'a') as file_pointer:
            for key, value in data.iteritems():
                file_pointer.write(': '.join([key, value[0]])+'\n')
            file_pointer.write("----------\n")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

httpd = HTTPServer(('', PORT), MojoHandler)
httpd.serve_forever()
