#!/usr/bin/env python3
# app.py - Web service per generare cookie per tutti gli account

import asyncio
import os
import random
from datetime import datetime
from supabase import create_client
from browser_use_sdk import AsyncBrowserUse
from playwright.async_api import async_playwright
from flask import Flask, jsonify, request
from config import ACCOUNTS, DEFAULT_PASSWORD, SERVICE_NAME, SERVICE_VERSION

# ==================== CONFIGURAZIONE ====================
KEYS_SUPABASE_URL = os.environ.get("KEYS_SUPABASE_URL", "https://kdqzfsmibquvvobjvjlj.supabase.co")
KEYS_SUPABASE_KEY = os.environ.get("KEYS_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkcXpmc21pYnF1dnZvYmp2amxqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDc2MzgyMywiZXhwIjoyMDk2MzM5ODIzfQ.IQ7frzgVPgyjix9gypSkka5jAfRzdj02028-4xdT3_Y")

app = Flask(__name__)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_random_working_key():
    try:
        supabase = create_client(KEYS_SUPABASE_URL, KEYS_SUPABASE_KEY)
        resp = supabase.table('browser_use_keys')\
            .select('id', 'api_key')\
            .eq('status', 'working')\
            .execute()
        if not resp.data:
            return None
        return random.choice(resp.data)['api_key']
    except Exception as e:
        log(f"❌ Errore Supabase: {e}")
        return None

def extract_nome_utente(email):
    if '+' in email:
        return email.split('+')[1].split('@')[0]
    return email.split('@')[0]

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
            await page.wait_for_timeout(3000)
            
            await page.fill('#username', email)
            await page.fill('#password', DEFAULT_PASSWORD)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(30000)
            
            cookies = await page.context.cookies()
            cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            sesids = next((c['value'] for c in cookies if c['name'] == 'sesids'), None)
            user_id = next((c['value'] for c in cookies if c['name'] == 'user_id'), None)
            
            if sesids and user_id:
                divella_format = f"{nome}|{cookie_string}"
                log(f"   ✅ OK - sesids={sesids}")
                return True, divella_format, sesids, user_id
            else:
                log(f"   ❌ Cookie non trovati")
                return False, None, None, None
            
    except Exception as e:
        log(f"   ❌ Errore: {str(e)[:80]}")
        return False, None, None, None
    finally:
        if profile:
            await client.profiles.delete(profile.id)
        await client.close()

async def generate_all_cookies(api_key):
    results = []
    success_count = 0
    
    for i, account in enumerate(ACCOUNTS):
        log(f"\n📌 [{i+1}/{len(ACCOUNTS)}]")
        success, divella_format, sesids, user_id = await generate_cookie_for_account(api_key, account)
        
        if success:
            success_count += 1
            results.append({
                'account': account['name'],
                'email': account['email'],
                'sesids': sesids,
                'user_id': user_id,
                'divella_format': divella_format
            })
        
        if i < len(ACCOUNTS) - 1:
            await asyncio.sleep(5)
    
    return success_count, results

# ==================== ENDPOINT API ====================
@app.route('/')
def home():
    return jsonify({
        'service': SERVICE_NAME,
        'version': SERVICE_VERSION,
        'accounts_total': len(ACCOUNTS),
        'endpoints': {
            '/health': 'GET - Health check',
            '/cookies': 'GET - Genera cookie per TUTTI gli account',
            '/cookies?account=nome': 'GET - Genera cookie per un account specifico',
            '/cookies/list': 'GET - Lista account disponibili'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/cookies/list')
def list_accounts():
    return jsonify({
        'total': len(ACCOUNTS),
        'accounts': [{'name': a['name'], 'email': a['email']} for a in ACCOUNTS]
    })

@app.route('/cookies')
def get_cookies():
    account_name = request.args.get('account')
    
    if account_name:
        account = next((a for a in ACCOUNTS if a['name'] == account_name), None)
        if not account:
            return jsonify({'error': f'Account "{account_name}" non trovato'}), 404
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        api_key = get_random_working_key()
        if not api_key:
            return jsonify({'error': 'Nessuna chiave working'}), 500
        
        success, divella_format, sesids, user_id = loop.run_until_complete(
            generate_cookie_for_account(api_key, account)
        )
        
        if success:
            return jsonify({
                'success': True,
                'account': account['name'],
                'email': account['email'],
                'sesids': sesids,
                'user_id': user_id,
                'divella_format': divella_format
            })
        else:
            return jsonify({'success': False, 'error': 'Generazione fallita'}), 500
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    api_key = get_random_working_key()
    if not api_key:
        return jsonify({'error': 'Nessuna chiave working'}), 500
    
    success_count, results = loop.run_until_complete(generate_all_cookies(api_key))
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'total_accounts': len(ACCOUNTS),
        'success_count': success_count,
        'failed_count': len(ACCOUNTS) - success_count,
        'results': results
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
