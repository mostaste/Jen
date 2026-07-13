########################################################################
###################            Libraries             ###################

import os
import io
import re
import cv2
import docx
import json
import random
import base64
import PyPDF2
import numpy as np

from PIL import Image
from PyPDF2 import PdfReader
from pydub import AudioSegment
from langdetect import detect
from elevenlabs import Voice, VoiceSettings, play, stream

import azure.cognitiveservices.speech as speechsdk

# You need a Global Memory.. Unique User ID that is recognized across Discord / Telegram / Line / Web

########################################################################
####################            Media               ####################

class Media:
    ########################################################################
    #################                Init                  #################
    
    def __init__(self, settings):   
        self.Settings   = settings
        self.Vectors    = {}

    ########################################################################
    #################               Audio                  #################

    def Audio(self, client, audio_file):
        #                   Listener                       #
        with open(audio_file, "rb") as f:    ## Send Raw Sound File, and it will Transcribe from Speech to Text
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
                response_format="text"
            )
        print(f"📝 Transcription: {transcription}")
        return transcription.strip()
    
    def Voice(self, client, audio_file):
        #                   Listener                       #
        with open(audio_file, "rb") as f:    ## Send Raw Sound File, and it will Transcribe from Speech to Text
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
                response_format="text"
            )
        print(f"📝 Transcription: {transcription}")
        return transcription.strip()

    def Transcribe(self, client, audio_file):
        #                   Listener                       #
        with open(audio_file, "rb") as f:    ## Send Raw Sound File, and it will Transcribe from Speech to Text
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
                response_format="text"
            )
        print(f"📝 Transcription: {transcription}")
        return transcription.strip()

    def Speak(self, client, text, voice="nova", fmt="mp3"):
        ''' # Voices
        alloy   - default, neutral/mid-range
        echo    - lighter and youthful
        fable   - warm, story-teller tone (soft female)
        onyx    - deep, calm male
        nova    - bright, energetic female
        shimmer - smooth, slightly playful female
        '''
        if not (text or "").strip():    return b""
        r = client.audio.speech.create(model="gpt-4o-mini-tts", voice=voice, input=text)
        return r.read() if hasattr(r, "read") else (r.content if hasattr(r, "content") else bytes(r))

    def Eleven(self, text, voice_id="qF5xwhsg4ywh2zmBC3dd"):
        #                   Speaker                        *
        #  qF5xwhsg4ywh2zmBC3dd ( Taylor Voice ID )
        #  GkcE27eS9IqgzZJ5uy9U ( Jen Voice ID )
        #  mrDxfGKIrc5Uc0OCJvXx ( Ink Voice ID )
        #  9F4C8ztpNUmXkdDDbz3J ( Dan Voice ID )
        #  KAfayB3Tt9MnwYSZqexY ( Hermione Voice ID ) 
        # Randomize Voice Settings Values to see if the Dynamical Range Works ( Perhaps we should set 3 Different Ranges to achieve the Maximum Equalization ) 

        ##          Calculus        ##
        # - Requires Emotional Embedding

        ###      -   For some reason the Web Interface is better than the API 
        ###      -   Maybe this is the part where it makes it Funny? * I DONT THINKS SO ~ 
        ###      -   Can we just join it as a byte object like that?  The audio file is a generator; if only can play from ElevenLabs by returning a .wav File or return the byte object like Microsoft Azure

        # Generation ( Feels Funny compared to Web; Maybe it generates new everytime there are new sentences? )
        ## audio = self.Settings.ElevenClient.generate(text=text, voice=Voice( voice_id='KAfayB3Tt9MnwYSZqexY', settings=VoiceSettings(stability=0.4, similarity_boost=0.9, style=0.9, use_speaker_boost=True)))
        
        
        # Generation ( All Corporate Voice Cloning Software no longer allow you to clone the Voice of others without Verification )
        audio = self.Settings.ElevenClient.generate(text=text, voice=Voice(voice_id=voice_id, settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True)))

        # <class 'generator'>
        #print(type(audio))  

        # Collect all parts of the audio from the generator into a single bytes object
        audio_data = b''.join(chunk for chunk in audio)  # Join all chunks from generator into one bytes object
        
        # Check if any audio data was collected
        if audio_data:  print("Audio data collected successfully. Length:", len(audio_data))
        else:           print("No audio data generated.")
        return audio_data

    # Grok
    
    ########################################################################
    #################              Encoders                #################

    def FileEncoder(self, file_path):
        with open(file_path, "rb") as file:         return base64.b64encode(file.read()).decode('utf-8')

    def WCFileEncoder(self, file_path):
        with open(file_path, "rb") as file:          return base64.b64encode(file.read()).decode("ascii")

    def TextEncoder(self, text_file):
        data = ''
        if text_file.endswith('.pdf'):
            with open(text_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    data += page.extract_text()
        elif text_file.endswith('.docx'):
            doc     = docx.Document(text_file)
            data    = ' '.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            with open(text_file, 'r') as file:  data = file.read()
        return data
    
    def AudioEncoder(self, audio_file):
        '''
        # Export the audio to .mp3 format
        mp3_file = os.path.splitext(audio_file)[0] + ".mp3"
        audio.export(mp3_file, format="mp3")
        '''
        wav_file = os.path.splitext(audio_file)[0] + ".wav"

        if audio_file.endswith('.ogg'):     audio = AudioSegment.from_file(audio_file, format="ogg")    # Load the .ogg file    ( OGG is Used for BOTH Telegram and Discord )
        elif audio_file.endswith('.m4a'):   audio = AudioSegment.from_file(audio_file, format="m4a")    # Load the .m4a file    ( M4A is Used for Line )
        elif audio_file.endswith('.aac'):   audio = AudioSegment.from_file(audio_file, format="aac")    # Load the .aac file        
        elif audio_file.endswith('.mp3'):   audio = AudioSegment.from_file(audio_file, format="mp3")    # Load the .mp3 file
        elif audio_file.endswith('.mp4'):   audio = AudioSegment.from_file(audio_file, format="mp4")    # Load the .mp4 file
        elif audio_file.endswith('.amr'):   audio = AudioSegment.from_file(audio_file, format="amr")    # Load the .amr file
        audio.export(wav_file, format="wav")
        return wav_file

    def VideoEncoder(self, video_file):
        video = cv2.VideoCapture(video_file)

        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)    # Resize the Resolution as the AI dont need Full Resolution to comprehend and Image
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()
        nFrames = len(base64Frames)         # NOTE We need to return this and put it in the message for the User to know
        print(nFrames, "frames read.")      # Frame Counter
        return base64Frames

    def ImageVideoEncoder(self, image, video):
        # Combine the pre-encoded base64 image string with the list of video frames
        imagevideo = [image] + video
        
        # Print the total number of frames (including the image)
        print(f"Total frames (including image): {len(imagevideo)}")
        
        return imagevideo

    def ImageSquareEncoder(self, image1, image2):
        # Decode the base64 string to binary image
        img1 = Image.open(io.BytesIO(base64.b64decode(image1)))
        img2 = Image.open(io.BytesIO(base64.b64decode(image2)))
        
        # Get the dimensions to ensure the images can be combined side by side
        width = img1.width + img2.width
        height = max(img1.height, img2.height)
        
        # Create a new blank image with a white background
        new_img = Image.new('RGB', (width, height), "white")
        
        # Paste image1 at x=0 and image2 next to image1
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (img1.width, 0))
        
        # Convert PIL image back to base64
        img_byte_arr = io.BytesIO()
        new_img.save(img_byte_arr, format='PNG')   # Format: PNG, JPEG, GIF, BMP, TIFF, PPM, WebP
        img_byte_arr = img_byte_arr.getvalue()

        return base64.b64encode(img_byte_arr).decode('utf-8')
    
    def VideoSquareEncoder(self, video1, video2):
        combined_frames = []
        # Iterate over the shorter list to ensure there's no index error
        min_length = min(len(video1), len(video2))
        
        for i in range(min_length):
            combined_frames.append(video1[i])
            combined_frames.append(video2[i])

        # Optionally, handle remaining frames if one list is longer than the other
        combined_frames.extend(video1[min_length:])
        combined_frames.extend(video2[min_length:])

        print(f"{len(combined_frames)} frames combined from both videos.")
        return combined_frames

    ########################################################################
    ###############               Embeddings                 ###############

    # Vector
    def VectorLoad(self, key=None):
        """
        Load a vector JSON by name from Media.Vectors.
        Example: load_vectors("profile") -> loads Vector/profile.json
        """
        if not key: return {}

        path = self.Vectors.get(key)
        if not path or not os.path.exists(path):    return {}

        try:
            with open(path, "r", encoding="utf-8") as f:    return json.load(f)
        except Exception:   return {}

    def VectorSave(self, key, vectors):
        """
        Save a vector JSON back to its file in Media.Vectors.
        Example: save_vectors("profile", {...})
        """
        path = self.Vectors.get(key)
        if not path:    return False

        try:
            with open(path, "w", encoding="utf-8") as f:    json.dump(vectors, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def PDFText(self, path):
        with open(path, "rb") as f:
            reader = PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

    def ChunkText(self, s, max_chars=6000):
        s = s.strip()
        return [s[i:i+max_chars] for i in range(0, len(s), max_chars)]

    def EmbedText(self, texts, client, model):
        # Batch embed (list of strings). Keep each chunk safely under token limits.
        resp = client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]

    def EmbedFile(self, file_path, client, model="text-embedding-3-small"):
        if not os.path.exists(file_path):   raise FileNotFoundError(f"File not found: {file_path}")

        # --- extract text ---
        if file_path.lower().endswith(".pdf"):
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            raise ValueError("No text extracted from file")

        # --- chunk text (avoid token limit) ---
        CHUNK_SIZE = 2000
        chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

        vectors = {}
        for i, chunk in enumerate(chunks):
            resp = client.embeddings.create(model=model, input=chunk)
            vectors[i] = {
                "text": chunk,
                "embedding": resp.data[0].embedding
            }

        # save to a JSON next to file
        out_path = os.path.splitext(file_path)[0] + ".embeds.json"
        with open(out_path, "w", encoding="utf-8") as f:    json.dump(vectors, f, ensure_ascii=False, indent=2)
        return vectors

    # RAG
    def search_embeddings(self, query, model="openai"):
        vectors = self.load_vectors()
        qv = np.array(self.embed_text(query, model))
        best = None
        best_score = -999
        for fname, vec in vectors.items():
            score = np.dot(qv, np.array(vec)) / (np.linalg.norm(qv)*np.linalg.norm(vec))
            if score > best_score:
                best_score = score
                best = fname
        return {"file": best, "score": float(best_score)}

    def json_get(self, source, path, default=""):
        """
        Resolve a dot-path from a JSON dict or a JSON file path.
        Supports simple list indices like: contacts[0].email
        Basic redaction for obviously sensitive fields (e.g., full card numbers).
        """
        
        # load dict if 'source' is a file path
        if isinstance(source, str):
            try:
                if not os.path.exists(source):
                    return default
                with open(source, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
            except Exception:
                return default
        else:
            data = source

        cur = data
        # split on dots, but allow [idx] after a key
        tokens = path.split(".") if path else []
        for tok in tokens:
            if not tok:
                return default
            # key or key[index]
            m = re.match(r'^([^\[]+)(?:\[(\d+)\])?$', tok)
            if not m:
                return default
            key, idx = m.group(1), m.group(2)

            if isinstance(cur, dict) and (key in cur):
                cur = cur[key]
            else:
                return default

            if idx is not None:
                i = int(idx)
                if isinstance(cur, list) and 0 <= i < len(cur):
                    cur = cur[i]
                else:
                    return default

        # basic redaction
        path_l = (path or "").lower()
        if isinstance(cur, str) and any(w in path_l for w in ("password", "passcode", "secret")):
            return "****"
        if isinstance(cur, str) and any(w in path_l for w in ("card", "cc", "credit")):
            digits = "".join(ch for ch in cur if ch.isdigit())
            if len(digits) >= 8:
                return f"{cur[:4]} **** **** {cur[-4:]}"
        return cur

    def _flatten_json(self, obj, prefix=""):
        """
        Flattens a small JSON object to 'dot.path = value' lines.
        Redacts obvious sensitive fields like card numbers.
        """
        import json
        lines = []
        def red(s):
            s = str(s)
            # basic redaction rules
            if "card" in prefix.lower() or "card" in s.lower():
                return s[:4] + " **** **** " + s[-4:] if s.replace(" ", "").isdigit() and len(s.replace(" ", "")) >= 8 else "****"
            return s
        def walk(x, p):
            if isinstance(x, dict):
                for k, v in x.items():
                    walk(v, f"{p}.{k}" if p else k)
            elif isinstance(x, list):
                for i, v in enumerate(x):
                    walk(v, f"{p}[{i}]")
            else:
                lines.append(f"{p} = {red(x)}")
        try:
            data = json.loads(obj) if isinstance(obj, str) else obj
        except Exception:
            return []
        walk(data, prefix)
        return lines

    def vector_lookup(self, query: str, model: str = "openai", threshold: float = 0.55):
        """
        Uses your search_embeddings() to pick the best file for a user query.
        If the cosine score is above threshold, returns {"path","score","text"}.
        """
        try:
            hit = self.search_embeddings(query, model=model) or {}
            best = hit.get("file")
            score = float(hit.get("score") or 0.0)
            if not best or score < threshold:   return None
            # read the winning file so we can surface content into chat
            with open(best, "r", encoding="utf-8", errors="ignore") as f:   return {"path": best, "score": score, "text": f.read()}
        except Exception:   return None

    def vector_context_block(self, query: str, *, model: str = "openai", threshold: float = 0.55, max_lines: int = 16, max_chars: int = 1200):
        """
        High-level: retrieve best file for `query`, flatten JSON if it is JSON,
        and return a compact context string we can prepend to chat.
        """
        hit = self.vector_lookup(query, model=model, threshold=threshold)
        if not hit:  return ""
        text = hit["text"]
        # JSON → neat facts; else fall back to first chunk of raw text
        try:
            facts = self._flatten_json(text)
            body = "\n".join(facts[:max_lines])
        except Exception:
            body = text.strip().replace("\r", "")
            if len(body) > max_chars:
                body = body[:max_chars] + " …"
        return f"User knowledge (source: {hit['path']}, score={hit['score']:.2f}):\n{body}"

########################################################################
##################              Legacy                ##################

    # Azure ( No longer using Microsoft Server ) [ Change from Wherever you call this; API, Line, Telegram, Discord ] { Time to Shelve as Legacy }
    def Language(self, text):
        try:
            response = self.Settings.Azure_Text.detect_language(documents=[text])
            if response[0].is_error:
                print(f"Error detecting language: {response[0].error}")
                return "Language Detection Error", None
            
            language_name = response[0].primary_language.name
            language_code = response[0].primary_language.iso6391_name
            print(f"Detected Language: {language_name} (Code: {language_code})")
            return language_name, language_code
        except Exception as e:
            print(f"Exception during language detection: {e}")
            return "Language Detection Error", None

    def ASpeak(self, text):
        language, code = self.Language(text)
        if code == "zh_chs" or code == "zh_cht":            self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.ChineseVoice
        elif language == "Burmese":                         self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.BurmeseVoice
        elif language == "French":                          self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.FrenchVoice
        elif language == "Hindi":                           self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.HindiVoice
        elif language == "Malay":                           self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.MalayVoice
        elif language == "Indonesian":                      self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.IndoVoice
        elif language == "Thai":                            self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.ThaiVoice
        else:                                               self.Settings.Azure_Speech.speech_synthesis_voice_name = self.Settings.EnglishJane
        
        self.Settings.Azure_Synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.Settings.Azure_Speech, audio_config=None)
        try:
            result = self.Settings.Azure_Synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                print("[Azure]: Speech synthesis succeeded.\n")
                print(type(audio_data))
                return audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:  print(f"[Azure] CANCELED: Reason={result.cancellation_details.reason}")
        except Exception as e:                                      print("[Azure] Error during audio synthesis:", e)

    def AVoice(self, audio_file):
        # Voice Message [ Voice Recognition ]
        wav_file        = self.AudioEncoder(audio_file)
        audio_config    = speechsdk.audio.AudioConfig(filename=wav_file)

        # NOTE 
        # - Add Dynamic Range by Localization in Future
        # - Manual Language Detection  ( language_config = speechsdk.languageconfig.SourceLanguageConfig("th-TH") )
        language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "zh-CN", "th-TH", "my-MM"])   # Automatic Language Detection can detect up to 4
        Azure_Decrypt   = speechsdk.SpeechRecognizer(speech_config=self.Settings.Azure_Speech, audio_config=audio_config, auto_detect_source_language_config=language_config)
        
        try:
            result = Azure_Decrypt.recognize_once_async().get()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                detected_language   = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
                corrected_text      = result.text.replace("Faye", "Fay").replace("Warrenton", "Waruntorn")
                print(f"Detected language: {detected_language}")
                return corrected_text
            elif result.reason == speechsdk.ResultReason.NoMatch:   print(f"[Azure]: No speech could be recognized: {result.no_match_details}")
            elif result.reason == speechsdk.ResultReason.Canceled:  print(f"[Azure]: Speech Recognition canceled:   {result.cancellation_details.reason}")
        except Exception as e:                                      print(f"[Azure]: Error during audio synthesis:  {e}")

    ''' # Classic Embedding
    def embed_text(self, text, client, model):
        if model == "openai":
            emb = client.embeddings.create(input=text, model="text-embedding-ada-002")
            return emb['data'][0]['embedding']
        # Add DeepSeek or others here
        return None

    def embed_file(self, file_path, client, model):
        # Add your file reading and text extraction logic here (pdf/docx/ocr)
        with open(file_path, encoding='utf-8', errors='ignore') as f:   text = f.read()
        vector = self.embed_text(text, client, model)
        # Save to store
        vectors = self.load_vectors()
        vectors[file_path] = vector
        self.save_vectors(vectors)
        return vector
    
    def embed_file(self, file_path, client, model="text-embedding-3-small"):
        # 1) Extract text (PDF images ignored; needs OCR if image-only)
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":   text = self._pdf_text(file_path)
        else:
            with open(file_path, encoding="utf-8", errors="ignore") as f:   text = f.read()

        # 2) Chunk to avoid 300k-token request limit
        chunks = self._chunk_text(text, max_chars=6000)
        if not chunks:  raise ValueError("No extractable text in file (PDF may be image-only).")

        # 3) Embed in batches
        vectors = []
        BATCH = 32
        for i in range(0, len(chunks), BATCH):
            batch = chunks[i:i+BATCH]
            vectors.extend(self.embed_texts(batch, client, model))

        # 4) Save: store both chunks and embeddings
        store = self.load_vectors() or {}
        store[file_path] = {
            "model": model,
            "dim": len(vectors[0]) if vectors else 0,
            "chunks": [{"i": i, "text": chunks[i], "embedding": vectors[i]} for i in range(len(chunks))]
        }
        self.save_vectors(store)
        return store[file_path]
    '''
    ''' # Classic Vectors
    def load_vectors(self):
        if os.path.exists(self.Vector):
            with open(self.Vector, 'r', encoding="utf-8") as f:   return json.load(f)
        return {}

    def save_vectors(self, vectors):
        with open(self.Vector, 'w') as f:   json.dump(vectors, f)
    '''

