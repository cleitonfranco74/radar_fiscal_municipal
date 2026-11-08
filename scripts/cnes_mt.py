"""Estrutura de saúde dos municípios de MT (CNES, Ministério da Saúde, OpenDataSUS).

Uso:  python scripts/cnes_mt.py [--ano-leitos 2025]

- Estabelecimentos ativos por município: total, unidades básicas e postos de saúde,
  hospitais, estabelecimentos públicos (natureza jurídica)
  e que atendem o SUS no ambulatório (arquivo cnes_estabelecimentos, posição atual)
- Leitos existentes, leitos SUS e leitos de UTI em dezembro do ano (arquivo Leitos_<ano>)

Gera dados/mt/saude_cnes_mt.csv.
"""
import argparse, collections, csv, io, os, sys, urllib.request, zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/'
BASICA = {'01', '02', '32', '71', '74'}       # posto, centro de saúde/UBS, unidade móvel fluvial, centro de apoio à saúde da família, polo academia
HOSPITAL = {'05', '07', '15', '62'}           # hospital geral, especializado, unidade mista, hospital-dia


def csv_zip(url):
    with urllib.request.urlopen(url, timeout=600) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    nome = next(n for n in z.namelist() if n.lower().endswith('.csv'))
    return csv.DictReader(io.TextIOWrapper(z.open(nome), encoding='latin1'), delimiter=';')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ano-leitos', type=int, default=2025)
    a = ap.parse_args()
    est = collections.defaultdict(collections.Counter)
    for r in csv_zip(BASE + 'CNES/cnes_estabelecimentos_csv.zip'):
        if r['CO_UF'] != '51' or (r.get('CO_MOTIVO_DESAB') or '').strip():
            continue
        m, tipo = r['CO_IBGE'], (r['TP_UNIDADE'] or '').zfill(2)
        est[m]['estabelecimentos'] += 1
        est[m]['atencao_basica'] += tipo in BASICA
        est[m]['hospitais'] += tipo in HOSPITAL
        est[m]['publicos'] += (r['CO_NATUREZA_JUR'] or '').startswith('1')  # natureza jurídica: administração pública
        est[m]['atendem_sus'] += (r.get('CO_AMBULATORIAL_SUS') or '').strip().upper() == 'SIM'
    comp = f'{a.ano_leitos}12'
    for r in csv_zip(BASE + f'Leitos_SUS/Leitos_csv_{a.ano_leitos}.zip'):
        if r['UF'] != 'MT' or r['COMP'] != comp:
            continue
        m = r['CO_IBGE']
        for k, col in (('leitos', 'LEITOS_EXISTENTES'), ('leitos_sus', 'LEITOS_SUS'), ('leitos_uti', 'UTI_TOTAL_EXIST'), ('leitos_uti_sus', 'UTI_TOTAL_SUS')):
            est[m][k] += int(float(r[col] or 0))
    campos = ['estabelecimentos', 'atencao_basica', 'hospitais', 'publicos', 'atendem_sus', 'leitos', 'leitos_sus', 'leitos_uti', 'leitos_uti_sus']
    with open(os.path.join(RAIZ, 'dados', 'mt', 'saude_cnes_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['co_municipio_ibge6', 'competencia_leitos'] + campos)
        for m in sorted(est):
            w.writerow([m, comp] + [est[m][c] for c in campos])
    print(len(est), 'municípios', file=sys.stderr)


if __name__ == '__main__':
    main()
