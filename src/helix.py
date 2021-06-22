from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

class Helix():

    def __init__(self, cfg):

        self.scope = [AuthScope.MODERATION_READ]
        self.twitch = Twitch(cfg.secrets["helix_id"], cfg.secrets["helix_secret"], target_app_auth_scope=self.scope)
        self.twitch.authenticate_app([])
        self.channel_info = self.twitch.get_users(logins=['cptwalrus'])
        self.channel_id = self.channel_info['data'][0]['id']

        self.auth = UserAuthenticator(self.twitch, self.scope)
        self.token, self.refresh_token = self.auth.authenticate()
        self.twitch.set_user_authentication(self.token, self.scope, self.refresh_token)
        self.modlist = self.twitch.get_moderators(self.channel_id)

    def is_moderator(self, name):

        if name in self.modlist:
            return True

        return False
