import os
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import wraps
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import openai
from dotenv import load_dotenv
import PyPDF2
import requests
from PIL import Image
from flask_sqlalchemy import SQLAlchemy

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS", "").split(",")))
FREE_LIMIT = int(os.getenv("FREE_LIMIT", 10))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# تحقق من القيم المطلوبة
if not (TELEGRAM_TOKEN and OPENAI_API_KEY and WEBHOOK_URL):
    raise ValueError("يرجى ضبط TELEGRAM_TOKEN و OPENAI_API_KEY و WEBHOOK_URL في .env")

# إعدادات OpenAI
openai.api_key = OPENAI_API_KEY

# إعداد Flask و Telegram
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# النماذج
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    free_usage_count = db.Column(db.Integer, default=0)
    free_usage_reset = db.Column(db.DateTime, default=datetime.utcnow)

class PaidUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active(self):
        return self.joined_at + relativedelta(months=1) > datetime.utcnow()

with app.app_context():
    db.create_all()

# GPT
def ask_openai(prompt, paid=False):
    model = "gpt-4" if paid else "gpt-3.5-turbo"
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

# توليد صورة
def generate_image(prompt: str) -> bytes:
    resp = openai.Image.create(prompt=prompt, n=1, size="512x512")
    return requests.get(resp['data'][0]['url']).content

# التحقق من الاشتراك
def subscription_required(func):
    @wraps(func)
    def wrapper(update: Update, context):
        tg_id = update.effective_user.id
        with app.app_context():
            user = User.query.filter_by(telegram_id=tg_id).first()
            if not user:
                user = User(telegram_id=tg_id)
                db.session.add(user)
            paid = PaidUser.query.filter_by(telegram_id=tg_id).first()

            if user.free_usage_reset.date() != datetime.utcnow().date():
                user.free_usage_count = 0
                user.free_usage_reset = datetime.utcnow()

            if tg_id in ADMIN_IDS:
                db.session.commit()
                return func(update, context)

            if paid and paid.is_active():
                db.session.commit()
                return func(update, context)

            if user.free_usage_count < FREE_LIMIT:
                user.free_usage_count += 1
                db.session.commit()
                return func(update, context)
            else:
                update.message.reply_text(
                    f"❌ لقد استنفدت الحد المجاني اليومي ({FREE_LIMIT} استخدام).\n"
                    "🔓 راسل المشرف للترقية إلى GPT-4 بلا حدود."
                )
    return wrapper

# المعالجات
def start(update, context):
    update.message.reply_text(
        "🤖 أهلاً بك!\n"
        "- النسخة المجانية: GPT-3.5 | 10 طلبات يومياً\n"
        "- النسخة المدفوعة: GPT-4 بلا حدود\n"
        "أرسل سؤالك أو استخدم /image لتوليد صورة.\n"
        "راسل المشرف للاشتراك."
    )

@subscription_required
def handle_text(update, context):
    paid = bool(PaidUser.query.filter_by(telegram_id=update.effective_user.id).first())
    reply = ask_openai(update.message.text, paid=paid)
    update.message.reply_text(reply)

@subscription_required
def handle_document(update, context):
    file = update.message.document.get_file()
    bio = io.BytesIO()
    file.download(out=bio)
    bio.seek(0)

    if update.message.document.file_name.lower().endswith('.pdf'):
        reader = PyPDF2.PdfReader(bio)
        text = "".join(page.extract_text() for page in reader.pages)
    else:
        text = bio.read().decode(errors="ignore")

    if len(text) > 2000:
        text = text[:2000] + "\n\n...[مختصر]"

    paid = bool(PaidUser.query.filter_by(telegram_id=update.effective_user.id).first())
    answer = ask_openai(f"هذا محتوى الملف:\n{text}", paid=paid)
    update.message.reply_text(answer)

@subscription_required
def handle_photo(update, context):
    photo = update.message.photo[-1].get_file()
    bio = io.BytesIO()
    photo.download(out=bio)
    bio.seek(0)
    update.message.reply_photo(photo=bio, caption="✅ استلمت الصورة، كيف تريد تحليلها؟")

@subscription_required
def handle_image_command(update, context):
    prompt = ' '.join(context.args)
    if not prompt:
        update.message.reply_text("❗ استخدم: /image وصف_الصورة")
        return
    update.message.reply_text("🖼️ جاري توليد الصورة…")
    img_data = generate_image(prompt)
    bio = io.BytesIO(img_data)
    bio.name = 'generated.png'
    update.message.reply_photo(photo=bio)

def add_paid(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        target = int(context.args[0])
    except:
        update.message.reply_text("❗ استخدم: /addpaid <telegram_id>")
        return
    with app.app_context():
        if not PaidUser.query.filter_by(telegram_id=target).first():
            db.session.add(PaidUser(telegram_id=target))
            db.session.commit()
            update.message.reply_text(f"✅ تم تفعيل الاشتراك للـ ID: {target}")
        else:
            update.message.reply_text("ℹ️ هذا المستخدم مشترك مسبقاً.")

def remove_paid(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        target = int(context.args[0])
    except:
        update.message.reply_text("❗ استخدم: /removepaid <telegram_id>")
        return
    with app.app_context():
        paid = PaidUser.query.filter_by(telegram_id=target).first()
        if paid:
            db.session.delete(paid)
            db.session.commit()
            update.message.reply_text(f"❌ تم إلغاء الاشتراك للـ ID: {target}")
        else:
            update.message.reply_text("ℹ️ لم أجد هذا المستخدم في قائمة المشتركين.")

# تسجيل المعالجات
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addpaid", add_paid))
dispatcher.add_handler(CommandHandler("removepaid", remove_paid))
dispatcher.add_handler(CommandHandler("image", handle_image_command))
dispatcher.add_handler(MessageHandler(Filters.document, handle_document))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

# نقطة Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# تعيين Webhook تلقائيًا داخل Flask
@app.before_first_request
def activate_webhook():
    bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set from Flask")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
