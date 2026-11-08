"""Ideb e matrículas dos municípios de MT (INEP).

Uso:  python scripts/inep_mt.py [--pasta pasta_para_os_zips]

- Ideb dos anos iniciais e finais do ensino fundamental, por município e rede, 2015 a 2025
  (planilhas "divulgacao_anos_*_municipios_2025")
- Matrículas da educação básica por município e dependência administrativa
  (Sinopse Estatística do Censo Escolar 2025)

O servidor download.inep.gov.br não envia o certificado intermediário da cadeia TLS;
o script o baixa do endereço indicado no próprio certificado (GlobalSign) e mantém a
verificação ligada.

Gera dados/mt/educacao_ideb_mt.csv e dados/mt/educacao_matriculas_mt_2025.csv.
"""
import argparse, csv, io, os, ssl, sys, urllib.request, zipfile
import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://download.inep.gov.br/'
INTERMEDIARIO = 'https://secure.globalsign.com/cacert/rnpicpedugr46ovtlsca2025.crt'
ANOS_IDEB = [2015, 2017, 2019, 2021, 2023, 2025]


def contexto():
    ctx = ssl.create_default_context()
    der = urllib.request.urlopen(INTERMEDIARIO, timeout=60).read()
    ctx.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(der))
    return ctx


def baixar(caminho, pasta, ctx):
    destino = os.path.join(pasta, os.path.basename(caminho))
    if not os.path.exists(destino):
        with urllib.request.urlopen(BASE + caminho, timeout=600, context=ctx) as r, open(destino, 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
    return destino


def num(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None


def ideb(pasta, ctx):
    linhas = []
    for etapa, nome in (('Anos iniciais', 'iniciais'), ('Anos finais', 'finais')):
        z = zipfile.ZipFile(baixar(f'ideb/resultados/divulgacao_anos_{nome}_municipios_2025.zip', pasta, ctx))
        arq = next(n for n in z.namelist() if n.endswith('.xlsx'))
        ws = openpyxl.load_workbook(io.BytesIO(z.read(arq)), read_only=True).active
        cab = None
        for row in ws.iter_rows(values_only=True):
            if row[0] == 'SG_UF':
                cab = {c: i for i, c in enumerate(row) if c}
                continue
            if not cab or row[0] != 'MT':
                continue
            for ano in ANOS_IDEB:
                def col(prefixo):
                    k = next((c for c in cab if c.startswith(f'{prefixo}_{ano}')), None)
                    return num(row[cab[k]]) if k else None
                linhas.append([row[cab['CO_MUNICIPIO']], row[cab['NO_MUNICIPIO']], etapa, row[cab['REDE']], ano,
                               col('VL_OBSERVADO'), col('VL_PROJECAO'), col('VL_NOTA_MEDIA'), col('VL_INDICADOR_REND')])
    with open(os.path.join(RAIZ, 'dados', 'mt', 'educacao_ideb_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['cod_ibge', 'municipio', 'etapa', 'rede', 'ano', 'ideb', 'meta', 'nota_saeb', 'indicador_rendimento'])
        w.writerows([['' if v is None else v for v in l] for l in linhas])
    return len(linhas)


# Sinopse 2025: (planilha, coluna) de cada variável; colunas contadas a partir de 0
MATRICULAS = {
    'total': ('1.2', 4), 'rede_publica': ('1.2', 5), 'rede_estadual': ('1.2', 7), 'rede_municipal': ('1.2', 8),
    'rede_privada': ('1.2', 9), 'educacao_infantil_municipal': ('Educação Infantil 1.8', 8),
    'creche_municipal': ('Educação Infantil 1.8', 18), 'pre_escola_municipal': ('Educação Infantil 1.8', 28),
    'fundamental_municipal': ('Ensino Fundamental 1.20', 8), 'fundamental_estadual': ('Ensino Fundamental 1.20', 7),
    'eja_total': ('Educação Básica 1.1', 33),
}


def matriculas(pasta, ctx, ano=2025):
    z = zipfile.ZipFile(baixar(f'dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_{ano}.zip', pasta, ctx))
    arq = next(n for n in z.namelist() if n.endswith('.xlsx'))
    destino = os.path.join(pasta, os.path.basename(arq))
    if not os.path.exists(destino):
        with z.open(arq) as src, open(destino, 'wb') as dst:
            dst.write(src.read())
    wb = openpyxl.load_workbook(destino, read_only=True)
    dados = {}
    for planilha in sorted({p for p, _ in MATRICULAS.values()}):
        for row in wb[planilha].iter_rows(values_only=True):
            cod = str(row[3] or '').strip()
            if not cod.startswith('51') or len(cod) != 7:
                continue
            d = dados.setdefault(cod, {'municipio': str(row[2]).strip()})
            for nome, (p, c) in MATRICULAS.items():
                if p == planilha:
                    d[nome] = int(num(row[c]) or 0)
    with open(os.path.join(RAIZ, 'dados', 'mt', f'educacao_matriculas_mt_{ano}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['cod_ibge', 'municipio'] + list(MATRICULAS))
        for cod in sorted(dados, key=lambda c: dados[c]['municipio']):
            w.writerow([cod, dados[cod]['municipio']] + [dados[cod].get(k, '') for k in MATRICULAS])
    return len(dados)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pasta', default=os.path.join(RAIZ, '.cache_inep'))
    a = ap.parse_args()
    os.makedirs(a.pasta, exist_ok=True)
    ctx = contexto()
    print(ideb(a.pasta, ctx), 'linhas do Ideb', file=sys.stderr)
    print(matriculas(a.pasta, ctx), 'municípios com matrículas', file=sys.stderr)


if __name__ == '__main__':
    main()
