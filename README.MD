# 📈 Cubic Splines — Interpolação por Spline Cúbica Natural

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-success.svg)](https://github.com/Giovanny29/Cubic_Splines)

Projeto desenvolvido para a disciplina de **Álgebra Linear Aplicada** com foco em:

- Interpolação por **Splines Cúbicas Naturais**
- Simulação de **aritmética de precisão finita**
- Comparação entre métodos iterativos
- Visualização gráfica da convergência e interpolação

O sistema permite ao usuário selecionar pontos em um plano cartesiano interativo e gerar a spline cúbica correspondente utilizando métodos numéricos executados sob uma máquina finita simulada.

---

# 🧠 Conceitos Implementados

| Área | Conteúdo |
|---|---|
| **Interpolação** | Splines Cúbicas Naturais |
| **Métodos Iterativos** | Jacobi e Gauss-Seidel |
| **Álgebra Linear** | Sistemas tridiagonais |
| **Aritmética Finita** | Base, mantissa, arredondamento e truncamento |
| **Análise Numérica** | Propagação de erro, overflow e underflow |
| **Visualização** | Plano cartesiano interativo com reconstrução gráfica |

---

# 📂 Estrutura do Projeto

```bash
Cubic_Splines/
├── main.py                 # Inicialização da aplicação
│
├── ui/                     # Interface gráfica
│   ├── canvas.py           # Plano cartesiano interativo
│   └── controls.py         # Controles da interface
│
├── spline/                 # Núcleo matemático da spline
│   ├── system_generator.py # Montagem do sistema linear
│   ├── spline_builder.py   # Construção dos coeficientes
│   └── spline_segment.py   # Representação de cada intervalo
│
├── numerical/              # Métodos numéricos
│   ├── machine.py          # Máquina de precisão finita
│   ├── jacobi.py           # Método de Jacobi
│   ├── gauss_seidel.py     # Método de Gauss-Seidel
│   └── norms.py            # Normas e cálculo de erro
│
├── models/
│   └── point.py            # Estrutura de ponto 2D
│
└── utils/
```

---

# 🔢 Fundamentação Matemática

## Máquina de Precisão Finita

A simulação utiliza o modelo:

:contentReference[oaicite:0]{index=0}

Onde:

- $\beta$ → base numérica
- $t$ → tamanho da mantissa
- $L$ → menor expoente
- $U$ → maior expoente

Toda operação aritmética passa pelo processo de:

- normalização
- arredondamento/truncamento
- limitação de expoentes

permitindo observar os efeitos reais da computação numérica finita.

---

## Métodos Iterativos

### Método de Jacobi

:contentReference[oaicite:1]{index=1}

---

### Método de Gauss-Seidel

:contentReference[oaicite:2]{index=2}

---

## Spline Cúbica Natural

Cada segmento da spline é definido por:

:contentReference[oaicite:3]{index=3}

O sistema linear gerado garante:

- Continuidade da função
- Continuidade da primeira derivada
- Continuidade da segunda derivada
- Condições naturais:

:contentReference[oaicite:4]{index=4}

---

# 🖥️ Funcionalidades

- Seleção de pontos via mouse
- Construção automática da spline
- Comparação entre Jacobi e Gauss-Seidel
- Simulação de máquina finita configurável
- Visualização gráfica da curva interpolada
- Exibição de erro numérico
- Reconstrução dinâmica da spline

---

# 🚀 Como Executar

## 1. Clone o repositório

```bash
git clone https://github.com/Giovanny29/Cubic_Splines.git
```

---

## 2. Acesse a pasta do projeto

```bash
cd Cubic_Splines
```

---

## 3. Execute a aplicação

```bash
python main.py
```

---

# 📈 Status do Projeto

- [x] Interface gráfica interativa
- [x] Sistema de spline cúbica natural
- [x] Métodos iterativos
- [x] Máquina de precisão finita
- [x] Visualização da interpolação
- [x] Controle de erro numérico
- [ ] Exportação de resultados
- [ ] Relatórios automáticos de convergência

---

# 📚 Objetivo Acadêmico

Este projeto foi desenvolvido com fins educacionais para demonstrar conceitos de:

- Álgebra Linear Aplicada
- Métodos Numéricos
- Interpolação
- Computação Numérica
- Estabilidade Numérica

---
