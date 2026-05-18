```markdown
# 📈 Projeto ALA - Spline Cúbica & Máquina Finita

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-finalizando-success.svg)]()

Este projeto foi desenvolvido para a disciplina de **Álgebra Linear Aplicada**. O objetivo é demonstrar a interpolação por **Splines Cúbicas Naturais** e o impacto da **aritmética de precisão finita** na convergência de métodos iterativos.

---

## 📂 Estrutura do Projeto

```bash
project/
├── main.py                # Ponto de entrada (UI + Orquestração)
├── ui/                    # Interface Gráfica (Tkinter)
│   ├── canvas.py          # Plano Cartesiano Interativo
│   └── controls.py        # Sliders, botões e configurações
├── spline/                # Núcleo de Interpolação
│   ├── system_generator.py# Geração do sistema tridiagonal
│   ├── spline_builder.py  # Construção e reconstrução de coeficientes
│   └── spline_segment.py  # Representação matemática do intervalo
├── numerical/             # O "Coração" Numérico
│   ├── machine.py         # Simulação da Máquina F(b, t, k1, k2)
│   ├── jacobi.py          # Solver Iterativo Jacobi
│   ├── gauss_seidel.py    # Solver Iterativo Gauss-Seidel
│   └── norms.py           # Cálculo de Erros (Norma Infinito)
├── models/                # Estruturas de Dados
│   └── point.py           # Entidade Ponto(x, y)
└── utils/                 # Auxiliares
    └── constants.py       # Cores, tolerâncias e limites

```

---

## 🛠️ Temas Numéricos Implementados

| Categoria | Tópicos |
| --- | --- |
| **Aritmética** | Precisão da mantissa ($t$), Base ($\beta$), Arredondamento e Truncamento. |
| **Erros** | Overflow, Underflow, Erro de cancelamento e Propagação. |
| **Métodos** | Jacobi e Gauss-Seidel com aritmética estritamente finita. |
| **Interpolação** | Splines Cúbicas Naturais via Sistema Tridiagonal. |

---

## 🔢 Fundamentação Matemática

### 1. Máquina Finita

A simulação segue o padrão de ponto flutuante:


$$F(\beta, t, L, U)$$


Onde cada operação ($+$, $-$, $\times$, $\div$) é processada passando pelo filtro de normalização e arredondamento da máquina configurada.

### 2. Métodos Iterativos

O projeto permite comparar a convergência entre os métodos:

* **Jacobi:** 
$$x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j \neq i} a_{ij} x_j^{(k)} \right)$$


* **Gauss-Seidel:** 
$$x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j < i} a_{ij} x_j^{(k+1)} - \sum_{j > i} a_{ij} x_j^{(k)} \right)$$



### 3. Spline Cúbica Natural

A equação do segmento entre dois pontos $(x_i, y_i)$ e $(x_{i+1}, y_{i+1})$ é dada por:


$$S_i(x) = \frac{M_i(x_{i+1}-x)^3}{6h_i} + \frac{M_{i+1}(x-x_i)^3}{6h_i} + A(x_{i+1}-x) + B(x-x_i)$$

---

## 🚀 Como Executar

1. Certifique-se de ter o Python 3 instalado.
2. Clone o repositório:
```bash
git clone [https://github.com/seu-usuario/projeto-spline.git](https://github.com/seu-usuario/projeto-spline.git)

```


3. Execute a aplicação:
```bash
python main.py

```



---

## 📈 Status do Desenvolvimento

* [x] Simulação de Máquina Finita
* [x] Solvers Iterativos (Jacobi/Gauss-Seidel)
* [x] Sistema de Splines Naturais
* [x] Interface Gráfica Interativa
* [x] Visualização de Erro de Aproximação
* [ ] Exportação de dados para CSV
* [ ] Relatórios de Convergência Automáticos

---

**Desenvolvido como projeto acadêmico para fins de estudo de métodos numéricos.**
