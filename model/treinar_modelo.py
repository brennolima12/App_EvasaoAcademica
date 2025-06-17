# treinar_modelo.py
import joblib

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

# ========================
# 1. Carregar dados
# ========================
data = pd.read_csv(r"../dataset/base-sintetica-turma-4-corrigido-atualizada.csv")

# ========================
# 2. Calcular slope das notas
# ========================
grade_cols = [col for col in data.columns if col.startswith("nota_disciplina")]

def extrair_slope(row):
    notas = row[grade_cols].dropna().values
    if len(notas) < 2:
        return 0
    X = np.arange(len(notas)).reshape(-1, 1)
    y = notas
    model_lr = LinearRegression() # Renomeado para evitar conflito com 'model' global
    model_lr.fit(X, y)
    return model_lr.coef_[0]

data["slope_notas"] = data.apply(extrair_slope, axis=1)
data["std_notas"] = data[grade_cols].std(axis=1).fillna(0) # Calcula std_notas aqui

# ========================
# 3. Seleção de features
# ========================
features = ["total_semestres_cursados", "media_notas", "frequencia",
            "slope_notas", "qtd_trancamentos", "taxa_aprovacao", "std_notas"]
X = data[features].copy()
y = data["evadiu"]

# ========================
# 4. Normalização feature por feature
# ========================
scaler_dict = {}
for col in features:
    scaler = StandardScaler()
    X[[col]] = scaler.fit_transform(X[[col]])
    scaler_dict[col] = scaler # salva o scaler para cada coluna se quiser aplicar depois em novos dados

# ========================
# 5. Divisão treino/teste
# ========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ========================
# 6. Treinar MLP (com GridSearchCV para otimização)
# ========================
param_grid = {
    'hidden_layer_sizes': [(50, 30), (100,)],
    'activation': ['relu', 'tanh'],
    'solver': ['adam'],
    'alpha': [0.0001, 0.001],
    'max_iter': [500, 1000]
}

