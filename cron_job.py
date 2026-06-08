#!/usr/bin/env python3
# cron_job.py - Generazione cookie con cambio chiave automatico su 429

import asyncio
import os
import random
import gc
from datetime import datetime
from supabase import create_client
from browser_use_sdk import AsyncBrowserUse
from playwright.async_api import async_playwright

# ==================== CONFIGURAZIONE ====================
KEYS_SUPABASE_URL = os.environ.get("KEYS_SUPABASE_URL", "https://kdqzfsmibquvvobjvjlj.supabase.co")
KEYS_SUPABASE_KEY = os.environ.get("KEYS_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkcXpmc21pYnF1dnZvYmp2amxqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDc2MzgyMywiZXhwIjoyMDk2MzM5ODIzfQ.IQ7frzgVPgyjix9gypSkka5jAfRzdj02028-4xdT3_Y")

COOKIE_SUPABASE_URL = os.environ.get("COOKIE_SUPABASE_URL", "https://ofijopixtpwahgbwyutc.supabase.co")
COOKIE_SUPABASE_KEY = os.environ.get("COOKIE_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9maWpvcGl4dHB3YWhnYnd5dXRjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTkyODIxMiwiZXhwIjoyMDkxNTA0MjEyfQ.BkWb8EuUUJSUUgg3sepDmOdUzsXY7pjGjykQnPMK9q4")

DEFAULT_PASSWORD = "DDnmVV45!!"
MAX_ATTEMPTS = 5  # Tentativi massimi per account
PAUSE_BETWEEN_ACCOUNTS = 20  # Secondi tra un account e l'altro

