"""Detalhamento da receita e da despesa de cada município de MT (SICONFI, DCA), 2015 em diante.

Uso:  python scripts/detalhe_mt.py [--cache pasta]   (depois de scripts/siconfi_mt.py, que deixa o cache pronto)

Para cada município e ano:
- receita por espécie (DCA I-C, terceiro nível do código, como Impostos, Taxas, Transferências da União)
- despesa liquidada por elemento (DCA I-D: aplicações diretas por elemento e demais modalidades pelo nome)
- despesa liquidada por subfunção (DCA I-E, sem as despesas intraorçamentárias)

Gera dados/mt/municipios/<código IBGE>.json, carregado pela página quando o município é escolhido.
"""
import argparse, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import siconfi_mt as s  # noqa: E402

PASTA = os.path.join(s.RAIZ, 'dados', 'mt', 'municipios')


def nome(conta):
    """Tira o código do início do nome da conta: '1.1.1.0.00.0.0 - Impostos' -> 'Impostos'."""
    return re.sub(r'^[\d.]+\s*-\s*', '', conta).strip()


def especies(dc):
    """Receita bruta realizada no nível de espécie (a.b.c), sem as intraorçamentárias."""
    out = {}
    for i in dc:
        if i['coluna'] != 'Receitas Brutas Realizadas':
            continue
        m = re.fullmatch(r'RO(\d)\.(\d)\.(\d)\.0\.00\.0{1,2}\.0{1,2}', i['cod_conta'])
        if m and m[3] != '0':
            out[f'{m[1]}.{m[2]}.{m[3]}'] = (nome(i['conta']), round(i['valor'], 2))
    return out


def elementos(dd):
    """Despesa liquidada: aplicações diretas (modalidade 90) por elemento; demais modalidades pelo nome."""
    out = {}
    for i in dd:
        if i['coluna'] != 'Despesas Liquidadas':
            continue
        m = re.fullmatch(r'DO(\d)\.(\d)\.(\d\d)\.(\d\d)\.00\.00', i['cod_conta'])
        if not m or m[3] == '00':
            continue
        cat, grp, mod, ele = m.groups()
        if mod == '90' and ele != '00':
            out[f'{cat}.{grp}.{ele}'] = (nome(i['conta']), round(i['valor'], 2))
        elif mod not in ('90', '91') and ele == '00':
            out[f'{cat}.{grp}.m{mod}'] = (nome(i['conta']), round(i['valor'], 2))
    return out


def subfuncoes(de):
    out = {}
    for i in de:
        if i['coluna'] != 'Despesas Liquidadas':
            continue
        if i['conta'].startswith('Despesas Intraor'):
            break
        m = re.match(r'(\d\d\.\d\d\d|FU\d\d) - (.+)', i['conta'])
        if m:
            k = m[1] if m[1][0] != 'F' else m[1][2:] + '.999'
            out[k] = (m[2].strip(), round(i['valor'], 2))
    return out


def municipio(ente, anos, cache):
    cod = ente['cod_ibge']
    nomes, dados = {'ele': {}, 'sub': {}}, {}
    for ano in anos:
        dc = s.baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-C', id_ente=cod)
        dd = s.baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-D', id_ente=cod)
        de = s.baixar('dca', cache, an_exercicio=ano, no_anexo='DCA-Anexo I-E', id_ente=cod)
        if not (dc or dd or de):
            continue
        a = {}
        # espécies: o mesmo código muda de sentido entre planos de contas, então vai com o nome do ano
        a['esp'] = [[k, n, v] for k, (n, v) in sorted(especies(dc).items())]
        for tipo, itens in (('ele', elementos(dd)), ('sub', subfuncoes(de))):
            a[tipo] = {k: v for k, (n, v) in itens.items()}
            for k, (n, _) in itens.items():
                nomes[tipo][k] = n  # fica o nome do ano mais recente
        dados[str(ano)] = a
    with open(os.path.join(PASTA, f'{cod}.json'), 'w', encoding='utf-8') as f:
        json.dump({'cod': cod, 'nome': ente['ente'], 'nomes': nomes, 'anos': dados}, f, ensure_ascii=False, separators=(',', ':'))
    return cod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--anos', default='2015-2025')
    ap.add_argument('--cache', default=os.path.join(s.RAIZ, '.cache_siconfi'))
    a = ap.parse_args()
    i, f = map(int, a.anos.split('-'))
    os.makedirs(PASTA, exist_ok=True)
    entes = [e for e in s.baixar('entes', a.cache) if e['uf'] == 'MT' and e['esfera'] == 'M']
    with ThreadPoolExecutor(4) as ex:
        feitos = list(ex.map(lambda e: municipio(e, range(i, f + 1), a.cache), entes))
    print(f'{len(feitos)} arquivos em {PASTA}', file=sys.stderr)


if __name__ == '__main__':
    main()
