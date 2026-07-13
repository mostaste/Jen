########################################################################
###################            Libraries             ###################

import os
import io
import re
import json
import random
import argparse
import mimetypes

from hub import Greenprint
from settings import Settings

from pydub import AudioSegment
from datetime import datetime
from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.models import MessageEvent, MessageAction, QuickReply, QuickReplyButton
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, URIAction
from linebot.models import FileMessage, StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage, LocationAction
from linebot.models import TextMessage, TextSendMessage, AudioMessage, AudioSendMessage, ImageMessage, ImageSendMessage, VideoMessage, VideoSendMessage
from linebot.exceptions import InvalidSignatureError

########################################################################
#################                Config                #################

parser      = argparse.ArgumentParser(description="Run Fay Line server")
parser.add_argument('-m', '--mode',   help='Run mode: local or server', required=False)
parser.add_argument('-c', '--client', help='AI client: openai, deepseek, grok, claude', default='openai', choices=["openai", "deepseek", "grok", "claude"])
args        = parser.parse_args()

app         = Flask(__name__)

settings    = Settings()

FAY         = Greenprint(settings=settings, 
                         channel_token=settings.LineAccess, 
                         channel_secret=settings.LineSecret, 
                         name=settings.FayName, 
                         character=settings.Fay, 
                         knowledge=settings.Product, 
                         client=args.client)

LineAPI     = FAY.LineAPI
handler     = FAY.Handler
logger      = FAY.Logger

hub         = FAY.Hub
media       = FAY.Media
wallet      = FAY.Wallet      
stickers    = FAY.Stickers

