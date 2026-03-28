app.py
import streamlit as st
from utils import extrair_texto_pdf
from avaliador import avaliar_projeto

st.set_page_config(page_title="Avaliador de Projetos", layout="wide")

st.title("🤖 Avaliador de Projetos de Extensão")
st.write("Baseado no Edital PRX 25/2025")

opcao = st.radio("Escolha o tipo de entrada:", ["Texto", "PDF"])

texto_projeto = ""

if opcao == "Texto":
    texto_projeto = st.text_area("Cole o texto do projeto aqui:", height=300)

elif opcao == "PDF":
    arquivo = st.file_uploader("Envie o PDF do projeto", type=["pdf"])
    if arquivo:
        texto_projeto = extrair_texto_pdf(arquivo)
        st.success("Texto extraído com sucesso!")

if st.button("🚀 Avaliar Projeto"):
    if not texto_projeto:
        st.warning("Insira um projeto para avaliação.")
    else:
        with st.spinner("Avaliando..."):
            resultado = avaliar_projeto(texto_projeto)

        st.subheader("📊 Resultado")

        st.metric("Nota Final", f"{resultado['nota_total']} / 140")

        st.write("### 📌 Critérios")
        for criterio, dados in resultado["criterios"].items():
            st.write(f"**{criterio.capitalize()}**: {dados['nota']}")
            st.write(f"Comentário: {dados['comentario']}")

        st.write("### ⚠️ Eliminatórios")
        st.write(f"ODS: {'✔️' if resultado['ods'] else '❌'}")
        st.write(f"Ações de extensão: {'✔️' if resultado['acoes'] else '❌'}")

        st.write("### ✅ Status Final")
        st.success("APROVADO" if resultado["aprovado"] else "REPROVADO")