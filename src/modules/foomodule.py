from module import Module


class Foomodule(Module):

    def __init__(self, cfg):
        super().__init__(cfg)

        self.CALLBACKS = {"!fizz": self.foo, "!buzz": self.test, "$bar": self.bar}

    def foo(self, msg):
        resp = f"Foo me {msg.user}?! No FOO YOU!"
        return resp

    def test(self, msg):
        resp = f"{msg.user} called the test command"
        return resp

    def bar(self, msg):
        self.cfg.debug_print(f"BAR was called by {msg.user}")
