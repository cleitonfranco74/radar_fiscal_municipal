"""Calcula o Índice de Gestão Fiscal dos municípios de MT e embute os dados no index.html.

Uso:  python scripts/indicadores_mt.py   (depois de scripts/siconfi_mt.py)

Entradas: dados/mt/siconfi_mt.csv e dados/mt/populacao_mt.csv
Saídas:   dados/mt/indice_gestao_fiscal_mt.csv e o bloco <script id="dados-mt"> do index.html

O índice segue os cinco pilares do IGFM do TCE-MT (receita própria, gasto com pessoal,
liquidez, investimentos e custo da dívida), com pesos e faixas de conceito do IFGF da
FIRJAN, em que o IGFM se baseia. As notas de corte de cada pilar foram definidas aqui e
estão em CORTES: o resultado é uma reprodução didática, não o índice oficial do TCE-MT.
"""
import csv, json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MT = os.path.join(RAIZ, 'dados', 'mt')

# pilar: (peso, valor em que a nota é 0, valor em que a nota é 1); a nota é linear entre os dois
CORTES = {
    'receita_propria': (0.225, 0.0, 0.25),   # receita tributária própria ÷ RCL
    'pessoal':         (0.225, 0.60, 0.30),  # despesa total com pessoal do Executivo ÷ RCL (RGF)
    'liquidez':        (0.225, 0.0, 0.10),   # caixa livre após restos a pagar ÷ RCL
    'investimentos':   (0.225, 0.0, 0.20),   # investimentos liquidados ÷ RCL
    'custo_divida':    (0.10, 0.13, 0.0),    # (juros + amortização) ÷ RCL
}
CONCEITOS = [(0.8, 'A', 'Gestão de excelência'), (0.6, 'B', 'Boa gestão'), (0.4, 'C', 'Gestão em dificuldade'), (0, 'D', 'Gestão crítica')]
GRUPOS = [(5000, 'Grupo 1 (até 5 mil hab.)'), (10000, 'Grupo 2 (5 a 10 mil hab.)'), (20000, 'Grupo 3 (10 a 20 mil hab.)'),
          (50000, 'Grupo 4 (20 a 50 mil hab.)'), (100000, 'Grupo 5 (50 a 100 mil hab.)'), (10 ** 9, 'Grupo 6 (mais de 100 mil hab.)')]
# variáveis em reais levadas para a página (por município e ano)
VARS = ['rcl', 'receita_corrente', 'receita_tributaria', 'iptu', 'iss', 'itbi', 'fpm', 'icms', 'sus_uniao', 'sus_estado',
        'fundeb', 'despesa_total_pessoal', 'caixa_liquida_apos_rp_nv', 'investimentos', 'juros', 'amortizacao']


def nota(x, zero, um):
    if x is None:
        return None
    t = (x - zero) / (um - zero)
    return max(0.0, min(1.0, t))


def num(s):
    return float(s) if s not in ('', None) else None


def main():
    pop = {}
    with open(os.path.join(MT, 'populacao_mt.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            pop[int(r['cod_ibge'])] = {a: int(r[c]) if r[c] else None for a, c in
                                       (('2021', 'estimativa_2021'), ('2022', 'censo_2022'), ('2023', 'censo_2022'),
                                        ('2024', 'estimativa_2024'), ('2025', 'estimativa_2025'))}
    linhas = []
    with open(os.path.join(MT, 'siconfi_mt.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            linhas.append(r)
    out, mun = [], {}
    for r in linhas:
        cod, ano = int(r['cod_ibge']), int(r['ano'])
        v = {k: num(r[k]) for k in VARS}
        rcl, rc = v['rcl'], v['receita_corrente']
        obs = ''
        if not r['periodo_rgf']:
            obs = 'RGF do último período não publicado no SICONFI'
        elif r['receita_tributaria'] == '' or r['investimentos'] == '':
            obs = 'DCA não publicada no SICONFI'
        elif not rcl or not rc or not (0.6 <= rcl / rc <= 1.05):
            obs = 'RCL do RGF incompatível com a receita corrente do DCA'
        elif v['caixa_liquida_apos_rp_nv'] is None:
            obs = 'RGF sem o quadro de disponibilidade de caixa'
        ok = not obs
        x = {}
        if ok:
            x['receita_propria'] = v['receita_tributaria'] / rcl
            x['pessoal'] = num(r['pct_pessoal_rcl']) / 100 if r['pct_pessoal_rcl'] else v['despesa_total_pessoal'] / rcl
            x['liquidez'] = v['caixa_liquida_apos_rp_nv'] / rcl
            x['investimentos'] = v['investimentos'] / rcl
            x['custo_divida'] = ((v['juros'] or 0) + (v['amortizacao'] or 0)) / rcl
        notas = {k: nota(x.get(k), z, u) for k, (_, z, u) in CORTES.items()}
        indice = None
        if ok and all(n is not None for n in notas.values()):
            indice = sum(CORTES[k][0] * notas[k] for k in CORTES)
        conceito = next((c for lim, c, _ in CONCEITOS if indice is not None and indice >= lim), '')
        p = pop.get(cod, {}).get(str(ano))
        out.append({'cod_ibge': cod, 'municipio': r['municipio'], 'ano': ano, 'populacao': p or '',
                    **{f'{k}_rcl': '' if x.get(k) is None else round(x[k] * 100, 2) for k in CORTES},
                    **{f'nota_{k}': '' if notas[k] is None else round(notas[k], 3) for k in CORTES},
                    'indice': '' if indice is None else round(indice, 3), 'conceito': conceito, 'observacao': obs})
        m = mun.setdefault(cod, {'c': cod, 'n': r['municipio'], 'pop': pop.get(cod, {}), 'a': {}})
        m['a'][ano] = {'v': [None if v[k] is None else round(v[k]) for k in VARS],
                       'x': [None if x.get(k) is None else round(x[k] * 100, 2) for k in CORTES],
                       'nt': [None if notas[k] is None else round(notas[k], 3) for k in CORTES],
                       'i': None if indice is None else round(indice, 3), 'per': r['periodo_rgf'], 'obs': obs}
    campos = list(out[0].keys())
    with open(os.path.join(MT, 'indice_gestao_fiscal_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, campos, delimiter=';')
        w.writeheader()
        w.writerows(sorted(out, key=lambda o: (o['municipio'], o['ano'])))
    for m in mun.values():
        p24 = m['pop'].get('2024') or m['pop'].get('2025') or m['pop'].get('2022')
        m['g'] = next(i for i, (lim, _) in enumerate(GRUPOS) if (p24 or 0) <= lim) if p24 else None
    bloco = {'VARS': VARS, 'PIL': list(CORTES), 'CORTES': CORTES, 'GRUPOS': [g for _, g in GRUPOS],
             'CONC': [[lim, c, d] for lim, c, d in CONCEITOS],
             'M': sorted(mun.values(), key=lambda m: m['n'])}
    js = json.dumps(bloco, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    p = os.path.join(RAIZ, 'index.html')
    html = open(p, encoding='utf-8').read()
    tag = '<script type="application/json" id="dados-mt">'
    novo = tag + js + '</script>'
    if tag in html:
        html = re.sub(re.escape(tag) + r'.*?</script>', lambda _: novo, html, count=1, flags=re.S)
    else:
        html = html.replace('<script>\n(function(){', novo + '\n<script>\n(function(){', 1)
    open(p, 'w', encoding='utf-8').write(html)
    print(f'{len(out)} linhas; {len(mun)} municípios; bloco de {len(js) // 1024} KB no index.html')


if __name__ == '__main__':
    main()
