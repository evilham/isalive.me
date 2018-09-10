from twisted.web import server, resource, static
from twisted.python.filepath import FilePath

import json
import datetime
import os

from .TokenResource import TokenResource


dataDir = FilePath(os.getenv('ISALIVEME_DATA_DIR', 'data'))


class IsAliveMeForbiddenResource(resource.Resource):
    """
    Basic resource serving the update page.
    """
    def render(self, request):
        request.write(FilePath('static/update.html').getContent())
        request.finish()
        return server.NOT_DONE_YET


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
        self.putChild(b'data', static.File(str(dataDir)))

    def processToken(self, token_data, request):
        """
        Create or update the status file for the passed token.

        @param token_data: The object associated with the passed token.
        @param request: The request object associated to this request.
        """

        if not dataDir.isdir():
            dataDir.makedirs(True)

        f = dataDir.child(token_data.person_id + '.json')
        data = dict(lastseen=datetime.datetime.utcnow(),
                    alive=True,
                    source=token_data.token_id,
                    name=token_data.person)
        _bytes = json.dumps(data, default=date_handler).encode('utf-8')
        f.setContent(_bytes)
        f.chmod(0o444)
        return True

    def unauthorizedPage(self):
        """
        Page to show when there is no valid token.
        """
        return IsAliveMeForbiddenResource()


def date_handler(obj):
    """
    json helper for ``datetime.datetime``.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
