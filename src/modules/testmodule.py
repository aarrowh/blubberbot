from module import Module


class Testmodule(Module):

    def __init__(self, cfg):
        super().__init__(cfg)

        self.CALLBACKS = {"!foo": self.foo, "!test": self.test, "$bar": self.bar}
        self.COOLDOWNS = {"!foo": { "cooldown": 5, "lastcall": 0}, 
                "!test": { "cooldown": 10, "lastcall": 0}, 
                "!bar": { "cooldown": 10, "lastcall": 0}}

    def foo(self, msg):
        resp = f"Foo me {msg.user}?! No FOO YOU!"
        return resp

    def test(self, msg):
        resp = f"{msg.user} called the FAKE command"
        return resp

    def bar(self, msg):
        self.cfg.debug_print(f"BAR was called by {msg.user}")
