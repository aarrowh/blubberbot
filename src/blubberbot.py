import time
import socket
import argparse

from config import Config
from message import Message

cfg = Config()


def irc_print(msg, level='MSG'):

    if level.upper() not in ['ERROR', 'DEBUG', 'INFO', 'MSG']:
        return

    if level.upper() == 'DEBUG' and not cfg.debug:
        return

    print(f"[{level.upper()}]\t{msg}")


class BlubberBot():
    def __init__(self, cfg=None):
        if cfg is None:
            raise ValueError("BlubberBot requires a config object")
        self.server = cfg.server
        self.port = cfg.port
        self.io_socket = None
        self.secrets = cfg.secrets
        self.channel = cfg.channel

    def get_connection(self):

        self.io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_socket.connect((self.server, self.port))
        self.io_socket.sendall(("PASS " + self.secrets["secret"] + "\r\n").encode('utf-8'))
        self.io_socket.sendall("NICK blubber_bot\r\n".encode('utf-8'))
        print("sleeping 5")
        time.sleep(5)
        self.io_socket.sendall("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
        self.io_socket.sendall(f"JOIN #{self.channel}\r\n".encode('utf-8'))


    def run(self):
        while True:
            msg = self.io_socket.recv(2048).decode('utf-8')
            # print(msg)

            # Need to actually parse/process messages - though I like the idea of a terminal chat
            self.parse_msg(msg)

    def parse_msg(self, rawMsg):

        irc_print(rawMsg, "DEBUG")

        msg = Message(rawMsg, cfg)

        # If message is a PING - stop processing and PONG - if message type is unsupported, also don't do anything -
        #   cause it will break stuff
        if msg.is_ping:
            self.send_pong()
            return
        elif msg.is_server_message or msg.is_blubberbot:
            return

        if msg.message_type not in cfg.RESP_TYPES:
            return

        if msg.message[0] == "!":
            irc_print("Command detected", "INFO")
            if msg.message.split(" ")[0][1:].lower() == "test":
                irc_print("TEST COMMAND CALLED", "INFO")
                resp = f"{msg.user} called the test command"
                self.send_msg(resp)

    def send_msg(self, msg):
        if self.io_socket is None:
            print("IO socket is None")
            return

        irc_msg = f"PRIVMSG #{self.channel} :{msg}\r\n".encode('utf-8')
        irc_print(f"Sending: {irc_msg}", "DEBUG")
        self.io_socket.sendall(irc_msg)

    def send_pong(self):
        irc_print("SENDING PONG", "DEBUG")
        irc_msg = "PONG :tmi.twitch.tv\r\n".encode('utf-8')
        self.io_socket.sendall(irc_msg)


def main():
    bot = BlubberBot(cfg)
    bot.get_connection()
    bot.run()


if __name__ == "__main__":
    main()
