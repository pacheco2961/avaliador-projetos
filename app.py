import streamlit as st
from utils import extrair_texto_pdf
from avaliador import avaliar_projeto

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import io

# -----------------------------
# PDF
# -----------------------------
def gerar_pdf_parecer(texto_parecer):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("<b>PARECER TÉCNICO DE AVALIAÇÃO</b>", styles["Title"]))
    elementos.append(Spacer(1, 12))

    for linha in texto_parecer.split("\n"):
        elementos.append(Paragraph(linha, styles["Normal"]))
        elementos.append(Spacer(1, 8))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

# -----------------------------
# APP
# -----------------------------
st.set_page_config(page_title="Avaliador", layout="wide")

st.title("🤖 Avaliador de Projetos")

opcao = st.radio("Entrada:", ["Texto", "PDF"])

texto_projeto = ""

if opcao == "Texto":
    texto_projeto = st.text_area("Cole o projeto", height=300)

else:
    arquivo = st.file_uploader("Envie PDF", type=["pdf"])
    if arquivo:
        texto_projeto = extrair_texto_pdf(arquivo)
        st.success("PDF carregado")

# -----------------------------
# EXECUÇÃO
# -----------------------------
if st.button("🚀 Avaliar Projeto"):
    if not texto_projeto:
        st.warning("Insira um projeto")
    else:
        resultado = avaliar_projeto(texto_projeto)

        st.subheader("📊 Resultado")
        st.metric("Nota", f"{resultado['nota_total']} / 140")

        for c, d in resultado["criterios"].items():
            st.write(f"{c}: {d['nota']}")

        st.write("ODS:", "✔️" if resultado["ods"] else "❌")

        if resultado["ods"]:
            st.write("ODS detectados:", resultado["ods_lista"])

        st.write("Ações:", "✔️" if resultado["acoes"] else "❌")

        st.success("APROVADO" if resultado["aprovado"] else "REPROVADO")

        # -----------------------------
        # PARECER
        # -----------------------------
        st.write("### 📄 Parecer Técnico")

        parecer = resultado["parecer"]

        st.text_area("Parecer", parecer, height=300)

        pdf = gerar_pdf_parecer(parecer)

        st.download_button(
            "📥 Baixar PDF",
            pdf,
            file_name="parecer.pdf",
            mime="application/pdf"
        )
