"""
RexSint Bot - Main Entry Point
Bot Telegram OSINT untuk pencarian data kebocoran
"""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from telegram.ext import ContextTypes

# Import core modules
from core.database import DatabaseManager
from core.api_manager import APIManager
from core.auth import AuthManager
from core.utils import load_config, setup_logging

# Import handlers
from handlers.start import StartHandler
from handlers.search import SearchHandler
from handlers.admin import AdminHandler
from handlers.shop import ShopHandler
from handlers.settings import SettingsHandler

class RexSintBot:
    """Main bot class"""
    
    def __init__(self):
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.db_manager = DatabaseManager(self.config['Database']['db_name'])
        self.api_manager = APIManager(self.config)
        self.auth_manager = AuthManager(self.config)
        
        # Initialize handlers
        self.start_handler = StartHandler(self.db_manager, self.auth_manager)
        self.search_handler = SearchHandler(self.db_manager, self.api_manager)
        self.admin_handler = AdminHandler(self.db_manager, self.config)
        self.shop_handler = ShopHandler(self.db_manager, self.config)
        self.settings_handler = SettingsHandler(self.db_manager)
        
        # Create application
        self.application = Application.builder().token(
            self.config['Telegram']['bot_token']
        ).build()
        
        self.logger.info("RexSint Bot initialized successfully")
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_handler.start))
        self.application.add_handler(CommandHandler("admin", self.admin_handler.admin_menu))
        self.application.add_handler(CommandHandler("activatetrial", self.admin_handler.activate_trial))
        self.application.add_handler(CommandHandler("generate", self.admin_handler.generate_token))
        self.application.add_handler(CommandHandler("setnewapi", self.admin_handler.set_new_api))
        
        # Message handlers - Reply keyboard
        self.application.add_handler(MessageHandler(
            filters.Regex("^🔎 Fitur Pencarian Data$"), 
            self.search_handler.search_menu
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^ℹ️ Informasi$"), 
            self.start_handler.user_info
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^🛒 Toko$"), 
            self.shop_handler.shop_menu
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^⚙️ Pengaturan$"), 
            self.settings_handler.settings_menu
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^📖 Menu$"), 
            self.start_handler.info_menu
        ))
        
        # Search type handlers
        self.application.add_handler(MessageHandler(
            filters.Regex("^📧 Cari melalui Email$"), 
            self.search_handler.search_email
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^👤 Cari dengan Nama$"), 
            self.search_handler.search_name
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^🔑 Pencarian Kata Sandi$"), 
            self.search_handler.search_password
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^📍 Cari dengan IP$"), 
            self.search_handler.search_ip
        ))
        
        self.application.add_handler(MessageHandler(
            filters.Regex("^📃 Pencarian Massal$"), 
            self.search_handler.search_bulk
        ))
        
        # File upload handler
        self.application.add_handler(MessageHandler(
            filters.Document.ALL, 
            self.search_handler.handle_file_upload
        ))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Text message handler (for search queries)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_text_message
        ))
        
        self.logger.info("All handlers registered successfully")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Route to appropriate handler based on callback data
        if data.startswith("search_"):
            await self.search_handler.handle_callback(update, context)
        elif data.startswith("admin_"):
            await self.admin_handler.handle_callback(update, context)
        elif data.startswith("shop_"):
            await self.shop_handler.handle_callback(update, context)
        elif data.startswith("settings_"):
            await self.settings_handler.handle_callback(update, context)
        elif data.startswith("info_"):
            await self.start_handler.handle_callback(update, context)
        else:
            await query.edit_message_text("❌ Callback tidak dikenali")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (search queries)"""
        # Check if user is in search mode
        user_id = update.effective_user.id
        user_data = self.db_manager.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ Silakan /start terlebih dahulu")
            return
        
        # Route to search handler for processing
        await self.search_handler.process_search_query(update, context)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Exception while handling update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi kesalahan. Silakan coba lagi atau hubungi admin."
            )
    
    def run(self):
        """Run the bot"""
        try:
            # Initialize database
            self.db_manager.init_db()
            
            # Setup handlers
            self.setup_handlers()
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            self.logger.info("Starting RexSint Bot...")
            
            # Start the bot
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            self.logger.info("Bot stopped")

def main():
    """Main function"""
    bot = RexSintBot()
    bot.run()

if __name__ == "__main__":
    main()