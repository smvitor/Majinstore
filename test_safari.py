import requests
from pathlib import Path

urls=[s.strip() for s in Path('links.txt').read_text(encoding='utf-8').splitlines() if s.strip().startswith('https://ggmax.com.br/anuncio/')][:2]
headersets={
 'atual': {'User-Agent':'MajinStorePriceMonitor/1.0 (public pages; low frequency)'},
 'safari_iphone': {
  'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.7 Mobile/15E148 Safari/604.1',
  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language':'pt-BR,pt;q=0.9,en-US;q=0.7',
 }
}
if not urls: raise SystemExit('Nenhum link válido em links.txt')
for url in urls:
 print('\nAnúncio:',url.split('/')[-1][:85])
 for mode,headers in headersets.items():
  try:
   r=requests.get(url,headers=headers,timeout=20,allow_redirects=False)
   content_type=r.headers.get('content-type','')
   html=('text/html' in content_type and '<html' in r.text[:3000].lower())
   print(f'  {mode}: HTTP {r.status_code}; HTML={html}; bytes={len(r.content)}; redirect={bool(r.headers.get("location"))}')
   if r.status_code==200 and html:
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(r.text,'html.parser')
    print('    título:',(soup.title.get_text(' ',strip=True) if soup.title else 'ausente')[:100])
  except requests.RequestException as e:print(f'  {mode}: erro {type(e).__name__}: {str(e)[:120]}')
print('\nTeste somente leitura: nenhum preço ou JSON foi alterado.')
