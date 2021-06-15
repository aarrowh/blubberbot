import socket

from config import Config
from message import Message
from time import sleep
from time import time


cfg = Config()


class BlubberBot():
    def __init__(self, cfg=None):
        if cfg is None:
            raise ValueError("BlubberBot requires a config object")
        self.server = cfg.server
        self.port = cfg.port
        self.io_socket = None
        self.secrets = cfg.secrets
        self.channel = cfg.channel
        self.CALLBACKS = []
        self.MODULES = []

        # {"<module_fn>": <hash> }
        self.MODULE_FILES = {}
        self.LAST_UPDATE = 0

    def get_connection(self):

        self.io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_socket.connect((self.server, self.port))
        self.io_socket.sendall(("PASS " + self.secrets["chat_secret"] + "\r\n").encode('utf-8'))
        self.io_socket.sendall("NICK blubber_bot\r\n".encode('utf-8'))
        if cfg.debug:
            print("sleeping 10")
            sleep(10)

        self.io_socket.sendall("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
        self.io_socket.sendall(f"JOIN #{self.channel}\r\n".encode('utf-8'))

    def run(self):

        self.load_modules()
        self.get_connection()

        while True:
            msg = self.io_socket.recv(2048).decode('utf-8')

            self.parse_msg(msg)

            if self.get_epoch() - self.LAST_UPDATE >= 5:
                self.check_modules()
                self.LAST_UPDATE = self.get_epoch()

    def parse_msg(self, rawMsg):

        cfg.debug_print(rawMsg, "DEBUG")

        msg = Message(rawMsg, cfg)

        # If message is a PING - stop processing and PONG - if message type is unsupported, also don't do anything -
        #   cause it will break stuff
        if msg.message_type == "PING":
            self.send_pong()
            return
        elif msg.message_type in cfg.SERV_MSGS or msg.is_blubberbot:
            return

        if msg.message_type not in cfg.RESP_TYPES:
            return

        for module in self.MODULES:
            trigger = msg.message.split(" ")[0]
            if trigger in module.CALLBACKS:
                cur_time = self.get_epoch()
                if (cur_time - module.COOLDOWNS[trigger]["lastcall"]) < module.COOLDOWNS[trigger]["cooldown"]:
                    break
                module.COOLDOWNS[trigger]["lastcall"] = cur_time
                resp = module.CALLBACKS[trigger](msg)

                if resp is not None:
                    self.send_msg(resp)
                break

    def send_msg(self, msg):
        if self.io_socket is None:
            print("IO socket is None")
            return

        irc_msg = f"PRIVMSG #{self.channel} :{msg}\r\n".encode('utf-8')
        cfg.debug_print(f"Sending: {irc_msg}", "DEBUG")
        self.io_socket.sendall(irc_msg)

    def send_pong(self):
        cfg.debug_print("SENDING PONG", "DEBUG")
        irc_msg = "PONG :tmi.twitch.tv\r\n".encode('utf-8')
        self.io_socket.sendall(irc_msg)

    def load_modules(self):

        '''
        get list of all *.py files
        remove first 2 characters (numbers) should we skip files that don't follow convention? - append to end?
        import all of them - need to import at global scope, not local
        create module object in self.modules, and register callbacks in self.CALLBACKS
        '''
        from os import listdir
        module_list = listdir(f"src/{cfg.modules_dir}")
        for module_fn in module_list:
            # this is very weak detection
            if module_fn == "__init__.py" or ".py" not in module_fn:
                continue
            self.load_module(module_fn)
        self.LAST_UPDATE = self.get_epoch()

    def load_module(self, module_fn):

        import importlib
            # if we get here, in theory loading the module won't crash everything
        class_name = module_fn[:-3]
        class_name = f"{class_name[0].upper()}{class_name[1:]}"
        module_name = f"{cfg.modules_dir}.{module_fn[:-3]}"
        module = importlib.import_module(module_name, class_name)

        try:
            _class = getattr(module, class_name)
            module_instance = _class(cfg)
            self.MODULES.append(module_instance)
            # {"<module_fn>": <mtime> }
            if module_fn not in self.MODULE_FILES:
                self.MODULE_FILES[module_fn] = {}
            self.MODULE_FILES[module_fn]["mtime"] = self.get_mtime(f"src/{cfg.modules_dir}/{module_fn}")
            self.MODULE_FILES[module_fn]["module"] = module

        except Exception:
            import pdb; pdb.set_trace()
            cfg.debug_print(f"Failed to load/instantiate {module_name}.{class_name}", "ERROR")

    def get_mtime(self, module_fn):

        from pathlib import Path
        mod = Path(module_fn)
        return mod.stat().st_mtime

    def get_epoch(self):

        return time()

    def check_modules(self):

        from importlib import reload
        for module_fn in self.MODULE_FILES:
            cur_mtime = self.get_mtime(f"src/{cfg.modules_dir}/{module_fn}")
            if cur_mtime > self.MODULE_FILES[module_fn]["mtime"]:

                cfg.debug_print(f"Reloading module: {module_fn}")
                reload(self.MODULE_FILES[module_fn]["module"])
                self.MODULE_FILES[module_fn]["mtime"] = cur_mtime


def main():

    '''
    OAUTH SUCKS - fix this later... 

    test = cfg.helix.is_moderator("blubberbot")
    cfg.debug_print(f"Blubber bot is a mod: {test}")
    exit()
    '''

    bot = BlubberBot(cfg)
    bot.run()


if __name__ == "__main__":
    main()
