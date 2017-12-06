#!/usr/bin/env python3

# Run with twistd -ny app.py

from twisted.internet import reactor, endpoints
from twisted.application import service, strports
from twisted.application.internet import ClientService
from twisted.web import server

# Load config
from isaliveme import Config, ManholeNamespace

# Setup application
from isaliveme import IsAliveMeTokenResource
application = service.Application('IsAlive.me')
serv_collection = service.IServiceCollection(application)

# TokenResource
site = server.Site(IsAliveMeTokenResource(tokens=Config.isaliveme.tokens))
i = strports.service(Config.isaliveme.endpoint, site)
i.setServiceParent(serv_collection)


# Set up SSH config service
from isaliveme import conch_helper, IsAliveMeSSHProtocol
i = conch_helper(
    Config.manhole.endpoint,
    namespace=ManholeNamespace,
    proto=IsAliveMeSSHProtocol,
    keyDir=Config.manhole.keyDir,
    keySize=Config.manhole.keySize)
i.setServiceParent(serv_collection)
