"""Bolsa Família e BPC por município de MT (Portal da Transparência, CGU).

Uso:  python scripts/transparencia_mt.py [--meses 202312,202412,202512]

Os arquivos mensais do Portal da Transparência trazem um registro por pagamento, com nome,
CPF e NIS de cada beneficiário. O script os lê em fluxo, sem gravá-los, e guarda só a
contagem e o valor por município: nenhum dado pessoal sai daqui.

- Bolsa Família: famílias com parcela do próprio mês (mês de referência = mês de competência)
  e valor dessas parcelas
- BPC: benefícios pagos no mês e valor

O código de município do Portal é o do SIAFI; a ligação com o código do IBGE é feita pelo nome.
Gera dados/mt/assistencia_transparencia_mt.csv. Requer stream-unzip.
"""
import argparse, csv, os, sys, unicodedata, urllib.request
from stream_unzip import stream_unzip

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/{t}/{m}_{n}.zip'


def norm(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().upper()
    return ' '.join(s.replace("'", ' ').replace('-', ' ').split())


def linhas(url):
    r = urllib.request.urlopen(url, timeout=600)
    for _, _, conteudo in stream_unzip(iter(lambda: r.read(1 << 20), b'')):
        resto = b''
        for c in conteudo:
            partes = (resto + c).split(b'\n')
            resto = partes.pop()
            for p in partes:
                yield p.decode('latin1').rstrip('\r')
        if resto:
            yield resto.decode('latin1')
        break


def valor(s):
    return float(s.strip('"').replace('.', '').replace(',', '.') or 0)


def agrega(tipo, nome, mes, nomes_ibge):
    out, sem = {}, set()
    it = linhas(URL.format(t=tipo, m=mes, n=nome))
    cab = [c.strip('"') for c in next(it).split(';')]
    iuf, imun, iref, ival = cab.index('UF'), cab.index('NOME MUNICÍPIO'), cab.index('MÊS REFERÊNCIA'), cab.index('VALOR PARCELA')
    for ln in it:
        if ';"MT";' not in ln:
            continue
        f = [c.strip('"') for c in ln.split(';')]
        if f[iuf] != 'MT' or (tipo == 'novo-bolsa-familia' and f[iref] != mes):
            continue
        cod = nomes_ibge.get(norm(f[imun]))
        if not cod:
            sem.add(f[imun])
            continue
        d = out.setdefault(cod, [0, 0.0])
        d[0] += 1
        d[1] += valor(f[ival])
    if sem:
        print(f'{tipo} {mes}: municípios sem correspondência: {sorted(sem)}', file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--meses', default='202312,202412,202512')
    a = ap.parse_args()
    with open(os.path.join(RAIZ, 'dados', 'mt', 'populacao_mt.csv'), encoding='utf-8') as f:
        nomes_ibge = {norm(r['municipio']): r['cod_ibge'] for r in csv.DictReader(f, delimiter=';')}
    nomes_ibge.update({  # grafias diferentes no SIAFI
        norm('Poxoréo'): nomes_ibge.get(norm('Poxoréu')),
        norm('Santo Antônio do Leverger'): nomes_ibge.get(norm('Santo Antônio de Leverger')),
    })
    linhas_csv = []
    for mes in a.meses.split(','):
        bf = agrega('novo-bolsa-familia', 'NovoBolsaFamilia', mes, nomes_ibge)
        bpc = agrega('bpc', 'BPC', mes, nomes_ibge)
        for cod in sorted(set(bf) | set(bpc)):
            linhas_csv.append([cod, f'{mes[:4]}-{mes[4:]}', bf.get(cod, [0, 0])[0], round(bf.get(cod, [0, 0])[1], 2),
                               bpc.get(cod, [0, 0])[0], round(bpc.get(cod, [0, 0])[1], 2)])
        print(f'{mes}: {len(bf)} municípios com Bolsa Família, {len(bpc)} com BPC', file=sys.stderr, flush=True)
    with open(os.path.join(RAIZ, 'dados', 'mt', 'assistencia_transparencia_mt.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['cod_ibge', 'referencia', 'familias_bolsa_familia', 'valor_bolsa_familia_reais', 'beneficios_bpc', 'valor_bpc_reais'])
        w.writerows(linhas_csv)


if __name__ == '__main__':
    main()
