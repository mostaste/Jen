########################################################################
###################            Libraries             ###################

import string
import asyncio
import keyboard
import pyautogui

import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pynput.keyboard import Controller as KeyboardController
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########################################################################
#########################         Audio        #########################

class Audio:
    def __init__(self, settings, redprint):
        # Azure
        self.Azure_Speech                = settings.Azure_Speech
        self.Azure_Speaker               = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.Azure_Microphone            = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.Azure_Recognizer            = speechsdk.SpeechRecognizer(speech_config=self.Azure_Speech, audio_config=self.Azure_Microphone)

        # Processor
        self.listening_mode              = False

        # I / O
        self.speech_done                 = asyncio.Event()
        self.keyboard                    = KeyboardController()

        # Music
        self.music_queue                 = []

        # Wake
        self.wake                        = "wake"

        # Name
        self.USER                        = "Adam"
        self.AI                          = "Fay"

        # Engine
        self.RedPrint                    = redprint

    async def Eavesdrop(self, channel):
        await channel.send(f"\nListening... 🎧")

    async def Wake(self, discord, wake):
        # NOTE Create a List of Wake Words or Phrases
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while self.listening_mode:
                await discord.channel.send('Listening for Wake 💤')
                audio = r.listen(source, phrase_time_limit=7)
                try:
                    text = r.recognize_google(audio)
                    print(f"Heard: {text}")
                    if wake.lower() in text.lower():    
                        print(f'Wake word: "{wake}" Detected!')
                        try:
                            await asyncio.wait_for(self.Listen(discord), timeout=30.0)
                        except asyncio.TimeoutError:
                            print('AzureListen timed out, going back to listening for wake word.')
                            self.Azure_Recognizer.stop_continuous_recognition()
                            continue
                except Exception as e:  print(f'Could not understand audio.\n{e}')
        return

    async def Escape(self, discord, voice):
        while voice.is_playing():
            if keyboard.is_pressed('esc'):
                voice.stop()
                await discord.channel.send("Playback stopped!")
                break
            await asyncio.sleep(0.1)

        if self.listening_mode:
            await self.Eavesdrop(discord.channel)
            self.Azure_Recognizer.start_continuous_recognition()

    async def Listen(self, discord):
        transcript = []
        bEavesdrop = True  # Control flag to start eavesdropping

        def recognized_handler(evt):    transcript.append(evt.result.text)

        self.Azure_Recognizer.recognized.connect(recognized_handler)
        
        while self.listening_mode:
            if bEavesdrop:
                await self.Eavesdrop(discord.channel)
                self.Azure_Recognizer.start_continuous_recognition()
                bEavesdrop = False
            if keyboard.is_pressed('esc'):
                await discord.channel.send('Finished Listening... 🔇')
                self.Azure_Recognizer.stop_continuous_recognition()
                prompt = ' '.join(transcript)

                #self.keyboard.type(prompt)  # Types the Prompt on any Edit Text Box
                transcript.clear()

                decrypt = f"\n{self.USER}:\n{prompt}\n\n{self.AI}:"
                await discord.channel.send(decrypt)

                clean_result = prompt.lower().translate(str.maketrans('', '', string.punctuation))
                if any(word in clean_result.split() for word in ['quit', 'console', 'terminal']):
                    self.listening_mode = False
                    await discord.channel.send("Stopped Listening ⛔️\nGoing back to Text Mode 📝")
                    break
                
                try:    
                    await self.RedPrint.Reply(discord, self.USER, discord.author.id, discord.channel.id, prompt)
                    while self.RedPrint.Channel.voice_client and self.RedPrint.Channel.voice_client.is_playing():  await asyncio.sleep(0.1) # Event Handler doesn't work as well because it's too slow to trigger with the async and all
                    bEavesdrop = True  # Allow eavesdropping again after processing is complete
                except Exception as e:
                    print(f"\nWe have an intruder: {e}")
            else:   await asyncio.sleep(0.1)
        return

    async def Volume(self, discord, vol):
        devices                 = AudioUtilities.GetSpeakers()
        interface               = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume                  = cast(interface, POINTER(IAudioEndpointVolume))
        currentVolume           = volume.GetMasterVolumeLevel()
        minVolume, maxVolume, _ = volume.GetVolumeRange()

        currentVolume           = round(currentVolume, 2)
        print(f"Volume Current: {currentVolume:.2f}")
        print(f"Volume Range Min / Max: {minVolume} / {maxVolume}")

        # Volume Control should be done with Derivative
        if vol:
            currentVolume += 10
            print(f"Volume Increase")
            if currentVolume >= maxVolume: currentVolume = maxVolume
            await discord.channel.send("Increasing the Volume by 10 🔊")
        else:
            currentVolume -= 10
            print(f"Volume Decrease")
            if currentVolume <= minVolume: currentVolume = minVolume
            await discord.channel.send("Decreasing the Volume by 10 🔊")
        print(f"Volume: {currentVolume:.2f}")
        
        volume.SetMasterVolumeLevel(currentVolume, None)
        return

    async def Player(self, discord, cmd):
        if cmd == 'play' or cmd == 'pause':
            await discord.channel.send("Play/Pause Music ⏯")
            pyautogui.moveTo(205, 1930)
            pyautogui.click()
        elif cmd == 'next':
            await discord.channel.send("Playing Next Song ⏭")
            pyautogui.moveTo(350, 1930)
            pyautogui.click()
        elif cmd == 'previous':
            await discord.channel.send("Playing Previous Song ⏮")
            pyautogui.moveTo(70, 1930)
            pyautogui.click()
        return

    async def Queue(self, discord, list):
        return

########################################################################