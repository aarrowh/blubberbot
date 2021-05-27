import json


class Config():

    def __init__(self):

        self.debug = True

        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.secretsFile = "cfg/config.json"
        self.secrets = self.load_secrets(self.secretsFile)
        self.channel = "cptwalrus"

        self.RESP_TYPES = ["PRIVMSG"]

    def load_secrets(self, filepath):
        with open(filepath, "r") as cfgFile:
            return json.load(cfgFile)
