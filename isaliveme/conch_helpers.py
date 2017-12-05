from twisted.cred import portal
from twisted.conch.manhole_tap import chainedProtocolFactory
from twisted.conch import manhole_ssh
from twisted.conch.ssh import keys
from twisted.conch.checkers import IAuthorizedKeysDB, SSHPublicKeyChecker
from twisted.conch.checkers import readAuthorizedKeyFile

from twisted.python import filepath

from zope.interface import implementer

from twisted.application import service, strports


@implementer(IAuthorizedKeysDB)
class SSHKeyDirectory(object):
    """
    Provides SSH public keys based on a simple directory structure.

    For a user ``USER`` following files are returned if they exist:
      - ``$USER/*.key``
      - ``$USER.key``
    These paths are relative to L{SSHKeyDirectory.baseDir}

    @ivar baseDir: the base directory for key lookup.
    """
    def __init__(self, baseDir, parseKey=keys.Key.fromString):
        """
        Initialises a new L{SSHKeyDirectory}.

        @param base_dir: the base directory for key lookup.
        @param parseKey: L{callable}
        """
        self.baseDir = baseDir
        self.parseKey = parseKey


    def getAuthorizedKeys(self, username):
        userKeys = []
        keyFile = self.baseDir.child(username + b'.key')
        keyDir = self.baseDir.child(username)
        print(keyFile, keyDir)

        if keyFile.isfile():
            for key in readAuthorizedKeyFile(keyFile.open(), self.parseKey):
                yield key

        if keyDir.isdir():
            for f in keyDir.globChildren('*.key'):
                for key in readAuthorizedKeyFile(f.open(), self.parseKey):
                    yield key


def conch_helper(endpoint, namespace=dict(), keyDir=None, keySize=4096):
    """
    Return a L{SSHKeyDirectory} based SSH service with the given parameters.

    Authorized keys are read as per L{SSHKeyDirectory} with ``baseDir`` being
    ``keyDir/users``.

    @param endpoint: endpoint for the SSH service
    @param namespace: the manhole namespace
    @param keyDir: directory that holds server/server.key file and
        users directory, which is used as ``baseDir`` in L{SSHKeyDirectory}
    @see: L{SSHKeyDirectory}
    """
    if keyDir is None:
        from twisted.python._appdirs import getDataDirectory
        keyDir = getDataDirectory()

    keyDir = filepath.FilePath(keyDir)
    keyDir.child('server').makedirs(True)
    keyDir.child('users').makedirs(True)

    checker = SSHPublicKeyChecker(SSHKeyDirectory(keyDir.child('users')))

    sshRealm = manhole_ssh.TerminalRealm()
    sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)
    sshPortal = portal.Portal(sshRealm, [checker])


    sshKeyPath = keyDir.child('server').child('server.key')
    sshKey = keys._getPersistentRSAKey(sshKeyPath, keySize)

    sshFactory = manhole_ssh.ConchFactory(sshPortal)
    sshFactory.publicKeys[b'ssh-rsa'] = sshKey
    sshFactory.privateKeys[b'ssh-rsa'] = sshKey

    sshService = strports.service(endpoint, sshFactory)
    return sshService
