#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import tempfile
import time
from datetime import datetime
from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage

class MessageCopier:
    """Üzenetmásoló osztály"""
    
    def __init__(self, telegram_client, source_channel_id, destination_channel_id):
        self.client = telegram_client
        self.source_channel_id = source_channel_id
        self.destination_channel_id = destination_channel_id
        self.is_running = False
        self.source_entity = None
        self.destination_entity = None
        self.temp_dir = tempfile.mkdtemp(prefix='telegram_copier_')
        
    async def initialize(self):
        """Inicializálás - entitások lekérése"""
        try:
            # Forrás csatorna entitás lekérése
            if isinstance(self.source_channel_id, str):
                if self.source_channel_id.startswith('@'):
                    self.source_entity = await self.client.get_entity(self.source_channel_id)
                else:
                    try:
                        self.source_entity = await self.client.get_entity(int(self.source_channel_id))
                    except ValueError:
                        self.source_entity = await self.client.get_entity(self.source_channel_id)
            else:
                self.source_entity = await self.client.get_entity(int(self.source_channel_id))
            
            # Cél csatorna entitás lekérése
            if isinstance(self.destination_channel_id, str):
                if self.destination_channel_id.startswith('@'):
                    self.destination_entity = await self.client.get_entity(self.destination_channel_id)
                else:
                    try:
                        self.destination_entity = await self.client.get_entity(int(self.destination_channel_id))
                    except ValueError:
                        self.destination_entity = await self.client.get_entity(self.destination_channel_id)
            else:
                self.destination_entity = await self.client.get_entity(int(self.destination_channel_id))
            
            print(f"Forrás csatorna: {self.source_entity.title}")
            print(f"Cél csatorna: {self.destination_entity.title}")
            
            return True
            
        except Exception as e:
            print(f"Hiba az inicializálás során: {e}")
            return False
    
    async def start_copying(self):
        """Üzenetmásolás indítása"""
        try:
            self.is_running = True
            
            # Inicializálás
            if not await self.initialize():
                print("Inicializálás sikertelen!")
                return
            
            print("Üzenetmásolás elindítva...")
            
            # Eseménykezelő regisztrálása
            @self.client.on(events.NewMessage(chats=self.source_entity))
            async def handle_new_message(event):
                if self.is_running:
                    await self.copy_message(event.message)
            
            # Várakozás a leállításig
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Hiba a másolás során: {e}")
        finally:
            self.is_running = False
            print("Üzenetmásolás leállítva.")
    
    async def copy_message(self, message):
        """Egy üzenet másolása"""
        try:
            print(f"Új üzenet másolása: {message.id}")
            
            # Üzenet szövege
            text = message.text or ""
            
            # Média kezelése
            file_to_send = None
            
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    # Fotó letöltése
                    file_path = os.path.join(self.temp_dir, f"photo_{message.id}_{int(time.time())}.jpg")
                    downloaded_file = await self.client.download_media(message, file_path)
                    if downloaded_file:
                        file_to_send = downloaded_file
                        print(f"Fotó letöltve: {downloaded_file}")
                
                elif isinstance(message.media, MessageMediaDocument):
                    # Dokumentum/videó/audio letöltése
                    document = message.media.document
                    
                    # Fájlnév meghatározása
                    filename = f"document_{message.id}_{int(time.time())}"
                    
                    # MIME type alapján kiterjesztés
                    if document.mime_type:
                        if document.mime_type.startswith('video/'):
                            filename += '.mp4'
                        elif document.mime_type.startswith('audio/'):
                            filename += '.mp3'
                        elif document.mime_type.startswith('image/'):
                            filename += '.jpg'
                        else:
                            # Eredeti fájlnév keresése az attribútumokban
                            for attr in document.attributes:
                                if hasattr(attr, 'file_name') and attr.file_name:
                                    filename = f"{message.id}_{int(time.time())}_{attr.file_name}"
                                    break
                    
                    file_path = os.path.join(self.temp_dir, filename)
                    downloaded_file = await self.client.download_media(message, file_path)
                    if downloaded_file:
                        file_to_send = downloaded_file
                        print(f"Média letöltve: {downloaded_file}")
                
                elif isinstance(message.media, MessageMediaWebPage):
                    # Weboldal előnézet - csak a szöveget másoljuk
                    print("Weboldal előnézet - csak szöveg másolása")
            
            # Üzenet küldése a cél csatornára
            if text or file_to_send:
                await self.client.send_message(
                    self.destination_entity,
                    text,
                    file=file_to_send
                )
                print(f"Üzenet sikeresen másolva: {message.id}")
                
                # Ideiglenes fájl törlése
                if file_to_send and os.path.exists(file_to_send):
                    try:
                        os.remove(file_to_send)
                        print(f"Ideiglenes fájl törölve: {file_to_send}")
                    except Exception as e:
                        print(f"Hiba a fájl törlése során: {e}")
            
            # Kis késleltetés a rate limiting elkerülése érdekében
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Hiba az üzenet másolása során: {e}")
    
    def stop_copying(self):
        """Üzenetmásolás leállítása"""
        self.is_running = False
        print("Üzenetmásolás leállítási kérelem...")
    
    async def copy_recent_messages(self, limit=10):
        """Legutóbbi üzenetek másolása (teszteléshez)"""
        try:
            if not await self.initialize():
                print("Inicializálás sikertelen!")
                return False
            
            print(f"Legutóbbi {limit} üzenet másolása...")
            
            # Legutóbbi üzenetek lekérése
            messages = await self.client.get_messages(self.source_entity, limit=limit)
            
            for message in reversed(messages):  # Időrendi sorrendben
                if message.text or message.media:
                    await self.copy_message(message)
                    await asyncio.sleep(2)  # Nagyobb késleltetés a teszteléshez
            
            print("Legutóbbi üzenetek másolása befejezve.")
            return True
            
        except Exception as e:
            print(f"Hiba a legutóbbi üzenetek másolása során: {e}")
            return False
    
    def cleanup(self):
        """Takarítás - ideiglenes fájlok törlése"""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"Ideiglenes könyvtár törölve: {self.temp_dir}")
        except Exception as e:
            print(f"Hiba a takarítás során: {e}")
    
    def __del__(self):
        """Destruktor"""
        self.cleanup()
