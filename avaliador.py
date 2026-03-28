import streamlit as st
from openai import OpenAI
import json
import re

# Cliente OpenAI usando secrets do Streamlit Cloud
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

def extrair_json(texto):
    """
    Extrai o JSON mesmo que a resposta da IA venha com texto extra.
    """
    try:
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("JSON não encontrado")
    except Exception as e:
        return {
            "erro": str(e),
            "conteudo_bruto": texto
        }

def avaliar_projeto(texto):

    prompt = f"""
    Avalie o projeto abaixo com base nos critérios do edital PRX 25/2025.

    Para cada critério:
    - dê nota de 0 a 15
    - escreva um comentário curto

    Critérios:
    {CRITERIOS}

    Verifique também:
    - Se há menção a ODS (retorne true ou false)
    - Se há pelo menos duas ações de extensão (true ou false)

    Retorne SOMENTE em JSON no seguinte formato:

    {{
        "criterios": {{
            "coerencia": {{ "nota": int, "comentario": str }},
            "protagonismo estudantil": {{ "nota": int, "comentario": str }},
            "participação da sociedade": {{ "nota": int, "comentario": str }},
            "justificativa": {{ "nota": int, "comentario": str }},
            "objetivos": {{ "nota": int, "comentario": str }},
            "metodologia": {{ "nota": int, "comentario": str }},
            "acompanhamento e avaliação": {{ "nota": int, "comentario": str }},
            "resultados e produtos": {{ "nota": int, "comentario": str }}
        }},
        "ods": true,
        "acoes": true
    }}

    Projeto:
    {texto}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        conteudo = response.choices[0].message.content

        resultado = extrair_json(conteudo)

        # Verifica erro na extração
        if "erro" in resultado:
            return {
                "nota_total": 0,
                "criterios": {},
                "ods": False,
                "acoes": False,
                "aprovado": False,
                "erro": resultado["erro"],
                "resposta_bruta": resultado["conteudo_bruto"]
            }

        nota_total = sum([c["nota"] for c in resultado["criterios"].values()])

        return {
            "nota_total": nota_total,
            "criterios": resultado["criterios"],
            "ods": resultado["ods"],
            "acoes": resultado["acoes"],
            "aprovado": resultado["ods"] and resultado["acoes"]
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