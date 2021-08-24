import socket
import asyncio

from config import Config
from message import Message
from helix import Helix
from time import sleep
from time import time


class BlubberBot():
    def __init__(self):
        self.cfg = Config()
        self.server = self.cfg.server
        self.port = self.cfg.port
        self.io_socket = None
        self.io_reader = None
        self.io_writer = None
        self.secrets = self.cfg.secrets
        self.channel = self.cfg.channel
        self.CALLBACKS = []
        self.MODULES = []

        # {"<module_fn>": <hash> }
        self.MODULE_FILES = {}
        self.LAST_UPDATE = 0

    async def get_async_connection(self):

        self.io_reader, self.io_writer = await asyncio.open_connection(self.server, self.port)

        self.io_writer.write(("PASS " + self.secrets["chat_secret"] + "\r\n").encode('utf-8'))
        await self.io_writer.drain()
        self.io_writer.write("NICK blubber_bot\r\n".encode('utf-8'))
        await self.io_writer.drain()
        if self.cfg.debug:
            print("sleeping 5")
            await asyncio.sleep(5)

        self.io_writer.write("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
        await self.io_writer.drain()
        self.io_writer.write(f"JOIN #{self.channel}\r\n".encode('utf-8'))
        await self.io_writer.drain()

    def get_connection(self):

        self.io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_socket.connect((self.server, self.port))
        self.io_socket.sendall(("PASS " + self.secrets["chat_secret"] + "\r\n").encode('utf-8'))
        self.io_socket.sendall("NICK blubber_bot\r\n".encode('utf-8'))
        if self.cfg.debug:
            print("sleeping 5")
            sleep(10)

        self.io_socket.sendall("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
        self.io_socket.sendall(f"JOIN #{self.channel}\r\n".encode('utf-8'))

    async def run(self):

        await self.load_modules()
        await self.get_async_connection()
        # self.helix = Helix(self.cfg)

        while True:
            try:
                msg = await self.receive_msg()
                await self.parse_msg(msg)
            except asyncio.IncompleteReadError:
                pass

            ''' can replace this code with async timers
            if self.get_epoch() - self.LAST_UPDATE >= 5:
                self.check_modules()
                self.LAST_UPDATE = self.get_epoch()
            '''

    async def receive_msg(self):
        msg = await self.io_reader.readuntil()
        return msg.decode('utf-8')

    async def parse_msg(self, rawMsg):

        self.cfg.debug_print(rawMsg, "DEBUG")

        msg = Message(rawMsg, self.cfg)

        # If message is a PING - stop processing and PONG - if message type is unsupported, also don't do anything -
        #   cause it will break stuff
        if msg.message_type == "PING":
            self.send_pong()
            return
        elif msg.message_type in self.cfg.SERV_MSGS or msg.is_blubberbot:
            return

        if msg.message_type not in self.cfg.RESP_TYPES:
            return

        for module in self.MODULES:
            trigger = msg.message.split(" ")[0]
            if trigger in module.CALLBACKS:
                cur_time = await self.get_epoch()
                if (cur_time - module.COOLDOWNS[trigger]["lastcall"]) < module.COOLDOWNS[trigger]["cooldown"]:
                    break
                module.COOLDOWNS[trigger]["lastcall"] = cur_time
                await module.CALLBACKS[trigger](msg)

    async def send_msg(self, msg):
        if self.io_writer is None:
            print("IO socket is None")
            return

        irc_msg = f"PRIVMSG #{self.channel} :{msg}\r\n".encode('utf-8')
        self.cfg.debug_print(f"Sending: {irc_msg}", "DEBUG")
        self.io_writer.write(irc_msg)
        await self.io_writer.drain()

    async def send_pong(self):
        self.cfg.debug_print("SENDING PONG", "DEBUG")
        irc_msg = "PONG :tmi.twitch.tv\r\n".encode('utf-8')
        await self.io_writer.write(irc_msg)

    async def load_modules(self):

        '''
        get list of all *.py files
        remove first 2 characters (numbers) should we skip files that don't follow convention? - append to end?
        import all of them - need to import at global scope, not local
        create module object in self.modules, and register callbacks in self.CALLBACKS
        '''
        from os import listdir
        module_list = listdir(f"src/{self.cfg.modules_dir}")
        for module_fn in module_list:
            # this is very weak detection
            if module_fn == "__init__.py" or ".py" not in module_fn:
                continue
            await self.load_module(module_fn)
        self.LAST_UPDATE = await self.get_epoch()

    async def load_module(self, module_fn):

        import importlib
            # if we get here, in theory loading the module won't crash everything
        class_name = module_fn[:-3]
        class_name = f"{class_name[0].upper()}{class_name[1:]}"
        module_name = f"{self.cfg.modules_dir}.{module_fn[:-3]}"
        module = importlib.import_module(module_name, class_name)

        try:
            _class = getattr(module, class_name)
            module_instance = _class(self)
            self.MODULES.append(module_instance)
            # {"<module_fn>": <mtime> }
            if module_fn not in self.MODULE_FILES:
                self.MODULE_FILES[module_fn] = {}
            self.MODULE_FILES[module_fn]["mtime"] = await self.get_mtime(f"src/{self.cfg.modules_dir}/{module_fn}")
            self.MODULE_FILES[module_fn]["module"] = module

        except Exception:
            import pdb; pdb.set_trace()
            self.cfg.debug_print(f"Failed to load/instantiate {module_name}.{class_name}", "ERROR")

    async def get_mtime(self, module_fn):

        from pathlib import Path
        mod = Path(module_fn)
        return mod.stat().st_mtime

    async def get_epoch(self):

        return time()

    async def check_modules(self):

        from importlib import reload
        for module_fn in self.MODULE_FILES:
            cur_mtime = await self.get_mtime(f"src/{self.cfg.modules_dir}/{module_fn}")
            if cur_mtime > self.MODULE_FILES[module_fn]["mtime"]:

                self.cfg.debug_print(f"Reloading module: {module_fn}")
                reload(self.MODULE_FILES[module_fn]["module"])
                self.MODULE_FILES[module_fn]["mtime"] = cur_mtime


def main():

    # test = cfg.helix.is_moderator("blubberbot")
    # cfg.debug_print(f"Blubber bot is a mod: {test}")

    bot = BlubberBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
