---
tags:
  - gerenciamento-de-projetos
  - GVA
  - EVM
aliases:
  - GVA
  - EVM
  - Gerenciamento do Valor Agregado
---

# Gerenciamento do Valor Agregado (GVA / EVM)

O **Gerenciamento do Valor Agregado** (GVA), ou *Earned Value Management* (EVM), é uma metodologia que integra o escopo, o cronograma e os recursos (custos) para medir o desempenho e o progresso do projeto de forma objetiva.

---
## Pilares do GVA

Existem três métricas fundamentais que formam a base do GVA:

### 1. Valor Planejado (VP) ou [[Planned Value (PV)]]
É o orçamento autorizado alocado para o trabalho que *deveria ter sido* concluído até uma determinada data.
- **Pergunta-chave:** "Quanto trabalho eu deveria ter feito?"
- **Fórmula:** `VP = (Orçamento Total do Projeto) * (% Planejada de Conclusão)`

### 2. Valor Agregado (VA) ou [[Earned Value (EV)]]
É o valor do trabalho *realmente* concluído até a data de medição, expresso em termos do orçamento aprovado para esse trabalho.
- **Pergunta-chave:** "Quanto trabalho eu realmente fiz?"
- **Fórmula:** `VA = (Orçamento Total do Projeto) * (% Real de Conclusão)`

### 3. Custo Real (CR) ou [[Actual Cost (AC)]]
É o custo total incorrido para realizar o trabalho que foi efetivamente concluído até a data de medição.
- **Pergunta-chave:** "Quanto eu realmente gastei?"

---
## Análise de Variações (Desempenho)

As variações medem o desvio em relação à [[Linha de Base do Projeto]].

- **Variação de Custos (VC) ou [[Cost Variance (CV)]]**
  - Mede o desempenho do custo do projeto.
  - **Fórmula:** `VC = VA - CR`
  - `VC > 0`: Abaixo do custo (bom ✅)
  - `VC < 0`: Acima do custo (ruim ❌)
  - `VC = 0`: No custo (ideal 🎯)

- **Variação de Prazos (VPz) ou [[Schedule Variance (SV)]]**
  - Mede o desempenho do cronograma, expresso em termos monetários.
  - **Fórmula:** `VPz = VA - VP`
  - `VPz > 0`: Adiantado (bom ✅)
  - `VPz < 0`: Atrasado (ruim ❌)
  - `VPz = 0`: No prazo (ideal 🎯)

---
## Análise de Índices (Eficiência)

Os índices medem a eficiência com que os recursos do projeto estão sendo utilizados.

- **Índice de Desempenho de Custos (IDC) ou [[Cost Performance Index (CPI)]]**
  - Mede a eficiência do uso dos recursos orçamentários.
  - **Fórmula:** `IDC = VA / CR`
  - `IDC > 1`: Eficiente (bom ✅)
  - `IDC < 1`: Ineficiente (ruim ❌)
  - `IDC = 1`: Perfeitamente eficiente (ideal 🎯)
  - *Dica:* Para cada R$ 1,00 gasto, estou gerando `R$ [IDC]` de valor.

- **Índice de Desempenho de Prazos (IDP) ou [[Schedule Performance Index (SPI)]]**
  - Mede a eficiência do progresso do cronograma.
  - **Fórmula:** `IDP = VA / VP`
  - `IDP > 1`: Progredindo mais rápido (bom ✅)
  - `IDP < 1`: Progredindo mais lentamente (ruim ❌)
  - `IDP = 1`: No ritmo planejado (ideal 🎯)

---
## Projeções e Estimativas para o Término (Forecasts)

Essas métricas preveem o resultado futuro do projeto com base no desempenho atual.

- **Orçamento no Término (ONT) ou [[Budget at Completion (BAC)]]**
  - O orçamento total original do projeto. É o valor de referência.

- **Estimativa para o Término (EPT) ou [[Estimate to Complete (ETC)]]**
  - O custo estimado para concluir o *restante* do trabalho.
  - **Fórmula comum:** `EPT = (ONT - VA) / IDC` (assume que a variação de custo atual continuará)

- **Estimativa no Término (ENT) ou [[Estimate at Completion (EAC)]]**
  - O custo total *previsto* do projeto ao final.
  - **Fórmula principal:** `ENT = ONT / IDC`
  - **Outras fórmulas:**
    - `ENT = CR + EPT` (Genérica)
    - `ENT = CR + (ONT - VA)` (Assume que o futuro seguirá o plano)

- **Variação no Término (VNT) ou [[Variance at Completion (VAC)]]**
  - A variação projetada do custo total ao final do projeto.
  - **Fórmula:** `VNT = ONT - ENT`
  - `VNT > 0`: Projeto terminará abaixo do orçamento (bom ✅)
  - `VNT < 0`: Projeto irá estourar o orçamento (ruim ❌)

---

> [!tip] Dica para Concursos
> As bancas adoram cenários onde você precisa **calcular e interpretar** esses valores. Memorize as fórmulas e, principalmente, o que cada resultado significa (bom/ruim, adiantado/atrasado, eficiente/ineficiente). Questões conceituais sobre a finalidade do GVA também são muito comuns.