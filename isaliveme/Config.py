import yaml
import os

from munch import *

config_file = os.getenv("ISALIVEME_CONFIG", "config.yml")

ManholeNamespace = dict()


class ConfigClass(Munch):
    def __init__(self):
        self.reload()

    def reload(self):
        self.clear()
        self.update(Munch.fromYAML(open(config_file, "r")))

    def save(self):
        txt = self.toYAML()
        open(config_file, "w").write(txt)

    def add_token(self, token_id, person_id, person):
        import uuid

        token = uuid.uuid4().hex
        self.isaliveme.tokens[token] = munchify(
            {
                "token_id": token_id,
                "person_id": person_id,
                "person": person,
            }
        )
        self.save()
        return token


Config = ConfigClass()

ManholeNamespace["add_token"] = Config.add_token