mlp = MLPClassifier(random_state=42)
grid_search = GridSearchCV(mlp, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
grid_search.fit(X_train, y_train) # Usar os dados reamostrados

print(f"\nMelhores parâmetros encontrados: {grid_search.best_params_}")
print(f"Melhor score (ROC AUC) no treino: {grid_search.best_score_:.2f}")

model = grid_search.best_estimator_ # O melhor modelo treinado

# ====================================================================
# NOVO: Calcular Limiares de Risco Baseados em Percentil
# ====================================================================
# Obter as probabilidades de evasão para os dados de TREINO
y_prob_train = model.predict_proba(X_train)[:, 1]

# Definir os percentis para os limiares
# Exemplo: 33% para baixo risco, 33% para médio, 34% para alto
# Você pode ajustar esses valores!
percentil_baixo_risco = 33
percentil_medio_risco = 66

# Calcular os limiares de probabilidade baseados nos percentis do treino
threshold_baixo_risco_percentil = np.percentile(y_prob_train, percentil_baixo_risco)
threshold_medio_risco_percentil = np.percentile(y_prob_train, percentil_medio_risco)

print("\nLimiares de Risco (baseados nos percentis do treino):")
print(f"  Baixo Risco (prob <= {percentil_baixo_risco}º percentil): <= {threshold_baixo_risco_percentil:.4f}")
print(f"  Médio Risco ({percentil_baixo_risco}º < prob <= {percentil_medio_risco}º percentil): > {threshold_baixo_risco_percentil:.4f} e <= {threshold_medio_risco_percentil:.4f}")
print(f"  Alto Risco (prob > {percentil_medio_risco}º percentil): > {threshold_medio_risco_percentil:.4f}")


# ========================
# 7. Previsões e avaliação (usando os dados de teste originais)
# ========================
y_prob_test = model.predict_proba(X_test)[:, 1]
# Usar o threshold de 0.4 para a previsão binária de evasão (ou ajuste se quiser usar percentil aqui também)
threshold_binary_prediction = threshold_medio_risco_percentil
y_pred_test = (y_prob_test >= threshold_binary_prediction).astype(int)

print("\n--- Avaliação do Modelo nos Dados de Teste ---")
print(f"Acurácia: {accuracy_score(y_test, y_pred_test):.2f}")
print(f"ROC AUC: {roc_auc_score(y_test, y_prob_test):.2f}")
print("Relatório de Classificação:")
print(classification_report(y_test, y_pred_test, target_names=["Não Evadiu", "Evadiu"]))

# --- Função para Classificar Risco (AGORA USANDO PERCENTIS) ---
def classify_risk_percentile(prob, th_baixo, th_medio):
    if prob <= th_baixo:
        return "Baixo Risco"
    elif prob <= th_medio:
        return "Médio Risco"
    else:
        return "Alto Risco"

# --- FUNÇÃO: Processar e Prever Evasão para Novos Alunos ---
def process_and_predict_evasion(new_student_data_list, trained_model, feature_list, grade_columns, scalers_dict,
                                 th_baixo_percentil, th_medio_percentil, threshold_binary_prediction=0.4):
    """
    Processa dados de novos alunos, prevê a probabilidade de evasão e gera visualizações.

    Args:
        new_student_data_list (list): Uma lista de dicionários, onde cada dicionário representa um aluno.
        trained_model (sklearn.neural_network.MLPClassifier): O modelo MLPClassifier já treinado.
        feature_list (list): Lista das colunas de features que o modelo espera.
        grade_columns (list): Lista das colunas que contêm as notas das disciplinas.
        scalers_dict (dict): Dicionário de objetos StandardScaler, um para cada feature.
        th_baixo_percentil (float): Limiar de probabilidade para Baixo Risco (calculado a partir do treino).
        th_medio_percentil (float): Limiar de probabilidade para Médio Risco (calculado a partir do treino).
        threshold_binary_prediction (float): O limiar para a previsão binária (Evadiu/Não Evadiu).

    Returns:
        pd.DataFrame: Um DataFrame com as probabilidades de evasão e níveis de risco para cada aluno.
    """
    new_students_df = pd.DataFrame(new_student_data_list)

    # 1. Calcular slope_notas para os novos alunos
    def extrair_slope_single_student(row):
        notas = [row[col] for col in grade_columns if col in row and pd.notna(row[col])]
        if len(notas) < 2:
            return 0
        X_new = np.arange(len(notas)).reshape(-1, 1)
        y_new = np.array(notas)
        model_lr = LinearRegression()
        model_lr.fit(X_new, y_new)
        return model_lr.coef_[0]

    new_students_df["slope_notas"] = new_students_df.apply(extrair_slope_single_student, axis=1)

    # 2. Calcular std_notas para os novos alunos
    present_grade_cols_in_new_data = [col for col in grade_columns if col in new_students_df.columns]
    if present_grade_cols_in_new_data:
        new_students_df["std_notas"] = new_students_df[present_grade_cols_in_new_data].std(axis=1).fillna(0)
    else:
        new_students_df["std_notas"] = 0 # Default if no grade columns are present

    # 3. Selecionar apenas as features que o modelo espera
    X_new_processed = new_students_df[feature_list].copy()

    # 4. Aplicar a mesma normalização (usando os scalers pré-ajustados)
    for col in feature_list:
        if col in scalers_dict:
            X_new_processed[[col]] = scalers_dict[col].transform(X_new_processed[[col]])
        else:
            print(f"Aviso: Scaler não encontrado para a feature '{col}'. Pulando a normalização para esta feature.")

    # 5. Fazer as previsões
    y_prob_new = trained_model.predict_proba(X_new_processed)[:, 1]
    y_pred_new = (y_prob_new >= threshold_binary_prediction).astype(int) # Usando o threshold binário para a classificação 0/1

    # 6. Classificar níveis de risco USANDO OS LIMIARES DE PERCENTIL
    risk_levels_new = [classify_risk_percentile(p, th_baixo_percentil, th_medio_percentil) for p in y_prob_new]

    risk_df_new = pd.DataFrame({
        "ID Aluno": new_students_df["id_aluno"],
        "Probabilidade": y_prob_new,
        "Nível de Risco": risk_levels_new,
        "Previsão Evasão (0/1)": y_pred_new
    })

    return risk_df_new

# Salvar os objetos necessários
joblib.dump(model, "modelo_mlp.pkl")
joblib.dump(scaler_dict, "scalers.pkl")
joblib.dump((threshold_baixo_risco_percentil, threshold_medio_risco_percentil), "limiares_risco.pkl")
joblib.dump(features, "features.pkl")
joblib.dump(grade_cols, "grade_cols.pkl")
