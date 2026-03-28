import streamlit as st
from openai import OpenAI
import json
import re

import streamlit as st

if "OPENAI_API_KEY" not in st.secrets:
    raise ValueError("❌ API Key não encontrada. Configure em Settings → Secrets")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

CRITERIOS = [
    "coerencia",
    "protagonismo estudantil",
    "participação da sociedade",
    "justificativa",
    "objetivos",
    "metodologia",
    "acompanhamento e avaliação",
    "resultados e produtos"
]

ESCALA = [0, 5, 10, 15]


# -----------------------------
# EXTRAÇÃO SEGURA DE JSON
# -----------------------------
def extrair_json(texto):
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        return json.loads(match.group())
    return None


# -----------------------------
# REGRAS DETERMINÍSTICAS
# -----------------------------
def detectar_ods(texto):
    texto = texto.lower()
    return any(p in texto for p in [
        "ods", "agenda 2030", "desenvolvimento sustentável"
    ])


def detectar_acoes(texto):
    texto = texto.lower()
    palavras = ["oficina", "evento", "ação", "projeto", "atividade"]
    contagem = sum(texto.count(p) for p in palavras)
    return contagem >= 2


def normalizar_nota(nota):
    return min(ESCALA, key=lambda x: abs(x - nota))


# -----------------------------
# AVALIAÇÃO PRINCIPAL
# -----------------------------
def avaliar_projeto(texto):

    prompt = f"""
    Você é um avaliador institucional do IFSP.

    Avalie o projeto conforme o edital PRX 25/2025.

    REGRAS:
    - Use SOMENTE notas: 0, 5, 10 ou 15
    - Seja técnico e objetivo
    - Retorne JSON válido

    CRITÉRIOS:
    {CRITERIOS}

    FORMATO:

    {{
    "criterios": {{
        "coerencia": {{"nota": 10, "comentario": ""}},
        "protagonismo estudantil": {{"nota": 10, "comentario": ""}},
        "participação da sociedade": {{"nota": 10, "comentario": ""}},
        "justificativa": {{"nota": 10, "comentario": ""}},
        "objetivos": {{"nota": 10, "comentario": ""}},
        "metodologia": {{"nota": 10, "comentario": ""}},
        "acompanhamento e avaliação": {{"nota": 10, "comentario": ""}},
        "resultados e produtos": {{"nota": 10, "comentario": ""}}
    }}
    }}

    PROJETO:
    {texto}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        conteudo = response.choices[0].message.content
        resultado = extrair_json(conteudo)

        if not resultado:
            raise ValueError("JSON inválido")

        # -----------------------------
        # NORMALIZAÇÃO DAS NOTAS
        # -----------------------------
        for c in resultado["criterios"]:
            nota = resultado["criterios"][c]["nota"]
            resultado["criterios"][c]["nota"] = normalizar_nota(nota)

        # -----------------------------
        # REGRAS FIXAS (EDITAL)
        # -----------------------------
        ods = detectar_ods(texto)
        acoes = detectar_acoes(texto)

        nota_total = sum(c["nota"] for c in resultado["criterios"].values())

        return {
            "nota_total": nota_total,
            "criterios": resultado["criterios"],
            "ods": ods,
            "acoes": acoes,
            "aprovado": ods and acoes
        }

    except Exception as e:
        return {
            "nota_total": 0,
            "criterios": {},
            "ods": False,
            "acoes": False,
            "aprovado": False,
            "erro": str(e)
        }