########################################################################
################                Handlers                ################

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # - You can only use event.reply_token once ( With Respect to Time Limit ) 
    # - Push message allows you to send message without the use of the reply_token  [ * reply_token is received when the User talks first ] (  Example in Groupcast() ) 
    # - Work on Reply Initialization ??  This is hard way that requires storing all real time MongoDB ( message_data ) and referencing back to the message store dictionary
    # - Add Real time Chat logging when manual chatting ? STALKER ??  Do it so it send to the Jen Groups, so it doesn't fly the Fay DM too much
    # - Turn off LLM Reply when Manual Casting ( Backdoor ) [ Only applies to Proxycast as Global and ListenCast only Forwards the message to you ]
    # - Move Chat Flow structure to interface.py
    # - Location Links Do From Here ? Decode GeoCode can be a Universal Function in interface.py, Did I already do this ?
    # - Created Admin and Forward Cast into a small Helper Function

    # API
    user_id                = event.source.user_id                          # UseR iD for Data Vectors                     
    user_profile           = LineAPI.get_profile(user_id)                  # Returns a list of Tuples
    name                   = hub.Name(user_profile.display_name)           # Display name might have issues if User uses Line emoticons
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)        # ChatID is UserID if DM * Group is a boolean to check if it is a group chat ( GroupID )
    
    bot_info               = LineAPI.get_bot_info()
    BOT_USER_ID            = bot_info.user_id
    BOT_DISPLAY_NAME       = bot_info.display_name
    bot_user               = r'\b{}\b'.format(re.escape(FAY.AI))

    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Message
    message         = event.message.text
    message_id      = event.message.id
    message_user    = f"{name}:   {message}"                        # It's Confusing
    FAY.MessageStore[chat_id].append({message_id:    message})      # You also need to check if it's the User or Fay as they share the same message id 

    # Output
    response        = ""

    # Emotes        ( LINE Emoji metadata )
    emotes          = getattr(event.message, "emojis", None)
    if emotes:
        for e in emotes:
            product_id = getattr(e, "product_id", getattr(e, "productId", None))
            emoji_id   = getattr(e, "emoji_id",   getattr(e, "emojiId",   None))
            idx        = getattr(e, "index", None)
            length     = getattr(e, "length", None)
            hub.Terminal(logger, f"EMOTE -> product_id: {product_id}, emoji_id: {emoji_id}, index: {idx}, length: {length}")

    # Thinking
    FAY.Typing(user_id, 5)  # Legacy { if not group:   Typing(chat_id, 5) }

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, message, aliases=aliases): return  # This Stops Fay from Replying when you are Talking to a User

    # Balance
    bal = wallet.WalletBalance(user_id, name)   # Coin is used as a Message Counter ( A way to keep track of N Messages Sent )
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return  # This should return the Subscription Link immediately { LineAPI.push_message(user_id, TextSendMessage(text="⚠️ You’re out of Fay Coins. Use /buy to top up your balance 💰")); return } 

    # Response
    response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, message, None, FAY.Hub.fay_Pattern)

    # Terminal
    if response:    FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    # - Line has a very special Encoding for Sound; Gotta Decode properly when passing to Azure (.m4a ? But there are times when I download it, it becomes aac )
    # - We need to see how we can pull the data from a temproray server as resources might be wonky with regards to networking.  Also all Line files are temporary
    # - Check if it's a Group or DM [ Use "fay" to modulate Replies ].  It's important to do this in the Line Interface as voice messages are common, you do not want to process all incoming
    # = Processing ( This needs to change !! ALL DONE ) { prompt = media.Transcribe(ClientDict[chat_id], audio_url) or ""     * If Empty String, tell User then Return ? Do this, and then log the error more cleanly [ DONE ] }
    # = Turn off Processing, if /audio is off
    # = Use OpenAI instead of Microsoft
    # = Get duration of audio (e.g., using pydub or ffmpeg)   [ duration_ms = get_audio_duration_ms(audio_path) ] DONE

    # API
    user_id                = event.source.user_id
    user_profile           = LineAPI.get_profile(user_id)
    name                   = hub.Name(user_profile.display_name)
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)
    
    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Get the audio ID
    message_id      = event.message.id
    message_user    = f"{name} has sent an Audio"
    
    # Download the audio file
    content         = LineAPI.get_message_content(message_id)
    content_type    = "Audio"
   
    # Audio
    audio_file  = f"{name}_{message_id}.m4a"
    audio_url   = f"{FAY.PUBLIC_BASE}/Media/Line/Files/{audio_file}"   # Serve Media ( App Route )
    audio_path  = os.path.join("Media", "Line", "Files", audio_file)
    hub.Terminal(logger, f"Downloaded Audio from {name}")  

    # Download from LINE’s blob store
    with open(audio_path, "wb") as fd:
        for chunk in content.iter_content(chunk_size=8192):     fd.write(chunk)     # Buffer: 8192 [ So we don't write 1 Byte at a time ]
    timestamp   = FAY.TimeStamp()
    audio_ms    = len(AudioSegment.from_file(audio_path))

    # Thinking
    FAY.Typing(user_id, 10)

    # Processing 
    prompt = media.Transcribe(FAY.ClientDict[chat_id], audio_path) or ""    # This should always be OpenAI ? They have the best Transcription NOTE
    if not prompt:
        LineAPI.reply_message(event.reply_token, [TextSendMessage(text="⚠️ Sorry, I couldn't understand your audio. Please try again with a clearer recording.")])
        hub.Terminal(logger, f"Failed to transcribe audio from {name} (ID: {user_id}) at {timestamp}")
        return

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, prompt, content_type, audio_file, audio_path)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"url": audio_url, "duration": audio_ms}, content_type, aliases): return  # This Should include File URL, Duration for Audio derive from within.. Check What you need for other Media Handlers 

    # Balance
    bal = wallet.WalletBalance(user_id, name)
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return

    # Output
    if FAY.bAudioDict[chat_id]:  
        response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, prompt, None, FAY.Hub.fay_Pattern, content_type) # hub.Chat(event, LineAPI, user_name, user_id, chat_id, prompt)
        FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # - This has no Prompt because you can't put Caption on Line

    # API
    user_id                = event.source.user_id
    user_profile           = LineAPI.get_profile(user_id)
    name                   = hub.Name(user_profile.display_name)
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)

    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Get the image ID
    message_id      = event.message.id
    message_user    = f"{name} has sent an Image"
    
    # Download the image file
    content         = LineAPI.get_message_content(message_id)
    content_type    = "Image"

    # Image ( Already stored in Database ) [ There are Server Temporary Files; Database only Stores the Binaries ]
    image_file  = f"{name}_{message_id}.jpg"
    image_url   = f"{FAY.PUBLIC_BASE}/Media/Line/Files/{image_file}"    # image_url   = f"{ngrok}/media/{image_file}"
    image_path  = os.path.join("Media", "Line", "Files", image_file)
    hub.Terminal(logger, f"Downloaded Image from {name}")  
    
    # Download from LINE’s blob store
    with open(image_path, 'wb') as fd:
        for chunk in content.iter_content(chunk_size=8192):    fd.write(chunk)

    # Thinking
    FAY.Typing(user_id, 10)

    # Processing
    image = media.FileEncoder(image_path)   # Base64 might not be needed, we can host the image url on the website

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message_user, content_type, image_file, image_path)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"original": image_url, "preview": image_url}, content_type, aliases): return  # This Should include File URL, Duration for Audio derive from within.. Check What you need for other Media Handlers 
    
    # Balance
    bal = wallet.WalletBalance(user_id, name)
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return

    # Output    [ Perhaps we dont need this, we simply always turn it on for users? However we need to turn it off in Groups, otherwise it reads everything !!! ]
    if FAY.bImageDict[chat_id]:
        FAY.MemoryDict[chat_id].append({settings.gptRole: settings.gptUser, settings.gptName: name, settings.gptContent: [{"type": "text", "text": f"{FAY.VisionBreak} "}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64, {image}"}}]}) # FAY.MemoryDict[chat_id].append({settings.gptRole: settings.gptUser, settings.gptName: name, settings.gptContent: [{"type": "text", "text": f"{FAY.VisionBreak}"}, {"type": "image_url", "image_url": {"url": image_url}}]})    # 
        response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, "", image, FAY.Hub.fay_Pattern, content_type) # hub.Chat(event, LineAPI, user_name, user_id, chat_id, prompt="")
        FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)

@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    # API
    user_id                = event.source.user_id
    user_profile           = LineAPI.get_profile(user_id)
    name                   = hub.Name(user_profile.display_name)
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)

    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Get the video message ID
    message_id      = event.message.id
    message_user    = f"{name} has sent a Video"

    # Download the video file
    content         = LineAPI.get_message_content(message_id)
    content_type    = "Video"

    # Video
    video_file  = f"{name}_{message_id}.mp4"
    video_url   = f"{FAY.PUBLIC_BASE}/Media/Line/Files/{video_file}"
    video_path  = os.path.join("Media", "Line", "Files", video_file)
    hub.Terminal(logger, f"Downloaded Video from {name}")

    # Preview
    preview_file  = f"{name}_{message_id}_preview.jpg"
    default_url   = f"{FAY.PUBLIC_BASE}/Media/Line/Files/default_preview.jpg"
    preview_path  = os.path.join("Media", "Line", "Files", preview_file)
    
    # Download from LINE’s blob store
    with open(video_path, 'wb') as fd:
        for chunk in content.iter_content():    fd.write(chunk)
    preview_url   = FAY.VideoPreview(video_path, preview_path, default_url)

    # Thinking
    FAY.Typing(user_id, 10)

    # Processing
    video = media.VideoEncoder(video_path)

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message_user, content_type, video_file, video_path)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"original": video_url, "preview": preview_url}, content_type, aliases): return  # This Should include File URL, Duration for Audio derive from within.. Check What you need for other Media Handlers 

    # Balance
    bal = wallet.WalletBalance(user_id, name)
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return
    
    # Output
    if FAY.bImageDict[chat_id]:
        FAY.MemoryDict[chat_id].append({settings.gptRole: settings.gptUser, settings.gptName: name, settings.gptContent: [{"type": "text", "text": f"{FAY.VideoPrompt}"}, *map(lambda x: {"image": x, "resize": 768}, video[0::250])]})
        response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, "", video, FAY.Hub.fay_Pattern, content_type)  # hub.Chat(event, LineAPI, user_name, user_id, chat_id, prompt="", image=video, video=True)
        FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    # API
    user_id                = event.source.user_id
    user_profile           = LineAPI.get_profile(user_id)
    name                   = hub.Name(user_profile.display_name)
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)

    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Get the file message ID
    message_id      = event.message.id
    message_user    = f"{name} has sent a Document"

    # Download the document file
    content         = LineAPI.get_message_content(message_id)
    content_type    = "Document"

    # Document
    file_extension  = event.message.file_name.split('.')[-1] if '.' in event.message.file_name else 'unknown'
    file_name       = f"{name}_{message_id}.{file_extension}"
    file_url        = f"{FAY.PUBLIC_BASE}/Media/Line/Files/{file_name}"
    file_path       = os.path.join("Media", "Line", "Files", file_name)
    hub.Terminal(logger, f"Downloaded Document from {name}")

    # Download from LINE’s blob store 
    with open(file_path, "wb") as fd:
        for chunk in content.iter_content(chunk_size=8192):       fd.write(chunk)

    # Json [ Not sure if Casting Works ]
    file = [{"type": "file", "originalContentUrl": file_url, "fileName": file_name}]    # Raw Json to pass in GroupCast ( PUSH )

    # Thinking
    FAY.Typing(user_id, 10)

    # Processing [ What about other document types ? ]
    prompt = media.TextEncoder(file_path)

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message_user, content_type, file_name, file_path)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"original": file_url, "file_name": file_name}, content_type, aliases): return  # This Should include File URL, Duration for Audio derive from within.. Check What you need for other Media Handlers 

    # Balance
    bal = wallet.WalletBalance(user_id, name)
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return

    # Output   ( Add a /file On and Off ? )
    response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, prompt, None, FAY.Hub.fay_Pattern, content_type) # hub.Chat(event, LineAPI, user_name, user_id, chat_id, prompt)

    # Terminal
    if response:    FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # API
    user_id       = event.source.user_id
    user_profile  = LineAPI.get_profile(user_id)
    name          = hub.Name(user_profile.display_name)
    chat_id, group, gname = FAY.ChatInitialization(event, LineAPI)

    # Alias
    if group:  AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")
    else:      AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Sticker info
    message_id   = event.message.id
    in_pid       = str(event.message.package_id)
    in_sid       = str(event.message.sticker_id)

    content_type = "Sticker"
    message_user = f"Sticker ~ Sent Package ID: {in_pid}, Sent Sticker ID: {in_sid}"

    # Thinking
    FAY.Typing(user_id, 5)

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message_user, content_type, in_pid, in_sid)

    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"package_id": in_pid, "sticker_id": in_sid}, content_type, aliases):  return

    # Pick reply sticker (NEW WAY)
    if in_pid in stickers.Packs and stickers.Packs[in_pid]:
        out_pid = in_pid
        out_sid = str(random.choice(stickers.Packs[in_pid]))
    else:
        out_pid, out_sid = stickers.RandomSticker()
        out_pid, out_sid = str(out_pid), str(out_sid)

    # Output
    LineAPI.reply_message(event.reply_token, StickerSendMessage(package_id=out_pid, sticker_id=out_sid)) # OR Push

    # Terminal
    message_bot = f"Sticker ~ Sent Package ID: {out_pid}, Sent Sticker ID: {out_sid}"
    FAY.LogOut(chat_id, user_id, FAY.AI, message_id, message_bot, content_type, out_pid, out_sid)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # API
    user_id                = event.source.user_id
    user_profile           = LineAPI.get_profile(user_id)
    name                   = hub.Name(user_profile.display_name)
    chat_id, group, gname  = FAY.ChatInitialization(event, LineAPI)

    # Alias
    if group: AliasDB, alias = FAY.AliasUpdate(chat_id, gname, "group")  
    else:     AliasDB, alias = FAY.AliasUpdate(user_id, name, "user")
    aliases = AliasDB["aliases"]

    # Message
    msg             = event.message
    lat, lon        = msg.latitude, msg.longitude
    label           = msg.address or msg.title or ""
    meta            = {
        "address": msg.address,
        "title": msg.title,
        "raw_type": "location",
        "timestamp": datetime.now().isoformat()
    }

    # --- Store a synthetic message instead of .text (which doesn't exist) ---
    content_type    = "Location"
    message_id      = msg.id
    message_text    = f"[LOCATION] {lat},{lon}" + (f" ({label})" if label else "")
    message_user    = f"{name}:    {message_text}"
    FAY.MessageStore[chat_id].append({message_id: message_text})

    # --- Cache to memory or file for downstream tools (Trips/Maps) ---
    file_path       = os.path.join(location_dir, f"{user_id}_location.json")
    location_dir    = os.path.join("Media", "Line", "Locations")
    with open(file_path, "w", encoding="utf-8") as f:   json.dump({"lat": lat, "lon": lon, "label": label, "meta": meta}, f, indent=2, ensure_ascii=False)

    # Synthesis
    prompt = (
        f"My live location is {lat},{lon}"
        + (f" ({label})" if label else "")
        + ". Reply with a short acknowledgement and ONE 'Open in Maps' link for this coordinate."
    )

    # Thinking
    FAY.Typing(user_id, 5)

    # Config
    FAY.LogIn(chat_id, user_id, name, message_id, message_user, content_type)
    if FAY.ForwardCasts(event, LineAPI, chat_id, user_id, name, message_id, {"lat": lat, "lon": lon, "label": label, "address": msg.address or "", "title": msg.title or ""}, content_type, aliases): return 

    # Balance
    bal = wallet.WalletBalance(user_id, name)
    if bal <= 0:    wallet.Subscribe(user_id, name, event.reply_token); return

    # --- 2nd location in same chat_id => generate directions immediately (NO LLM) ---
    prev = FAY.LastLocByChat.get(chat_id)
    if prev:
        origin = prev.get("q") or f"{prev.get('lat')},{prev.get('lon')}"
        dest   = f"{float(lat)},{float(lon)}"

        if (not origin) or ("None" in origin):  FAY.LastLocByChat.pop(chat_id, None)
        else:
            route_url = hub.GoogleMapsSmartLink(f"{origin} -> {dest}")
            response  = f"🧭 {prev['user_name']} → {name}\nOpen in Maps → {route_url}"

            hub.Reply(event, LineAPI, response)
            FAY.LastLocByChat.pop(chat_id, None)
            FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)
            return

    # Otherwise: store this as the first pin for this chat
    FAY.LastLocByChat[chat_id] = {"q": f"{float(lat)},{float(lon)}", "user_name": name}

    # Output
    response = FAY.LineChat(event, LineAPI, group, name, user_id, chat_id, prompt, None, FAY.Hub.fay_Pattern, content_type)  # hub.Chat(event, LineAPI, name, user_id, chat_id, prompt)

    # Terminal
    FAY.LogOut(chat_id, user_id, settings.FayName, message_id, response, content_type)

