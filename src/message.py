from config import Config

class Message():

    def __init__(self, raw_msg, cfg=None):

        if cfg is None:
            raise ValueError("Message requires a Config object")

        self.cfg = cfg
        self.raw_data = raw_msg
        self.is_blubberbot = False
        self.message_type = self.get_message_type()

        if self.message_type not in cfg.RESP_TYPES or self.message_type in cfg.SERV_MSGS:
            return

        self.user = self.get_user()
        if self.user == "blubber_bot":
            self.is_blubberbot = True
            return

        self.message = self.get_message()
        self.channel = self.get_channel()

    def get_user(self):

        m = self.raw_data.split(":", 2)
        user = m[1][:m[1].find("!")]
        return user

    def get_message(self):
        m = self.raw_data.split(":", 2)
        msg_text = m[2].rstrip()
        return msg_text

    def get_message_type(self):

        # TODO: We get random messages with a blank message - Figure out why, and fix it - 99% chance my fault.

        try:
            msg = self.raw_data.split(" ")
            if msg[0] == "PING":
                return "PING"
            elif msg[0] == ":tmi.twitch.tv" or "blubber_bot" in msg[0]:
                return "SRV"
            return msg[1]
        except IndexError:
            return "SRV"

    def get_channel(self):
        # Could split on '#' and get channel name that way
        msg = self.raw_data.split("#")
        return msg[1][:msg[1].find(" ")]
