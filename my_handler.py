# -*- coding: utf-8 -*-
"""
Created on Tue Apr 01 06:26:29 2014

@author: Eric Conklin
"""

import SimpleHTTPServer, io, json, os

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, cache, *args, **kwargs):
        self.__cache = cache
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)
        
    def send_head(self):
        """Common code for GET and HEAD commands.
 
        This sends the response code and MIME headers.
 
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
 
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200, 'OK')
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
        return f
        
    def do_OPTIONS(self):
        self.send_response(200, 'OK')
        self.send_header('Allow', 'HEAD, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()        

    def do_GET(self):
        """Serve a GET request."""

        f = self.JSONheader()
            
        if f:
            self.copyfile(f, self.wfile)
            f.close()
    #end __init__

    def JSONheader(self):
        args = self.path.strip().split('/')
        try:
            sinceTime = int(args[1])
        except:
            self.send_error(404, "File not found")
            return None
            
        try:
            twts = self.__cache.requestTweets(sinceTime)
            twts = json.dumps(twts)

            f = io.BytesIO(twts.encode('utf-8'))
        
        except IOError:
            self.send_error(404, "File not found")
            return None
            
        self.send_response(200, 'OK')
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(f.getvalue()))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
        
        return f
    #end JSONheader
#end MyHandler