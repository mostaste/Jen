########################################################################
###################            Libraries             ###################

import argparse
import threading

from node import Blueprint
from settings import Settings

########################################################################
#####################             Fay              #####################

class FayOS:
    def __init__(self, settings, blueprint):
        self.Settings   = settings
        self.Blueprint  = blueprint
        self.Handlers()

    def Handlers(self):
        # Command Handlers
        self.Blueprint.StartHandler()
        self.Blueprint.SystemHandler()
        self.Blueprint.SysHandler()
        self.Blueprint.HelpHandler()
        self.Blueprint.ChatIDHandler()
        self.Blueprint.ClientHandler()
        self.Blueprint.ModelHandler()
        self.Blueprint.TokenHandler()
        self.Blueprint.DrawSizeHandler()
        self.Blueprint.GoodHandler()
        self.Blueprint.BadHandler()
        self.Blueprint.RefreshHandler()
        self.Blueprint.SummaryHandler()
        self.Blueprint.OptionHandler()
        self.Blueprint.VoiceHandler()
        self.Blueprint.SenseHandler()
        self.Blueprint.SpeakHandler()
        self.Blueprint.ListenHandler()
        self.Blueprint.VisionHandler()
        self.Blueprint.TextHandler()
        self.Blueprint.DrawHandler()
        self.Blueprint.WebHandler()

        # Vector Handlers
        self.Blueprint.VectorHandler()
        self.Blueprint.EmbedHandler()
        self.Blueprint.ProfileHandler()
        self.Blueprint.SearchHandler()
        self.Blueprint.RecipeHandler()

        # Console Handler
        self.Blueprint.CastHandler()
        self.Blueprint.ListenCastHandler()
        self.Blueprint.ProxyCastHandler()
        self.Blueprint.GlobalCastHandler()
        self.Blueprint.StopCastHandler()

        # Service Handlers ( LLM can actually improvise a reply and invoke the corresponding functions in tool calling )
        self.Blueprint.WeatherHandler()
        self.Blueprint.GoogleHandler()
        self.Blueprint.MusicHandler()
        self.Blueprint.YoutubeHandler()
        self.Blueprint.SpotifyHandler()
        self.Blueprint.WikipediaHandler()

        # Message Handlers ( Add after CommandHandlers so it doesn't Intercept; Telegram Structure )
        self.Blueprint.MessageHandler()
        self.Blueprint.AudioHandler()
        self.Blueprint.ImageHandler()
        self.Blueprint.VideoHandler()
        self.Blueprint.DocumentHandler()
        self.Blueprint.LocationHandler()

    def Polling(self):
        updates = self.Blueprint.updater.bot.get_updates(offset=-1)
        if updates: self.Blueprint.updater.bot.get_updates(offset=updates[-1].update_id + 1)
        self.Blueprint.Polling()

########################################################################
###################              Main                ###################

def main():
    print(f"\n~~~~~~~~~  Telegram Started !  ~~~~~~~~~\n")
    print(f"\nWe have logged in as Fay#2911\n")

    # Options
    parser      = argparse.ArgumentParser(description="Run Fay locally or on server")
    parser.add_argument('-m', '--mode',   help='Run mode: local or server', required=False)
    parser.add_argument('-c', '--client', help='AI client: openai, deepseek, grok, claude', default='openai', choices=["openai", "deepseek", "grok", "claude"])
    args        = parser.parse_args()

    # System
    settings    = Settings()
    blueprint   = Blueprint(settings, settings.FayTelegram, settings.FayName, settings.Fay, settings.Product, client=args.client)
    
    # Input
    threading.Thread(target=blueprint.Node.Listener, daemon=True).start()

    # Telegram
    Fay         = FayOS(settings, blueprint)
    Fay.Polling()
    
if __name__ == "__main__":  main()

########################################################################