# Radar Fiscal de Mato Grosso

Painel das finanças municipais, da saúde e da educação dos seis polos da disciplina **Introdução à Economia** (Bacharelado em Administração Pública EaD, UNEMAT/DEAD, 2026/2), organizado por secretaria, com dados do **Radar de Controle Público do TCE-MT**.

**Acesse o painel:** https://cleitonfranco74.github.io/radar_fiscal_municipal/

| Horário da aula síncrona | Polos |
|---|---|
| 19h | Ribeirão Cascalheira, São Félix do Araguaia |
| 20h | Água Boa, Canarana |
| 21h | Arenápolis, Alto Araguaia |

## O que o painel mostra

- **Roteiro da AD2**: os quatro eixos da Avaliação a Distância 2 (A a D), com o conceito, a pergunta, um ponto de partida numérico para o município escolhido e a aba onde buscar os dados; eficiência, eficácia e efetividade; fontes oficiais com modelos de referência; rubrica e checklist de entrega.
- **Secretarias**: despesa de cada órgão municipal por natureza (pessoal, custeio, investimento, dívida), elemento de despesa, fonte de recurso, programa e mês, com a ficha de indicadores usada no Trabalho Interdisciplinar.
- **Receitas**: receita arrecadada por origem, principais impostos e transferências (ICMS, FPM, ISS, IPTU e outros) e receita por espécie; composição da receita de 2023 a 2025 em percentual (Eixo D); e a economia do município pelo IBGE (PIB, PIB por habitante, valor adicionado por setor e receita própria ÷ PIB).
- **Situação fiscal**: indicadores calculados pelo TCE-MT (Educação, Saúde, pessoal, Art. 167-A, FUNDEB, repasse à Câmara, quociente financeiro, resultado orçamentário, receita própria).
- **Saúde: gasto e resultado**: gasto em saúde por habitante ao lado da cobertura vacinal, da cobertura da Saúde da Família, de médicos e leitos por mil habitantes e da população com plano privado.
- **Assistência, agricultura e saneamento**: gasto da função ao lado do Cadastro Único, Bolsa Família e BPC (MDS), da produção agrícola e do rebanho (IBGE, PAM e PPM) e de água e esgoto nos domicílios (Censo 2022).
- **Educação: gasto e resultado**: gasto por aluno da rede municipal ao lado do Ideb e das matrículas por rede e etapa.
- **Mato Grosso: gestão fiscal**: os 142 municípios do estado, com busca por nome. Índice de gestão fiscal construído com os cinco pilares do IGFM do TCE-MT (receita própria, gasto com pessoal, liquidez, investimentos e custo da dívida), conceito de A a D, posição no estado, comparação com a mediana do grupo populacional, receita própria e transferências (FPM, ICMS, FUNDEB e SUS) por habitante, ranking de 2021 a 2025 e cobertura vacinal de crianças em 2025 (BCG, pentavalente, pólio, pneumocócica, rotavírus e tríplice viral), com um gráfico do repasse do SUS por habitante contra a cobertura média.
- **Mato Grosso: receitas e despesas**: para os 142 municípios, composição da receita de 2021 a 2025 (tributos próprios, União, Estado, FUNDEB e outras), receita por origem e despesa liquidada por função de governo por habitante, com a mediana do grupo populacional.
- **Comparar municípios**: qualquer município de MT ao lado do seu grupo populacional, dos polos ou de todo o estado: gasto por habitante em cada função de governo e indicadores no padrão do Radar Situação Fiscal do TCE-MT (pessoal, art. 167-A, resultado orçamentário e receita própria por habitante), recalculados com o SICONFI.
- **Valores nominais ou em reais de 2025**: seletor no topo que corrige os valores pelo IPCA.
- **Quadro para o Word**: a ficha de indicadores da secretaria pode ser baixada como quadro com título e fonte.
- **Pesquisar**: busca por palavra em todas as secretarias e receitas.

## Dados

Os arquivos em [`dados/`](dados/) estão em CSV (separador `;`, codificação UTF-8) e podem ser abertos no Excel, no LibreOffice ou no R:

