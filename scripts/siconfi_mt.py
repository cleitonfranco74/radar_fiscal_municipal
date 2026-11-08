"""Extrai do SICONFI (Tesouro Nacional) os dados fiscais dos 142 municípios de MT.

Uso:  python scripts/siconfi_mt.py  [--anos 2015-2025] [--cache pasta]

Gera dados/mt/siconfi_mt.csv: uma linha por município e ano, com os valores
usados nos indicadores de gestão fiscal (ver scripts/indicadores_mt.py).

Fontes (API pública https://apidatalake.tesouro.gov.br/ords/siconfi/tt/):
- DCA Anexo I-C: receita orçamentária realizada (receita própria, transferências)
- DCA Anexo I-D: despesa liquidada por natureza (investimentos, juros, amortização)
- RGF Anexo 01, Poder Executivo, último período: despesa com pessoal e RCL
- RGF Anexo 05, Poder Executivo, último período: disponibilidade de caixa e restos a pagar
- DCA Anexo I-E: despesa liquidada por função de governo

Gera também dados/mt/receita_origem_mt.csv (receita por origem) e
dados/mt/despesa_funcao_mt.csv (despesa liquidada por função).
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

API = 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# conta do DCA I-C (coluna "Receitas Brutas Realizadas") -> nome da variável.
# Cada variável tem os códigos do ementário atual (2022 em diante) e, separados por "|",
# os de 2018 a 2021 e os de 2015 a 2017; vários códigos na mesma lista são somados.
RECEITAS = {
    'receita_corrente': ['RO1.0.0.0.00.0.0', '|', 'RO1.0.0.0.00.00.00'],
    'receita_tributaria': ['RO1.1.0.0.00.0.0', '|', 'RO1.1.0.0.00.00.00'],      # impostos, taxas e contribuição de melhoria
    'iptu': ['RO1.1.1.2.50.0.0', '|', 'RO1.1.1.8.01.1.0', '|', 'RO1.1.1.2.02.00.00'],
    'iss': ['RO1.1.1.4.51.1.0', '|', 'RO1.1.1.8.02.3.0', '|', 'RO1.1.1.3.05.00.00'],
    'itbi': ['RO1.1.1.2.53.0.0', '|', 'RO1.1.1.8.01.4.0', '|', 'RO1.1.1.2.08.00.00'],
    'fpm': ['RO1.7.1.1.51.0.0', '|', 'RO1.7.1.8.01.2.0', 'RO1.7.1.8.01.3.0', 'RO1.7.1.8.01.4.0', '|', 'RO1.7.2.1.01.02.00'],
    'icms': ['RO1.7.2.1.50.0.0', '|', 'RO1.7.2.8.01.1.0', '|', 'RO1.7.2.2.01.01.00'],
    'sus_uniao': ['RO1.7.1.3.00.0.0', '|', 'RO1.7.1.8.03.0.0', 'RO1.7.1.8.04.0.0', '|', 'RO1.7.2.1.33.00.00'],
    'sus_estado': ['RO1.7.2.3.00.0.0', '|', 'RO1.7.2.8.03.0.0', '|', 'RO1.7.2.2.33.00.00'],
    'fundeb': ['RO1.7.5.1.00.0.0', '|', 'RO1.7.5.8.01.0.0', '|', 'RO1.7.2.4.01.00.00'],
    'operacoes_credito': ['RO2.1.0.0.00.0.0', '|', 'RO2.1.0.0.00.00.00'],
}
# conta do DCA I-D (coluna "Despesas Liquidadas")
DESPESAS = {
    'despesa_total': 'TotalDespesas',
    'despesa_pessoal_orc': 'DO3.1.00.00.00.00',
    'juros': 'DO3.2.00.00.00.00',
    'investimentos': 'DO4.4.00.00.00.00',
    'amortizacao': 'DO4.6.00.00.00.00',
}
# totais para o resultado orçamentário e o art. 167-A da Constituição (despesa empenhada)
EMPENHADAS = {
    'despesa_empenhada_total': 'TotalDespesas',
    'despesa_corrente_empenhada': 'DO3.0.00.00.00.00',
}
CAMPOS = (['cod_ibge', 'municipio', 'ano', 'periodo_rgf', 'rcl', 'despesa_total_pessoal', 'pct_pessoal_rcl',
           'caixa_bruta_nv', 'caixa_liquida_apos_rp_nv', 'rp_total_nv']
          + list(RECEITAS) + ['receita_total', 'deducoes_total', 'deducoes_correntes'] + list(DESPESAS) + list(EMPENHADAS))


# receita orçamentária por origem: nome -> (códigos somados, códigos subtraídos), coluna "Receitas Brutas Realizadas"
def _r(n):
    return f'RO{n}' + '.0' * (3 - n.count('.')) + '.00.0.0'


ORIGENS = {
    'Tributos próprios': ([_r('1.1')], []),
    'Contribuições': ([_r('1.2')], []),
    'Patrimonial, serviços e outras correntes': ([_r('1.3'), _r('1.4'), _r('1.5'), _r('1.6'), _r('1.9')], []),
    'Transferências da União': ([_r('1.7.1'), _r('2.4.1')], []),
    'Transferências do Estado': ([_r('1.7.2'), _r('2.4.2')], []),
    'FUNDEB': ([_r('1.7.5')], []),
    'Outras transferências': ([_r('1.7'), _r('2.4')], [_r('1.7.1'), _r('1.7.2'), _r('1.7.5'), _r('2.4.1'), _r('2.4.2')]),
    'Operações de crédito': ([_r('2.1')], []),
    'Outras receitas de capital': ([_r('2')], [_r('2.1'), _r('2.4')]),
}


# 2015 a 2017: códigos com sete níveis e transferências agrupadas de outro jeito
def _ra(n):
    return f'RO{n}' + '.0' * (3 - n.count('.')) + '.00.00.00'


ORIGENS_2015 = {
    'Tributos próprios': ([_ra('1.1')], []),
    'Contribuições': ([_ra('1.2')], []),
    'Patrimonial, serviços e outras correntes': ([_ra('1.3'), _ra('1.4'), _ra('1.5'), _ra('1.6'), _ra('1.9')], []),
    'Transferências da União': ([_ra('1.7.2.1'), _ra('2.4.2.1'), _ra('1.7.6.1'), _ra('2.4.7.1')], []),
    'Transferências do Estado': ([_ra('1.7.2.2'), _ra('2.4.2.2'), _ra('1.7.6.2'), _ra('2.4.7.2')], []),
    'FUNDEB': ([_ra('1.7.2.4')], []),
    'Outras transferências': ([_ra('1.7'), _ra('2.4')], [_ra('1.7.2.1'), _ra('2.4.2.1'), _ra('1.7.6.1'), _ra('2.4.7.1'),
                                                          _ra('1.7.2.2'), _ra('2.4.2.2'), _ra('1.7.6.2'), _ra('2.4.7.2'), _ra('1.7.2.4')]),
    'Operações de crédito': ([_ra('2.1')], []),
    'Outras receitas de capital': ([_ra('2')], [_ra('2.1'), _ra('2.4')]),
}


def baixar(ep, cache, **p):
    """Baixa um relatório (com paginação) e guarda em cache local."""
    nome = os.path.join(cache, ep + '_' + '_'.join(f'{k}-{v}' for k, v in sorted(p.items())).replace(' ', '') + '.json')
    if os.path.exists(nome):
        with open(nome, encoding='utf-8') as f:
            return json.load(f)
    itens, offset = [], 0
    while True:
        url = API + ep + '?' + urllib.parse.urlencode(dict(p, offset=offset))
        for tentativa in range(5):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    d = json.load(r)
                break
            except Exception as e:
                if tentativa == 4:
                    raise
                time.sleep(2 ** tentativa * 2)
        itens += d.get('items', [])
        if not d.get('hasMore'):
            break
        offset += len(d['items'])
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(itens, f, ensure_ascii=False)
    return itens


def rgf(anexo, cod, ano, cache):
    """RGF do Executivo no último período: quadrimestral (3º) ou semestral (2º).
    Municípios com menos de 50 mil habitantes podem publicar o RGF Simplificado,
    que traz todos os anexos numa consulta só."""
    for per, nr in (('Q', 3), ('S', 2)):
        it = baixar('rgf', cache, an_exercicio=ano, in_periodicidade=per, nr_periodo=nr, co_tipo_demonstrativo='RGF',
                    no_anexo=anexo, co_esfera='M', co_poder='E', id_ente=cod)
        if it:
            return it, f'{nr}{per}'
    for per, nr in (('S', 2), ('Q', 3)):
        it = baixar('rgf', cache, an_exercicio=ano, in_periodicidade=per, nr_periodo=nr,
                    co_tipo_demonstrativo='RGF Simplificado', co_esfera='M', co_poder='E', id_ente=cod)
        it = [i for i in it if i['anexo'] == anexo]
        if it:
            return it, f'{nr}{per} simplificado'
    return [], ''


def valor(itens, coluna, cod_conta, conta=None):
    """Valor de uma conta numa coluna; nomes comparados sem diferenciar maiúsculas (os anos antigos variam)."""
    coluna, conta = coluna.upper(), conta.upper() if conta else None
    for i in itens:
        if i['coluna'].upper().startswith(coluna) and i['cod_conta'] == cod_conta and (conta is None or i['conta'].upper().startswith(conta)):
            return i['valor']
    return None


def linha(ente, ano, cache):
    cod = ente['cod_ibge']
    r = {'cod_ibge': cod, 'municipio': ente['ente'], 'ano': ano}
    a1, per = rgf('RGF-Anexo 01', cod, ano, cache)
    r['periodo_rgf'] = per
    r['rcl'] = valor(a1, 'Valor', 'ReceitaCorrenteLiquidaAjustada') or valor(a1, 'Valor', 'ReceitaCorrenteLiquidaLimiteLegal')
    r['despesa_total_pessoal'] = valor(a1, 'Valor', 'DespesaComPessoalTotal')
    r['pct_pessoal_rcl'] = valor(a1, '% sobre a RCL', 'DespesaComPessoalTotal')
    a5, _ = rgf('RGF-Anexo 05', cod, ano, cache)
    nv = 'TOTAL DOS RECURSOS NÃO VINCULADOS'
    r['caixa_bruta_nv'] = valor(a5, 'DISPONIBILIDADE DE CAIXA BRUTA', 'DisponibilidadeDeCaixaBruta', nv)
    r['caixa_liquida_apos_rp_nv'] = valor(a5, 'DISPONIBILIDADE DE CAIXA LÍQUIDA (APÓS', 'DisponibilidadeDeCaixaLiquidaAposRP', nv)
    if r['caixa_liquida_apos_rp_nv'] is None:  # anos antigos: caixa líquida menos restos a pagar não processados
        cl = valor(a5, 'DISPONIBILIDADE DE CAIXA LÍQUIDA', 'DisponibilidadeDeCaixaLiquida', nv) or valor(a5, 'DISPONIBILIDADE DE CAIXA LÍQUIDA', 'DisponibilidadeDeCaixaLiquida', 'Total dos Recursos Não Vinculados')
        rpnp = valor(a5, 'RESTOS A PAGAR EMPENHADOS E NÃO LIQUIDADOS DO', 'RestosAPagarEmpenhadosENaoLiquidadosDoExercicio', nv) or valor(a5, 'RESTOS A PAGAR EMPENHADOS E NÃO LIQUIDADOS DO', 'RestosAPagarEmpenhadosENaoLiquidadosDoExercicio', 'Total dos Recursos Não Vinculados')
        if cl is not None:
            r['caixa_liquida_apos_rp_nv'] = cl - (rpnp or 0)
    rp = [valor(a5, c, k, nv) for c, k in (
        ('De Exercícios Anteriores', 'RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores'),
        ('Do Exercício', 'RestosAPagarLiquidadosENaoPagosDoExercicio'),
        ('Restos a Pagar Empenhados e Não Liquidados de Exercícios Ant', 'RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores'),
        ('RESTOS A PAGAR EMPENHADOS E NÃO LIQUIDADOS DO EXERCÍCIO', 'RestosAPagarEmpenhadosENaoLiquidadosDoExercicio'))]
    r['rp_total_nv'] = sum(v for v in rp if v) if a5 else None
    dc = baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-C', id_ente=cod)
    realizadas = {i['cod_conta']: i['valor'] for i in dc if i['coluna'] == 'Receitas Brutas Realizadas'}
    for n, codigos in RECEITAS.items():
        r[n] = None
        if not dc:
            continue
        for lista in (alt.split() for alt in ' '.join(codigos).split('|')):
            if any(c in realizadas for c in lista):
                r[n] = sum(realizadas.get(c, 0) for c in lista)
                break
        else:
            r[n] = 0
    dd = baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-D', id_ente=cod)
    for n, k in DESPESAS.items():
        r[n] = valor(dd, 'Despesas Liquidadas', k) if dd else None
        if dd and r[n] is None:
            r[n] = 0
    r['receita_total'] = realizadas.get('TotalReceitas') if dc else None
    deducoes = [i for i in dc if i['coluna'].startswith('Deduções') or i['coluna'] == 'Outras Deduções da Receita']
    r['deducoes_total'] = sum(i['valor'] for i in deducoes if i['cod_conta'] == 'TotalReceitas') if dc else None
    r['deducoes_correntes'] = sum(i['valor'] for i in deducoes if i['cod_conta'] == 'RO1.0.0.0.00.0.0') if dc else None
    for n, k in EMPENHADAS.items():
        r[n] = valor(dd, 'Despesas Empenhadas', k) if dd else None
    r['_origem'] = {}
    if dc:
        tabela = ORIGENS_2015 if _ra('1') in realizadas else ORIGENS
        for n, (mais, menos) in tabela.items():
            r['_origem'][n] = round(sum(realizadas.get(c, 0) for c in mais) - sum(realizadas.get(c, 0) for c in menos), 2)
    r['_funcao'] = {}
    de = baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-E', id_ente=cod)
    for i in de:
        if i['coluna'] != 'Despesas Liquidadas':
            continue
        if i['conta'].startswith('Despesas Intraor'):
            break  # o bloco seguinte repete as funções para as despesas intraorçamentárias
        m = re.match(r'(\d\d) - (.+)', i['conta'])
        if m:
            r['_funcao'][f'{m[1]} - {m[2].strip()}'] = round(i['valor'], 2)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--anos', default='2015-2025')
    ap.add_argument('--cache', default=os.path.join(RAIZ, '.cache_siconfi'))
    ap.add_argument('--threads', type=int, default=4)
    a = ap.parse_args()
    i, f = map(int, a.anos.split('-'))
    os.makedirs(a.cache, exist_ok=True)
    entes = [e for e in baixar('entes', a.cache) if e['uf'] == 'MT' and e['esfera'] == 'M']
    entes.sort(key=lambda e: e['ente'])
    tarefas = [(e, y) for e in entes for y in range(i, f + 1)]
    feitos = 0

    def um(t):
        nonlocal feitos
        r = linha(*t, a.cache)
        feitos += 1
        if feitos % 50 == 0:
            print(f'{feitos}/{len(tarefas)}', file=sys.stderr, flush=True)
        return r

    with ThreadPoolExecutor(a.threads) as ex:
        linhas = list(ex.map(um, tarefas))
    saida = os.path.join(RAIZ, 'dados', 'mt', 'siconfi_mt.csv')
    with open(saida, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, CAMPOS, delimiter=';')
        w.writeheader()
        for r in linhas:
            w.writerow({k: ('' if r.get(k) is None else (round(r[k], 2) if isinstance(r[k], float) else r[k])) for k in CAMPOS})
    with open(os.path.join(RAIZ, 'dados', 'mt', 'receita_origem_mt.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['cod_ibge', 'municipio', 'ano', 'origem', 'arrecadada'])
        for r in linhas:
            for n, v in r['_origem'].items():
                w.writerow([r['cod_ibge'], r['municipio'], r['ano'], n, v])
    with open(os.path.join(RAIZ, 'dados', 'mt', 'despesa_funcao_mt.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['cod_ibge', 'municipio', 'ano', 'funcao', 'liquidado'])
        for r in linhas:
            for n, v in sorted(r['_funcao'].items()):
                w.writerow([r['cod_ibge'], r['municipio'], r['ano'], n, v])
    print(f'{len(linhas)} linhas em {saida}', file=sys.stderr)


if __name__ == '__main__':
    main()
