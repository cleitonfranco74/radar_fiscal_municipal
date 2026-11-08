"""Doses de vacina aplicadas em residentes de MT, a partir dos microdados do PNI
(Ministério da Saúde, OpenDataSUS), e nascidos vivos do SINASC.

Uso:  python scripts/vacinacao_mt.py [--ano 2025]

Os arquivos mensais do PNI têm o Brasil inteiro (cerca de 1,8 GB compactados cada).
O script lê cada arquivo em fluxo, sem gravá-lo em disco, guarda só as linhas de
pacientes residentes em MT e soma as doses. Gera:
- dados/mt/vacinacao_doses_mt_<ano>.csv: doses por município de residência,
  imunobiológico, dose e idade (em anos)
- dados/mt/nascidos_vivos_mt_<ano>.csv: nascidos vivos por município de residência
Requer o pacote stream-unzip (pip install stream-unzip).
"""
import argparse, collections, csv, io, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from stream_unzip import stream_unzip

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/'
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']


def linhas_zip(url):
    """Lê um .zip remoto em fluxo e devolve as linhas (bytes) do primeiro arquivo."""
    r = urllib.request.urlopen(url, timeout=300)
    pedacos = iter(lambda: r.read(1 << 20), b'')
    for _, _, conteudo in stream_unzip(pedacos):
        resto = b''
        for c in conteudo:
            partes = (resto + c).split(b'\n')
            resto = partes.pop()
            yield from partes
        if resto:
            yield resto
        break


def doses_mes(ano, mes):
    url = f'{BASE}PNI/csv/vacinacao_{mes}_{ano}_csv.zip'
    cont = collections.Counter()
    it = linhas_zip(url)
    cab = next(it).decode('latin1').rstrip('\r').split(';')
    i = {c: cab.index(c) for c in ('sg_uf_paciente', 'co_municipio_paciente', 'sg_imunobiologico', 'co_vacina',
                                    'ds_tipo_dose', 'nu_idade_paciente', 'st_documento', 'dt_deletado_rnds')}
    n = 0
    for ln in it:
        n += 1
        if b';MT;' not in ln:
            continue
        f = ln.decode('latin1').rstrip('\r').split(';')
        if len(f) < len(cab) or f[i['sg_uf_paciente']] != 'MT' or f[i['dt_deletado_rnds']]:
            continue
        if f[i['st_documento']] not in ('final', ''):
            continue
        cont[(f[i['co_municipio_paciente']], f[i['sg_imunobiologico']], f[i['co_vacina']], f[i['ds_tipo_dose']],
              f[i['nu_idade_paciente']])] += 1
    print(f'{mes}/{ano}: {n:,} registros no Brasil, {sum(cont.values()):,} doses de residentes em MT', file=sys.stderr, flush=True)
    return cont


def nascidos(ano):
    cont = collections.Counter()
    it = linhas_zip(f'{BASE}SINASC/csv/SINASC_{ano}_csv.zip')
    cab = [c.strip('"').upper() for c in next(it).decode('latin1').rstrip('\r').split(';')]
    j = cab.index('CODMUNRES')
    for ln in it:
        f = ln.decode('latin1').rstrip('\r').split(';')
        if len(f) > j and f[j].strip('"').startswith('51'):
            cont[f[j].strip('"')[:6]] += 1
    return cont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ano', type=int, default=2025)
    ap.add_argument('--threads', type=int, default=3)
    a = ap.parse_args()
    total = collections.Counter()
    with ThreadPoolExecutor(a.threads) as ex:
        for c in ex.map(lambda m: doses_mes(a.ano, m), MESES):
            total.update(c)
    saida = os.path.join(RAIZ, 'dados', 'mt', f'vacinacao_doses_mt_{a.ano}.csv')
    with open(saida, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['co_municipio_ibge6', 'sg_imunobiologico', 'co_vacina', 'ds_tipo_dose', 'idade_anos', 'doses'])
        for k in sorted(total):
            w.writerow([*k, total[k]])
    nv = nascidos(a.ano)
    with open(os.path.join(RAIZ, 'dados', 'mt', f'nascidos_vivos_mt_{a.ano}.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['co_municipio_ibge6', 'nascidos_vivos'])
        for k in sorted(nv):
            w.writerow([k, nv[k]])
    print(f'{sum(total.values()):,} doses; {sum(nv.values()):,} nascidos vivos', file=sys.stderr)


if __name__ == '__main__':
    main()
