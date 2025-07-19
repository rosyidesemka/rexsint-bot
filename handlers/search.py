"""
Search Handler for RexSint Bot
Handles all search-related operations and queries
"""
import asyncio
import tempfile
from datetime import datetime
import logging
import os
import tempfile
from typing import Dict, Any, List, Optional
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from core.database import DatabaseManager
from core.api_manager import APIManager
from core.auth import AuthManager
from core.utils import (
    get_search_keyboard,
    get_search_result_keyboard,
    get_file_search_keyboard,
    validate_user_input,
    parse_file_content,
    sanitize_filename,
    generate_report_filename,
    log_search_activity,
    create_error_message,
    create_success_message,
    create_warning_message,
    truncate_text,
    get_maintenance_message
)

class SearchHandler:
    """Handles all search operations"""
    
    def __init__(self, db_manager: DatabaseManager, api_manager: APIManager):
        self.db_manager = db_manager
        self.api_manager = api_manager
        self.logger = logging.getLogger(__name__)
        self.user_search_context = {}  # Store user search context
    
    async def search_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show search menu"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            # Check if user can search
            auth_manager = AuthManager({'Admin': {'admin_chat_id': None}})
            access_check = await auth_manager.check_trial_activation(user_data)
            
            if not access_check['can_search']:
                await update.message.reply_text(
                    access_check['message'],
                    parse_mode='Markdown'
                )
                return
            
            # Check bot maintenance mode
            bot_status = self.db_manager.get_bot_status()
            if bot_status and bot_status.get('is_maintenance'):
                await update.message.reply_text(
                    get_maintenance_message(user_data.get('language_code', 'id')),
                    parse_mode='Markdown'
                )
                return
            
            lang = user_data.get('language_code', 'id')
            
            if lang == 'id':
                message = f"""
🔎 **Fitur Pencarian Data**

💡 **Status Akun:**
• Token tersisa: {user_data.get('token_balance', 0)} 🪙
• Total pencarian: {user_data.get('total_requests', 0)} 📊
• Pencarian file: {user_data.get('file_requests', 0)} 📁

🔍 **Jenis Pencarian:**
• **Email** - Cari berdasarkan alamat email
• **Nama** - Cari berdasarkan nama lengkap
• **Password** - Cari berdasarkan kata sandi
• **Kendaraan** - Cari data kendaraan
• **Telegram** - Cari akun Telegram
• **Facebook** - Cari akun Facebook
• **Instagram** - Cari akun Instagram
• **IP Address** - Cari berdasarkan IP (Premium)
• **Pencarian Massal** - Upload file untuk pencarian bulk
• **Pencarian Gabungan** - Kombinasi multiple query

⚡ **Fitur Khusus:**
• AI Summary dengan Google Gemini
• Laporan HTML lengkap
• Export hasil pencarian

Pilih jenis pencarian yang Anda inginkan di bawah ini.
                """
            else:
                message = f"""
🔎 **Search Features**

💡 **Account Status:**
• Remaining tokens: {user_data.get('token_balance', 0)} 🪙
• Total searches: {user_data.get('total_requests', 0)} 📊
• File searches: {user_data.get('file_requests', 0)} 📁

🔍 **Search Types:**
• **Email** - Search by email address
• **Name** - Search by full name
• **Password** - Search by password
• **Vehicle** - Search vehicle data
• **Telegram** - Search Telegram accounts
• **Facebook** - Search Facebook accounts
• **Instagram** - Search Instagram accounts
• **IP Address** - Search by IP (Premium)
• **Bulk Search** - Upload file for bulk search
• **Combined Search** - Multiple query combination

⚡ **Special Features:**
• AI Summary with Google Gemini
• Complete HTML reports
• Export search results

Select the type of search you want below.
                """
            
            await update.message.reply_text(
                message,
                reply_markup=get_search_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing search menu: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan menu pencarian"),
                parse_mode='Markdown'
            )
    
    async def search_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle email search"""
        await self._initiate_search(update, context, "email", "📧", "email address")
    
    async def search_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle name search"""
        await self._initiate_search(update, context, "name", "👤", "full name")
    
    async def search_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle password search"""
        await self._initiate_search(update, context, "password", "🔑", "password")
    
    async def search_ip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle IP search"""
        await self._initiate_search(update, context, "ip", "📍", "IP address", premium=True)
    
    async def search_bulk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bulk search"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            # Check premium access
            auth_manager = AuthManager({'Admin': {'admin_chat_id': None}})
            has_premium = await auth_manager.check_premium_feature(user_data, 'bulk_search')
            
            if not has_premium:
                lang = user_data.get('language_code', 'id')
                if lang == 'id':
                    message = "❌ Pencarian massal hanya tersedia untuk pengguna premium. Silakan upgrade akun Anda di menu 🛒 Toko."
                else:
                    message = "❌ Bulk search is only available for premium users. Please upgrade your account in the 🛒 Shop menu."
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            lang = user_data.get('language_code', 'id')
            
            if lang == 'id':
                message = """
📃 **Pencarian Massal (Bulk Search)**

📁 **Format File yang Didukung:**
• Text (.txt)
• CSV (.csv)
• JSON (.json)

📋 **Format Konten:**
• Satu query per baris
• Maksimal 100 query per file
• Maksimal ukuran file: 1MB

💡 **Contoh Format:**
```
john@example.com
user@domain.com
jane.doe@gmail.com
```

📤 **Cara Penggunaan:**
1. Siapkan file dengan format yang sesuai
2. Upload file ke chat ini
3. Bot akan memproses semua query
4. Dapatkan laporan lengkap

Silakan upload file Anda sekarang.
                """
            else:
                message = """
📃 **Bulk Search**

📁 **Supported File Formats:**
• Text (.txt)
• CSV (.csv)
• JSON (.json)

📋 **Content Format:**
• One query per line
• Maximum 100 queries per file
• Maximum file size: 1MB

💡 **Example Format:**
```
john@example.com
user@domain.com
jane.doe@gmail.com
```

📤 **How to Use:**
1. Prepare file with proper format
2. Upload file to this chat
3. Bot will process all queries
4. Get complete report

Please upload your file now.
                """
            
            # Store search context
            self.user_search_context[user_id] = {
                'type': 'bulk',
                'waiting_for_file': True
            }
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error initiating bulk search: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memulai pencarian massal"),
                parse_mode='Markdown'
            )
    
    async def handle_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle file upload for bulk search"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            # Check if user is in bulk search context
            if user_id not in self.user_search_context or not self.user_search_context[user_id].get('waiting_for_file'):
                await update.message.reply_text(
                    "❌ Silakan gunakan menu 📃 Pencarian Massal terlebih dahulu.",
                    parse_mode='Markdown'
                )
                return
            
            document = update.message.document
            lang = user_data.get('language_code', 'id')
            
            # Validate file size (max 1MB)
            if document.file_size > 1024 * 1024:
                if lang == 'id':
                    message = "❌ Ukuran file terlalu besar. Maksimal 1MB."
                else:
                    message = "❌ File size too large. Maximum 1MB."
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Validate file type
            allowed_extensions = ['.txt', '.csv', '.json']
            file_extension = os.path.splitext(document.file_name)[1].lower()
            
            if file_extension not in allowed_extensions:
                if lang == 'id':
                    message = "❌ Format file tidak didukung. Gunakan .txt, .csv, atau .json"
                else:
                    message = "❌ Unsupported file format. Use .txt, .csv, or .json"
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Download and process file
            if lang == 'id':
                processing_msg = await update.message.reply_text(
                    "⏳ Memproses file... Harap tunggu.",
                    parse_mode='Markdown'
                )
            else:
                processing_msg = await update.message.reply_text(
                    "⏳ Processing file... Please wait.",
                    parse_mode='Markdown'
                )
            
            # Download file
            file = await context.bot.get_file(document.file_id)
            file_content = await file.download_as_bytearray()
            
            # Parse file content
            queries = parse_file_content(bytes(file_content), document.file_name)
            
            if not queries:
                if lang == 'id':
                    message = "❌ File kosong atau format tidak valid."
                else:
                    message = "❌ File is empty or format is invalid."
                
                await processing_msg.edit_text(message, parse_mode='Markdown')
                return
            
            if len(queries) > 100:
                queries = queries[:100]
                if lang == 'id':
                    warning = f"⚠️ Hanya 100 query pertama yang akan diproses dari {len(queries)} query."
                else:
                    warning = f"⚠️ Only first 100 queries will be processed from {len(queries)} queries."
                
                await update.message.reply_text(warning, parse_mode='Markdown')
            
            # Clear search context
            self.user_search_context[user_id] = {'type': 'bulk', 'waiting_for_file': False}
            
            # Process bulk search
            await self._process_bulk_search(update, context, queries, processing_msg)
            
        except Exception as e:
            self.logger.error(f"Error handling file upload: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memproses file upload"),
                parse_mode='Markdown'
            )
    
    async def process_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process search query from text message"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                return
            
            # Check if user is in search context
            if user_id not in self.user_search_context:
                return
            
            search_context = self.user_search_context[user_id]
            search_type = search_context.get('type')
            
            if not search_type or search_context.get('waiting_for_file'):
                return
            
            query = update.message.text.strip()
            
            # Validate input
            validation = validate_user_input(query, search_type)
            if not validation['valid']:
                await update.message.reply_text(
                    create_error_message(validation['error']),
                    parse_mode='Markdown'
                )
                return
            
            # Process single search
            await self._process_single_search(update, context, query, search_type)
            
        except Exception as e:
            self.logger.error(f"Error processing search query: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memproses query pencarian"),
                parse_mode='Markdown'
            )
    
    async def _initiate_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              search_type: str, icon: str, display_name: str, premium: bool = False) -> None:
        """Initiate search process"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            # Check premium access if required
            if premium:
                auth_manager = AuthManager({'Admin': {'admin_chat_id': None}})
                has_premium = await auth_manager.check_premium_feature(user_data, search_type)
                
                if not has_premium:
                    lang = user_data.get('language_code', 'id')
                    if lang == 'id':
                        message = f"❌ Pencarian {display_name} hanya tersedia untuk pengguna premium. Silakan upgrade akun Anda di menu 🛒 Toko."
                    else:
                        message = f"❌ {display_name} search is only available for premium users. Please upgrade your account in the 🛒 Shop menu."
                    
                    await update.message.reply_text(message, parse_mode='Markdown')
                    return
            
            lang = user_data.get('language_code', 'id')
            
            if lang == 'id':
                message = f"""
{icon} **Pencarian {display_name.title()}**

