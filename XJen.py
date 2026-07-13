########################################################################
###################            Libraries             ###################

import argparse
import platform
from enginex import RedPrint
from settings import Settings

########################################################################
###################              Main                ###################

def main():
    print(f"\n~~~~~~~~~  Discord Started !  ~~~~~~~~~\n")
    print(f"\nWe have logged in as Jen#2911\n")

    # ARGS
    parser      = argparse.ArgumentParser(description="Run Jen locally or on server")
    parser.add_argument('-m', '--mode', help='Run mode: local or server', required=False)
    parser.add_argument('-c', '--client', help='AI client: openai, deepseek, grok, claude', default='openai', choices=["openai", "deepseek", "grok", "claude"])
    args        = parser.parse_args()

    # System
    settings    = Settings()
    Jen         = RedPrint(settings, settings.JenName, client=args.client)

    # Windows
    if args.mode == "local" or args.mode == "audio":
        from audio import Audio
        audio = Audio(settings, Jen)
        Jen.Audio(audio)
        print("Audio Initialized")
    
    # Discord
    Jen.Bot.run(settings.JenID)
    
if __name__ == "__main__":  main()

########################################################################