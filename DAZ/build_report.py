from pathlib import Path
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'pdf'; OUT.mkdir(parents=True,exist_ok=True)
d=pd.read_csv(ROOT/'kandidatka_ltm.csv',sep=';',encoding='utf-8-sig')
d=d.map(lambda x:x.replace('\u200b','').strip() if isinstance(x,str) else x)
listcol,agecol=d.columns[1],d.columns[4]
d[agecol]=pd.to_numeric(d[agecol],errors='raise')
labels=['ODS','Boží Litoměřice - KDU-ČSL','ANO 2011','SEN pro Litoměřice','Naše Litoměřice 2026','STAN a Sport a zdraví','SPD / Stačilo! / PRO','TEAM','DSZ a nezávislí']
names=d[listcol].drop_duplicates().tolist()
print('LISTINY',names)
# Labels are keyed by the source list number, never by alphabetical order.
short={}
for name in names:
    if name.startswith('Občansk'): s='ODS'
    elif name.startswith('Boží'): s='Boží Litoměřice - KDU-ČSL'
    elif name.startswith('STAROST'): s='STAN a Sport a zdraví'
    elif name.startswith('SPD'): s='SPD / Stačilo! / PRO'
    elif name.startswith('DSZ'): s='DSZ a nezávislí'
    else:s=name
    short[name]=s
d['Listina']=d[listcol].map(short)
g=d.groupby('Listina')[agecol].agg(['count','mean','median','min','max']).sort_values('mean')
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialB','C:/Windows/Fonts/arialbd.ttf'))
W,H=595.28,841.89
c=canvas.Canvas(str(OUT/'statistika_kandidatky_litomerice.pdf'),pagesize=(W,H))
c.setTitle('Kandidátky Litoměřice - strany a věk')
ink=HexColor('#17324D'); blue=HexColor('#267C9F'); gray=HexColor('#667482')
def text(x,y,t,size=10,bold=False,color=ink):
    c.setFillColor(color);c.setFont('ArialB' if bold else 'Arial',size);c.drawString(x,y,str(t))
def para(t,y,size=10):
    for line in simpleSplit(t,'Arial',size,505): text(45,y,line,size);y-=15
    return y-8
def start(num,title,subtitle):
    text(45,795,'LITOMĚŘICE / ANALÝZA KANDIDÁTEK',10,True,blue)
    text(45,760,title,23,True);para(subtitle,735,10)
    text(45,28,'Zdroj: kandidatka_ltm.csv • zpracováno 9. 10. 2026',8,color=gray)
    text(525,28,str(num),9)
def bars(title,items,y,maxval=None,suffix='',dec=0):
    text(45,y,title,14,True);y-=32
    maxval=maxval or max(v for _,v in items)
    for label,v in items:
        text(45,y,label,9)
        c.setFillColor(blue);c.rect(240,y-3,230*v/maxval,12,fill=1,stroke=0)
        text(480,y,f'{v:.{dec}f}'.replace('.',',')+suffix,9,True)
        y-=28
    return y
def table(headers,rows,y,widths):
    x=45;c.setFillColor(ink);c.rect(45,y-7,sum(widths),23,fill=1,stroke=0)
    for h,w in zip(headers,widths):text(x+5,y,h,9,True,white);x+=w
    y-=27
    for i,row in enumerate(rows):
        if i%2==0:c.setFillColor(HexColor('#EDF3F6'));c.rect(45,y-7,sum(widths),24,fill=1,stroke=0)
        x=45
        for v,w in zip(row,widths):text(x+5,y,v,9);x+=w
        y-=24
    return y
def cz(v):return f'{v:.1f}'.replace('.',',')
N=len(d);a=d[agecol]
start(1,'Strany a věk kandidátů','Popisná statistika 218 kandidátů na 9 kandidátních listinách. Údaje popisují kandidáty, nikoli voliče nebo výsledky voleb.')
for x,value,label in [(45,str(N),'kandidátů'),(215,cz(a.mean()),'průměrný věk'),(385,cz(a.median()),'medián věku')]:
    text(x,665,value,30,True,blue);text(x,641,label,11)
