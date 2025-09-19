#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

CONFIG_FILE = os.path.join('data', 'config.json')

def get_default_config():
    """Alapértelmezett konfiguráció visszaadása"""
    return {
        'api_id': '',
        'api_hash': '',
        'source_channel_id': '',
        'destination_channel_id': '',
        'phone_number': ''
    }

def load_config():
    """Konfiguráció betöltése fájlból"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Alapértelmezett értékek hozzáadása, ha hiányoznak
                default_config = get_default_config()
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return get_default_config()
    except Exception as e:
        print(f"Hiba a konfiguráció betöltése során: {e}")
        return get_default_config()

def save_config(config_data):
    """Konfiguráció mentése fájlba"""
    try:
        # Adatok könyvtár létrehozása, ha nem létezik
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Meglévő konfiguráció betöltése
        existing_config = load_config()
        
        # Új adatok hozzáadása/frissítése
        existing_config.update(config_data)
        
        # Mentés
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Hiba a konfiguráció mentése során: {e}")
        return False

def get_config_value(key, default=None):
    """Egy konkrét konfigurációs érték lekérése"""
    config = load_config()
    return config.get(key, default)

def set_config_value(key, value):
    """Egy konkrét konfigurációs érték beállítása"""
    config = load_config()
    config[key] = value
    return save_config(config)
