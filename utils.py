import pdfplumber

def extrair_texto_pdf(arquivo):
    texto = ""
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto