# Radar dos Polos

Painel das finanças municipais dos seis polos da disciplina **Introdução à Economia** (Bacharelado em Administração Pública EaD, UNEMAT/DEAD, 2026/2), organizado por secretaria, com dados do **Radar de Controle Público do TCE-MT**.

**Acesse o painel:** https://cleitonfranco74.github.io/radar_fiscal_municipal/

| Horário da aula síncrona | Polos |
|---|---|
| 19h | Ribeirão Cascalheira, São Félix do Araguaia |
| 20h | Água Boa, Canarana |
| 21h | Arenápolis, Alto Araguaia |

## O que o painel mostra

- **Secretarias**: despesa de cada órgão municipal por natureza (pessoal, custeio, investimento, dívida), elemento de despesa, fonte de recurso, programa e mês, com a ficha de indicadores usada no Trabalho Interdisciplinar.
- **Receitas**: receita arrecadada por origem, principais impostos e transferências (ICMS, FPM, ISS, IPTU e outros) e receita por espécie.
- **Situação fiscal**: indicadores calculados pelo TCE-MT (Educação, Saúde, pessoal, Art. 167-A, FUNDEB, repasse à Câmara, quociente financeiro, resultado orçamentário, receita própria).
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
| `situacao_fiscal.csv` | Indicadores do Radar Situação Fiscal dos Municípios (2020 a 2024) |

**Fonte:** Tribunal de Contas do Estado de Mato Grosso, Radar de Controle Público: módulos [Despesas](https://radardespesa.tce.mt.gov.br/), [Receita](https://radarreceita.tce.mt.gov.br/) e [Situação Fiscal dos Municípios](https://radarsituacaofiscalmunicipios.tce.mt.gov.br/), base APLIC. Extração em 26/09/2026.

### Como ler

- Exercícios de 2021 a 2025 encerrados; 2026 parcial até a data da extração.
- Valores em reais correntes (sem correção pela inflação), com o filtro Orçamento Fiscal e da Seguridade Social (OFSS) do Radar.
- No Radar, cada secretaria é um **órgão**. O nome muda de um município para outro e às vezes entre anos; para comparar municípios, use a **função de governo**.
- São dados declaratórios, não auditados. Para o relatório, confirme cada valor no próprio Radar e registre a data de acesso e os filtros usados.

## Como citar

> TRIBUNAL DE CONTAS DO ESTADO DE MATO GROSSO. *Radar de Controle Público: Módulo Despesas*. Cuiabá: TCE-MT, 2026. Disponível em: https://radardespesa.tce.mt.gov.br/. Acesso em: dd mmm. aaaa.

---

Material de apoio da disciplina Introdução à Economia, Prof. Dr. Cleiton Franco (UNEMAT).
