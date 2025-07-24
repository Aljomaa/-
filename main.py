import asyncio
import os
import logging
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_audio_stream import InputAudioStream
from flask import Flask

# ⚙️ إعداد المتغيرات من البيئة
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
AUDIO_STREAM_URL = "https://qurango.net/radio/yasser_aldosari"

# 📋 تهيئة اللوغ
logging.basicConfig(level=logging.INFO)

# 🧠 إعداد البوت والصوت
app = Client("quran_voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
voice = PyTgCalls(app)

# 🌐 سيرفر Flask وهمي ليرضي Render
web = Flask(__name__)

@web.route("/")
def index():
    return "✅ Quran Radio Bot is running."

# 🚀 وظيفة تشغيل البث في المكالمة
async def start_stream():
    await app.start()
    await voice.start()
    logging.info("✅ البوت بدأ بنجاح.")

    while True:
        try:
            await voice.join_group_call(
                CHAT_ID,
                InputStream(InputAudioStream(AUDIO_STREAM_URL)),
                stream_type="local_stream"
            )
            logging.info("🎧 تم بدء البث بصوت ياسر الدوسري")
            while True:
                await asyncio.sleep(30)
        except Exception as e:
            logging.warning(f"❌ خطأ: {e}")
            await asyncio.sleep(10)

# ✅ تشغيل Flask و البث معًا
def run_all():
    import threading
    threading.Thread(target=lambda: web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    asyncio.get_event_loop().run_until_complete(start_stream())

if __name__ == "__main__":
    run_all()
