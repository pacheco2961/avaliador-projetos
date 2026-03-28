import re

def identificar_ods(texto):
    texto = texto.lower()
    ods_encontrados = set()

    # 1. padrões diretos: "ods 4", "ods-4"
    matches = re.findall(r"ods[\s\-]*(\d{1,2})", texto)
    for m in matches:
        n = int(m)
        if 1 <= n <= 17:
            ods_encontrados.add(n)

    # 2. padrão completo: "objetivo(s) de desenvolvimento sustentável"
    if "objetivo de desenvolvimento sustentável" in texto or \
       "objetivos de desenvolvimento sustentável" in texto:

        # tenta capturar número próximo
        matches = re.findall(r"(?:objetivo[s]? de desenvolvimento sustentável.*?)(\d{1,2})", texto)
        for m in matches:
            n = int(m)
            if 1 <= n <= 17:
                ods_encontrados.add(n)

    # 3. padrão textual mais solto (caso comum)
    matches = re.findall(r"desenvolvimento sustentável.*?(\d{1,2})", texto)
    for m in matches:
        n = int(m)
        if 1 <= n <= 17:
            ods_encontrados.add(n)

    return sorted(list(ods_encontrados))


def detectar_ods(texto):
    return len(identificar_ods(texto)) > 0

# -----------------------------
# AÇÕES
# -----------------------------
def detectar_acoes(texto):
    texto = texto.lower()
    palavras = ["oficina", "evento", "ação", "atividade", "sequência didática"]
    return sum(texto.count(p) for p in palavras) >= 2


# -----------------------------
# PONTUAÇÃO
# -----------------------------
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

    texto += "1. Análise por Critérios\n\n"
    for c, d in resultado["criterios"].items():
        texto += f"- {c.capitalize()}: Nota {d['nota']}\n"

    texto += "\n2. Critérios Eliminatórios\n\n"

    if resultado["ods"]:
        ods_str = ", ".join([f"ODS {i}" for i in resultado["ods_lista"]])
        texto += f"Relação com ODS: Atendido ({ods_str})\n"
    else:
        texto += "Relação com ODS: Não atendido\n"

    texto += f"Ações de extensão: {'Atendido' if resultado['acoes'] else 'Não atendido'}\n"

    texto += "\n3. Resultado Final\n\n"
    texto += f"Pontuação total: {resultado['nota_total']} / 140\n"
    texto += f"Situação: {'APROVADO' if resultado['aprovado'] else 'REPROVADO'}\n"

    texto += "\n4. Considerações Finais\n\n"
    texto += "O projeto apresenta consistência e potencial de impacto acadêmico e social.\n"

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

    ods_lista = identificar_ods(texto)
    ods = len(ods_lista) > 0
    acoes = detectar_acoes(texto)

    nota_total = sum(c["nota"] for c in criterios.values())

    resultado = {
        "nota_total": nota_total,
        "criterios": criterios,
        "ods": ods,
        "ods_lista": ods_lista,
        "acoes": acoes,
        "aprovado": ods and acoes
    }

    resultado["parecer"] = gerar_parecer(resultado)

    return resultado

