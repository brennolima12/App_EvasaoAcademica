# 🎓 Previsão de Evasão Acadêmica com Redes Neurais

Este projeto tem como objetivo desenvolver uma ferramenta preditiva capaz de identificar, com base em dados acadêmicos, alunos com risco de evasão nos cursos de graduação em exatas. A solução combina inteligência artificial com visualizações interativas para apoiar decisões estratégicas por parte de coordenadores e professores.

Alunos:
Brenno Pinto Lapa Rego Lima
Franciele Silva De França
Larissa Xavier De Arruda
Lucas Romero Emilio Corrêa

## 📌 Objetivos

- Prever o risco de evasão de alunos com acurácia mínima de 80%.
- Classificar os alunos em níveis de risco: Baixo, Médio e Alto.
- Fornecer dashboards interativos para análise individual e coletiva.
- Apoiar intervenções pedagógicas baseadas em dados.

## 🧠 Tecnologias Utilizadas

| Componente         | Descrição                                 |
|--------------------|-------------------------------------------|
| `Python`           | Linguagem principal                       |
| `Scikit-Learn`     | Treinamento do modelo MLP                 |
| `Pandas / NumPy`   | Manipulação e análise de dados            |
| `Matplotlib / Seaborn / Plotly` | Visualização de dados       |
| `Streamlit`        | Interface web interativa                  |
| `Joblib`           | Serialização de modelos e objetos         |
| `ClickUp / Miro`   | Planejamento e colaboração (fora do código) |

## 🧪 Modelo Preditivo

- Tipo: Multi-Layer Perceptron (MLP)
- Features utilizadas:
  - Média de notas
  - Frequência
  - Slope das notas (tendência de desempenho)
  - Desvio padrão das notas
  - Total de semestres cursados
  - Taxa de aprovação
  - Quantidade de trancamentos
- Classificação de risco baseada em percentis:
  - **Baixo Risco**: ≤ 33º percentil
  - **Médio Risco**: 34º–66º percentil
  - **Alto Risco**: > 66º percentil


## 🚀 Como Executar

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/previsao-evasao.git
   cd previsao-evasao
   ```
2. Instale as dependências:
   ```
    pip install -r requirements.txt
    ```
3. Treine o modelo (opcional, se quiser re-treinar):
    ```
    python treinar_modelo.py
    ```
4. Execute a interface web:
    ```
    streamlit run app_streamlit.py
    ```
## 📊 Exemplo de Saída

- Probabilidade de evasão: 0.78
- Nível de risco: Alto
- Previsão: Evadiu (1)

## 🧩 Contribuições Futuras

- Integração com banco de dados real
- Inclusão de dados socioeconômicos
- Sistema de alertas automatizados
- Expansão para outros cursos e instituições

## 📄 Licença
Este projeto é de uso acadêmico e experimental. Para uso institucional ou comercial, entre em contato com os autores.
