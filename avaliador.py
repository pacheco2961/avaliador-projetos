import streamlit as st
import re

# IA opcional
try:
    from openai import OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None
except:
    client = None

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

# -----------------------------
# REGRAS
# -----------------------------
def detectar_ods(texto):
    texto = texto.lower()
    return any(p in texto for p in [
        "ods", "agenda 2030", "desenvolvimento sustentável"
    ])

def detectar_acoes(texto):
    texto = texto.lower()
    palavras = ["oficina", "evento", "ação", "atividade", "sequência didática"]
    return sum(texto.count(p) for p in palavras) >= 2

def pontuar(texto, criterio):
    texto = texto.lower()

    regras = {
        "coerencia": 10 if "objetivo" in texto else 5,
        "protagonismo estudantil": 15 if "estudantes" in texto else 5,
        "participação da sociedade": 15 if "escola" in texto else 5,
        "justificativa": 10 if "justificativa" in texto else 5,
        "objetivos": 15 if "objetivo geral" in texto else 10,
        "metodologia": 15 if "etapa" in texto else 10,
        "acompanhamento e avaliação": 10 if "avaliação" in texto else 5,
        "resultados e produtos": 10 if "resultados" in texto else 5
    }

    return regras.get(criterio, 5)

# -----------------------------
# PARECER
# -----------------------------
def gerar_parecer(resultado):
    texto = "PARECER TÉCNICO DE AVALIAÇÃO DE PROJETO DE EXTENSÃO\n\n"

    for c, d in resultado["criterios"].items():
        texto += f"{c.capitalize()}: Nota {d['nota']}\n"

    texto += f"\nODS: {'Atendido' if resultado['ods'] else 'Não atendido'}"
    texto += f"\nAções: {'Atendido' if resultado['acoes'] else 'Não atendido'}"
    texto += f"\n\nNota final: {resultado['nota_total']} / 140"
    texto += f"\nSituação: {'APROVADO' if resultado['aprovado'] else 'REPROVADO'}"

    return texto

# -----------------------------
# PRINCIPAL
# -----------------------------
def avaliar_projeto(texto):

    criterios = {}
    for c in CRITERIOS:
        criterios[c] = {
            "nota": pontuar(texto, c),
            "comentario": "Avaliação baseada em regras estruturais."
        }

    ods = detectar_ods(texto)
    acoes = detectar_acoes(texto)

    nota_total = sum(c["nota"] for c in criterios.values())

    resultado = {
        "nota_total": nota_total,
        "criterios": criterios,
        "ods": ods,
        "acoes": acoes,
        "aprovado": ods and acoes
    }

    resultado["parecer"] = gerar_parecer(resultado)

    return resultado
