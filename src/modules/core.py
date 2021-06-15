from module import Module
from message import Message

class Core(Module):

    def __init__(self, cfg):

        super().__init__(cfg)
        self.CALLBACKS = {"!so": self.shoutout, "!shoutout": self.shoutout}
        self.COOLDOWNS = {"!so": {"cooldown": 5, "lastcall": 0}}

    def shoutout(self, msg):

        words = msg.message.split(" ")
        homie = words[1]

        resp = f"Checkout the homie {homie} at https://twitch.tv/{homie}!"
        return resp

    def boom(self, msg):
        pass
