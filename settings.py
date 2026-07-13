########################################################################w
#########################        Library       #########################

import json
import gridfs

from openai import OpenAI
from spotipy import Spotify
from pymongo import MongoClient
from newsapi import NewsApiClient
from elevenlabs.client import ElevenLabs
from elevenlabs.client import AsyncElevenLabs
from spotipy.oauth2 import SpotifyClientCredentials

from media import Database 
from character import Character

########################################################################
#########################       Settings       #########################

class Settings():

    def __init__(self):

        ########################################################################
        ########################          Static        ########################

        with open('tools.json') as tools_file:          tools   = json.load(tools_file)
        with open('config.json') as config_file:        configs = json.load(config_file)

        ########################################################################
        #######################         Character        #######################

        # System
        character                        = Character()

        # Names
        self.FayName                     = character.FayName
        self.JenName                     = character.JenName
        self.InkName                     = character.InkName
        self.JoyName                     = character.JoyName

        # Overview
        self.Preface                     = character.Preface
        self.Product                     = character.Product
        self.Domum                       = character.Domum

        # Personalities
        self.Fay                         = character.Fay
        self.Jen                         = character.Jen
        self.Ink                         = character.Ink

        self.Bad                         = character.Bad
        
        self.JenLine                     = character.JenLine
        self.InkLine                     = character.InkLine

        self.FayLine                     = character.FayLine
        self.FayTele                     = character.FayTele

        self.FayWeb                      = character.FayWeb
        self.FayAir                      = character.FayAir

        self.Joy                         = character.Joylila
        self.JoyAir                      = character.JoyAir

        self.Sorene                      = character.Sorene

        ########################################################################
        #########################         Config       #########################

        # xAI
        self.xAI_Key                     = configs['Grok']

        # OpenAI
        self.OpenAI_Key                  = configs['VOpenAI']    # configs['OpenAI']

        # DeepSeek
        self.DeepSeek_Key                = configs['DeepSeek']   # configs['VDeepSeek']
        
        # Claude
        self.Claude_Key                  = configs['Claude']     # configs['VClaude']
        
        # Perplexity
        self.Perplexity_Key              = configs['Perplexity']

        # Gemini
        self.Gemini_Key                  = configs['Gemini']

        # Meta
        self.Meta_Key                    = configs['Groq']

        # HuggingFace
        self.HF_Key                      = configs['HuggingFace']

        # GPT
        self.gptRole                     = configs['gptRole']
        self.gptSystem                   = configs['gptSystem']
        self.gptUser                     = configs['gptUser']
        self.gptAssistant                = configs['gptAssistant']
        self.gptContent                  = configs['gptContent']
        self.gptName                     = configs['gptName']
        self.gptType                     = configs['gptType']

        # Discord                             
        self.FayID                       = configs['Fay_Discord']                                                      
        self.JenID                       = configs['Jen_Discord']                                                      

        # Telegram
        self.InkID                       = configs['Ink_Telegram']
        self.FayTelegram                 = configs['Fay_Telegram']
        self.TeleInkGroup                = configs['Tele_InkGroup']
        self.TeleFayGroup                = configs['Tele_FayGroup']
        self.TeleAdmin                   = configs['Tele_Admin']

        # Line
        self.LineID                      = configs['Line_ID']     
        self.LineSecret                  = configs['Line_Secret']
        self.LineAccess                  = configs['Line_Access']  

        self.LineInk                     = configs['Line_Ink']
        self.LineInkA                    = configs['Line_InkA']

        self.LinePayID                   = configs['LinePay_ID']
        self.LinePaySecret               = configs['LinePay_Secret']

        self.LineAdmin                   = configs['Line_Admin']
        self.LineGroup                   = configs['Line_Group']

        # Instagram
        self.IG_User                     = configs['IG_User']
        self.IG_Pass                     = configs['IG_Pass']
        self.IG_Session                  = configs['IG_Session']

        # Slack
        self.SlackToken                  = configs['Slack_Token']
        self.SlackSecret                 = configs['Slack_Secret']

        # Wechat
        self.WechatToken                 = configs['Wechat_Token']
        self.WechatApp                   = configs['Wechat_App']
        self.WechatSecret                = configs['Wechat_Secret']
        self.WechatAES                   = configs['Wechat_AES']

        # Pico
        self.Pico_Key                    = configs['Pico']

        # Eleven                         
        self.Eleven                      = configs['ElevenLabs']
        self.ElevenVoice                 = configs['ElevenVoice']
        self.ElevenClient                = ElevenLabs(api_key=self.Eleven)

        # Weather
        self.Weather_Key                 = configs['Weather_API']

        # Time
        self.Time_Key                    = configs['Time_API']

        # Currency
        self.Currency_Key                = configs['Currency_API']

        # News
        self.News_Key                    = configs['News_API']
        self.NewsClient                  = NewsApiClient(api_key=self.News_Key)

        # Spotify
        self.Spotify_ID                  = configs['Spotify_API']
        self.Spotify_Secret              = configs['Spotify_Secret']
        self.SpotifyClient               = Spotify(auth_manager=SpotifyClientCredentials(client_id=self.Spotify_ID, client_secret=self.Spotify_Secret))
        
        # Global
        self.Client                      = OpenAI(api_key=self.OpenAI_Key)
        
        # OpenAI
        self.OAClient                    = OpenAI(api_key=self.OpenAI_Key)

        # Grok
        self.GClient                     = OpenAI(api_key=self.xAI_Key, base_url="https://api.x.ai/v1"),

        # DeepSeek
        self.DSClient                    = OpenAI(api_key=self.DeepSeek_Key, base_url="https://api.deepseek.com/v1")

        # Claude
        self.CLClient                    = OpenAI(api_key=self.Claude_Key, base_url= "https://api.anthropic.com/v1")

        # Image
        self.ImageSizes                  = {"normal": "1024x1024", "landscape": "1792x1024", "portrait": "1024x1792"}
        self.ImageQuality                = {"standard", "hd"}

        # Tools
        self.Tools                       = tools['tools']

        # Cloudflare
        self.Cloudflare                  = configs['Website']

        # Ngrok
        self.Ngrok                       = configs['Ngrok']

        # Providers
        self.Clients                     = {
            "openai":                      OpenAI(api_key=self.OpenAI_Key),
            "grok":                        OpenAI(api_key=self.xAI_Key, base_url="https://api.x.ai/v1"),
            "meta":                        OpenAI(api_key=self.Meta_Key, base_url="https://api.groq.com/openai/v1"),
            "claude":                      OpenAI(api_key=self.Claude_Key, base_url= "https://api.anthropic.com/v1"),
            "deepseek":                    OpenAI(api_key=self.DeepSeek_Key, base_url="https://api.deepseek.com/v1"),
            "gemini":                      OpenAI(api_key=self.Gemini_Key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        }

        # Models
        self.Models                      = {
            # Grok
            'GROK41':  {'name': configs['model_grok41'],   'max_tokens': 128000, 'buffer': 4096},   
            'GROK4':   {'name': configs['model_grok4'],    'max_tokens': 128000, 'buffer': 4096},

            # OpenAI
            'GPT5':    {'name': configs['model_gpt5'],     'max_tokens': 128000, 'buffer': 5120},
            'GPT41':   {'name': configs['model_gpt41'],    'max_tokens': 128000, 'buffer': 5120},
            'GPT32K':  {'name': configs['model_gpt4_32k'], 'max_tokens': 128000, 'buffer': 5120},
            'GPT4M':   {'name': configs['model_gpt4M'],    'max_tokens': 128000, 'buffer': 5120},
            'GPT4O':   {'name': configs['model_gpt4O'],    'max_tokens': 128000, 'buffer': 5120},
            'GPT4T':   {'name': configs['model_gpt4T'],    'max_tokens': 128000, 'buffer': 1280},
            'GPT4V':   {'name': configs['model_gpt4V'],    'max_tokens': 128000, 'buffer': 1280},
            'GPT4L':   {'name': configs['model_gpt4L'],    'max_tokens': 8192,   'buffer': 192},
            'GPT4':    {'name': configs['model_gpt4'],     'max_tokens': 8192,   'buffer': 192},
            'GPT3':    {'name': configs['model_gpt3'],     'max_tokens': 16385,  'buffer': 285},
            'O1':      {'name': configs['model_o1'],       'max_tokens': 128000, 'buffer': 5120},
            'O1M':     {'name': configs['model_o1m'],      'max_tokens': 128000, 'buffer': 5120},
            'DAVINCI': {'name': configs['model_davinci'],  'max_tokens': 4096,   'buffer': 96},
            'CURIE':   {'name': configs['model_curie'],    'max_tokens': 4096,   'buffer': 96},
            'BABBAGE': {'name': configs['model_babbage'],  'max_tokens': 4096,   'buffer': 96},
            'ADA':     {'name': configs['model_ada'],      'max_tokens': 4096,   'buffer': 96},

            # Claude
            'CLAUDEO': {'name': configs['model_claudeO'],  'max_tokens': 200000, 'buffer': 5120},
            'CLAUDES': {'name': configs['model_claudeS'],  'max_tokens': 200000, 'buffer': 5120},
            'CLAUDEH': {'name': configs['model_claudeH'],  'max_tokens': 200000, 'buffer': 5120},

            # DeepSeek
            'DSCHAT':  {'name': configs['model_dschat'],   'max_tokens': 8192,   'buffer': 192},
            'DSCODE':  {'name': configs['model_dscode'],   'max_tokens': 8192,   'buffer': 192},
            'DSVL':    {'name': configs['model_dsvl'],     'max_tokens': 16384,  'buffer': 256},
            
            # Gemini
            'GEMINIP':  {'name': configs['model_geminiP'],  'max_tokens': 65536, 'buffer': 1536},
            'GEMINIF':  {'name': configs['model_geminiF'],  'max_tokens': 65536, 'buffer': 1536},
            'GEMINIL':  {'name': configs['model_geminiL'],  'max_tokens': 65536, 'buffer': 1536},

            # Draw
            'DALLE':    {'name': configs['model_dalle'],    'max_tokens': 4096,  'buffer': 96},
            'GROKIMG':  {'name': configs['model_grokimg'],  'max_tokens': 4096,  'buffer': 96},
            'GEMINIMG': {'name': configs['model_geminimg'], 'max_tokens': 4096,  'buffer': 96},
        }

        # Shelly
        self.ShellyDevices               = {
            # -------- Library Zone --------
            "library":      "192.168.1.100",   # Library
            "restroom":     "192.168.1.101",   # Restroom
            # -------- Bedroom Zone --------
            "bedroom":      "192.168.1.102",   # Bedroom ( Channel 0 )
            "balcony":      "192.168.1.102",   # Balcony ( Channel 1 )
            "closet":       "192.168.1.103",   # Closet
            "bathroom":     "192.168.1.104",   # Bathroom
            # -------- Sky Deck --------
            "sky":           "192.168.1.105",
            "deck":          "192.168.1.105",
            "loft":          "192.168.1.105"
            # Hallway / Stairs
            # -------- Kitchen Zone --------
            # Kitchen
            # Doorway
            # Foyer / Kitchenway
            # Toilet
        }

        self.ShellyAliases               = {
            "libram": "library",
            "lavatory": "restroom",
            "vestia": "closet",
            "caelum": "sky",
            "solarium": "deck",
            "cenaculum": "loft",
            "armarium": "closet",
            "balconeum": "balcony",
            "cubiculum": "bedroom",
            "latrina": "bathroom",
        }

        # Stripe
        self.Stripe_Prices               = {
            "starter_1":                   configs['Stripe_Price_Starter_Monthly'],
            "starter_6":                   configs['Stripe_Price_Starter_6Month'],
            "pro_1":                       configs['Stripe_Price_Pro_Monthly'],
            "pro_6":                       configs['Stripe_Price_Pro_6Month'],
        }
        self.Subscription_Credits        = {
            "free":                         30,
            "starter_1":                    100,      
            "starter_6":                    600,      
            "pro_1":                        500,      
            "pro_6":                        3000,     
        }
        self.Stripe_Secret               = configs['Stripe_Secret']
        self.Stripe_Webhook_Secret       = configs['Stripe_Webhook_Secret']

        # Database
        self.LineMessages                = Database(base="Media/Line/DB")
        self.TelegramMessages            = Database(base="Media/Telegram/DB")
        self.DiscordMessages             = Database(base="Media/Discord/DB")
        self.WechatMessages              = Database(base="Media/Wechat/DB")
        self.WebMessages                 = Database(base="Media/Web/DB")
        print("🟢 Connected to Local DB 🍃")

        ########################################################################
        #######################          Legacy          #######################
        
        #  Knowledge Base { Embedding Layer } [ Experiment with your own File Base; Just Documents and Images, and Code !!! That would be Cool ~ ] ( And that Vector thingy looks Cool; find out how to do it. DONE )
        #  General Embedding Handler has been built, but the File Process functions needs to vary with each type of File ( Build on-the-go ? ) 
        #  MongoDB Cloud Configs is available below

        # Mongo
        '''       
        # [ Make this part configurable, easy to take out ]  High Priority, Try to save by yourself, in computer hard drive, use external * MongoDB as a Toggle ?
        self.MongoURI                    = configs['MongoURI']
        self.Mongo                       = MongoClient(self.MongoURI)
        self.MongoDB                     = self.Mongo['Chats']
        self.MongoFS                     = gridfs.GridFS(self.MongoDB)

        self.LineMessages                = self.MongoDB['Line']
        self.TeleMessages                = self.MongoDB['Telegram']
        self.DiscordMessages             = self.MongoDB['Discord']
     
        try:    self.Mongo.admin.command('ping');   print("🟢 Connected to MongoDB 🍃")
        except Exception as e:                      print(f"Error {e}")
        '''   

########################################################################