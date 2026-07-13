#### Jen

✨ **Virtual Assistant**

  Jen is a Software developed by Universal Intelligence™

  She is a Virtual Assistant on Line and Telegram and Wechat.
  Integration with Mobile and Web is also possible.
  We aim to elevate business operations with a new way to interact with Computers.

  Experience smarter interactions with Jen ~

🧱 **Project structure**

```
.
├── README.md
├── requirements.txt
├── settings.py           # runtime/config loader + API keys + model routing
├── config.json           # your local secrets (git-ignored; example below)
├── character.py          # system prompts & persona knobs for the LLM
├── media.py              # file encoding/decoding, storage hooks, embeddings
├── interface.py          # misc helpers/services used by adapters/tools
```

🚀 *Quickstart*

Python: 3.10+ recommended (3.11 works great)

🖥 _Create a virtualenv_ ( Optional ) [ You can install all the Libraries Globally on your Computer ]

```
python -m venv .venv
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

🛠 _Install dependencies_

```
pip install --upgrade pip
pip install -r requirements.txt
```

⚙️ _Configure settings_

Put your secrets in config.json

Confirm settings.py points to the right file/keys !
