from pathlib import Path
import nbformat
root=Path('15_10_2026')
s='''## 12. Interpretace dosažených výsledků

- U stanice S02 dne 1. 1. 2026 v 08:00 vybere původní pořadí teplotu 6,9 °C; sestupné řazení aktualizace správně ponechá opravenou verzi 7,5 °C z 8. 1. 2026.
- Rozdíl agregací je patrný například u S02 v únoru: přímý průměr je 6,0833 °C, průměr denních průměrů 6,3571 °C. Denní četnost kolísá mezi jedním a dvěma provozními měřeními. U skupin se dvěma měřeními každý den se oba postupy shodují.
- Jedna substituce v názvu Most sníží skóre na 75 %, zatímco v dlouhém názvu na 96,67 %. Stejný práh 85 % tak rozhodne rozdílně. Přidaná téměř shodná reference sníží odstup pro „Teplice centurm“ z 33,33 na 13,33 bodu a změní nejlepšího kandidáta; samotné vysoké skóre nemůže zaručit věcnou správnost.
- Pořadí logistické regrese a lesa sdílejí 10 z prvních 15 kandidátů. Společná diagnostika sdílí s regresí 13 a s lesem 12 kandidátů. Modelová fronta a neshoda anotátorů se překrývají v 8 případech; 7 zachytí jen model a 4 jen neshoda. Postupy se doplňují.
- Následná učitelská reference potvrzuje v každé frontě 9 skutečně změněných labelů z 15: precision@15 = 60 % a recall@15 = 100 % v tomto malém syntetickém experimentu. Šest dalších kandidátů nemá změněný label generátoru, což názorně ukazuje, proč modelové podezření není důkaz chyby.
'''
p=root/'vytvor_notebook.py'
t=p.read_text(encoding='utf-8-sig')
t=t.replace('notebook=nb.v4.new_notebook', 'md('+repr(s)+')\nnotebook=nb.v4.new_notebook')
p.write_text(t,encoding='utf-8')
n=nbformat.read(root/'cviceni.ipynb',4)
n.cells.append(nbformat.v4.new_markdown_cell(s))
nbformat.validate(n)
nbformat.write(n,root/'cviceni.ipynb')
# Notebook obsahuje veškerý kód, pomocné skripty umožňují jeho obnovu a ověření.
assert all(not any(o.output_type=='error' for o in c.get('outputs',[])) for c in n.cells)
assert sum(c.cell_type=='code' and c.execution_count is not None for c in n.cells)==24
print('Notebook ověřen:',len(n.cells),'buněk,', (root/'cviceni.ipynb').stat().st_size,'bajtů')
