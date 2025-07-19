"""
API Manager for RexSint Bot
Handles LeakOSINT API and Google Gemini API integration
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import google.generativeai as genai

class APIManager:
    """Manages API calls to LeakOSINT and Google Gemini"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.leakosint_url = "https://leakosintapi.com/"
        
        # Initialize Gemini API
        if self.config.get('APIs', {}).get('gemini_api_key'):
            genai.configure(api_key=self.config['APIs']['gemini_api_key'])
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
            self.logger.warning("Gemini API key not found")
    
    async def generate_user_token(self, user_id: int, active_token: str) -> Optional[str]:
        """Generate new API token for user using active bot token"""
        try:
            data = {
                "token": active_token,
                "action": "generate_token",
                "user_id": user_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.leakosint_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "token" in result:
                            self.logger.info(f"Generated token for user {user_id}")
                            return result["token"]
                    
                    self.logger.error(f"Failed to generate token for user {user_id}: {await response.text()}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error generating token for user {user_id}: {e}")
            return None
    
    async def search_data(self, query: str, api_token: str, limit: int = 100, lang: str = "id") -> Optional[Dict[str, Any]]:
        """Search data using LeakOSINT API"""
        try:
            data = {
                "token": api_token,
                "request": query,
                "limit": limit,
                "lang": lang,
                "type": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.leakosint_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Check for errors
                        if "Error code" in result:
                            self.logger.error(f"API Error: {result['Error code']}")
                            return {"error": result["Error code"]}
                        
                        self.logger.info(f"Search completed for query: {query[:50]}...")
                        return result
                    
                    self.logger.error(f"API request failed: {response.status}")
                    return {"error": f"API request failed: {response.status}"}
                    
        except Exception as e:
            self.logger.error(f"Error searching data: {e}")
            return {"error": str(e)}
    
    async def search_bulk(self, queries: List[str], api_token: str, limit: int = 100, lang: str = "id") -> Optional[Dict[str, Any]]:
        """Search multiple queries at once"""
        try:
            data = {
                "token": api_token,
                "request": queries,
                "limit": limit,
                "lang": lang,
                "type": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.leakosint_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if "Error code" in result:
                            self.logger.error(f"Bulk API Error: {result['Error code']}")
                            return {"error": result["Error code"]}
                        
                        self.logger.info(f"Bulk search completed for {len(queries)} queries")
                        return result
                    
                    self.logger.error(f"Bulk API request failed: {response.status}")
                    return {"error": f"Bulk API request failed: {response.status}"}
                    
        except Exception as e:
            self.logger.error(f"Error in bulk search: {e}")
            return {"error": str(e)}
    
    def validate_search_input(self, query: str, search_type: str) -> Dict[str, Any]:
        """Validate search input based on type"""
        query = query.strip()
        
        if not query:
            return {"valid": False, "error": "Query tidak boleh kosong"}
        
        if search_type == "email":
            if "@" not in query:
                return {"valid": False, "error": "Format email tidak valid"}
        
        elif search_type == "ip":
            # Simple IP validation
            parts = query.split(".")
            if len(parts) != 4:
                return {"valid": False, "error": "Format IP tidak valid"}
            
            try:
                for part in parts:
                    if not 0 <= int(part) <= 255:
                        return {"valid": False, "error": "Format IP tidak valid"}
            except ValueError:
                return {"valid": False, "error": "Format IP tidak valid"}
        
        elif search_type == "phone":
            # Remove common phone number characters
            clean_phone = query.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not clean_phone.isdigit() or len(clean_phone) < 8:
                return {"valid": False, "error": "Format nomor telepon tidak valid"}
        
        return {"valid": True, "cleaned_query": query}
    
    async def summarize_with_gemini(self, search_results: Dict[str, Any], lang: str = "id") -> str:
        """Summarize search results using Gemini AI"""
        if not self.gemini_model:
            return "❌ Fitur AI Summary tidak tersedia"
        
        try:
            # Prepare prompt based on language
            if lang == "id":
                prompt = f"""
                Ringkas hasil pencarian OSINT berikut dalam bahasa Indonesia:
                
                {json.dumps(search_results, indent=2)}
                
                Berikan ringkasan yang mencakup:
                1. Jumlah database yang ditemukan
                2. Jenis data yang terekspos
                3. Tingkat risiko (rendah/sedang/tinggi)
                4. Rekomendasi tindakan
                
                Format dalam bahasa Indonesia yang mudah dipahami, maksimal 500 kata.
                """
            else:
                prompt = f"""
                Summarize the following OSINT search results in English:
                
                {json.dumps(search_results, indent=2)}
                
                Include:
                1. Number of databases found
                2. Types of exposed data
                3. Risk level (low/medium/high)
                4. Recommended actions
                
                Format in clear English, maximum 500 words.
                """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.gemini_model.generate_content, prompt
            )
            
            if response and response.text:
                return f"🤖 **AI Summary:**\n\n{response.text}"
            else:
                return "❌ Gagal membuat ringkasan AI"
                
        except Exception as e:
            self.logger.error(f"Error generating AI summary: {e}")
            return "❌ Error dalam pembuatan ringkasan AI"
    
    def format_search_results(self, results: Dict[str, Any], lang: str = "id") -> str:
        """Format search results for display"""
        if "error" in results:
            if lang == "id":
                return f"❌ **Error:** {results['error']}"
            else:
                return f"❌ **Error:** {results['error']}"
        
        if "List" not in results:
            if lang == "id":
                return "❌ Tidak ada hasil ditemukan"
            else:
                return "❌ No results found"
        
        formatted_text = ""
        database_count = 0
        
        for database_name, database_data in results["List"].items():
            if database_name == "No results found":
                continue
                
            database_count += 1
            formatted_text += f"📊 **{database_name}**\n"
            
            if "InfoLeak" in database_data:
                formatted_text += f"ℹ️ {database_data['InfoLeak']}\n"
            
            if "Data" in database_data and database_data["Data"]:
                formatted_text += "\n🔍 **Data Ditemukan:**\n"
                
                # Show first few results
                for i, record in enumerate(database_data["Data"][:3]):
                    formatted_text += f"**Record {i+1}:**\n"
                    for key, value in record.items():
                        if value and str(value).strip():
                            formatted_text += f"  • {key}: {value}\n"
                    formatted_text += "\n"
                
                if len(database_data["Data"]) > 3:
                    remaining = len(database_data["Data"]) - 3
                    formatted_text += f"... dan {remaining} record lainnya\n"
            
            formatted_text += "\n" + "="*50 + "\n\n"
        
        if database_count == 0:
            if lang == "id":
                return "❌ Tidak ada data ditemukan"
            else:
                return "❌ No data found"
        
        # Add summary header
        if lang == "id":
            header = f"🔍 **Hasil Pencarian OSINT**\n\n📊 Ditemukan {database_count} database\n\n"
        else:
            header = f"🔍 **OSINT Search Results**\n\n📊 Found {database_count} databases\n\n"
        
        return header + formatted_text
    
    def create_html_report(self, results: Dict[str, Any], query: str) -> str:
        """Create HTML report from search results"""
        try:
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>RexSint OSINT Report</title>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 10px; }}
                    .database {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .data-record {{ background-color: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 3px; }}
                    .timestamp {{ color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔍 RexSint OSINT Report</h1>
                    <p><strong>Query:</strong> {query}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """
            
            if "List" in results:
                for database_name, database_data in results["List"].items():
                    if database_name == "No results found":
                        continue
                    
                    html_template += f"""
                    <div class="database">
                        <h2>📊 {database_name}</h2>
                        <p>{database_data.get('InfoLeak', 'No information available')}</p>
                    """
                    
                    if "Data" in database_data and database_data["Data"]:
                        for i, record in enumerate(database_data["Data"]):
                            html_template += f'<div class="data-record"><strong>Record {i+1}:</strong><br>'
                            for key, value in record.items():
                                if value and str(value).strip():
                                    html_template += f"<strong>{key}:</strong> {value}<br>"
                            html_template += "</div>"
                    
                    html_template += "</div>"
            
            html_template += """
                <div class="timestamp">
                    <p><em>Generated by RexSint OSINT Bot</em></p>
                </div>
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            self.logger.error(f"Error creating HTML report: {e}")
            return f"<html><body><h1>Error creating report: {e}</h1></body></html>"
    
    async def check_api_health(self, token: str) -> bool:
        """Check if API token is working"""
        try:
            data = {
                "token": token,
                "request": "test",
                "limit": 1,
                "type": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.leakosint_url, json=data, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        return "Error code" not in result
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error checking API health: {e}")
            return False