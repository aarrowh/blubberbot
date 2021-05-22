import json
import time
import socket
import argparse

DEBUG = False


def irc_print(msg, level='MSG'):
    global DEBUG

    if level.upper() not in ['ERROR', 'DEBUG', 'INFO', 'MSG']:
        return

    # TODO this will be in a utils file later, and DEBUG will be maintained in a cfg obj
    if level.upper() == 'DEBUG' and not DEBUG:
        return

    print(f"[{level.upper()}]\t{msg}")


class BlubberBot():
    def __init__(self, server="irc.chat.twitch.tv", port=6667, cfg="cfg/config.json", channel="cptwalrus"):
        self.server = server
        self.port = port
        self.io_socket = None
        self.cfg = self.load_cfg(cfg)
        self.channel = channel

    def get_connection(self):

        self.io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_socket.connect((self.server, self.port))
        self.io_socket.sendall(("PASS " + self.cfg["secret"] + "\r\n").encode('utf-8'))
        self.io_socket.sendall("NICK blubber_bot\r\n".encode('utf-8'))
        print("sleeping 5")
        time.sleep(5)
        self.io_socket.sendall("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
        self.io_socket.sendall(f"JOIN #{self.channel}\r\n".encode('utf-8'))

    def load_cfg(self, filepath):
        with open(filepath, "r") as cfgFile:
            return json.load(cfgFile)

    # TODO: Want to add console to manage loaded modules - way more work haha
    # TODO: Parse messages - create PONG so I don't keep getting disconnected
    def run(self):
        while True:
            msg = self.io_socket.recv(2048).decode('utf-8')
            # print(msg)

            # Need to actually parse/process messages - though I like the idea of a terminal chat
            self.parse_msg(msg)

    def parse_msg(self, msg):

        # CONFIG
        RESP_TYPES = ["PRIVMSG"]
        msg_type = msg.split()[1]

        # TODO this whole thing needs to not be nasty - no way PONG currently works
        # need to detect PING in the first part of message but the number of times
        # I have already split this string hurts me

        if msg_type == "PING":
            self.send_pong()
            return

        if msg_type not in RESP_TYPES:
            return

        f = msg.split(":", 2)
        user = f[1][:f[1].find("!")]
        msg_text = f[2].rstrip()

        if msg_text[0] == "!":
            irc_print("Command detected", "INFO")
            if msg_text.split(" ")[0][1:].lower() == "test":
                irc_print("TEST COMMAND CALLED", "INFO")
                resp = f"{user} called the test command"
                self.send_msg(resp)

    def send_msg(self, msg):
        if self.io_socket is None:
            print("IO socket is None")
            return

        irc_msg = f"PRIVMSG #{self.channel} :{msg}\r\n".encode('utf-8')
        print(irc_msg)
        self.io_socket.sendall(irc_msg)

    def send_pong(self):
        irc_print("SENDING PONG", "INFO")
        irc_msg = "PONG :tmi.twitch.tv\r\n"
        self.io_socket.sendall(irc_msg)


def main():
    irc_print("DEBUG TEST", "DEBUG")
    exit()
    bot = BlubberBot()
    bot.get_connection()
    bot.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    DEBUG = args.debug

# TODO: Need to move stuff into different files to make this make sense - need a config.py to manage global debug/logging state

    main()
