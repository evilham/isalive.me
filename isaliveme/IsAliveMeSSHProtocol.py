from .conch_helpers import SSHSimpleProtocol

from .Config import Config


class IsAliveMeSSHProtocol(SSHSimpleProtocol):
    def do_add_token(self, token_id, person=None):
        """
        Add and generate a token. Usage: add_token TOKEN_ID [PERSON]

          - TOKEN_ID:
              Will be used to differentiate tokens. May be shown on the site.
          - PERSON (optionl):
              The name that will be shown on the site when using this token.
              Defaults to username.capitalize().
        """
        person_id = self.user.username
        if person is None:
            person = person_id.capitalize()

        # Everything is bytes, we have to go back to unicode before
        try:
            token_id = token_id.decode('utf-8')
            person = person.decode('utf-8')
            person_id = person_id.decode('utf-8')
        except:
            self.terminal.write('Could not decode your arguments.')
            self.terminal.nextLine()
            return

        token = Config.add_token(token_id, person_id, person)
        self.terminal.write('Your new Token is: {}'.format(token))
        self.terminal.nextLine()
