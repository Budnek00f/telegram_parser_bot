import os
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler

from config import Config
from src.bot.handlers import (
    start_command, 
    help_command, 
    handle_photo, 
    handle_document,
    button_callback
)

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Проверка токена
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле!")
        return
    
    # Создание приложения
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрация обработчиков медиа
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Регистрация обработчика callback-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запуск бота
    logger.info("Bot is starting...")
    print("🤖 Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()