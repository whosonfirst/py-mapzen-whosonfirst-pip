# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import requests
import json

class server:

    def __init__(self, **kwargs):

        self.scheme = kwargs.get('scheme', 'http')
        self.hostname = kwargs.get('hostname', 'localhost')
        self.port = kwargs.get('port', 8080)

    def reverse_geocode(self, lat, lon, placetype=None):

        url = self.scheme + "://" + self.hostname

        if self.port:
            url = url + ":%s/" % self.port

        params = { "latitude": lat, "longitude": lon }
        
        if placetype:
            params[ "placetype" ] = placetype

        rsp = requests.get(url, params=params)
        data = json.loads(rsp.content)

        return data

if __name__ == '__main__':

    s = server()
    r = s.reverse_geocode(40.677524,-73.987343)
    
    print r
    
