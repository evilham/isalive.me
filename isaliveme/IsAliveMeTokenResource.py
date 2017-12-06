from twisted.web import server, resource, static
from twisted.python.filepath import FilePath

import json
import datetime


from .TokenResource import TokenResource

class IsAliveMeTokenResource(TokenResource):
    """
    TokenResource used for isalive.me.

    It shows a README.public file if no valid Token is passed and
    creates or updates the status file for any valid tokens.
    """
    HEADER = 'Auth-Token'

    def __init__(self, tokens=dict()):
        TokenResource.__init__(self, tokens=tokens)
        self.putChild(b'', static.File('static/index.html'))
        self.putChild(b'static', static.File('static'))
        self.putChild(b'data', static.File('data'))

    def processToken(self, token_data, request):
        """
        Create or update the status file for the passed token.

        @param token_data: The object associated with the passed token.
        @param request: The request object associated to this request.
        """

        dataDir = FilePath('data')
        if not dataDir.isdir():
            dataDir.makedirs(True)

        f = FilePath('data').child(token_data.person_id + '.json')
        data = dict(lastseen=datetime.datetime.utcnow(),
                    alive=True,
                    source=token_data.token_id,
                    name=token_data.person)
        _bytes = json.dumps(data, default=date_handler).encode('utf-8')
        f.setContent(_bytes)
        f.chmod(0o444)
        return True

    def unauthorizedMessage(self):
        """
        Message to show when there is no valid token.
        """
        try:
            content = FilePath('README.public').getContent().decode('utf-8')
        except:
            content = ''
        return "<pre>{}</pre>".format(content)


def date_handler(obj):
    """
    json helper for ``datetime.datetime``.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