########################################################################
##################               Menu                 ##################

@app.route("/line", methods=["POST"])
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)
    try:                            handler.handle(body, signature)
    except InvalidSignatureError:   abort(400)
    return "OK"

@app.route("/Media/<platform>/Files/<path:filename>")
def serve_media_platform(platform, filename):
    media_dir = os.path.join("Media", platform, "Files")
    return send_from_directory(media_dir, filename)

@app.route("/<platform>/<kind>/<path:filename>")
def get_asset(kind, platform, filename):
    if platform not in FAY.ALLOWED_PLATFORMS or kind not in FAY.ALLOWED_KINDS:  abort(404)

    base_dir = os.path.join("Media", platform, "Files")
    kind_dir = os.path.join(base_dir, kind)
    folder   = kind_dir if os.path.isdir(kind_dir) else base_dir

    mimetype, _ = mimetypes.guess_type(filename)
    return send_from_directory(folder, filename, mimetype=mimetype)

########################################################################
###################              Main                ###################

def main():
    print(f"\n~~~~~~~~~  LINE Started !  ~~~~~~~~~\n")
    print(f"\nWe have logged in as Fay#2911\n")

    host    = "0.0.0.0"
    port    = 5000
    app.run(host=host, port=port)

if __name__ == "__main__":  main()

########################################################################