| Arquivo | Conteúdo |
|---|---|
| `municipios.csv` | Polo, população, grupo populacional e região |
| `despesa_natureza.csv` | Empenhado, liquidado e pago por órgão e natureza da despesa |
| `despesa_elemento.csv` | Liquidado por órgão e elemento de despesa |
| `despesa_fonte.csv` | Liquidado por órgão e fonte de recurso |
| `despesa_programa.csv` | Liquidado por órgão e programa |
| `despesa_mensal.csv` | Liquidado por órgão e mês |
| `despesa_funcao.csv` | Liquidado e empenhado por função de governo |
| `credores_agregado.csv` | Número de credores e concentração nos cinco maiores (custeio e investimento), sem identificação |
| `receita_totais.csv` | Receita prevista, arrecadada, própria e principais tributos e transferências |
| `receita_grupo.csv` | Receita arrecadada por grupo de origem |
| `receita_especie.csv` | Receita por categoria, origem e espécie |
| `receita_detalhe.csv` | Receita por desdobramento |
| `receita_composicao.csv` | Participação de cada origem na receita arrecadada (sem RPPS): própria, União, Estado, FUNDEB e operações de crédito; receita tributária própria, FPM, ICMS e arrecadado ÷ previsto, por ano |
| `assistencia_mds.csv` | Cadastro Único, Bolsa Família, BPC e CRAS em dezembro de 2023, 2024 e 2025 (MDS, VIS Data) |
| `agricultura_ibge.csv` | Área colhida e valor da produção agrícola (PAM), rebanho bovino (PPM) e soja, 2022 a 2024 |
| `saneamento_censo2022.csv` | Domicílios com rede de água, esgoto ligado à rede e fossas (Censo 2022) |
| `populacao_ibge.csv` | Estimativas de população do IBGE (2021, 2024 a 2026) e Censo 2022 |
| `ipca.csv` | IPCA de dezembro e fator para reais de 2025 |
| `ibge_pib.csv` | PIB 2021 a 2023, população do Censo 2022, PIB por habitante 2022 e valor adicionado por setor 2021 (IBGE) |
| `situacao_fiscal.csv` | Indicadores do Radar Situação Fiscal dos Municípios (2020 a 2024) |
| `saude_vacinacao.csv` | Cobertura vacinal por vacina, ano e município (2021 a 2026), com doses, público-alvo e meta |
| `saude_vacinacao_media.csv` | Cobertura vacinal média por município e de Mato Grosso |
| `saude_planos_privados.csv` | Beneficiários de planos privados de saúde por trimestre |
| `saude_estrutura_cnes.csv` | Equipes, profissionais, médicos, estabelecimentos e leitos (CNES, 08/2026) |
| `educacao_ideb.csv` | Ideb, meta, nota Saeb e rendimento por etapa e rede (2017 a 2025) |
| `educacao_matriculas_2025.csv` | Matrículas da educação básica por rede e etapa (Censo Escolar 2025) |
| `mt/siconfi_mt.csv` | Os 142 municípios de MT, 2021 a 2025: RCL, despesa com pessoal, caixa e restos a pagar (RGF do Executivo), receita tributária, IPTU, ISS, ITBI, FPM, ICMS, FUNDEB, SUS da União e do Estado (DCA I-C) e investimentos, juros e amortização (DCA I-D) |
| `mt/receita_origem_mt.csv` | Receita arrecadada por origem (bruta), por município e ano (DCA I-C) |
| `mt/despesa_funcao_mt.csv` | Despesa liquidada por função de governo, por município e ano (DCA I-E) |
| `mt/indicadores_padrao_tce_mt.csv` | Pessoal (% da RCL), despesa corrente ÷ receita corrente, resultado orçamentário (% da RCL) e receita tributária própria por habitante |
| `mt/indice_gestao_fiscal_mt.csv` | Indicadores (% da RCL), notas de 0 a 1, índice e conceito de cada município e ano |
| `mt/vacinacao_doses_mt_2025.csv` | Doses aplicadas em 2025 em residentes de MT, por município, imunobiológico, dose e idade (microdados do PNI) |
| `mt/nascidos_vivos_mt_2025.csv` | Nascidos vivos de 2025 por município de residência (SINASC) |
| `mt/cobertura_vacinal_mt_2025.csv` | Cobertura vacinal de crianças por município (doses ÷ nascidos vivos, em %) |
| `mt/populacao_mt.csv` | População dos 142 municípios: estimativas 2021, 2024 e 2025 e Censo 2022 (IBGE) |

