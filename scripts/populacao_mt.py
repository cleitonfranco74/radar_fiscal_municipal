"""Baixa do IBGE (SIDRA) a população dos municípios de MT: estimativas 2015 a 2021, 2024 e 2025
(tabela 6579) e Censo 2022 (tabela 4709). Gera dados/mt/populacao_mt.csv."""
import csv, json, os, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://apisidra.ibge.gov.br/values/t/{t}/n6/in%20n3%2051/v/{v}/p/{p}'


def sidra(t, v, p):
    with urllib.request.urlopen(URL.format(t=t, v=v, p=p), timeout=120) as r:
        return json.load(r)[1:]


pop = {}
for r in sidra(6579, 9324, '2015,2016,2017,2018,2019,2020,2021,2024,2025'):
    d = pop.setdefault(r['D1C'], {'municipio': r['D1N'].removesuffix(' - MT')})
    d['estimativa_' + r['D3C']] = r['V'] if r['V'].isdigit() else ''
for r in sidra(4709, 93, '2022'):
    d = pop.setdefault(r['D1C'], {'municipio': r['D1N'].removesuffix(' - MT')})
    d['censo_2022'] = r['V'] if r['V'].isdigit() else ''
campos = ['cod_ibge', 'municipio'] + [f'estimativa_{a}' for a in range(2015, 2022)] + ['censo_2022', 'estimativa_2024', 'estimativa_2025']
with open(os.path.join(RAIZ, 'dados', 'mt', 'populacao_mt.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, campos, delimiter=';', restval='')
    w.writeheader()
    for cod in sorted(pop, key=lambda c: pop[c]['municipio']):
        w.writerow({'cod_ibge': cod, **pop[cod]})
print(len(pop), 'municípios')