# Account EasyHits4U
ACCOUNTS = [
    {'email': 'sandrominori50+ulugarecexisa@gmail.com', 'name': 'ulugarecexisa'},
    {'email': 'sandrominori50+ukageluli@gmail.com', 'name': 'ukageluli'},
    {'email': 'sandrominori50+ukaxiloki@gmail.com', 'name': 'ukaxiloki'},
    {'email': 'sandrominori50+uchikilaremu@gmail.com', 'name': 'uchikilaremu'},
    {'email': 'sandrominori50+ufrrmncrachinora@gmail.com', 'name': 'ufrrmncrachinora'},
    {'email': 'sandrominori50+unenomasagebebe@gmail.com', 'name': 'unenomasagebebe'},
    {'email': 'sandrominori50+uisnrnafwttvvceer@gmail.com', 'name': 'uisnrnafwttvvceer'},
    {'email': 'sandrominori50+ujuenpaorgl@gmail.com', 'name': 'ujuenpaorgl'},
    {'email': 'sandrominori50+uvuoobe@gmail.com', 'name': 'uvuoobe'},
    {'email': 'sandrominori50+uoovoge@gmail.com', 'name': 'uoovoge'},
    {'email': 'sandrominori50+ukafifoko@gmail.com', 'name': 'ukafifoko'},
    {'email': 'sandrominori50+ubozogaza@gmail.com', 'name': 'ubozogaza'},
    {'email': 'sandrominori50+udapasa@gmail.com', 'name': 'udapasa'},
    {'email': 'sandrominori50+uluglqupgbe@gmail.com', 'name': 'uluglqupgbe'},
    {'email': 'sandrominori50+unaglbene@gmail.com', 'name': 'unaglbene'},
    {'email': 'sandrominori50+umachizo@gmail.com', 'name': 'umachizo'},
    {'email': 'sandrominori50+ulaaacummgl@gmail.com', 'name': 'ulaaacummgl'},
    {'email': 'sandrominori50+ufrrageboki@gmail.com', 'name': 'ufrrageboki'},
    {'email': 'sandrominori50+unomama@gmail.com', 'name': 'unomama'},
    {'email': 'sandrominori50+ucuquaacuge@gmail.com', 'name': 'ucuquaacuge'},
    {'email': 'sandrominori50+ukufeno@gmail.com', 'name': 'ukufeno'},
    {'email': 'sandrominori50+ukitulobbqu@gmail.com', 'name': 'ukitulobbqu'},
    {'email': 'sandrominori50+udaglkilerm@gmail.com', 'name': 'udaglkilerm'},
    {'email': 'sandrominori50+usaadgapa@gmail.com', 'name': 'usaadgapa'},
    {'email': 'sandrominori50+uqumopgne@gmail.com', 'name': 'uqumopgne'},
    {'email': 'sandrominori50+upgximamazo@gmail.com', 'name': 'upgximamazo'},
    {'email': 'sandrominori50+uboooggnale@gmail.com', 'name': 'uboooggnale'},
    {'email': 'sandrominori50+uenqufetr@gmail.com', 'name': 'uenqufetr'},
    {'email': 'sandrominori50+umumure@gmail.com', 'name': 'umumure'},
    {'email': 'sandrominori50+udabbpgnc@gmail.com', 'name': 'udabbpgnc'},
    {'email': 'sandrominori50+uquliufnemu@gmail.com', 'name': 'uquliufnemu'},
    {'email': 'sandrominori50+ukikreazala@gmail.com', 'name': 'ukikreazala'},
    {'email': 'sandrominori50+ulibbra@gmail.com', 'name': 'ulibbra'},
    {'email': 'sandrominori50+uzarawalita@gmail.com', 'name': 'uzarawalita'},
    {'email': 'sandrominori50+ufitamina@gmail.com', 'name': 'ufitamina'},
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_all_working_keys():
    """Prende tutte le chiavi working dal database"""
    try:
        supabase = create_client(KEYS_SUPABASE_URL, KEYS_SUPABASE_KEY)
        resp = supabase.table('browser_use_keys')\
            .select('api_key')\
            .eq('status', 'working')\
            .execute()
        if not resp.data:
            return []
        return [row['api_key'] for row in resp.data]
    except Exception as e:
        log(f"❌ Errore Supabase: {e}")
        return []

def get_random_working_key(exclude_keys=None):
    """Prende una chiave working casuale, escludendo quelle in exclude_keys"""
    keys = get_all_working_keys()
    if not keys:
        return None
    if exclude_keys:
        keys = [k for k in keys if k not in exclude_keys]
        if not keys:
            return None
    return random.choice(keys)

def update_key_status(api_key, status):
    """Aggiorna lo status di una chiave"""
    try:
        supabase = create_client(KEYS_SUPABASE_URL, KEYS_SUPABASE_KEY)
        supabase.table('browser_use_keys')\
            .update({'status': status, 'last_used': datetime.now().isoformat()})\
            .eq('api_key', api_key)\
            .execute()
        log(f"   📝 Chiave {api_key[:20]}... -> {status}")
    except Exception as e:
        log(f"   ❌ Errore aggiornamento status: {e}")

def save_cookie_to_db(email, nome_utente, cookie_string, sesids, user_id):
    """Salva i cookie su Supabase"""
    try:
        supabase = create_client(COOKIE_SUPABASE_URL, COOKIE_SUPABASE_KEY)
        divella_format = f"{nome_utente}|{cookie_string}"
        data = {
            'email': email,
            'nome_utente': nome_utente,
            'divella_format': divella_format,
            'cookie_string': cookie_string,
            'sesids': sesids,
            'user_id': user_id,
            'status': 'active',
            'updated_at': datetime.now().isoformat()
        }
        supabase.table('account_cookies').upsert(data, on_conflict='email').execute()
        log(f"   💾 Salvato su Supabase")
        return True
    except Exception as e:
        log(f"   ❌ Errore salvataggio: {e}")
        return False

async def generate_cookie_for_account(api_key, account):
    """Genera cookie per un account usando una chiave specifica"""
    email = account['email']
    nome = account['name']
    
    log(f"🚀 {nome} - {email}")
    log(f"   🔑 Chiave: {api_key[:20]}...")
    
    client = AsyncBrowserUse(api_key=api_key)
    profile = None
    
    try:
        profile = await client.profiles.create(name=f"cookie_{nome}")
        browser = await client.browsers.create(profile_id=profile.id)
        
        async with async_playwright() as p:
            pw_browser = await p.chromium.connect_over_cdp(browser.cdp_url)
            page = pw_browser.contexts[0].pages[0]
            
            await page.goto("https://www.easyhits4u.com/logon/")
            await page.wait_for_timeout(5000)
            
            await page.fill('#username', email)
            await page.fill('#password', DEFAULT_PASSWORD)
            await page.keyboard.press('Enter')
            
            await page.wait_for_timeout(45000)
            
            cookies = await page.context.cookies()
            cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            sesids = next((c['value'] for c in cookies if c['name'] == 'sesids'), None)
            user_id = next((c['value'] for c in cookies if c['name'] == 'user_id'), None)
            
            if sesids and user_id:
                log(f"   ✅ OK - sesids={sesids}")
                save_cookie_to_db(email, nome, cookie_string, sesids, user_id)
                return True
            else:
                log(f"   ❌ Cookie non trovati")
                return False
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            log(f"   ⚠️ RATE LIMIT (429)")
            update_key_status(api_key, 'rate_limited')
            return "rate_limit"
        else:
            log(f"   ❌ Errore: {error_msg[:80]}")
            return False
    finally:
        if profile:
            try:
                await client.profiles.delete(profile.id)
                log(f"   🗑️ Profilo eliminato")
            except:
                pass
        try:
            await client.close()
            log(f"   🔒 Client chiuso")
        except:
            pass
        await asyncio.sleep(2)
        gc.collect()

async def main():
    log("=" * 60)
    log("CRON JOB - CAMBIO CHIAVE SU 429")
    log(f"Account totali: {len(ACCOUNTS)}")
    log(f"Tentativi massimi per account: {MAX_ATTEMPTS}")
    log("=" * 60)
    
    # Verifica chiavi disponibili
    all_keys = get_all_working_keys()
    if not all_keys:
        log("❌ Nessuna chiave working nel database")
        return
    
    log(f"🔑 Chiavi working disponibili: {len(all_keys)}")
    
    successi = 0
    falliti = 0
    
    for i, account in enumerate(ACCOUNTS):
        log(f"\n📌 [{i+1}/{len(ACCOUNTS)}] {account['name']}")
        
        # Lista delle chiavi già usate in questo tentativo
        used_keys = []
        
        for attempt in range(MAX_ATTEMPTS):
            # Prendi una chiave non ancora usata
            api_key = get_random_working_key(exclude_keys=used_keys)
            if not api_key:
                log(f"   ❌ Nessuna chiave disponibile (tentativo {attempt+1}/{MAX_ATTEMPTS})")
                break
            
            result = await generate_cookie_for_account(api_key, account)
            
            if result == True:
                successi += 1
                break
            elif result == "rate_limit":
                used_keys.append(api_key)
                log(f"   🔄 Tentativo {attempt+1}/{MAX_ATTEMPTS} - cambio chiave...")
                continue
            else:
                falliti += 1
                break
        
        if i < len(ACCOUNTS) - 1:
            log(f"   ⏳ Pausa {PAUSE_BETWEEN_ACCOUNTS} secondi...")
            await asyncio.sleep(PAUSE_BETWEEN_ACCOUNTS)
    
    log("\n" + "=" * 60)
    log("📊 RIEPILOGO FINALE")
    log("=" * 60)
    log(f"✅ Successi: {successi}")
    log(f"❌ Falliti: {falliti}")
    log(f"📊 Totale account: {len(ACCOUNTS)}")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
