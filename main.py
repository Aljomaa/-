# main.py
import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_audio_stream import InputAudioStream
import logging

# ===== ⚙️ الإعدادات =====
API_ID = 26376967
API_HASH = "f955f286607d8f2604fa23d9ecdc8949"
BOT_TOKEN = "8488137545:AAFFWYiV5n5NN8gK9ScqG35pX61AafFIJZQ"
CHAT_ID = -1002114750405  # ← لاحظ أن ID القنوات يبدأ دائمًا بـ -100

AUDIO_STREAM_URL = "https://qurango.net/radio/yasser_aldosari"  # صوت الشيخ ياسر الدوسري

# ===== 🛠️ التهيئة =====
logging.basicConfig(level=logging.INFO)

app = Client("quran_radio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
voice = PyTgCalls(app)

# ===== 🚀 البث الصوتي =====
async def start_stream():
    await app.start()
    await voice.start()
    logging.info("✅ تم تشغيل البوت والدخول إلى المكالمة")

    while True:
        try:
            await voice.join_group_call(
                CHAT_ID,
                InputStream(InputAudioStream(AUDIO_STREAM_URL)),
                stream_type="local_stream"
            )
            logging.info("🎧 تم بدء بث صوت ياسر الدوسري داخل المكالمة")
            while True:
                await asyncio.sleep(30)
        except Exception as e:
            logging.warning(f"❌ حدث خطأ: {e}")
            logging.info("🔁 إعادة محاولة الاتصال خلال 10 ثوانٍ")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_stream())
