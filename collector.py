"""MajinStore 3.0: diagnóstico de ofertas públicas; não infere preços de variantes."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'offers.json'
LINKS = ROOT / 'links.txt'
NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
ALLOWED_HOSTS = {'ggmax.com.br', 'www.ggmax.com.br'}


def money(text):
    m = re.search(r'R\$\s*([\d.]+,\d{2})', text)
    return round(float(m.group(1).replace('.', '').replace(',', '.')), 2) if m else None


def extract(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.select_one('h1')
    if not title:
        return None, None, 'Título principal não encontrado'
    # Only extract from the explicitly known primary-price element.
    # Other R$ values may be from related ads or different variants.
    price_node = soup.select_one('.price__container h3')
    if not price_node:
        return title.get_text(' ', strip=True), None, 'Seletor do preço principal não encontrado; layout possivelmente mudou'
    price = money(price_node.get_text(' ', strip=True))
    if price is None:
        return title.get_text(' ', strip=True), None, 'Preço principal sem valor reconhecível'
    return title.get_text(' ', strip=True), price, None


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    urls = list(dict.fromkeys(line.strip() for line in LINKS.read_text(encoding='utf-8').splitlines()
                              if line.strip() and not line.lstrip().startswith('#')))[:100]
    offers = {item['url']: item for item in data.get('offers', []) if item.get('url')}
    failures, changes, checks = [], [], []
    session = requests.Session()
    session.headers.update({'User-Agent': 'MajinStorePriceMonitor/1.1 (public pages; contact site for access)'})
    for url in urls:
        checked = NOW()
        result = {'url': url, 'checked_at': checked, 'status': 'error'}
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS or not parsed.path.startswith('/anuncio/'):
            result['reason'] = 'URL fora do formato permitido'
        else:
            try:
                response = session.get(url, timeout=20, allow_redirects=False)
                result['http_status'] = response.status_code
                result['content_type'] = response.headers.get('Content-Type', '')[:100]
                result['bytes'] = len(response.content)
                if 300 <= response.status_code < 400:
                    target = response.headers.get('Location', '')
                    result['reason'] = 'Redirecionamento HTTP; destino: ' + target[:120]
                elif response.status_code != 200:
                    result['reason'] = 'Servidor respondeu HTTP ' + str(response.status_code)
                elif 'html' not in result['content_type'].lower():
                    result['reason'] = 'Resposta não é HTML'
                else:
                    title, price, error = extract(response.text)
                    if error:
                        result['reason'] = error
                    else:
                        old = offers.get(url, {})
                        old_price = old.get('price')
                        if isinstance(old_price, (int, float)) and abs(old_price - price) > 0.001:
                            changes.append({'url': url, 'before': old_price, 'after': price, 'title': title})
                        offers[url] = {**old, 'url': url, 'title': title, 'price': price,
                                       'checked_at': checked, 'price_scope': 'Preço principal do anúncio; variante NÃO confirmada'}
                        result['status'] = 'ok'
                        result['price'] = price
                        result['title'] = title
            except requests.exceptions.RequestException as exc:
                result['reason'] = 'Erro de rede: ' + str(exc)[:160]
            except Exception as exc:
                result['reason'] = 'Erro de extração: ' + str(exc)[:160]
        if result['status'] != 'ok':
            failures.append({'url': url, 'error': result.get('reason', 'Desconhecido'),
                             'http_status': result.get('http_status'), 'checked_at': checked})
        checks.append(result)
        print(f"[{len(checks)}/{len(urls)}] {result['status'].upper()} HTTP {result.get('http_status','-')} {url} | {result.get('reason', 'preço '+str(result.get('price')))}", flush=True)
        time.sleep(2)
    data['offers'] = list(offers.values())
    data['updated_at'] = NOW()
    data['failures'] = failures
    data['checks'] = checks
    data['monitor_summary'] = {'total': len(urls), 'success': len(urls)-len(failures),
                               'failures': len(failures), 'changes': len(changes)}
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    msg = f"MajinStore: {len(urls)-len(failures)}/{len(urls)} consultas OK, {len(failures)} falhas, {len(changes)} alterações verificadas."
    print(msg)
    token, chat = os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_ID')
    if token and chat and (changes or failures):
        try:
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
                          json={'chat_id': chat, 'text': msg}, timeout=12).raise_for_status()
        except requests.exceptions.RequestException as exc:
            print('Falha no Telegram:', exc)


if __name__ == '__main__':
    main()
