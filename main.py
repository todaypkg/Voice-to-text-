import os
import whisper
from telethon import TelegramClient, events

# إعداد متغيرات Telegram API من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
username = os.getenv('USERNAME')
target_channel = os.getenv('TARGET_CHANNEL')

# إنشاء العميل
client = TelegramClient(username, api_id, api_hash)

# تحميل نموذج Whisper (استخدم نموذج صغير لتوفير الموارد في الخطة المجانية)
model = whisper.load_model("base")

# التعامل مع أمر .تحويل
@client.on(events.NewMessage(pattern=r'\.تحويل'))
async def convert_audio_to_text(event):
    reply_message = await event.get_reply_message()
    if not reply_message or not (reply_message.voice or reply_message.audio):
        await event.reply("❌ يرجى الرد على رسالة صوتية أو ملف صوتي.")
        return

    await event.reply("🔄 جاري تحويل الصوت إلى نص...")
    try:
        # تحميل الملف الصوتي
        file_path = await reply_message.download_media(file="audio_files/")
        
        # تحويل الصوت إلى نص باستخدام Whisper
        result = model.transcribe(file_path, language="ar")  # يدعم العربية والإنجليزية تلقائيًا
        text = result['text']
        
        # إرسال النص المحول إلى القناة المستهدفة
        await client.send_message(target_channel, f"🎙 النص المحول:\n{text}")
        
        # حذف الملف الصوتي بعد المعالجة
        os.remove(file_path)
        
        await event.reply("✅ تم تحويل الصوت إلى نص وإرساله إلى القناة.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء التحويل: {e}")

# تشغيل العميل
with client:
    print("🚀 البوت قيد التشغيل...")
    client.run_until_disconnected()
