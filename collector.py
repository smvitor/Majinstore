"""Conservative public-page fetcher. No login, CAPTCHA bypass or fabricated variants."""
import json,os,re,time,datetime,pathlib,requests
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).parent
f=P/'data/offers.json'
d=json.loads(f.read_text()); urls=[x.strip() for x in (P/'links.txt').read_text().splitlines() if x.strip() and not x.startswith('#')][:100]
byurl={r.get('url'):r for r in d.get('offers',[])};fail=[];changes=[]
headers={'User-Agent':'MajinStorePriceMonitor/1.0 (public pages; low frequency)'}
for url in urls:
    if not re.match(r'^https://ggmax\.com\.br/anuncio/[a-zA-Z0-9_-]+$',url):
        fail.append({'url':url,'error':'URL inválida ou domínio não permitido'});continue
    try:
        response=requests.get(url,headers=headers,timeout=18,allow_redirects=False)
        if response.status_code!=200:raise ValueError('HTTP '+str(response.status_code)+' (acesso automatizado pode diferir do Safari; não significa necessariamente anúncio removido)')
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.select_one('h1')
        price=soup.select_one('.price__container h3')
        if not title or not price:raise ValueError('HTML sem título/preço verificáveis; possível bloqueio ou mudança de layout')
        raw=price.get_text(' ',strip=True);m=re.search(r'R\$\s*([\d.,]+)',raw)
        if not m:raise ValueError('Preço principal não reconhecido')
        val=float(m.group(1).replace('.','').replace(',','.'))
        old=byurl.get(url,{})
        if old.get('price') is not None and old['price']!=val:
            changes.append({'url':url,'title':title.get_text(' ',strip=True),'before':old['price'],'after':val})
        byurl[url]={**old,'url':url,'title':title.get_text(' ',strip=True),'price':val,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'price_scope':'Preço principal do anúncio; variante NÃO confirmada'}
    except Exception as e:fail.append({'url':url,'error':str(e)[:150]})
    time.sleep(2)
d['offers']=list(byurl.values());d['last_attempt_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();
if len(fail)<len(urls):d['updated_at']=d['last_attempt_at'];d['failures']=fail[-100:];d['monitor_status']={'attempted':len(urls),'success':len(urls)-len(fail),'failed':len(fail),'automatic_collection_ok':len(fail)<len(urls)};f.write_text(json.dumps(d,ensure_ascii=False,indent=2))
# Only report verified listing-level changes, never label them as variant alerts.
msg='MajinStore: '+str(len(changes))+' alteração(ões) de preço principal e '+str(len(fail))+' falha(s). Confira o painel.'
token=os.getenv('TELEGRAM_BOT_TOKEN');chat=os.getenv('TELEGRAM_CHAT_ID')
if token and chat and (changes or fail):
    try:requests.post('https://api.telegram.org/bot'+token+'/sendMessage',json={'chat_id':chat,'text':msg},timeout=12).raise_for_status()
    except Exception as e:print('Falha no alerta Telegram:',e)
print(msg)
