import json, textwrap
from pathlib import Path
import nbformat as nb
ROOT=Path(__file__).resolve().parent
base=json.loads((ROOT/'PYR_Data_cleaning_python.ipynb').read_text(encoding='utf-8'))
cells=[]
def md(s): cells.append(nb.v4.new_markdown_cell(textwrap.dedent(s).strip()))
def code(s): cells.append(nb.v4.new_code_cell(textwrap.dedent(s).strip()))
def original(i): code(''.join(base['cells'][i]['source']))
md('''# Cvičení 15. 10. 2026 — čištění dat a kvalita anotací
Řešení vychází z `PYR_Data_cleaning_python.ipynb`. Každý oddíl obsahuje postup, spustitelný kód a výsledky. Meteorologická data a anotace zůstávají oddělené. Původní soubory neměníme; pracovní kopie a exporty ukládáme do `vystup`. Neprovádíme imputaci ani detekci odlehlých hodnot.

Notebook spouštějte od začátku v adresáři `15_10_2026`. Závislosti: Python, pandas, numpy, matplotlib, scikit-learn a IPython. Soubor `requirements.txt` uvádí jejich seznam.''')
original(1)
code('''import hashlib
otisky = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.csv')}
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_colwidth', 100)
''')
md('''## 1. Načtení, kontrola schématu a pracovní kopie
Povinné vstupní sloupce jsou identifikátor, čas, teplota a jednotka. Bez nich nelze vytvořit klíč ani teplotu v °C. Stav, vlhkost a čas aktualizace jsou nepovinné: jejich absence je přípustná, ale omezuje provozní výběr nebo určení nejnovější verze. Chybějící vlhkost nijak nedoplňujeme. Řádek zdroje je číslován od 2 včetně hlavičky.

Experiment odstraní vlhkost pouze z pracovní kopie února. Ukazuje běžné spojení i okamžité odmítnutí souboru bez povinného sloupce. Hlavní analýza pak využívá úplné originály.''')
code('''prejmenovani = {
    'station': 'stanice_id', 'timestamp': 'datum', 'temperature': 'teplota',
    'unit': 'jednotka', 'status': 'stav', 'humidity': 'vlhkost', 'updated': 'aktualizovano'
}
povinne_vstup = ['stanice_id', 'datum', 'teplota', 'jednotka']
nepovinne_vstup = ['stav', 'vlhkost', 'aktualizovano']
def nacti_mesic(cesta, mapa):
    tab = pd.read_csv(cesta, sep=';', dtype='string').rename(columns=mapa)
    chybi = set(povinne_vstup) - set(tab.columns)
    if chybi:
        raise ValueError(f'{Path(cesta).name}: chybí povinné sloupce {sorted(chybi)}')
    for col in nepovinne_vstup:
        if col not in tab:
            tab[col] = pd.Series(pd.NA, index=tab.index, dtype='string')
    return tab.assign(zdroj=Path(cesta).name, radek_zdroje=np.arange(2, len(tab)+2))
pracovni = VYSTUP / 'pracovni_kopie'
pracovni.mkdir(exist_ok=True)
u = pd.read_csv(DATA/'mereni_unor.csv', sep=';', dtype='string')
u.drop(columns='humidity').to_csv(pracovni/'unor_bez_vlhkosti.csv', sep=';', index=False)
experiment = pd.concat([nacti_mesic(DATA/'mereni_leden.csv', {}),
                        nacti_mesic(pracovni/'unor_bez_vlhkosti.csv', prejmenovani)], ignore_index=True)
display(experiment.groupby('zdroj').agg(radku=('datum','size'), zname_vlhkosti=('vlhkost','count')))
u.drop(columns='temperature').to_csv(pracovni/'unor_bez_teploty.csv', sep=';', index=False)
try:
    nacti_mesic(pracovni/'unor_bez_teploty.csv', prejmenovani)
except ValueError as e:
    print('Očekávané přerušení načítání:', e)
else:
    raise AssertionError('Kontrola povinných sloupců nefunguje')
cesty = sorted(DATA.glob('mereni_*.csv'))
assert len(cesty) == 2
raw = pd.concat([nacti_mesic(p, prejmenovani) for p in cesty], ignore_index=True)
raw['vstup_id'] = np.arange(len(raw))
df = raw.copy(deep=True)
display(raw.groupby('zdroj').size().to_frame('pocet_radku'))
''')
md('''## 2. Normalizace, převody a pravidla vyřazení
Identifikátor musí odpovídat celému řetězci `S[0-9]{2,3}`. Bílé znaky a velikost písmen sjednocujeme před validací. Číselné a časové chyby převádíme na chybějící hodnotu a evidujeme je. Fahrenheit převádíme přesně vztahem `(F − 32) × 5/9`; neznámá jednotka znamená neznámou teplotu v °C.

Pro zachování řádku požadujeme platný identifikátor, datum a teplotu v °C. Neznámý stav ponecháme, avšak nezařadíme jej mezi provozní měření.''')
original(14)
code('''priklady_id = pd.Series(['S01','S99','S100','S001','S1','S1000','s01','XS01','S01x','S１２'])
test_id = pd.DataFrame({'id': priklady_id, 'platne': priklady_id.str.fullmatch(r'S[0-9]{2,3}', na=False)})
assert test_id.platne.tolist() == [True]*4 + [False]*6
display(test_id)
format_id_ok = df.stanice_id.str.fullmatch(r'S[0-9]{2,3}', na=False)
display(df.loc[~format_id_ok])
''')
original(21)
code('''# Obě masky nad naprosto stejnou tabulkou po převodech, před jakýmkoli mazáním.
povinne = ['stanice_id','datum','teplota_C']
navic_odstranene = df.loc[df.isna().any(axis=1) & df[povinne].notna().all(axis=1)].copy()
navic_odstranene['chybejici_nepovinne'] = navic_odstranene.apply(
    lambda r: ', '.join(c for c in df.columns if c not in povinne and pd.isna(r[c])), axis=1)
display(nav ic_odstranene if False else navic_odstranene)
'''.replace('nav ic_odstranene if False else ',''))
code('''duvody = pd.Series('', index=df.index, dtype='string')
for col in povinne:
    mask = df[col].isna()
    duvody.loc[mask] += f'chybí/neplatné {col}; '
duvody.loc[~format_id_ok] += 'neplatný formát stanice_id; '
vyrazeno_na = df.loc[duvody.ne('')].copy()
vyrazeno_na['duvod'] = duvody.loc[duvody.ne('')]
df = df.loc[duvody.eq('')].copy()
display(vyrazeno_na)
''')
md('''## 3. Duplicity a nejnovější oprava
`keep="first"` závisí na pořadí. Po vzestupném seřazení vybere nejstarší aktualizaci; pro nejnovější verzi proto třídíme sestupně. Chybějící aktualizace řadíme nakonec, při shodném čase ponecháme první vstupní řádek. Následující srovnání zobrazuje všechny konfliktní klíče včetně opraveného měření.''')
code('''klic = ['stanice_id','datum']
konflikt = df.loc[df.duplicated(klic, keep=False)].copy()
varianty = []
for varianta, tab in {
    'původní pořadí': df,
    'čas vzestupně + first': df.sort_values('aktualizovano', kind='stable', na_position='last'),
    'čas sestupně + first (volíme)': df.sort_values('aktualizovano', ascending=False, kind='stable', na_position='last')
}.items():
    vyber = tab.drop_duplicates(klic, keep='first')
    varianty.append(vyber.merge(konflikt[klic].drop_duplicates(), on=klic).assign(varianta=varianta))
display(pd.concat(varianty)[klic+['teplota_C','aktualizovano','vstup_id','varianta']])
serazeno = df.sort_values('aktualizovano', ascending=False, kind='stable', na_position='last')
stare_verze = serazeno.loc[serazeno.duplicated(klic, keep='first')].copy()
stare_verze['duvod'] = 'duplicitní klíč: ponechána nejnovější dostupná aktualizace, při shodě první vstup'
df = serazeno.drop_duplicates(klic, keep='first').copy()
assert not df.duplicated(klic).any()
''')
md('''## 4. Spojování a kontrola číselníku
`many_to_one` zabraňuje násobení měření duplicitním číselníkem. Left zachová měření, inner jen spárovaná měření a outer také stanice bez měření. Nespárované identifikátory exportujeme odděleně. Stanici S777 přidáváme výhradně do pracovní kopie číselníku.''')
original(27)
code('''stanice_test = pd.concat([stanice, pd.DataFrame([{'stanice_id':'S777','nazev':'Testovací stanice bez měření','oblast':'Test'}])], ignore_index=True)
spojeni = {}
for jak in ['left','inner','outer']:
    tab = df.merge(stanice_test, on='stanice_id', how=jak, validate='many_to_one', indicator=True)
    spojeni[jak] = tab
    print(jak, 'řádků:', len(tab), 'ID:', sorted(tab.stanice_id.dropna().unique()))
display(pd.DataFrame({j:t['_merge'].value_counts() for j,t in spojeni.items()}).fillna(0))
bez_mereni = spojeni['outer'].loc[spojeni['outer']['_merge'].eq('right_only'), ['stanice_id','nazev']]
display(bez_mereni)
nesparovana_id = nesparovane[['stanice_id']].drop_duplicates().sort_values('stanice_id')
nesparovana_id.to_csv(VYSTUP/'nesparovane_stanice.csv', index=False)
display(nesparovana_id)
''')
md('''## 5. Denní a měsíční statistiky
Podíl `ok` má ve jmenovateli všechny vyčištěné záznamy známých stanic, tedy také poruchy, údržbu a neznámé stavy. Denní počty nejprve vypočteme pro všechny známé stanice, zatímco průměry teplot počítáme jen z provozních měření.

Přímý měsíční průměr váží každý den počtem provozních měření. Průměr denních průměrů dává každému dni stejnou váhu. Při nestejném počtu měření se výsledky mohou lišit; dny bez provozního měření se do průměru denních průměrů nezapočtou.''')
original(29)
code('''podily = mereni.assign(je_ok=mereni.stav.eq('ok').fillna(False)).groupby(['stanice_id','mesic']).agg(
    vsechny=('stav','size'), pocet_ok=('je_ok','sum'), podil_ok=('je_ok','mean'))
denni = mereni.groupby(['stanice_id','den']).agg(pocet_teplot=('teplota_C','count'), pocet_vlhkosti=('vlhkost','count'))
provozni['denni_prumer'] = provozni.groupby(['stanice_id','den']).teplota_C.transform('mean')
denni_provoz = provozni.groupby(['stanice_id','mesic','den'], as_index=False).agg(prumer=('teplota_C','mean'), n=('teplota_C','size'))
mesic_denni = denni_provoz.groupby(['stanice_id','mesic']).agg(prumer_dnu=('prumer','mean'), min_n=('n','min'), max_n=('n','max'))
porovnani = prehled.set_index(['stanice_id','mesic'])[['prumer_teploty']].join(mesic_denni)
porovnani['rozdil'] = porovnani.prumer_teploty - porovnani.prumer_dnu
siroka_teplota = prehled.pivot(index='stanice_id', columns='mesic', values='prumer_teploty')
display(podily, denni, provozni[klic+['teplota_C','denni_prumer']].head(12), porovnani, siroka_teplota)
# Kontrolovaný příklad: dva dny s 1 a 3 měřeními.
ukazka = pd.DataFrame({'den':[1,2,2,2], 'teplota':[0.,10.,10.,10.]})
print('Příklad: přímý průměr', ukazka.teplota.mean(), 'průměr dnů', ukazka.groupby('den').teplota.mean().mean())
ax = siroka_teplota.plot.bar(ylabel='Průměrná teplota [°C]', title='Provozní teploty známých stanic')
plt.xticks(rotation=0); plt.tight_layout(); plt.show()
''')
md('''## 6. Audit meteorologických úprav
Audit změn je veden po vstupním řádku a sloupci, vždy s původní i výslednou hodnotou. Vyřazení chyb, duplicit a oddělení neznámých stanic mají vlastní soubory. Typový převod bez změny textového zápisu není samostatná věcná oprava; vytvoření teploty v °C evidujeme jako odvození.''')
code('''# Srovnáme i vyřazené řádky: převedená tabulka vznikne z raw stejným postupem.
# Předchozí tabulky stále obsahují všechny vstup_id v součtu těchto tří skupin.
prevedene = pd.concat([df, stare_verze, vyrazeno_na], ignore_index=True).set_index('vstup_id')
zmeny=[]
for r in raw.itertuples(index=False):
    po = prevedene.loc[r.vstup_id]
    for col in ['stanice_id','jednotka','stav','teplota','vlhkost','datum','aktualizovano']:
        a,b=getattr(r,col),po[col]
        if (pd.isna(a) and pd.isna(b)) or (not pd.isna(a) and not pd.isna(b) and str(a)==str(b)):
            continue
        zmeny.append({'vstup_id':r.vstup_id,'zdroj':r.zdroj,'radek_zdroje':r.radek_zdroje,
                       'sloupec':col,'pred':a,'po':b,'duvod':'normalizace / typový převod; neplatné na NA'})
    zmeny.append({'vstup_id':r.vstup_id,'zdroj':r.zdroj,'radek_zdroje':r.radek_zdroje,
                   'sloupec':'teplota_C','pred':r.teplota,'po':po.teplota_C,'duvod':f'převod z jednotky {r.jednotka} na °C'})
audit_zmen = pd.DataFrame(zmeny)
assert len(raw) == len(vyrazeno_na)+len(stare_verze)+len(df)
audit = pd.DataFrame({'krok':['vstup','neplatné/chybějící povinné','duplicitní klíče','neznámé stanice','známé stanice','provozní'],
                      'pocet':[len(raw),len(vyrazeno_na),len(stare_verze),len(nesparovane),len(mereni),len(provozni)]})
display(audit, audit_zmen.head(15))
for name,tab in {'audit':audit,'audit_zmen':audit_zmen,'chyby_prevodu':chyby_prevodu,'vyrazene_chybejici':vyrazeno_na,
                 'stare_verze':stare_verze,'nesparovane':nesparovane,'mereni_cista':mereni,'prehled_mesicni':prehled,
                 'denni_souhrn':denni.reset_index(),'podily_ok':podily.reset_index(),'porovnani_prumeru':porovnani.reset_index()}.items():
    tab.to_csv(VYSTUP/f'{name}.csv', index=False)
siroka_teplota.to_csv(VYSTUP/'skutecne_teploty_siroka.csv')
''')
md('''## 7. Názvy: podobnost, nejednoznačnost a ověření prahů
Používáme normalizaci diakritiky, velikosti a mezer a Levenshteinovo skóre `100 × (1 − vzdálenost / maximální délka)`. Jedna chyba více poškodí krátký název. Přesná shoda je přijatelná jen při jedinečném normalizovaném názvu. Ostatní návrhy nad prahem skóre i odstupu zařazujeme k ruční kontrole, zbývající nemají dostatečnou shodu. Ani silný návrh automaticky nepřepisuje zdrojový název.''')
original(8)
code('''kratke_dlouhe = pd.DataFrame([{'puvodni':a,'chyba':b,'skore':podobnost(normalizuj_nazev(a),normalizuj_nazev(b))}
                            for a,b in [('Most','Mast'),('Meteorologická stanice centrum','Meteorologická stanice centrvm')]])
kratke_dlouhe['nad_85'] = kratke_dlouhe.skore.ge(85)
display(kratke_dlouhe)
def kandidati(text, ref):
    poradi = sorted([(podobnost(normalizuj_nazev(text), normalizuj_nazev(r.nazev)),r.stanice_id,r.nazev)
                     for r in ref.itertuples()], key=lambda x:(-x[0],x[1]))
    a,b = poradi[:2]
    n_exact = sum(normalizuj_nazev(text)==normalizuj_nazev(r) for r in ref.nazev)
    return {'navrh_id':a[1], 'navrh_nazvu':a[2], 'skore':a[0], 'druhy_kandidat':b[2],
            'druhe_skore':b[0], 'odstup':a[0]-b[0], 'jedina_presna':n_exact==1 and a[0]==100}
rozsirena = pd.concat([reference_nazvu,pd.DataFrame([{'stanice_id':'S888','nazev':'Teplice centurm'}])],ignore_index=True)
display(pd.DataFrame([kandidati('Teplice centurm', reference_nazvu),kandidati('Teplice centurm',rozsirena)],index=['před','po přidání podobného názvu']))
''')
md('''### Kalibrační a oddělené testovací dvojice
Očekávané cíle níže stanovujeme ručně ze syntetických názvů, nikoli podle skóre. Neexistující stanice mají cíl `None`. Kalibrační a testovací texty jsou odlišné, ale používají tentýž malý číselník; konečná kvalita proto neprokazuje přenositelnost na jiné regiony. Falešné spojení je přijatý návrh s nesprávným ID. Nenalezená shoda je skutečná shoda, pro kterou správné ID nebylo přijato (zahrnuje i chybný návrh). Pro vyhodnocení je návrh považován za přijatý do fronty kontroly, nikoliv automaticky aplikovaný.''')
code('''kalibrace = [('Ústí centrum','S01'),('Decin centrum','S02'),('Teplice centurm','S03'),('Usti sevr','S04'),
              ('Brno centrum',None),('Praha',None),('Děčín sever',None),('Most',None)]
test = [(' ÚSTÍ centrum ','S01'),('Děčín centrm','S02'),('Teplice cetrum','S03'),('Usti sever','S04'),
        ('Brno centrm',None),('Ostrava',None),('Teplice sever',None),('Ústí jih',None)]
assert not set(a for a,b in kalibrace) & set(a for a,b in test)
def vyhodnot_dvojice(dvojice, prah, odstup):
    rows=[]
    for text,cil in dvojice:
        r=kandidati(text,reference_nazvu)
        prijato=r['jedina_presna'] or (r['skore']>=prah and r['odstup']>=odstup)
        rows.append({'text':text,'cil':cil,**r,'prijato':prijato,
                     'falesne_spojeni':prijato and r['navrh_id']!=cil,
                     'nenalezena_shoda':cil is not None and not(prijato and r['navrh_id']==cil)})
    return pd.DataFrame(rows)
ladeni=[]
for p in [65,75,85,90,95]:
    for o in [0,10,15,25]:
        t=vyhodnot_dvojice(kalibrace,p,o)
        fp,fn=int(t.falesne_spojeni.sum()),int(t.nenalezena_shoda.sum())
        ladeni.append({'prah':p,'odstup':o,'FP':fp,'FN':fn,'ztrata':2*fp+fn})
ladeni=pd.DataFrame(ladeni).sort_values(['ztrata','FP','prah','odstup'])
volba=ladeni.iloc[0]; prah=float(volba.prah); odstup=float(volba.odstup)
print('Volba pouze na kalibraci, falešné spojení má dvojnásobnou cenu:',prah,odstup)
display(ladeni)
# Více prahů na testu ukazujeme jen pro srovnání; volbu už neměníme.
srovnani_test=[]
for p in [65,75,85,90,95]:
    t=vyhodnot_dvojice(test,p,odstup)
    srovnani_test.append({'prah':p,'odstup':odstup,'FP':t.falesne_spojeni.sum(),'FN':t.nenalezena_shoda.sum()})
display(pd.DataFrame(srovnani_test),vyhodnot_dvojice(test,prah,odstup))
navrhy=pd.concat([nazvy,nazvy.nazev_zdroj.apply(lambda x:kandidati(x,reference_nazvu)).apply(pd.Series)],axis=1)
navrhy['skupina']=np.select([navrhy.jedina_presna,navrhy.skore.ge(prah)&navrhy.odstup.ge(odstup)],
                            ['přesná shoda po normalizaci','k ruční kontrole'],default='bez dostatečné shody')
display(navrhy)
navrhy.to_csv(VYSTUP/'navrhy_nazvu.csv',index=False)
''')
md('''**Blocking pro velký číselník:** omezit kandidáty na stejný ověřený region, případně sousední regiony; uvnitř použít prefix nebo znakové trigramy. Při neznámém regionu použít širší záložní hledání. Region nesmí být odvozen z již chybně spárovaného názvu. Kontrolovat recall blockingu na ručně ověřených shodách: vyřazeného správného kandidáta již podobnost nezachrání. Dodaný číselník názvů region neobsahuje, proto zde regionální filtr neaplikujeme.''')
md('''## 8. Kvalita anotací a většinový label
Chybějící a nepovolené anotace evidujeme a vyloučíme z hlasování i párových statistik. Většinu přiznáme pouze při nejméně dvou platných hlasech a více než polovině platných hlasů pro jednu třídu. Jeden hlas, remíza a absence hlasů znamenají nejednoznačný výsledek. Žádný původní target tím nepřepisujeme.''')
original(38)
original(42)
code('''for a,b in [('A','B'),('A','C'),('B','C')]:
    par=anotace_siroka[[a,b]].dropna()
    print(f'Kontingenční tabulka {a}–{b}, n={len(par)}')
    display(pd.crosstab(par[a],par[b]).reindex(index=tridy,columns=tridy,fill_value=0))
# Každý anotátor má přesně 95 % A; jejich pět menšinových hlasů se nepřekrývá.
a=np.array(['A']*95+['B']*5)
b=np.array(['B']*5+['A']*95)
print('Podíly A:',(a=='A').mean(),(b=='A').mean())
print('Prostá shoda:',(a==b).mean(),'kappa:',cohen_kappa_score(a,b))
assert not anotace.duplicated(['zaznam_id','anotator']).any()
hlasy = platne_anotace.groupby(['zaznam_id','label']).size().unstack(fill_value=0).reindex(columns=tridy,fill_value=0)
hlasy=hlasy.reindex(objekty.zaznam_id,fill_value=0)
vetsina=hlasy.copy()
vetsina['platnych']=hlasy.sum(axis=1)
vetsina['jednoznacna']=(vetsina.platnych>=2)&(hlasy.max(axis=1)>vetsina.platnych/2)
vetsina['vetsinovy_label']=hlasy.idxmax(axis=1).where(vetsina.jednoznacna,pd.NA)
display(vetsina, vetsina.loc[~vetsina.jednoznacna])
vetsina.to_csv(VYSTUP/'vetsinove_labely.csv')
''')
md('''V umělém příkladu je 90% shoda, přesto záporná kappa: vysoká četnost A vede k očekávané náhodné shodě 90,5 %. Prostá shoda tedy může působit vysoká i bez užitečné shody nad úrovní náhody.''')
md('''## 9. Out-of-fold diagnostika a oddělená pořadí modelů
Stejně jako ve výchozím notebooku diagnostikujeme label anotátora A. Dvě modelové rodiny a tři opakování pětinásobné validace používají `StratifiedGroupKFold` podle objektu. Standardizace se učí pouze na trénovací části. Učitelská reference se dosud vůbec nenačítá. Skóre podezření je jedna minus medián OOF pravděpodobnosti pozorovaného labelu; nízká pravděpodobnost pouze doporučuje kontrolu.''')
original(44)
code('''# P má pořadí seed × model, proto pro model vybíráme každý druhý běh.
k=min(15,len(model_data))
poradi_modelu={}
for j,name in enumerate(modely):
    tab=model_data[['zaznam_id','objekt_id','label']].copy()
    tab['skore_k_provereni']=1-np.median(p_obs[j::len(modely)],axis=0)
    tab=tab.sort_values(['skore_k_provereni','zaznam_id'],ascending=[False,True])
    poradi_modelu[name]=tab
    print(name); display(tab.head(k))
    tab.to_csv(VYSTUP/f'poradi_{name}.csv',index=False)
poradi_modelu['spolecna']=diagnostika
prekryvy=[]
for x,yname in combinations(poradi_modelu,2):
    a=set(poradi_modelu[x].head(k).zaznam_id); b=set(poradi_modelu[yname].head(k).zaznam_id)
    prekryvy.append({'poradi_1':x,'poradi_2':yname,'k':k,'spolecnych':len(a&b),'podil_z_k':len(a&b)/k,'Jaccard':len(a&b)/len(a|b)})
display(pd.DataFrame(prekryvy))
model_ids=set(diagnostika.head(k).zaznam_id)
neshoda_ids=set(konfliktni_id)
prehled_metod=objekty[['zaznam_id','objekt_id']].copy()
prehled_metod['model']=prehled_metod.zaznam_id.isin(model_ids)
prehled_metod['neshoda']=prehled_metod.zaznam_id.isin(neshoda_ids)
prehled_metod['skupina']=np.select([prehled_metod.model & prehled_metod.neshoda,prehled_metod.model,prehled_metod.neshoda],
                                 ['oba postupy','jen model','jen neshoda'],default='ani jeden')
display(prehled_metod.skupina.value_counts())
for skupina in ['oba postupy','jen model','jen neshoda']:
    print(skupina)
    display(prehled_metod.loc[prehled_metod.skupina.eq(skupina)].merge(anotace_siroka,on='zaznam_id',how='left'))
prehled_metod.to_csv(VYSTUP/'porovnani_model_neshoda.csv',index=False)
ax=prehled_metod.skupina.value_counts().plot.bar(ylabel='Počet záznamů',title=f'Modelová fronta top {k} a neshoda anotátorů')
plt.xticks(rotation=15); plt.tight_layout(); plt.show()
''')
md('''## 10. Následné vyhodnocení syntetického experimentu
Teprve po sestavení a exportu pořadí otevřeme učitelskou referenci. `precision@k` vyjadřuje podíl skutečně změněných labelů A ve frontě, nikoli klasifikační přesnost. Výběr k ani modelů podle této reference zpětně neupravujeme. Fronta revizí ponechává nové labely prázdné a čeká na člověka.''')
original(46)
code('''vysledky=[]
for name,tab in poradi_modelu.items():
    ev=tab.merge(reference_labelu,on='zaznam_id',validate='one_to_one')
    ev['chyba']=ev.label.ne(ev.label_generatoru)
    vysledky.append({'model':name,'k':k,'nalezenych_chyb':ev.head(k).chyba.sum(),
                     'precision_at_k':ev.head(k).chyba.mean(),'recall_at_k':ev.head(k).chyba.sum()/ev.chyba.sum() if ev.chyba.sum() else np.nan})
display(pd.DataFrame(vysledky))
assert otisky == {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.csv')}
print('Ověřeno: všechna zdrojová CSV jsou beze změny.')
''')
md('''## 11. Návrh diagnostiky regresního targetu
1. Nejprve ověřit jednotky, rozsah významu targetu, časovou návaznost a klíč při spojení objektů. Záměna kg/g či °C/°F může vysvětlit nesoulad bez chyby modelu.
2. Vytvořit opakované OOF predikce alespoň lineárního a stromového modelu. Opakované objekty držet v jedné skupině; časová data dělit podle času. Transformace učit výhradně na trénovací části.
3. Pro každý záznam evidovat znaménkové reziduum `y − predikce`, absolutní reziduum a jeho medián i rozptyl napříč opakováními a modely. Zohlednit různou přirozenou nejistotu skupin; samotné velké reziduum nemusí znamenat chybu targetu.
4. Kandidáty k ruční kontrole prioritizovat podle stabilního nesouladu více modelů. Kontrolovat původní protokol, jednotky, desetinný oddělovač a záměnu objektů; porovnat opakovaná měření stejného objektu. Zároveň prověřit nedostatečné příznaky a systematické selhání modelů.
5. Změnu smí potvrdit člověk na základě zdrojových podkladů. Audit obsahuje původní target, navrženou hodnotu, důkaz, kontrolujícího a čas. Bez důkazu target zachovat. Teprve po uzavření kontroly znovu vyhodnotit na nezávislých datech.

Jde o návrh postupu; v tomto cvičení neprovádíme detekci odlehlých hodnot ani automatické přepisování targetů.''')
md('## 12. Interpretace dosažených výsledků\n\n- U stanice S02 dne 1. 1. 2026 v 08:00 vybere původní pořadí teplotu 6,9 °C; sestupné řazení aktualizace správně ponechá opravenou verzi 7,5 °C z 8. 1. 2026.\n- Rozdíl agregací je patrný například u S02 v únoru: přímý průměr je 6,0833 °C, průměr denních průměrů 6,3571 °C. Denní četnost kolísá mezi jedním a dvěma provozními měřeními. U skupin se dvěma měřeními každý den se oba postupy shodují.\n- Jedna substituce v názvu Most sníží skóre na 75 %, zatímco v dlouhém názvu na 96,67 %. Stejný práh 85 % tak rozhodne rozdílně. Přidaná téměř shodná reference sníží odstup pro „Teplice centurm“ z 33,33 na 13,33 bodu a změní nejlepšího kandidáta; samotné vysoké skóre nemůže zaručit věcnou správnost.\n- Pořadí logistické regrese a lesa sdílejí 10 z prvních 15 kandidátů. Společná diagnostika sdílí s regresí 13 a s lesem 12 kandidátů. Modelová fronta a neshoda anotátorů se překrývají v 8 případech; 7 zachytí jen model a 4 jen neshoda. Postupy se doplňují.\n- Následná učitelská reference potvrzuje v každé frontě 9 skutečně změněných labelů z 15: precision@15 = 60 % a recall@15 = 100 % v tomto malém syntetickém experimentu. Šest dalších kandidátů nemá změněný label generátoru, což názorně ukazuje, proč modelové podezření není důkaz chyby.\n')
notebook=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}})
nb.write(notebook,ROOT/'cviceni.ipynb')
print('Vytvořeno buněk:',len(cells))
