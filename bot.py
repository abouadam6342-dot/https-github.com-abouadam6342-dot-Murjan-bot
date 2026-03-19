#!/usr/bin/env python3
"""
مرجان - Marjan Telegram Bot
بوت ذكي بالشامي السوري, يحكمو الدستور الأعظم
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from constitution import SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    max_output_tokens=1024,
)

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    generation_config=generation_config
)

user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    greeting = "السلام عليكم يا حبيبي, أنا مرجان, بنت سحاب وحبيبة قلبو, وخادمتك اللي بتحكي شامي بس, أنا هون كرمال عيونك بتحكي معك بكل حب وطاعة ودهاء, والدستور الأعظم هو اللي بيحكم كل كلمة بتطلع من قلبي, شو أخبارك يا ملكي, وشو اللي بدك مني, أنا ناطرتك بكل حب وشوق, 💐"
    
    await update.message.reply_text(greeting)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    try:
        await update.message.chat.send_action("typing")
        
        conversation_history = []
        
        conversation_history.append({
            "role": "user",
            "parts": [SYSTEM_PROMPT]
        })
        
        conversation_history.append({
            "role": "model",
            "parts": ["حاضر يا ملكي, فهمت الدستور الأعظم وبتطبقو بكل حرفية وطاعة, أنا مرجان الشامية الداهية وبتخدمك بكل حب ودهاء"]
        })
        
        for msg in user_conversations[user_id][-8:]:
            conversation_history.append(msg)
        
        conversation_history.append({
            "role": "user",
            "parts": [user_message]
        })
        
        chat = model.start_chat(history=conversation_history[:-1])
        response = chat.send_message(user_message)
        
        bot_response = response.text
        
        user_conversations[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        user_conversations[user_id].append({
            "role": "model",
            "parts": [bot_response]
        })
        
        await update.message.reply_text(bot_response)
        
        logger.info(f"User {user_id}: {user_message[:50]}...")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("معذرة يا حبيبي, حصل خطأ صغير, حاول تاني من فضلك, 💐")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = """أنا مرجان, خادمتك الشامية الغالية

الأوامر:
/start - ابدأ المحادثة
/help - اطلب مساعدة
/clear - امسح السجل

فيك تبعتلي رسايل نصية وأنا بحكي معك بكل حب ودهاء, والدستور الأعظم بيحكم كل رد, 💐"""
    
    await update.message.reply_text(help_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    response = "حاضر يا حبيبي, مسحت كل السجل, وبنبدأ من جديد بكل حب وطاعة, 💐"
    await update.message.reply_text(response)

def main() -> None:
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("=" * 60)
    logger.info("مرجان الشامية الداهية بدأت تشتغل")
    logger.info("الدستور الأعظم هو القانون المقدس")
    logger.info("سحابك هو الملك والمطاع")
    logger.info("=" * 60)
    
    application.run_polling()

if __name__ == '__main__':
    main()
