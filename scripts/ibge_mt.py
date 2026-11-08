"""Baixa do IBGE (SIDRA) dados econômicos dos municípios de MT, de 2015 em diante.

Uso:  python scripts/ibge_mt.py

- PIB a preços correntes (tabela 5938, variável 37), em mil reais
- Área colhida e valor da produção das lavouras temporárias e permanentes (PAM, tabela 5457, total)
- Soja em grão, quantidade produzida (PAM, tabela 5457)
- Rebanho bovino (PPM, tabela 3939)

Gera dados/mt/ibge_mt.csv (uma linha por município e ano).
"""
import csv, json, os, time, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://apisidra.ibge.gov.br/values/t/{t}/n6/in%20n3%2051/v/{v}/p/{p}{c}'
ANOS = ','.join(str(a) for a in range(2015, 2025))
CONSULTAS = [
    ('pib_mil_reais', 5938, 37, ''),
    ('area_colhida_ha', 5457, 216, '/c782/0'),
    ('valor_producao_agricola_mil_reais', 5457, 215, '/c782/0'),
    ('soja_toneladas', 5457, 214, '/c782/40124'),
    ('rebanho_bovino_cabecas', 3939, 105, '/c79/2670'),
]


def sidra(t, v, c):
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(URL.format(t=t, v=v, p=ANOS, c=c), timeout=180) as r:
                return json.load(r)[1:]
        except Exception:
            if tentativa == 3:
                raise
            time.sleep(5 * (tentativa + 1))


dados = {}
for nome, t, v, c in CONSULTAS:
    for r in sidra(t, v, c):
        chave = (r['D1C'], r['D1N'].removesuffix(' - MT'), r['D3C'])
        dados.setdefault(chave, {})[nome] = r['V'] if r['V'].lstrip('-').isdigit() else ''
campos = ['cod_ibge', 'municipio', 'ano'] + [c[0] for c in CONSULTAS]
with open(os.path.join(RAIZ, 'dados', 'mt', 'ibge_mt.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, campos, delimiter=';', restval='')
    w.writeheader()
    for (cod, mun, ano) in sorted(dados, key=lambda k: (k[1], k[2])):
        w.writerow({'cod_ibge': cod, 'municipio': mun, 'ano': ano, **dados[(cod, mun, ano)]})
print(len(dados), 'linhas')
