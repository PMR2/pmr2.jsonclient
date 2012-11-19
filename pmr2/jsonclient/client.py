import json
import urllib2


class PMR2Client(object):

    _opener = urllib2.build_opener()

    site = None
    _accept = 'application/vnd.physiome.pmr2.json.0'
    _auth = ''
    _ua = 'PMR2Client/0.1'
    lasturl = None

    dashboard = None

    def __init__(self):
        pass
        # XXX to be customized.
    
    def buildRequest(self, url, data=None, headers=None):
        base_headers = {
            'Authorization': self._auth, 
            'Accept': self._accept,
            'User-Agent': self._ua,
        }

        all_headers = {}
        # Can't decide who to give precedence to.
        if headers:
            all_headers.update(headers)
        all_headers.update(base_headers)

        if data and not isinstance(data, basestring):
            data = json.dumps(data)

        request = urllib2.Request(url, data=data, headers=all_headers)
        return request

    def open(self, request):
        return self._opener.open(request)

    def getResponse(self, url, data=None):
        request = self.buildRequest(url, data)
        fp = self.open(request)
        self.lasturl = fp.geturl()

        if fp.headers.get('Content-Type') != self._accept:
            # some kind of error?
            raise ValueError('Content-Type mismatch')

        result = json.load(fp)
        fp.close()
        return result

    def setSite(self, site):
        self.site = site

    def setCredentials(self, basic=None, oauth=None):
        if oauth:
            raise NotImplementedError('OAuth support not implemented')

        login = basic.get('login', '')
        password = basic.get('password', '')
        self._auth = 'Basic ' + ('%s:%s' % (login, password)).encode('base64')

    def updateDashboard(self):
        url = '%s/pmr2-dashboard' % self.site
        result = self.getResponse(url)
        self.dashboard = result

    def getDashboard(self):
        if self.dashboard is None:
            self.updateDashboard()
        return self.dashboard

    def getMethod(self, name):
        action = self.dashboard[name]
        # Can't have unicode.
        url = str(action['target'])
        response = self.getResponse(url)
        # Uhh this will have a reference to this object, maybe track
        # that somehow?
        return PMR2Method(self, self.lasturl, response)


class PMR2Method(object):

    def __init__(self, context, url, obj):
        self.context = context
        self._obj = obj
        self.url = url

    def fields(self):
        return self._obj['fields']

    def actions(self):
        return self._obj['actions']

    def call(self, action, fields):
        data = {}
        data['actions'] = {action: '1'}
        data['fields'] = fields
        result = self.context.getResponse(self.url, data)
        return result