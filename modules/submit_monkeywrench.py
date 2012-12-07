import httplib
import urllib

class MonkeyWrench():
    def __init__(self):
        self.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        self.conn = httplib.HTTPConnection("monkeywrench.de:80")

    def submit_monkeywrench(self, url):
        params = urllib.urlencode({'url': url + "&check=Check"})
        self.conn.request("POST", "/index.html", params, self.headers)
        response = self.conn.getresponse()
        print "Submission result: ", response.status, response.reason
        #data = response.read()
        self.conn.close()