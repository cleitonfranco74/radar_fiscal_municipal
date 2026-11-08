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
        'fundeb', 'despesa_total_pessoal', 'caixa_liquida_apos_rp_nv', 'investimentos', 'juros', 'amortizacao',
        'receita_total', 'deducoes_total', 'receita_corrente', 'deducoes_correntes', 'despesa_empenhada_total',
        'despesa_corrente_empenhada']
VARS = list(dict.fromkeys(VARS))
# indicadores no padrão do Radar Situação Fiscal do TCE-MT que o SICONFI permite calcular
TCE = ['Despesa com pessoal do Executivo (% da RCL)', 'Despesa corrente ÷ receita corrente (art. 167-A, %)',
       'Resultado orçamentário (% da RCL)', 'Receita tributária própria por habitante (R$)']


# cobertura vacinal de crianças: (rótulo, meta %, idade em anos, [(imunobiológico, dose), ...])
VACINAS = [
    ('BCG', 90, '0', [('BCG', 'Única'), ('BCG', 'Dose')]),
    ('Pentavalente (3ª dose)', 95, '0', [('Penta', '3ª Dose'), ('Hexa acelular', '3ª Dose'), ('Penta acelular', '3ª Dose')]),
    ('Poliomielite (3ª dose)', 95, '0', [('VIP', '3ª Dose'), ('Hexa acelular', '3ª Dose'), ('DTPa/VIP', '3ª Dose')]),
    ('Pneumocócica (2ª dose)', 95, '0', [('VPC10', '2ª Dose'), ('VPC13', '2ª Dose'), ('VPC15', '2ª Dose'), ('VPC20', '2ª Dose')]),
    ('Rotavírus (2ª dose)', 90, '0', [('ROTA', '2ª Dose'), ('ROTA5', '3ª Dose')]),
    ('Tríplice viral (1ª dose)', 95, '1', [('SCR', '1ª Dose')]),
]


