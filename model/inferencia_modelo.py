import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression

# ======================
# Carregar os objetos salvos
# ======================
modelo = joblib.load("model/modelo_mlp.pkl")
scalers = joblib.load("model/scalers.pkl")
features = joblib.load("model/features.pkl")
grade_cols = joblib.load("model/grade_cols.pkl")
limiares = joblib.load("model/limiares_risco.pkl")
limiar_baixo, limiar_medio = limiares

# ======================
# Classificação por risco
# ======================
def classificar_risco(prob):
    if prob <= limiar_baixo:
        return "🟢 Baixo"
    elif prob <= limiar_medio:
        return "🟠 Médio"
    else:
        return "🔴 Alto"

# ======================
# Função principal
# ======================
def prever_risco_evasao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Garantir que colunas estejam presentes
    for col in features:
        if col not in df.columns:
            df[col] = 0

    # slope das notas
    def calcular_slope(row):
        notas = [row[col] for col in grade_cols if col in df.columns and pd.notna(row[col])]
        if len(notas) < 2:
            return 0
        X = np.arange(len(notas)).reshape(-1, 1)
        y = np.array(notas)
        model_lr = LinearRegression()
        model_lr.fit(X, y)
        return model_lr.coef_[0]
    df["slope_notas"] = df.apply(calcular_slope, axis=1)

    # std das notas
    #df["std_notas"] = df[grade_cols].std(axis=1).fillna(0)
    notas_disponiveis = [col for col in grade_cols if col in df.columns]
    df["std_notas"] = df[notas_disponiveis].std(axis=1).fillna(0)

    # Preencher colunas ausentes com 0
    for col in grade_cols:
        if col not in df.columns:
            df[col] = 0

    # Normalizar features
    df_proc = df[features].copy()
    for col in features:
        scaler = scalers.get(col)
        if scaler:
            df_proc[[col]] = scaler.transform(df_proc[[col]])

    # Prever
    prob = modelo.predict_proba(df_proc)[:, 1]
    df["Probabilidade"] = prob
    df["Nível de Risco"] = [classificar_risco(p) for p in prob]
    df["Previsão Evasão (0/1)"] = (prob >= limiar_medio).astype(int)

    return df
