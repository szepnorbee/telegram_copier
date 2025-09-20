#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError
from telethon.tl.types import Channel, Chat, User

class TelegramClientManager:
    """Telegram kliens kezelő osztály"""
    
    def __init__(self, api_id, api_hash, session_file):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_file = session_file
        self.client = None
        self.phone_code_hash = None
        
    async def start_client(self):
        """Kliens indítása és csatlakozás"""
        if self.client is None:
            self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        
        if not self.client.is_connected():
            try:
                await self.client.connect()
                print("Telethon kliens csatlakoztatva.")
            except Exception as e:
                print(f"Hiba a Telethon kliens csatlakoztatása során: {e}")
                return False
        
        if not await self.client.is_user_authorized():
            print("Telethon kliens nincs bejelentkezve.")
        else:
            print("Telethon kliens bejelentkezve.")
        return True

    async def start_login(self, phone_number):
        """Bejelentkezési folyamat indítása"""
        try:
            if self.client is None:
                await self.start_client() # Biztosítsuk, hogy a kliens inicializálva és csatlakoztatva van

            # Ellenőrizzük, hogy már be van-e jelentkezve
            if await self.client.is_user_authorized():
                return {"success": True, "message": "Már be van jelentkezve!"}
            
            # Kód küldése
            sent_code = await self.client.send_code_request(phone_number)
            self.phone_code_hash = sent_code.phone_code_hash
            
            return {"success": True, "message": "Ellenőrző kód elküldve!"}
            
        except PhoneNumberInvalidError:
            return {"success": False, "message": "Érvénytelen telefonszám!"}
        except Exception as e:
            return {"success": False, "message": f"Hiba: {str(e)}"}
    
    async def verify_code(self, code):
        """Ellenőrző kód megerősítése"""
        try:
            if not self.client or not self.phone_code_hash:
                return {"success": False, "message": "Nincs aktív bejelentkezési folyamat!"}
            
            # Kód ellenőrzése
            await self.client.sign_in(code=code, phone_code_hash=self.phone_code_hash)
            
            return {"success": True, "message": "Sikeres bejelentkezés!"}
            
        except PhoneCodeInvalidError:
            return {"success": False, "message": "Érvénytelen ellenőrző kód!"}
        except SessionPasswordNeededError:
            return {"success": False, "message": "Kétfaktoros hitelesítés szükséges! Ez jelenleg nem támogatott."}
        except Exception as e:
            return {"success": False, "message": f"Hiba: {str(e)}"}
    
    async def is_logged_in_async(self):
        """Ellenőrzi, hogy be van-e jelentkezve (aszinkron)"""
        try:
            if not self.client:
                return False
            if not self.client.is_connected():
                await self.client.connect()
            return await self.client.is_user_authorized()
        except Exception:
            return False
    
    async def get_channels(self):
        """Elérhető csatornák listájának lekérése"""
        try:
            if not self.client:
                return []
            
            if not self.client.is_connected():
                await self.client.connect()
            
            if not await self.client.is_user_authorized():
                return []
            
            dialogs = await self.client.get_dialogs()
            
            channels = []
            for dialog in dialogs:
                entity = dialog.entity
                
                if isinstance(entity, (Channel, Chat)):
                    channel_info = {
                        "id": entity.id,
                        "title": entity.title,
                        "username": getattr(entity, "username", None),
                        "type": "channel" if isinstance(entity, Channel) else "chat"
                    }
                    channels.append(channel_info)
            
            return channels
            
        except Exception as e:
            print(f"Hiba a csatornák lekérése során: {e}")
            return []
    
    async def get_entity_by_id(self, channel_id):
        """Entitás lekérése ID alapján"""
        try:
            if not self.client:
                return None
            
            if not self.client.is_connected():
                await self.client.connect()
            
            if isinstance(channel_id, str):
                if channel_id.startswith("@"):
                    return await self.client.get_entity(channel_id)
                else:
                    try:
                        return await self.client.get_entity(int(channel_id))
                    except ValueError:
                        return await self.client.get_entity(channel_id)
            else:
                return await self.client.get_entity(int(channel_id))
                
        except Exception as e:
            print(f"Hiba az entitás lekérése során: {e}")
            return None
    
    async def send_message(self, entity, message, file=None):
        """Üzenet küldése"""
        try:
            if not self.client:
                return False
            
            if not self.client.is_connected():
                await self.client.connect()
            
            await self.client.send_message(entity, message, file=file)
            return True
            
        except Exception as e:
            print(f"Hiba az üzenet küldése során: {e}")
            return False
    
    async def download_media(self, message, file_path):
        """Média letöltése"""
        try:
            if not self.client:
                return None
            
            if not self.client.is_connected():
                await self.client.connect()
            
            return await self.client.download_media(message, file_path)
            
        except Exception as e:
            print(f"Hiba a média letöltése során: {e}")
            return None
    
    async def disconnect(self):
        """Kliens leválasztása"""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
                print("Telethon kliens leválasztva.")
        except Exception as e:
            print(f"Hiba a kliens leválasztása során: {e}")
    
    def __del__(self):
        """Destruktor"""
        # A __del__ metódus nem aszinkron, és nem hívhatunk benne await-et.
        # A kliens leválasztását a Flask alkalmazás leállításakor kell kezelni,
        # vagy a start_client() metódusban biztosítani, hogy a kliens mindig
        # csatlakoztatva legyen, amikor szükség van rá.
        pass

