from module import Module


class Testmodule(Module):

    def __init__(self, cfg):
        super().__init__(cfg)

        self.CALLBACKS = {"!foo": self.foo, "!test": self.test, "$bar": self.bar}
        self.COOLDOWNS = {"!foo": { "cooldown": 5, "lastcall": 0}, 
                "!test": { "cooldown": 10, "lastcall": 0}, 
                "!bar": { "cooldown": 10, "lastcall": 0}}

    async def foo(self, msg):
        await self.ctx.send_msg(f"Foo me {msg.user}?! No FOO YOU!")

    async def test(self, msg):
        await self.ctx.send_msg(f"{msg.user} called the FAKE command")

    async def bar(self, msg):
        await self.cfg.debug_print(f"BAR was called by {msg.user}")
