import os
import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from PIL import Image
import tempfile
from io import BytesIO

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni
TOKEN = "7654657103:AAGCkI1IFn_ThjLwKZRAiJyvHv76y5vEZvE"

# Foydalanuvchilar uchun vaqtinchalik ma'lumotlar
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni ishga tushirish"""
    await update.message.reply_text(
        "👋 Assalomu alaykum! Men JPG rasmlarni PDF ga aylantiruvchi botman.\n\n"
        "Bir nechta rasmlarni bitta PDF fayliga birlashtirish uchun:\n"
        "1. /newpdf - Yangi PDF yaratish\n"
        "2. Rasmlarni birma-bir yuboring\n"
        "3. /generate - PDFni yaratish\n\n"
        "Yoki oddiygina rasm yuboring - men uni alohida PDF qilib beraman."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam ma'lumoti"""
    await update.message.reply_text(
        "ℹ️ Botdan foydalanish usullari:\n\n"
        "1. Yakka rasm yuboring - alohida PDF qilib beraman\n"
        "2. Bir nechta rasmlarni bitta PDFga birlashtirish:\n"
        "   - /newpdf - yangi PDF uchun boshlash\n"
        "   - Rasmlarni yuboring (10 tagacha)\n"
        "   - /generate - PDFni yaratish\n\n"
        "Bot .jpg, .jpeg formatlarini qo'llab-quvvatlaydi."
    )

