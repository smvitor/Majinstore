"""Auditoria de páginas GGMAX salvas no Safari; não inventa variantes."""
import json,re,sys,pathlib,datetime
from bs4 import BeautifulSoup
root=pathlib.Path(__file__).parent
f=root/'data/offers.json';data=json.loads(f.read_text());reports=[]
for name in sys.argv[1:]:
 p=pathlib.Path(name);s=BeautifulSoup(p.read_text(encoding='utf-8',errors='replace'),'html.parser')
 desc=s.get_text(' ',strip=True);title=s.title.get_text(' ',strip=True) if s.title else p.name
 blocked=bool(re.search(r'n[aã]o\s+(?:fornecemos|vendemos|permitimos).{0,45}revenda|proibid[ao].{0,20}revenda',desc,re.I))
 manual=bool(re.search(r'entrega.{0,20}manual',desc,re.I))
 reports.append({'file':p.name,'title':title,'resale_warning':'Não permite revenda' if blocked else 'Não verificado','delivery':'Manual' if manual else 'Não verificado','variant_prices':'Não extraídos: exigem associação inequívoca a cada item'})
(root/'data/html_audit.json').write_text(json.dumps({'audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reports':reports},ensure_ascii=False,indent=2))
print(json.dumps(reports,ensure_ascii=False,indent=2))
