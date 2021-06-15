from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

class Helix():

    def __init__(self, cfg):

        self.twitch = Twitch(cfg.secrets["app_id"], cfg.secrets["helix_secret"])
        self.twitch.authenticate_app([])
        self.channel_info = self.twitch.get_users(logins=['blubberbot'])
        self.channel_id = self.channel_info['data'][0]['id']

        self.scope = [AuthScope.MODERATION_READ]
        self.auth = UserAuthenticator(self.twitch, self.scope, force_verify=False)

        self.token, self.refresh_token = self.auth.authenticate()
        self.twitch.set_user_authentication(self.token, self.scope, self.refresh_token)
        import pdb; pdb.set_trace()

    def is_moderator(self, name):

        modlist = self.twitch.get_moderators(self.channel_id)
        #modlist = self.twitch.get_stream_tags(self.channel_id)
        return modlist
        if name in modlist:
            return True

        return False
