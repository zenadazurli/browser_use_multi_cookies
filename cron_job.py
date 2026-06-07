#!/usr/bin/env python3
# cron_job.py - Versione per cron job con chiusura forzata sessioni

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
KEYS_SUPABASE_KEY = os.environ.get("KEYS_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

COOKIE_SUPABASE_URL = os.environ.get("COOKIE_SUPABASE_URL", "https://ofijopixtpwahgbwyutc.supabase.co")
COOKIE_SUPABASE_KEY = os.environ.get("COOKIE_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

DEFAULT_PASSWORD = "DDnmVV45!!"

# Account (importa da config)
try:
    from config import ACCOUNTS
except ImportError:
    # Fallback per test
    ACCOUNTS = [
        {'email': 'sandrominori50+ulugarecexisa@gmail.com', 'name': 'ulugarecexisa'},
        {'email': 'sandrominori50+ukageluli@gmail.com', 'name': 'ukageluli'},
    ]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_random_working_key():
    try:
        supabase = create_client(KEYS_SUPABASE_URL, KEYS_SUPABASE_KEY)
        resp = supabase.table('browser_use_keys')\
            .select('api_key')\
            .eq('status', 'working')\
            .execute()
        if not resp.data:
            return None
        return random.choice(resp.data)['api_key']
    except Exception as e:
        log(f"❌ Errore Supabase: {e}")
        return None

def save_cookie_to_db(email, nome_utente, cookie_string, sesids, user_id):
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
    email = account['email']
    nome = account['name']
    
    log(f"🚀 {nome} - {email}")
    
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
            
            # Attesa per redirect (45 secondi)
            await page.wait_for_timeout(45000)
            
            cookies = await page.context.cookies()
            cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            sesids = next((c['value'] for c in cookies if c['name'] == 'sesids'), None)
            user_id = next((c['value'] for c in cookies if c['name'] == 'user_id'), None)
            
            if sesids and user_id:
                log(f"   ✅ OK - sesids={sesids}")
                save_cookie_to_db(email, nome, cookie_string, sesids, user_id)
                return True, divella_format
            else:
                log(f"   ❌ Cookie non trovati")
                return False, None
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            log(f"   ❌ RATE LIMIT (429) - aspetto prima di continuare")
        else:
            log(f"   ❌ Errore: {error_msg[:80]}")
        return False, None
    finally:
        # === CHIUSURA FORZATA ===
        if profile:
            try:
                await client.profiles.delete(profile.id)
                log(f"   🗑️ Profilo {profile.id} eliminato")
            except:
                pass
        try:
            await client.close()
            log(f"   🔒 Client chiuso")
        except:
            pass
        # Pausa extra per permettere la chiusura completa
        await asyncio.sleep(2)
        gc.collect()  # Forza garbage collection

async def main():
    log("=" * 60)
    log("CRON JOB - GENERAZIONE COOKIE")
    log(f"Account: {len(ACCOUNTS)}")
    log("=" * 60)
    
    api_key = get_random_working_key()
    if not api_key:
        log("❌ Nessuna chiave working")
        return
    
    log(f"🔑 Chiave: {api_key[:20]}...")
    
    successi = 0
    falliti = 0
    rate_limits = 0
    
    for i, account in enumerate(ACCOUNTS):
        log(f"\n📌 [{i+1}/{len(ACCOUNTS)}]")
        
        success, _ = await generate_cookie_for_account(api_key, account)
        
        if success:
            successi += 1
        else:
            falliti += 1
        
        # === PAUSA TRA GLI ACCOUNT (20 secondi) ===
        if i < len(ACCOUNTS) - 1:
            log(f"   ⏳ Pausa 20 secondi prima del prossimo account...")
            await asyncio.sleep(20)
    
    log("\n" + "=" * 60)
    log("📊 RIEPILOGO FINALE")
    log("=" * 60)
    log(f"✅ Successi: {successi}")
    log(f"❌ Falliti: {falliti}")
    log(f"📊 Totale: {len(ACCOUNTS)}")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
