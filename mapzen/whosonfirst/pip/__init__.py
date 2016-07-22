# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import requests
import json

class base:

    def point_in_poly(self, endpoint, lat, lon, **kwargs):

        params = { "latitude": lat, "longitude": lon }
        
        for k, v in kwargs.items():
            params[k] = v

        rsp = requests.get(endpoint, params=params)
        data = json.loads(rsp.content)

        return data

# https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server

class server(base):

    def __init__(self, **kwargs):

        self.scheme = kwargs.get('scheme', 'http')
        self.hostname = kwargs.get('hostname', 'localhost')
        self.port = kwargs.get('port', 8080)

    def reverse_geocode(self, lat, lon, **kwargs):

        url = self.scheme + "://" + self.hostname

        if self.port:
            url = url + ":%s/" % self.port

        return self.point_in_poly(url, lat, lon, **kwargs)

# https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-proxy

class proxy(base):

    def __init__(self, **kwargs):

        self.scheme = kwargs.get('scheme', 'http')
        self.hostname = kwargs.get('hostname', 'localhost')
        self.port = kwargs.get('port', 1111)

    def reverse_geocode(self, target, lat, lon, **kwargs):

        url = self.scheme + "://" + self.hostname

        if self.port:
            url = url + ":%s/" % self.port

        url = url + target

        return self.point_in_poly(url, lat, lon, **kwargs)

if __name__ == '__main__':

    for t in ('locality', 'neighbourhood'):

        p = proxy()
        r = p.reverse_geocode(t, 40.677524,-73.987343)
        
        print "%s %s" % (t, r)    