async def new_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yangi PDF yaratishni boshlash"""
    chat_id = update.message.chat_id
    user_data[chat_id] = {'images': [], 'mode': 'multi'}
    
    await update.message.reply_text(
        "📄 Yangi PDF yaratish boshlandi!\n"
        "Endi menga PDFga qo'shmoqchi bo'lgan rasmlaringizni yuboring.\n"
        "10 ta rasmga qadar qabul qilaman.\n"
        "Tayyor bo'lganda /generate buyrug'ini yuboring."
    )

async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PDFni yaratish"""
    chat_id = update.message.chat_id
    
    if chat_id not in user_data or not user_data[chat_id]['images']:
        await update.message.reply_text("❌ PDF yaratish uchun hech qanday rasm yubormadingiz. Iltimos, avval rasmlarni yuboring.")
        return
    
    if len(user_data[chat_id]['images']) < 1:
        await update.message.reply_text("❌ Kamida 1 ta rasm yuborishingiz kerak. Iltimos, rasmlarni yuboring.")
        return
    
    message = await update.message.reply_text("🔄 PDF yaratilmoqda...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # PDF fayli uchun joy
            output_filename = "birlashtirilgan.pdf"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Barcha rasmlarni PDF ga aylantiramiz
            images = [Image.open(img) for img in user_data[chat_id]['images']]
            
            # Birinchi rasmni asos qilib PDF yaratamiz
            images[0].save(
                output_path, 
                "PDF", 
                resolution=100.0,
                save_all=True,
                append_images=images[1:]
            )
            
            # Foydalanuvchiga yuboramiz
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=InputFile(f, filename=output_filename),
                    caption=f"✅ {len(images)} ta rasmdan tayyor PDF fayli!"
                )
            
            # Ma'lumotlarni tozalab qo'yamiz
            del user_data[chat_id]
            await message.delete()
            
    except Exception as e:
        logger.error(f"PDF yaratishda xato: {e}")
        await message.edit_text("❌ PDF yaratishda xato yuz berdi. Iltimos, qayta urinib ko'ring.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegramdan yuborilgan rasmlarni qabul qilish"""
    chat_id = update.message.chat_id
   
    # Agar foydalanuvchi multi mode da bo'lmasa, oddiy PDF qilib qaytaramiz
    if chat_id not in user_data or user_data[chat_id].get('mode') != 'multi':
        await single_image_to_pdf(update, context)
        return
    
    # Multi mode da ishlaymiz
    if len(user_data[chat_id]['images']) >= 10:
        await update.message.reply_text("⚠️ 10 ta rasm limitiga yetdingiz. /generate buyrug'i bilan PDFni yarating.")
        return
    
    message = await update.message.reply_text("🔄 Rasm qabul qilindi...")
    
    try:
        # Rasmni yuklab olamiz
        photo_file = await update.message.photo[-1].get_file()
        img_data = BytesIO()
        await photo_file.download_to_memory(out=img_data)
        
        # Vaqtinchalik faylga yozamiz
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(img_data.getvalue())
            user_data[chat_id]['images'].append(tmp_file.name)
        
        await message.edit_text(f"✅ Rasm qabul qilindi! ({len(user_data[chat_id]['images'])}/10)\nTayyor bo'lganda /generate buyrug'ini yuboring.")
        
    except Exception as e:
        logger.error(f"Rasmni saqlashda xato: {e}")
        await message.edit_text("❌ Rasmni qabul qilishda xato yuz berdi. Iltimos, qayta urinib ko'ring.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuborilgan .jpg fayllarini qabul qilish"""
    document = update.message.document
    chat_id = update.message.chat_id
    
    # Fayl JPG ekanligini tekshiramiz
    if not (document.file_name.lower().endswith('.jpg') or 
            document.file_name.lower().endswith('.jpeg')):
        await update.message.reply_text("❌ Iltimos, .jpg yoki .jpeg formatidagi rasm yuboring.")
        return
    
    # Agar foydalanuvchi multi mode da bo'lmasa, oddiy PDF qilib qaytaramiz
    if chat_id not in user_data or user_data[chat_id].get('mode') != 'multi':
        await single_image_to_pdf(update, context)
        return
    
    # Multi mode da ishlaymiz
    if len(user_data[chat_id]['images']) >= 10:
        await update.message.reply_text("⚠️ 10 ta rasm limitiga yetdingiz. /generate buyrug'i bilan PDFni yarating.")
        return
    
    message = await update.message.reply_text("🔄 Fayl qabul qilindi...")
    
    try:
        # Faylni yuklab olamiz
        file = await context.bot.get_file(document.file_id)
        img_data = BytesIO()
        await file.download_to_memory(out=img_data)
        
        # Vaqtinchalik faylga yozamiz
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(img_data.getvalue())
            user_data[chat_id]['images'].append(tmp_file.name)
        
        await message.edit_text(f"✅ Fayl qabul qilindi! ({len(user_data[chat_id]['images'])}/10)\nTayyor bo'lganda /generate buyrug'ini yuboring.")
        
    except Exception as e:
        logger.error(f"Faylni saqlashda xato: {e}")
        await message.edit_text("❌ Faylni qabul qilishda xato yuz berdi. Iltimos, qayta urinib ko'ring.")

async def single_image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bitta rasmni PDF qilib qaytarish"""
    message = await update.message.reply_text("🔄 Rasm qayta ishlanmoqda...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Rasmni yuklab olamiz
            if update.message.photo:
                photo_file = await update.message.photo[-1].get_file()
                input_path = os.path.join(temp_dir, "image.jpg")
                await photo_file.download_to_drive(input_path)
                output_filename = "converted.pdf"
            else:
                document = update.message.document
                file = await context.bot.get_file(document.file_id)
                input_path = os.path.join(temp_dir, document.file_name)
                await file.download_to_drive(input_path)
                output_filename = os.path.splitext(document.file_name)[0] + ".pdf"
            
            output_path = os.path.join(temp_dir, output_filename)
            
            # PDF ga aylantiramiz
            image = Image.open(input_path)
            image.save(output_path, "PDF", resolution=100.0)
            
            # Foydalanuvchiga yuboramiz
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=InputFile(f, filename=output_filename),
                    caption="✅ PDF faylingiz tayyor!"
                )
            await message.delete()
            
    except Exception as e:
        logger.error(f"Yakka rasmni PDFga aylantirishda xato: {e}")
        await message.edit_text("❌ Rasmni PDFga aylantirishda xato yuz berdi. Iltimos, qayta urinib ko'ring.")

def main():
    """Botni ishga tushiramiz"""
    application = Application.builder().token(TOKEN).build()
    
    # Komandalar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("newpdf", new_pdf))
    application.add_handler(CommandHandler("generate", generate_pdf))
    
    # Rasmlar va fayllar
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    
    # Botni ishga tushiramiz
    application.run_polling()

if __name__ == "__main__":
    main()
