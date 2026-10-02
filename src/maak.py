# Bouwt alles opnieuw. Gebruik (vanuit de repo-root):
#   python src/maak.py          alleen de pagina's: docs/data/ -> docs/*.html  (geen bronbestanden nodig)
#   python src/maak.py alles    volledige pijplijn uit de bronbestanden -> docs/data/ -> docs/*.html
#   python src/maak.py raad     alleen raad uit de bronnen (idem: commissies)
# Tussenbestanden komen in de werkmap (paden.WERK, niet in git).
import os,sys,shutil,subprocess,glob
from paden import SRC,DOCS,WERK
ENV=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf8')
RAAD=f'{DOCS}/data/raad'; COMM=f'{DOCS}/data/commissies'   # jaardata, door de pagina's opgehaald
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
    run('bron.py'); run('emit_comm.py'); run('insights.py',RZ_OUT='outc')
    kopieer(f'{WERK}/outc',COMM,['*.zst','meta.json'])
def site():
    run('assemble.py',f'{DOCS}/raadzoeker.html',RZ_OUT=RAAD)
    run('assemble.py',f'{DOCS}/commissiezoeker.html',RZ_OUT=COMM)
if __name__=='__main__':
    os.makedirs(WERK,exist_ok=True)
    wat=sys.argv[1] if len(sys.argv)>1 else 'site'
    if wat in('alles','raad'): raad()
    if wat in('alles','commissies'): commissies()
    site()