**Fonte:** Tribunal de Contas do Estado de Mato Grosso, Radar de Controle Público: módulos [Despesas](https://radardespesa.tce.mt.gov.br/), [Receita](https://radarreceita.tce.mt.gov.br/) e [Situação Fiscal dos Municípios](https://radarsituacaofiscalmunicipios.tce.mt.gov.br/), base APLIC, e [Radar Saúde](https://radarsaude.tce.mt.gov.br/) (dados do Ministério da Saúde, CNES e ANS). INEP: [resultados do Ideb](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) e [Sinopse Estatística da Educação Básica 2025](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica). IBGE: [SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938) (PIB dos Municípios) e [tabela 4709](https://sidra.ibge.gov.br/tabela/4709) (Censo 2022). MDS: [VIS Data](https://aplicacoes.mds.gov.br/sagi/vis/data3/). IBGE: PAM (tabela 5457), PPM (tabela 3939), Censo 2022 (tabelas 6803 e 6805), estimativas de população (tabela 6579) e IPCA (tabela 1737). Tesouro Nacional: [SICONFI](https://siconfi.tesouro.gov.br/) (RGF e DCA, pela [API de dados abertos](https://apidatalake.tesouro.gov.br/docs/siconfi/)). Extração em 26 e 27/09/2026 (TCE-MT e INEP), 08/10/2026 (IBGE e MDS) e 08/11/2026 (SICONFI e população dos 142 municípios).

### Índice de gestão fiscal (aba Mato Grosso)

Reprodução para estudo, **não é o índice oficial do TCE-MT**. Cada pilar vira uma nota de 0 a 1, linear entre os cortes abaixo; o índice é a soma ponderada e o conceito segue as faixas do IFGF da FIRJAN, em que o IGFM se baseia (A ≥ 0,8; B 0,6 a 0,8; C 0,4 a 0,6; D < 0,4).

| Pilar | Indicador (÷ receita corrente líquida) | Nota 0 | Nota 1 | Peso |
|---|---|---|---|---|
| Receita própria | Receita tributária própria (impostos, taxas e contribuição de melhoria) | 0% | 25% ou mais | 22,5% |
| Gasto com pessoal | Despesa total com pessoal do Executivo (RGF) | 60% ou mais | 30% ou menos | 22,5% |
| Liquidez | Caixa de recursos não vinculados após restos a pagar (RGF Anexo 5) | 0% ou menos | 10% ou mais | 22,5% |
| Investimentos | Investimentos liquidados (DCA I-D) | 0% | 20% ou mais | 22,5% |
| Custo da dívida | Juros e amortização (DCA I-D) | 13% ou mais | 0% | 10% |

Para atualizar: `python scripts/populacao_mt.py`, `python scripts/siconfi_mt.py` (API pública do SICONFI, cerca de uma hora), `python scripts/vacinacao_mt.py` (lê os 12 arquivos mensais do PNI, cerca de 22 GB, sem gravá-los; requer `pip install stream-unzip`) e `python scripts/indicadores_mt.py`, que grava os CSV em `dados/mt/` e atualiza os dados dentro do `index.html`. Os cortes ficam em `CORTES`, no início de `scripts/indicadores_mt.py`.

### Como ler

- Exercícios de 2021 a 2025 encerrados; 2026 parcial até a data da extração.
- Valores em reais correntes por padrão; o seletor "Valores" converte para reais de 2025 pelo IPCA. Filtro Orçamento Fiscal e da Seguridade Social (OFSS) do Radar.
- Por habitante: estimativas do IBGE de cada ano (Censo 2022 para 2022 e 2023).
- O grupo "Demais Transferências do Município" do Radar Receita corresponde ao FUNDEB nos seis polos.
- No Radar, cada secretaria é um **órgão**. O nome muda de um município para outro e às vezes entre anos; para comparar municípios, use a **função de governo**.
- São dados declaratórios, não auditados. Para o relatório, confirme cada valor no próprio Radar e registre a data de acesso e os filtros usados.

## Como citar

O painel é material de estudo e não é fonte citável: no trabalho, cite a base original (TCE-MT, IBGE, INEP, DataSUS) e confira o valor nela.

> TRIBUNAL DE CONTAS DO ESTADO DE MATO GROSSO. *Radar de Controle Público: Módulo Despesas*. Cuiabá: TCE-MT, 2026. Disponível em: https://radardespesa.tce.mt.gov.br/. Acesso em: dd mmm. aaaa.

---

Material de apoio da disciplina Introdução à Economia, Prof. Dr. Cleiton Franco (UNEMAT).
