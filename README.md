# Radar dos Polos

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
- **Educação: gasto e resultado**: gasto por aluno da rede municipal ao lado do Ideb e das matrículas por rede e etapa.
- **Comparar polos**: gasto por habitante em cada função de governo e indicadores fiscais lado a lado.
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
| `receita_composicao.csv` | Participação de cada origem na receita arrecadada, receita tributária própria, FPM, ICMS e arrecadado ÷ previsto, por ano |
| `ibge_pib.csv` | PIB 2021 a 2023, população do Censo 2022, PIB por habitante 2022 e valor adicionado por setor 2021 (IBGE) |
| `situacao_fiscal.csv` | Indicadores do Radar Situação Fiscal dos Municípios (2020 a 2024) |
| `saude_vacinacao.csv` | Cobertura vacinal por vacina, ano e município (2021 a 2026), com doses, público-alvo e meta |
| `saude_vacinacao_media.csv` | Cobertura vacinal média por município e de Mato Grosso |
| `saude_planos_privados.csv` | Beneficiários de planos privados de saúde por trimestre |
| `saude_estrutura_cnes.csv` | Equipes, profissionais, médicos, estabelecimentos e leitos (CNES, 08/2026) |
| `educacao_ideb.csv` | Ideb, meta, nota Saeb e rendimento por etapa e rede (2017 a 2025) |
| `educacao_matriculas_2025.csv` | Matrículas da educação básica por rede e etapa (Censo Escolar 2025) |

**Fonte:** Tribunal de Contas do Estado de Mato Grosso, Radar de Controle Público: módulos [Despesas](https://radardespesa.tce.mt.gov.br/), [Receita](https://radarreceita.tce.mt.gov.br/) e [Situação Fiscal dos Municípios](https://radarsituacaofiscalmunicipios.tce.mt.gov.br/), base APLIC, e [Radar Saúde](https://radarsaude.tce.mt.gov.br/) (dados do Ministério da Saúde, CNES e ANS). INEP: [resultados do Ideb](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) e [Sinopse Estatística da Educação Básica 2025](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica). IBGE: [SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938) (PIB dos Municípios) e [tabela 4709](https://sidra.ibge.gov.br/tabela/4709) (Censo 2022). Extração em 26 e 27/09/2026 (TCE-MT e INEP) e 08/10/2026 (IBGE).

### Como ler

- Exercícios de 2021 a 2025 encerrados; 2026 parcial até a data da extração.
- Valores em reais correntes (sem correção pela inflação), com o filtro Orçamento Fiscal e da Seguridade Social (OFSS) do Radar.
- No Radar, cada secretaria é um **órgão**. O nome muda de um município para outro e às vezes entre anos; para comparar municípios, use a **função de governo**.
- São dados declaratórios, não auditados. Para o relatório, confirme cada valor no próprio Radar e registre a data de acesso e os filtros usados.

## Como citar

O painel é material de estudo e não é fonte citável: no trabalho, cite a base original (TCE-MT, IBGE, INEP, DataSUS) e confira o valor nela.

> TRIBUNAL DE CONTAS DO ESTADO DE MATO GROSSO. *Radar de Controle Público: Módulo Despesas*. Cuiabá: TCE-MT, 2026. Disponível em: https://radardespesa.tce.mt.gov.br/. Acesso em: dd mmm. aaaa.

---

Material de apoio da disciplina Introdução à Economia, Prof. Dr. Cleiton Franco (UNEMAT).
