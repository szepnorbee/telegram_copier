#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import asyncio
import threading
from config import load_config, save_config, get_default_config
from telethon_client import TelegramClientManager
from message_copier import MessageCopier

app = Flask(__name__)
app.secret_key = 'telegram_copier_secret_key_2024'

# Globális változók
telegram_client_manager = None
message_copier = None
copier_thread = None
is_copying = False

# Aszinkron eseményhurok kezelése a Telethon számára
def run_async_in_thread(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Kliens inicializálása az alkalmazás indításakor
@app.before_first_request
def initialize_telegram_client():
    global telegram_client_manager
    config = load_config()
    telegram_client_manager = TelegramClientManager(
        api_id=int(config.get('api_id', 0)),
        api_hash=config.get('api_hash', ''),
        session_file=os.path.join('data', 'session.session')
    )
    # A kliens elindítása egy külön szálon, hogy ne blokkolja a Flask-et
    # és hogy a Telethon eseményhurok futhasson
    def start_telethon_client_thread():
        asyncio.run(telegram_client_manager.start_client())
    
    client_thread = threading.Thread(target=start_telethon_client_thread)
    client_thread.daemon = True
    client_thread.start()

@app.route('/')
async def index():
    """Főoldal - alkalmazás állapotának megjelenítése"""
    global is_copying, telegram_client_manager
    
    config = load_config()
    
    is_logged_in = False
    if telegram_client_manager:
        is_logged_in = await telegram_client_manager.is_logged_in_async()
    
    return render_template('index.html', 
                         config=config, 
                         is_copying=is_copying,
                         is_logged_in=is_logged_in)

@app.route('/settings')
async def settings():
    """Beállítások oldal"""
    global telegram_client_manager
    
    config = load_config()
    
    channels = []
    if telegram_client_manager and await telegram_client_manager.is_logged_in_async():
        try:
            channels = await telegram_client_manager.get_channels()
        except Exception as e:
            flash(f'Hiba a csatornák lekérése során: {str(e)}', 'error')
    
    return render_template('settings.html', config=config, channels=channels)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    """Beállítások mentése"""
    global telegram_client_manager
    try:
        config_data = {
            'api_id': request.form.get('api_id'),
            'api_hash': request.form.get('api_hash'),
            'source_channel_id': request.form.get('source_channel_id'),
            'destination_channel_id': request.form.get('destination_channel_id'),
            'phone_number': request.form.get('phone_number', '')
        }
        
        if not config_data['api_id'] or not config_data['api_hash']:
            flash('API ID és API Hash megadása kötelező!', 'error')
            return redirect(url_for('settings'))
        
        save_config(config_data)
        flash('Beállítások sikeresen mentve!', 'success')
        
        # Frissítsük a telegram_client_manager-t az új API adatokkal
        telegram_client_manager.api_id = int(config_data['api_id'])
        telegram_client_manager.api_hash = config_data['api_hash']
        
    except Exception as e:
        flash(f'Hiba a beállítások mentése során: {str(e)}', 'error')
    
    return redirect(url_for('settings'))

@app.route('/login_telegram', methods=['POST'])
async def login_telegram():
    """Telegram bejelentkezés indítása"""
    global telegram_client_manager
    
    try:
        config = load_config()
        
        if not config.get('api_id') or not config.get('api_hash'):
            return jsonify({'success': False, 'message': 'API ID és API Hash megadása szükséges!'})
        
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({'success': False, 'message': 'Telefonszám megadása kötelező!'})
        
        result = await telegram_client_manager.start_login(phone_number)
        
        if result['success']:
            return jsonify({'success': True, 'message': 'Kód elküldve! Kérjük, adja meg a kapott kódot.'})
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hiba: {str(e)}'})

@app.route('/verify_code', methods=['POST'])
async def verify_code():
    """Telegram bejelentkezési kód ellenőrzése"""
    global telegram_client_manager
    
    try:
        code = request.json.get('code')
        if not code:
            return jsonify({'success': False, 'message': 'Kód megadása kötelező!'})
        
        if not telegram_client_manager:
            return jsonify({'success': False, 'message': 'Nincs aktív bejelentkezési folyamat!'})
        
        result = await telegram_client_manager.verify_code(code)
        
        if result['success']:
            return jsonify({'success': True, 'message': 'Sikeres bejelentkezés!'})
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hiba: {str(e)}'})

@app.route('/start_copier', methods=['POST'])
async def start_copier():
    """Üzenetmásoló indítása"""
    global message_copier, copier_thread, is_copying, telegram_client_manager
    
    try:
        if is_copying:
            return jsonify({'success': False, 'message': 'A másolás már fut!'})
        
        config = load_config()
        
        if not config.get('source_channel_id') or not config.get('destination_channel_id'):
            return jsonify({'success': False, 'message': 'Forrás és cél csatorna megadása kötelező!'})
        
        if not telegram_client_manager or not await telegram_client_manager.is_logged_in_async():
            return jsonify({'success': False, 'message': 'Nincs bejelentkezve a Telegramra!'})
        
        message_copier = MessageCopier(
            telegram_client=telegram_client_manager.client,
            source_channel_id=config['source_channel_id'],
            destination_channel_id=config['destination_channel_id']
        )
        
        # Másolás indítása külön szálban
        def run_copier():
            global is_copying
            is_copying = True
            try:
                asyncio.run(message_copier.start_copying())
            except Exception as e:
                print(f"Hiba a másolás során: {e}")
            finally:
                is_copying = False
        
        copier_thread = threading.Thread(target=run_copier)
        copier_thread.daemon = True
        copier_thread.start()
        
        return jsonify({'success': True, 'message': 'Üzenetmásolás elindítva!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hiba: {str(e)}'})

@app.route('/stop_copier', methods=['POST'])
def stop_copier():
    """Üzenetmásoló leállítása"""
    global message_copier, is_copying
    
    try:
        if not is_copying:
            return jsonify({'success': False, 'message': 'A másolás nem fut!'})
        
        if message_copier:
            message_copier.stop_copying()
        
        is_copying = False
        return jsonify({'success': True, 'message': 'Üzenetmásolás leállítva!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hiba: {str(e)}'})

@app.route('/status')
async def status():
    """Alkalmazás állapotának lekérése (AJAX-hoz)"""
    global is_copying, telegram_client_manager
    
    is_logged_in = False
    if telegram_client_manager:
        is_logged_in = await telegram_client_manager.is_logged_in_async()
    
    return jsonify({
        'is_copying': is_copying,
        'is_logged_in': is_logged_in
    })

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)

