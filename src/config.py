import json

from helix import Helix


class Config():

    def __init__(self):

        self.debug = True

        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.secretsFile = "cfg/config.json"
        self.secrets = self.load_secrets(self.secretsFile)
        self.channel = "cptwalrus"
        self.modules_dir = "modules"

        self.RESP_TYPES = ["PRIVMSG"]
        self.SERV_MSGS = ["PING", "SRV"]

        #self.helix = Helix(self)

    def load_secrets(self, filepath):
        with open(filepath, "r") as cfgFile:
            return json.load(cfgFile)

    def debug_print(self, msg, level='MSG'):

        if level.upper() not in ['ERROR', 'DEBUG', 'INFO', 'MSG']:
            return

        if level.upper() == 'DEBUG' and not self.debug:
            return

        print(f"[{level.upper()}]\t{msg}")