💡 **Petunjuk:**
• Masukkan {display_name} yang ingin dicari
• Pastikan format input benar
• Hasil akan ditampilkan dengan AI summary
• Laporan lengkap dapat diunduh

🔍 **Contoh Input:**
"""
            else:
                message = f"""
{icon} **{display_name.title()} Search**

💡 **Instructions:**
• Enter the {display_name} you want to search
• Make sure input format is correct
• Results will be shown with AI summary
• Complete report can be downloaded

🔍 **Input Example:**
"""
            
            # Add examples based on search type
            if search_type == "email":
                if lang == 'id':
                    message += "• user@example.com\n• john.doe@gmail.com"
                else:
                    message += "• user@example.com\n• john.doe@gmail.com"
            elif search_type == "name":
                if lang == 'id':
                    message += "• John Doe\n• Jane Smith"
                else:
                    message += "• John Doe\n• Jane Smith"
            elif search_type == "password":
                if lang == 'id':
                    message += "• password123\n• mypassword"
                else:
                    message += "• password123\n• mypassword"
            elif search_type == "ip":
                if lang == 'id':
                    message += "• 192.168.1.1\n• 10.0.0.1"
                else:
                    message += "• 192.168.1.1\n• 10.0.0.1"
            
            if lang == 'id':
                message += "\n\n📝 **Silakan ketik query Anda sekarang:**"
            else:
                message += "\n\n📝 **Please type your query now:**"
            
            # Store search context
            self.user_search_context[user_id] = {
                'type': search_type,
                'waiting_for_file': False
            }
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error initiating search: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memulai pencarian"),
                parse_mode='Markdown'
            )
    
    async def _process_single_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   query: str, search_type: str) -> None:
        """Process single search query"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            lang = user_data.get('language_code', 'id')
            
            # Check token balance
            if user_data.get('token_balance', 0) <= 0:
                if lang == 'id':
                    message = "❌ Token pencarian habis. Silakan beli token di menu 🛒 Toko."
                else:
                    message = "❌ Search tokens exhausted. Please buy tokens in 🛒 Shop menu."
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Show processing message
            if lang == 'id':
                processing_msg = await update.message.reply_text(
                    "🔍 **Melakukan pencarian...**\n\n⏳ Harap tunggu, proses ini membutuhkan beberapa detik.",
                    parse_mode='Markdown'
                )
            else:
                processing_msg = await update.message.reply_text(
                    "🔍 **Searching...**\n\n⏳ Please wait, this process takes a few seconds.",
                    parse_mode='Markdown'
                )
            
            # Get user API token
            api_token = user_data.get('api_token')
            if not api_token:
                await processing_msg.edit_text(
                    create_error_message("Token API tidak ditemukan"),
                    parse_mode='Markdown'
                )
                return
            
            # Perform search
            search_results = await self.api_manager.search_data(
                query, api_token, limit=100, lang=lang
            )
            
            if not search_results:
                if lang == 'id':
                    message = "❌ Gagal melakukan pencarian. Silakan coba lagi."
                else:
                    message = "❌ Failed to perform search. Please try again."
                
                await processing_msg.edit_text(message, parse_mode='Markdown')
                return
            
            # Check for errors
            if "error" in search_results:
                await processing_msg.edit_text(
                    create_error_message(search_results["error"]),
                    parse_mode='Markdown'
                )
                return
            
            # Update token balance and request count
            self.db_manager.update_user(user_id, token_balance=user_data.get('token_balance', 0) - 1)
            self.db_manager.increment_requests(user_id)
            self.db_manager.increment_api_count()
            
            # Format results
            formatted_results = self.api_manager.format_search_results(search_results, lang)
            
            # Generate AI summary
            ai_summary = await self.api_manager.summarize_with_gemini(search_results, lang)
            
            # Combine results
            full_message = f"{ai_summary}\n\n{formatted_results}"
            
            # Truncate if too long
            if len(full_message) > 4000:
                full_message = truncate_text(full_message, 3800)
            
            # Store results for download
            context.user_data['last_search_results'] = search_results
            context.user_data['last_search_query'] = query
            context.user_data['last_search_type'] = search_type
            
            # Send results
            has_results = "List" in search_results and search_results["List"]
            await processing_msg.edit_text(
                full_message,
                reply_markup=get_search_result_keyboard(has_results, lang),
                parse_mode='Markdown'
            )
            
            # Log search activity
            results_count = len(search_results.get("List", {})) if "List" in search_results else 0
            log_search_activity(user_id, query, search_type, results_count)
            
            # Clear search context
            if user_id in self.user_search_context:
                del self.user_search_context[user_id]
            
        except Exception as e:
            self.logger.error(f"Error processing single search: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memproses pencarian"),
                parse_mode='Markdown'
            )
    
    async def _process_bulk_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 queries: List[str], processing_msg) -> None:
        """Process bulk search queries"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            lang = user_data.get('language_code', 'id')
            
            # Check token balance
            required_tokens = len(queries)
            if user_data.get('token_balance', 0) < required_tokens:
                if lang == 'id':
                    message = f"❌ Token tidak mencukupi. Dibutuhkan {required_tokens} token, tersedia {user_data.get('token_balance', 0)}."
                else:
                    message = f"❌ Insufficient tokens. Required {required_tokens} tokens, available {user_data.get('token_balance', 0)}."
                
                await processing_msg.edit_text(message, parse_mode='Markdown')
                return
            
            # Get user API token
            api_token = user_data.get('api_token')
            if not api_token:
                await processing_msg.edit_text(
                    create_error_message("Token API tidak ditemukan"),
                    parse_mode='Markdown'
                )
                return
            
            # Process bulk search
            all_results = {}
            processed_count = 0
            
            for i, query in enumerate(queries):
                # Update progress
                progress = f"🔍 Memproses query {i+1}/{len(queries)}...\n⏳ {query[:50]}..."
                await processing_msg.edit_text(progress, parse_mode='Markdown')
                
                # Perform search
                result = await self.api_manager.search_data(
                    query, api_token, limit=50, lang=lang
                )
                
                if result and "error" not in result:
                    all_results[query] = result
                    processed_count += 1
                
                # Small delay to prevent rate limiting
                await asyncio.sleep(0.5)
            
            # Update token balance and request count
            used_tokens = min(processed_count, user_data.get('token_balance', 0))
            self.db_manager.update_user(user_id, token_balance=user_data.get('token_balance', 0) - used_tokens)
            self.db_manager.increment_requests(user_id, file_request=True)
            
            # Generate summary
            if lang == 'id':
                summary = f"""