def vacinacao(ano, cods):
    """Cobertura vacinal por município (código IBGE de 7 dígitos), se os arquivos existirem."""
    fd = os.path.join(MT, f'vacinacao_doses_mt_{ano}.csv')
    fn = os.path.join(MT, f'nascidos_vivos_mt_{ano}.csv')
    if not (os.path.exists(fd) and os.path.exists(fn)):
        return None
    seis = {str(c)[:6]: c for c in cods}
    with open(fn, encoding='utf-8') as f:
        nv = {seis[r['co_municipio_ibge6']]: int(r['nascidos_vivos']) for r in csv.DictReader(f, delimiter=';')
              if r['co_municipio_ibge6'] in seis}
    doses = {}
    with open(fd, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            c = seis.get(r['co_municipio_ibge6'])
            if c:
                k = (c, r['sg_imunobiologico'], r['ds_tipo_dose'], r['idade_anos'])
                doses[k] = doses.get(k, 0) + int(r['doses'])
    linhas, bloco = [], {}
    for c in cods:
        if not nv.get(c):
            continue
        cob = []
        for rot, meta, idade, pares in VACINAS:
            d = sum(doses.get((c, im, dose, idade), 0) for im, dose in pares)
            cob.append(round(d / nv[c] * 100, 1))
        bloco[c] = [nv[c]] + cob
        linhas.append([c, ano, nv[c]] + cob)
    with open(os.path.join(MT, f'cobertura_vacinal_mt_{ano}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['cod_ibge', 'ano', 'nascidos_vivos'] + [v[0] for v in VACINAS])
        w.writerows(linhas)
    return {'ano': ano, 'vac': [[v[0], v[1]] for v in VACINAS], 'm': bloco}


def ibge():
    """PIB, área colhida, valor da produção agrícola, soja e rebanho bovino (dados/mt/ibge_mt.csv)."""
    arq = os.path.join(MT, 'ibge_mt.csv')
    if not os.path.exists(arq):
        return None
    out = {}
    campos = ['pib_mil_reais', 'area_colhida_ha', 'valor_producao_agricola_mil_reais', 'soja_toneladas', 'rebanho_bovino_cabecas']
    with open(arq, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            out.setdefault(r['cod_ibge'], {})[r['ano']] = [int(r[c]) if r[c] else None for c in campos]
    return out


def educacao():
    """Ideb (anos iniciais e finais, redes municipal, estadual e pública) e matrículas 2025 (INEP)."""
    out = {}
    arq = os.path.join(MT, 'educacao_ideb_mt.csv')
    if os.path.exists(arq):
        with open(arq, encoding='utf-8') as f:
            for r in csv.DictReader(f, delimiter=';'):
                if r['ideb']:
                    k = ('i' if r['etapa'] == 'Anos iniciais' else 'f') + r['rede'][0]   # iM, iE, iP, fM, fE, fP
                    out.setdefault(r['cod_ibge'], {}).setdefault(k, {})[r['ano']] = float(r['ideb'])
    arq = os.path.join(MT, 'educacao_matriculas_mt_2025.csv')
    if os.path.exists(arq):
        with open(arq, encoding='utf-8') as f:
            for r in csv.DictReader(f, delimiter=';'):
                out.setdefault(r['cod_ibge'], {})['mat'] = [int(r[c] or 0) for c in list(r)[2:]]
    return out


def cnes():
    """Estabelecimentos e leitos (CNES)."""
    arq = os.path.join(MT, 'saude_cnes_mt.csv')
    if not os.path.exists(arq):
        return None
    with open(arq, encoding='utf-8') as f:
        return {r['co_municipio_ibge6']: [int(r[c]) for c in list(r)[2:]] for r in csv.DictReader(f, delimiter=';')}


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
            anos = [(str(a), f'estimativa_{a}') for a in range(2015, 2022)] + [
                ('2022', 'censo_2022'), ('2023', 'censo_2022'), ('2024', 'estimativa_2024'), ('2025', 'estimativa_2025')]
            pop[int(r['cod_ibge'])] = {a: int(r[c]) if r.get(c) else None for a, c in anos}
    origens, funcoes = {}, {}
    with open(os.path.join(MT, 'receita_origem_mt.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            origens.setdefault((int(r['cod_ibge']), int(r['ano'])), {})[r['origem']] = float(r['arrecadada'])
    with open(os.path.join(MT, 'despesa_funcao_mt.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            funcoes.setdefault((int(r['cod_ibge']), int(r['ano'])), {})[r['funcao']] = float(r['liquidado'])
    ORIG = list(dict.fromkeys(o for d in origens.values() for o in d))
    FUN = sorted({f for d in funcoes.values() for f in d})
    tce_linhas = []
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
        # indicadores no padrão do TCE-MT (receita líquida = bruta - deduções para o FUNDEB e outras)
        tce = [None] * len(TCE)
        if r['periodo_rgf'] and rcl and rc and 0.6 <= rcl / rc <= 1.05:
            tce[0] = num(r['pct_pessoal_rcl'])
        if v['receita_total'] is not None and v['despesa_empenhada_total'] is not None:
            rc_liq = rc - (v['deducoes_correntes'] or 0)
            if rc_liq and v['despesa_corrente_empenhada'] is not None:
                tce[1] = round(v['despesa_corrente_empenhada'] / rc_liq * 100, 2)
            if tce[0] is not None:
                tce[2] = round((v['receita_total'] - (v['deducoes_total'] or 0) - v['despesa_empenhada_total']) / rcl * 100, 2)
        if v['receita_tributaria'] is not None and p:
            tce[3] = round(v['receita_tributaria'] / p, 2)
        tce_linhas.append([cod, r['municipio'], ano] + ['' if t is None else t for t in tce])
        m = mun.setdefault(cod, {'c': cod, 'n': r['municipio'], 'pop': pop.get(cod, {}), 'a': {}})
        m['a'][ano] = {'v': [None if v[k] is None else round(v[k]) for k in VARS],
                       'x': [None if x.get(k) is None else round(x[k] * 100, 2) for k in CORTES],
                       'nt': [None if notas[k] is None else round(notas[k], 3) for k in CORTES],
                       'i': None if indice is None else round(indice, 3), 'per': r['periodo_rgf'], 'obs': obs,
                       'o': [round(origens[(cod, ano)].get(o, 0)) for o in ORIG] if (cod, ano) in origens else None,
                       'f': [round(funcoes[(cod, ano)].get(fn, 0)) for fn in FUN] if funcoes.get((cod, ano)) else None,
                       't': tce}
    campos = list(out[0].keys())
    with open(os.path.join(MT, 'indice_gestao_fiscal_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, campos, delimiter=';')
        w.writeheader()
        w.writerows(sorted(out, key=lambda o: (o['municipio'], o['ano'])))
    with open(os.path.join(MT, 'indicadores_padrao_tce_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['cod_ibge', 'municipio', 'ano'] + TCE)
        w.writerows(sorted(tce_linhas, key=lambda t: (t[1], t[2])))
    for m in mun.values():
        p24 = m['pop'].get('2024') or m['pop'].get('2025') or m['pop'].get('2022')
        m['g'] = next(i for i, (lim, _) in enumerate(GRUPOS) if (p24 or 0) <= lim) if p24 else None
    bloco = {'VARS': VARS, 'PIL': list(CORTES), 'CORTES': CORTES, 'GRUPOS': [g for _, g in GRUPOS],
             'CONC': [[lim, c, d] for lim, c, d in CONCEITOS], 'ORIG': ORIG, 'FUN': FUN, 'TCE': TCE,
             'M': sorted(mun.values(), key=lambda m: m['n']),
             'VAC': vacinacao(2025, list(mun)), 'IB': ibge(), 'EDU': educacao(), 'CNES': cnes()}
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
