import httplib
import urllib

class MonkeyWrench():
    """
    This simple class submits a URL to the monkeywrench.de URL analyzing
    service. It just returns if the submission was successful. This will
    be enhanced later.
    """
    def __init__(self, logger):
        self.logger = logger
        # Set header and define connection
        self.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        self.conn = httplib.HTTPConnection("monkeywrench.de:80")

    def submit_monkeywrench(self, url):
        # Submit the URL
        params = urllib.urlencode({'url': url + "&check=Check"})
        self.conn.request("POST", "/index.html", params, self.headers)
        response = self.conn.getresponse()
        self.logger.log_console("monkeywrench.de submission result: %s %s" % (response.status, response.reason), "debug")
        #data = response.read()
        self.conn.close()