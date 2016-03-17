# The code is modified to call ezid service in Python
# Greg Janee <gjanee@ucop.edu>
# May 2013
# link to original version: http://ezid.cdlib.org/doc/ezid-client.py

import codecs
import optparse
import re
import sys
import time
import types
import urllib
import urllib2

class MyHelpFormatter (optparse.IndentedHelpFormatter):
    def format_usage (self, usage):
        return USAGE_TEXT

class MyHTTPErrorProcessor (urllib2.HTTPErrorProcessor):
    def http_response (self, request, response):
        # Bizarre that Python leaves this out.
        if response.code == 201:
          return response
        else:
          return urllib2.HTTPErrorProcessor.http_response(self, request, response)
    https_response = http_response

class ezidClient:
    __options__ = {}
    __server__ = None
    __opener__ = None
    __cookie__ = None

    def __init__(self, user, password):
        parser = optparse.OptionParser(formatter=MyHelpFormatter())
        parser.add_option("-d", action="store_true", dest="decode", default=False)
        parser.add_option("-e", action="store", dest="outputEncoding", default="UTF-8")
        parser.add_option("-o", action="store_true", dest="oneLine", default=False)
        parser.add_option("-t", action="store_true", dest="formatTimestamps", default=True)    
        self.__options__, _ = parser.parse_args()        

        self.__server__ = "https://ezid.cdlib.org"
        self.__opener__ = urllib2.build_opener(MyHTTPErrorProcessor())
        self.__cookie__ = None

        self.handler(user, password)

    def handler(self, user, password):
        handler = urllib2.HTTPBasicAuthHandler()
        handler.add_password("EZID", self.__server__, user, password)
        self.__opener__.add_handler(handler)

    # args example = ['who', 'Proust, Marcel', 'what', 'Remembrance of Things Past', 'when', '1922']
    # or [@ metadata.txt] that contains the metadata to be appdened to the identifier
    def Mint(self, shoulder, args):        
        if(len(args) > 0):
            data = self.formatAnvlRequest(args)   
        else:
            data = None     
        response = self.issueRequest("shoulder/" + self.encode(shoulder), "POST", data)        
        self.printAnvlResponse(response)
        response = response.splitlines()        
        statusLine = response[0].split()        
        if "success" in statusLine[0]:                        
            return statusLine[1]

    # input: identifier
    def View(self, id):
        response = self.issueRequest("id/" + self.encode(id), "GET")
        self.printAnvlResponse(response)

    def Create(self, id, args):
        if(len(args) > 0):
            data = self.formatAnvlRequest(args)
        else:
            data = None
        response = self.issueRequest("id/" + self.encode(id), "PUT", data)
        self.printAnvlResponse(response)

    def Delete(self, id):
        response = self.issueRequest("id/" + self.encode(id), "DELETE")
        self.printAnvlResponse(response)

    def Update(self, id, args):
        if(len(args) > 0):
            data = self.formatAnvlRequest(args)
        else:
            data = None
        resposne = self.issueRequest("id/" + self.encode(id), "POST", data)
        self.printAnvlResponse(resposne)

    def formatAnvlRequest(self, args):
        request = []
        for i in range(0, len(args), 2):
            k = args[i]
            if k == "@":
                f = codecs.open(args[i+1], encoding="UTF-8")
                request += [l.strip("\r\n") for l in f.readlines()]
                f.close()
            else:
                if k == "@@":
                    k = "@"
                else:
                    k = re.sub("[%:\r\n]", lambda c: "%%%02X" % ord(c.group(0)), k)
                v = args[i+1]
                if v.startswith("@@"):
                    v = v[1:]
                elif v.startswith("@") and len(v) > 1:
                    f = codecs.open(v[1:], encoding="UTF-8")
                    v = f.read()
                    f.close()
                v = re.sub("[%\r\n]", lambda c: "%%%02X" % ord(c.group(0)), v)
                request.append("%s: %s" % (k, v))
        return "\n".join(request)

    def encode(self, id):
        return urllib.quote(id, ":/")

    def issueRequest(self, path, method, data=None, returnHeaders=False, streamOutput=False):
        request = urllib2.Request("%s/%s" % (self.__server__, path))
        request.get_method = lambda: method
        if data:
            request.add_header("Content-Type", "text/plain; charset=UTF-8")
            request.add_data(data.encode("UTF-8"))
        if self.__cookie__: request.add_header("Cookie", self.__cookie__)
        try:
            connection = self.__opener__.open(request)
            if streamOutput:
                while True:
                    sys.stdout.write(connection.read(1))
                    sys.stdout.flush()
            else:
                response = connection.read()
                if returnHeaders:
                    return response.decode("UTF-8"), connection.info()
                else:
                    return response.decode("UTF-8")
        except urllib2.HTTPError, e:
            sys.stderr.write("%d %s\n" % (e.code, e.msg))
            if e.fp != None:
                response = e.fp.read()
                if not response.endswith("\n"): response += "\n"
                sys.stderr.write(response)
            sys.exit(1)

    def printAnvlResponse(self, response, sortLines=False):
        response = response.splitlines()                
        if sortLines and len(response) >= 1:            
            statusLine = response[0]            
            response = response[1:]
            response.sort()
            response.insert(0, statusLine)
        for line in response:            
            if self.__options__.formatTimestamps and (line.startswith("_created:") or\
                line.startswith("_updated:")):
                ls = line.split(":")
                line = ls[0] + ": " + time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(int(ls[1])))
            if self.__options__.decode:
                line = re.sub("%([0-9a-fA-F][0-9a-fA-F])",lambda m: chr(int(m.group(1), 16)), line)
            if self.__options__.oneLine: line = line.replace("\n", " ").replace("\r", " ")
            print line.encode(self.__options__.outputEncoding)

if __name__ == '__main__':
    _client = ezidClient('apitest', 'apitest')    
    shoulder = 'ark:/99999/fk4'
    args = ['erc.who', 'API test', 'erc.what', 'test of ezid api', 'erc.when', '2016']

    print "Mint an ezid: "
    identifier = _client.Mint(shoulder, args)        

    print "Get identifier metadata: "
    _client.View(identifier)    

    print "Updating identifier"
    new_args = ['erc.who', 'new API test', 'erc.what', 'new test of ezid api', 'erc.when', '2016']
    _client.Update(identifier, new_args)    

    print "Here are the updated metadata: "
    _client.View(identifier)

    print "Deleting the identifier: "
    _client.Delete(identifier)


    


