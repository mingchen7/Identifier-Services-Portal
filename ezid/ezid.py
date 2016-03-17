# The ezidClient is modified based on the ezid command line tool as interface to call ezid service
# original author: Greg Janee <gjanee@ucop.edu>
# May 2013
# Link to the original version: http://ezid.cdlib.org/doc/ezid-client.py

# import codecs
# import optparse
import re
import sys
import time
import types
import urllib
import urllib2

class MyHTTPErrorProcessor (urllib2.HTTPErrorProcessor):
    def http_response (self, request, response):
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
        self.__options__["decode"] = False
        self.__options__["outputEncoding"] = "UTF-8"
        self.__options__["oneLine"] = False
        self.__options__["formatTimestamps"] = True

        self.__server__ = "https://ezid.cdlib.org"
        self.__opener__ = urllib2.build_opener(MyHTTPErrorProcessor())
        self.__cookie__ = None

        self.handler(user, password)

    def handler(self, user, password):
        handler = urllib2.HTTPBasicAuthHandler()
        handler.add_password("EZID", self.__server__, user, password)
        self.__opener__.add_handler(handler)
    
    def Mint(self, shoulder, metadata):        
        if(len(metadata) > 0):
            anvl = self.formatAnvlRequest(metadata)
        else:
            anvl = None     
        print anvl
        response = self.issueRequest("shoulder/" + self.encode(shoulder), "POST", anvl)                        
        response = self.parseAnvlResponse(response)
        if "success" in response.keys():
            return response["success"]            
    
    def View(self, id):
        response = self.issueRequest("id/" + self.encode(id), "GET")
        self.printAnvlResponse(response)
        response = self.parseAnvlResponse(response)
        return response

    def Create(self, id, metadata):
        if(len(metadata) > 0):
            anvl = self.formatAnvlRequest(metadata)
        else:
            anvl = None
        response = self.issueRequest("id/" + self.encode(id), "PUT", anvl)
        self.printAnvlResponse(response)

    def Delete(self, id):
        response = self.issueRequest("id/" + self.encode(id), "DELETE")
        self.printAnvlResponse(response)

    def Update(self, id, metadata):
        if(len(metadata) > 0):
            anvl = self.formatAnvlRequest(metadata)
        else:
            anvl = None
        response = self.issueRequest("id/" + self.encode(id), "POST", anvl)        
        response = self.parseAnvlResponse(response)
        return response

    def escape(self, s):
        return re.sub("[%:\r\n]", lambda c: "%%%02X" % ord(c.group(0)), s)

    def unescape(self, s):
        return re.sub("%([0-9A-Fa-f][0-9A-Fa-f])", lambda m: chr(int(m.group(1), 16)), s)

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

    def formatAnvlRequest(self, metadata):
        anvl = "\n".join("%s: %s" % (self.escape(name), self.escape(value)) for name, 
                value in metadata.items()).encode(self.__options__["outputEncoding"])
        return anvl

    def parseAnvlResponse(self, response):
        metadata = dict(tuple(self.unescape(v).strip() for v in l.split(":", 1)) \
            for l in response.decode("UTF-8").splitlines())
        return metadata
    
    def printAnvlResponse(self, response, sortLines=False):
        response = response.splitlines()                
        if sortLines and len(response) >= 1:            
            statusLine = response[0]            
            response = response[1:]
            response.sort()
            response.insert(0, statusLine)
        for line in response:            
            if self.__options__["formatTimestamps"] and (line.startswith("_created:") or\
                line.startswith("_updated:")):
                ls = line.split(":")
                line = ls[0] + ": " + time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(int(ls[1])))
            if self.__options__["decode"]:
                line = re.sub("%([0-9a-fA-F][0-9a-fA-F])",lambda m: chr(int(m.group(1), 16)), line)
            if self.__options__["oneLine"]: line = line.replace("\n", " ").replace("\r", " ")
            print line.encode(self.__options__["outputEncoding"])

if __name__ == '__main__':
    _client = ezidClient('apitest', 'apitest')    
    shoulder = 'ark:/99999/fk4'    

    metadata = {}
    metadata["erc.who"] = 'API test'
    metadata["erc.what"] = 'test of ezid api'
    metadata["erc.when"] = '2016'

    print "Mint an ezid: "
    identifier = _client.Mint(shoulder, metadata)        

    print "Get identifier metadata: "
    _client.View(identifier)    

    print "Updating identifier"
    metadata_new = {}
    metadata_new["erc.who"] = 'new API test'
    metadata_new["erc.what"] = 'new test of ezid api'
    metadata_new["erc.when"] = '2016'
    
    new_args = ['erc.who', 'new API test', 'erc.what', 'new test of ezid api', 'erc.when', '2016']
    _client.Update(identifier, metadata_new)    

    print "Here are the updated metadata: "
    _client.View(identifier)

    # DELETING IS NOT SUPPORTED BY THE TEST ACCOUNT
    # print "Deleting the identifier: "
    # _client.Delete(identifier)


    