y=para(f'Věk kandidátů sahá od {a.min()} do {a.max()} let. Prostředních 50 % kandidátů je mezi {cz(a.quantile(.25))} a {cz(a.quantile(.75))} lety; směrodatná odchylka je {cz(a.std())} roku.',598)
y=bars('Průměrný věk podle kandidátní listiny',[(n,r['mean']) for n,r in g.iterrows()],y-10,maxval=70,suffix=' let',dec=1)
y=para(f'Nejnižší průměr má {g.index[0]} ({cz(g.iloc[0]["mean"])} roku), nejvyšší {g.index[-1]} ({cz(g.iloc[-1]["mean"])} roku). Rozdíl je {cz(g.iloc[-1]["mean"]-g.iloc[0]["mean"])} roku.',y-15)
para('Osm listin má 27 kandidátů. DSZ a nezávislí mají pouze 2 kandidáty, proto jejich věkový průměr vychází z výrazně menšího souboru.',y)
c.showPage()
start(2,'Věkové složení','Porovnání průměru, mediánu a věkového rozpětí. N = počet kandidátů.')
rows=[[n,int(r['count']),cz(r['mean']),cz(r['median']),int(r['min']),int(r['max'])] for n,r in g.iterrows()]
y=table(['Listina','N','Průměr','Medián','Min.','Max.'],rows,675,[220,35,65,65,55,65])
groups=pd.cut(a,[0,29,39,49,59,69,200],labels=['Do 29 let','30-39 let','40-49 let','50-59 let','60-69 let','70 let a více']).value_counts(sort=False)
y=bars('Věkové skupiny v celém souboru',list(groups.items()),y-35)
para(f'Kandidátů mladších 40 let je {(a<40).sum()} ({cz(100*(a<40).mean())} %). Kandidátů ve věku 60 a více let je {(a>=60).sum()} ({cz(100*(a>=60).mean())} %).',y-15)
c.showPage()
start(3,'Věk uvnitř jednotlivých listin','Podíly věkových skupin v %. Každý řádek tvoří 100 % kandidátů dané listiny.')
colors=[HexColor(x) for x in ['#45A8B3','#8CC8BE','#D5E7C4','#F2CE79','#E89966','#AF6467']]
y=675
for i,(lab,col) in enumerate(zip(groups.index,colors)):
    x=45+(i%3)*170; yy=y-(i//3)*24
    c.setFillColor(col);c.rect(x,yy,10,10,fill=1,stroke=0);text(x+16,yy,lab,9)
y=580
for n in g.index:
    vals=d.loc[d.Listina==n,agecol]; counts=pd.cut(vals,[0,29,39,49,59,69,200],labels=groups.index).value_counts(sort=False)
    text(45,y+18,f'{n} (N={len(vals)})',10,True);x=45
    for count,col in zip(counts,colors):
        width=505*count/len(vals)
        c.setFillColor(col);c.rect(x,y-5,width,17,fill=1,stroke=0)
        if width>28:text(x+4,y,f'{100*count/len(vals):.0f} %',8,color=ink)
        x+=width
    y-=49
para('Procenta v grafu jsou zaokrouhlena na celá čísla; velmi malé segmenty nemají číselný popisek. Přesné podíly kandidátů pod 40 a od 60 let jsou na následující straně.',y-8)
rows=[]
for n in g.index:
    vals=d.loc[d.Listina==n,agecol]
    rows.append([n,f'{(vals<40).sum()} / {cz(100*(vals<40).mean())} %',f'{(vals>=60).sum()} / {cz(100*(vals>=60).mean())} %'])
# Detail is kept on next page to preserve readable chart labels.
c.showPage()
start(4,'Další zjištění','Politická příslušnost a bydliště doplňují srovnání kandidátních listin.')
y=table(['Listina','Pod 40 let: N / %','60+ let: N / %'],rows,675,[245,130,130])
pp=d['Politická příslušnost'].value_counts()
y=para(f'Bez politické příslušnosti (BEZPP) je {pp.get("BEZPP",0)} kandidátů ({cz(100*pp.get("BEZPP",0)/N)} %). Členství ve straně proto nelze zaměňovat za název kandidátní listiny.',y-25)
y=bars('Bydliště kandidátů',list(d['Bydliště'].value_counts().items()),y-10)
para('Počty politických příslušností: '+', '.join(f'{k}: {v}' for k,v in pp.items())+'.',y-15)
c.showPage()
start(5,'Metodika a úplné názvy','Jak číst výsledky a co lze ze souboru spolehlivě odvodit.')
y=675
for t in [
    'Jednotka analýzy: jeden řádek CSV = jeden kandidát. Počet řádků je 218. Ve všech 9 sloupcích je 0 chybějících hodnot; počet zcela duplicitních řádků je 0.',
    'Soubor je načten v UTF-8 a oddělen středníky. Z textových hodnot jsou odstraněny neviditelné znaky U+200B a krajní mezery. Věk je převzat přímo ze souboru, bez přepočtu k aktuálnímu datu.',
    'Průměr za celý soubor váží každého kandidáta stejně. Medián je prostřední hodnota seřazeného věku. Směrodatná odchylka je výběrová (ddof = 1); kvartily používají lineární interpolaci.',
    'Věkové skupiny jsou nepřekrývající se intervaly: do 29, 30-39, 40-49, 50-59, 60-69 a 70+ let. Podíly u listin používají jako jmenovatel počet kandidátů dané listiny.',
    'Jde o popis dodaného souboru. CSV neobsahuje hlasy, mandáty ani volební účast. Nelze z něj vyvozovat popularitu stran nebo věk jejich voličů. Pohlaví není uvedeno, proto není odhadováno ze jmen. Povolání jsou volný text a nejsou automaticky přiřazována k profesním kategoriím.'
]:y=para(t,y)
text(45,y-10,'Názvy listin v grafech a ve zdroji',13,True);y-=38
for n in names:
    text(45,y,short[n],10,True);y-=15
    for line in simpleSplit(n,'Arial',9,505):
        text(45,y,line,9);y-=12
    y-=10
c.save()
reader=PdfReader(OUT/'statistika_kandidatky_litomerice.pdf')
assert len(reader.pages)==5
assert sum(g['count'])==N
assert groups.sum()==N
assert d.isna().sum().sum()==0
print('PDF',OUT/'statistika_kandidatky_litomerice.pdf','pages',len(reader.pages))
print('MEAN',a.mean(),'MEDIAN',a.median(),'AGE_GROUPS',groups.to_dict())
