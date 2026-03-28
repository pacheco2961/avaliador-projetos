import pdfplumber

def extrair_texto_pdf(arquivo):
    texto = ""

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += conteudo + "\n"

    texto = texto.replace("\n\n", "\n")
    texto = texto.replace("  ", " ")

    return texto