########################################################################
#################              Database                #################

class Database:
    class JSONLStorage: # Node / Hub ? [ Interface ]
        def __init__(self, file_path):
            self.file_path = file_path

        def insert_one(self, doc):
            with open(self.file_path, "a", encoding="utf-8") as f:  f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        def find_all(self):
            if not os.path.exists(self.file_path):              return []
            with open(self.file_path, encoding="utf-8") as f:   return [json.loads(line) for line in f]

    def __init__(self, base="Media/DB"):
        self.base = base
        os.makedirs(self.base, exist_ok=True)

    def name(self, s):
        s = str(s or "unknown")
        s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
        # return re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(s or "unknown"))[:80]
        return s[:80]

    def insert_one(self, collection, doc):
        path = os.path.join(self.base, f"{collection}.jsonl")
        with open(path, "a", encoding="utf-8") as f:    f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    def find_all(self, collection):
        path = os.path.join(self.base, f"{collection}.jsonl")
        if not os.path.exists(path):                return []
        with open(path, encoding="utf-8") as f:     return [json.loads(line) for line in f]

    def user_db(self, user_id):
        """
        Return a lightweight wrapper that writes to <base>/<user_id>.jsonl
        Example:
            db = WechatMessages.user_db("wx_abc123")
            db.insert_one({...})
        """
        uid         = self.name(user_id)
        user_path   = os.path.join(self.base, f"{uid}.jsonl")

        # TODO Remove this soon 
        class _UserDB:
            def insert_one(_, doc):
                with open(user_path, "a", encoding="utf-8") as f:   f.write(json.dumps(doc, ensure_ascii=False) + "\n")

            def find_all(_):
                if not os.path.exists(user_path):               return []
                with open(user_path, encoding="utf-8") as f:    return [json.loads(line) for line in f]
        return _UserDB()

    def scoped_db(self, key, scope):
        folder_path = os.path.join(self.base, scope)
        file_path = os.path.join(folder_path, f"{key}.jsonl")
        return self.JSONLStorage(file_path)

########################################################################