📊 **Hasil Pencarian Massal**

✅ **Berhasil diproses:** {processed_count}/{len(queries)} query
🪙 **Token digunakan:** {used_tokens}
📁 **Database ditemukan:** {sum(len(r.get('List', {})) for r in all_results.values())}

🤖 **AI Summary akan diproses...**
                """
            else:
                summary = f"""
📊 **Bulk Search Results**

✅ **Successfully processed:** {processed_count}/{len(queries)} queries
🪙 **Tokens used:** {used_tokens}
📁 **Databases found:** {sum(len(r.get('List', {})) for r in all_results.values())}

🤖 **AI Summary will be processed...**
                """
            
            # Store results for download
            context.user_data['last_bulk_results'] = all_results
            context.user_data['last_bulk_queries'] = queries
            
            # Send summary
            await processing_msg.edit_text(
                summary,
                reply_markup=get_file_search_keyboard(lang),
                parse_mode='Markdown'
            )
            
            # Log bulk search activity
            log_search_activity(user_id, f"Bulk search: {len(queries)} queries", "bulk", processed_count)
            
            # Clear search context
            if user_id in self.user_search_context:
                del self.user_search_context[user_id]
            
        except Exception as e:
            self.logger.error(f"Error processing bulk search: {e}")
            await processing_msg.edit_text(
                create_error_message("Gagal memproses pencarian massal"),
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle search-related callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await query.edit_message_text("❌ Data pengguna tidak ditemukan. Silakan /start ulang.")
                return
            
            lang = user_data.get('language_code', 'id')
            
            if data == "download_full_report":
                await self._download_full_report(query, context, lang)
            elif data == "download_bulk_report":
                await self._download_bulk_report(query, context, lang)
            elif data == "new_search":
                await self._new_search(query, lang)
            elif data == "back_to_main":
                await self._back_to_main(query, lang)
            elif data == "view_summary":
                await self._view_bulk_summary(query, context, lang)
            
        except Exception as e:
            self.logger.error(f"Error handling search callback: {e}")
            await query.edit_message_text(
                create_error_message("Terjadi kesalahan dalam memproses permintaan")
            )
    
    async def _download_full_report(self, query, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
        """Download full search report"""
        try:
            search_results = context.user_data.get('last_search_results')
            search_query = context.user_data.get('last_search_query')
            search_type = context.user_data.get('last_search_type')
            
            if not search_results:
                if lang == 'id':
                    message = "❌ Data pencarian tidak ditemukan. Silakan lakukan pencarian ulang."
                else:
                    message = "❌ Search data not found. Please perform a new search."
                
                await query.edit_message_text(message)
                return
            
            # Generate HTML report
            html_report = self.api_manager.create_html_report(search_results, search_query)
            
            # Create temporary file
            filename = generate_report_filename(search_query, search_type)
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            temp_file.write(html_report)
            temp_file.close()
            
            # Send file
            with open(temp_file.name, 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=InputFile(f, filename=filename),
                    caption="📄 Laporan pencarian lengkap" if lang == 'id' else "📄 Complete search report"
                )
            
            # Clean up
            os.unlink(temp_file.name)
            
            if lang == 'id':
                message = "✅ Laporan berhasil diunduh!"
            else:
                message = "✅ Report downloaded successfully!"
            
            await query.edit_message_text(message)
            
        except Exception as e:
            self.logger.error(f"Error downloading report: {e}")
            await query.edit_message_text(
                create_error_message("Gagal mengunduh laporan")
            )
    
    async def _download_bulk_report(self, query, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
        """Download bulk search report"""
        try:
            bulk_results = context.user_data.get('last_bulk_results')
            bulk_queries = context.user_data.get('last_bulk_queries')
            
            if not bulk_results:
                if lang == 'id':
                    message = "❌ Data pencarian massal tidak ditemukan."
                else:
                    message = "❌ Bulk search data not found."
                
                await query.edit_message_text(message)
                return
            
            # Generate combined HTML report
            html_report = self._create_bulk_html_report(bulk_results, bulk_queries)
            
            # Create temporary file
            filename = f"RexSint_bulk_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            temp_file.write(html_report)
            temp_file.close()
            
            # Send file
            with open(temp_file.name, 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=InputFile(f, filename=filename),
                    caption="📄 Laporan pencarian massal lengkap" if lang == 'id' else "📄 Complete bulk search report"
                )
            
            # Clean up
            os.unlink(temp_file.name)
            
            if lang == 'id':
                message = "✅ Laporan massal berhasil diunduh!"
            else:
                message = "✅ Bulk report downloaded successfully!"
            
            await query.edit_message_text(message)
            
        except Exception as e:
            self.logger.error(f"Error downloading bulk report: {e}")
            await query.edit_message_text(
                create_error_message("Gagal mengunduh laporan massal")
            )
    
    def _create_bulk_html_report(self, bulk_results: Dict[str, Any], queries: List[str]) -> str:
        """Create HTML report for bulk search"""
        from datetime import datetime
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RexSint Bulk Search Report</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .query-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .database {{ margin: 15px 0; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                .data-record {{ margin: 10px 0; padding: 10px; background-color: #fff; border-radius: 3px; }}
                .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 RexSint Bulk Search Report</h1>
                <p><strong>Total Queries:</strong> {len(queries)}</p>
                <p><strong>Processed:</strong> {len(bulk_results)}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Summary</h2>
                <p><strong>Total Databases Found:</strong> {sum(len(r.get('List', {})) for r in bulk_results.values())}</p>
                <p><strong>Success Rate:</strong> {(len(bulk_results) / len(queries) * 100):.1f}%</p>
            </div>
        """
        
        for query, results in bulk_results.items():
            html_template += f"""
            <div class="query-section">
                <h3>🔍 Query: {query}</h3>
            """
            
            if "List" in results:
                for db_name, db_data in results["List"].items():
                    if db_name == "No results found":
                        html_template += "<p>❌ No results found</p>"
                        continue
                    
                    html_template += f"""
                    <div class="database">
                        <h4>📊 {db_name}</h4>
                        <p>{db_data.get('InfoLeak', 'No information available')}</p>
                    """
                    
                    if "Data" in db_data and db_data["Data"]:
                        for i, record in enumerate(db_data["Data"][:5]):  # Show first 5 records
                            html_template += f'<div class="data-record"><strong>Record {i+1}:</strong><br>'
                            for key, value in record.items():
                                if value and str(value).strip():
                                    html_template += f"<strong>{key}:</strong> {value}<br>"
                            html_template += "</div>"
                        
                        if len(db_data["Data"]) > 5:
                            remaining = len(db_data["Data"]) - 5
                            html_template += f"<p><em>... and {remaining} more records</em></p>"
                    
                    html_template += "</div>"
            
            html_template += "</div>"
        
        html_template += """
            <div class="footer">
                <p><em>Generated by RexSint OSINT Bot</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_template