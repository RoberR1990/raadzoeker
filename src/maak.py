# Bouwt alles opnieuw. Gebruik (vanuit de repo-root):
#   python src/maak.py          alleen de site: data/ -> docs/*.html  (geen bronbestanden nodig)
#   python src/maak.py alles    volledige pijplijn uit de bronbestanden -> data/ -> docs/
#   python src/maak.py raad     alleen raad uit de bronnen (idem: commissies)
# Tussenbestanden komen in build/ (niet in git).
import os,sys,shutil,subprocess,glob
from paden import SRC,DATA,DOCS,WERK
ENV=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf8')
RAAD=f'{DATA}/raad'; COMM=f'{DATA}/commissies'
CRANGES=[('2022-2023','2022,2023'),('2024-2025','2024,2025'),('2026','2026')]
def run(script,*args,**env):
    print('>>',script,*args,flush=True)
    subprocess.run([sys.executable,f'{SRC}/{script}',*args],cwd=WERK,env=dict(ENV,**env),check=True)
def kopieer(van,naar,patronen):
    os.makedirs(naar,exist_ok=True)
    for p in patronen:
        for f in glob.glob(f'{van}/{p}'): shutil.copy(f,naar)
def raad():
    run('bron.py'); run('extract.py'); run('agenda.py'); run('parse.py'); run('emit.py'); run('insights.py')
    kopieer(f'{WERK}/out',RAAD,['*.zst','meta.json'])
def commissies():
    run('bron.py'); run('emit_comm.py')
    kopieer(f'{WERK}/outc',COMM,['*.zst','meta.json'])
    for naam,jaren in CRANGES:
        run('insights.py',RZ_OUT='outc',RZ_YEARS=jaren,RZ_META=f'outc/meta_{naam}.json')
        kopieer(f'{WERK}/outc',COMM,[f'meta_{naam}.json'])
def site():
    run('assemble.py',f'{DOCS}/raadzoeker.html',RZ_OUT=RAAD)
    for naam,jaren in CRANGES:
        run('assemble.py',f'{DOCS}/commissiezoeker-{naam}.html',jaren,RZ_OUT=COMM,RZ_META=f'{COMM}/meta_{naam}.json')
if __name__=='__main__':
    os.makedirs(WERK,exist_ok=True)
    wat=sys.argv[1] if len(sys.argv)>1 else 'site'
    if wat in('alles','raad'): raad()
    if wat in('alles','commissies'): commissies()
    site()
