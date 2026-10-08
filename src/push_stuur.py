# Pushmeldingen laten versturen na een bijwerkronde: stuurt volg.json plus de VAPID-privésleutel (alleen op deze machine,
# WERK/geheim/vapid.json) naar https://raadzoeker.nl/api/push. De server bewaart de sleutel niet.
#   python src/push_stuur.py
import json,os,urllib.request
from paden import DOCS,WERK
def main():
    p=os.path.join(WERK,'geheim','vapid.json')
    if not os.path.exists(p): print('geen vapid.json; overgeslagen'); return
    body=json.dumps({'vapid':json.load(open(p,encoding='utf8'))['jwk'],'volg':json.load(open(os.path.join(DOCS,'volg.json'),encoding='utf8'))}).encode()
    r=urllib.request.Request('https://raadzoeker.nl/api/push',data=body,method='POST',headers={'content-type':'application/json','User-Agent':'raadzoeker-nas'})
    print(urllib.request.urlopen(r,timeout=120).read().decode())
if __name__=='__main__': main()
