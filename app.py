import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Time Jorge Nascimento",
    layout="wide"
)

# ===============================
# ESTILO - FUNDO AZUL ESCURO + RODAPÉ FIXO
# ===============================
st.markdown("""
<style>
    body {
        background-color: #0A2647 !important;
        color: white !important;
    }
    .main {
        background-color: #0A2647 !important;
    }
    h1,h2,h3,h4,label,span,p,div {
        color: white !important;
    }
    .stDataFrame tbody tr td {
        color: white !important;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0A2647;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        border-top: 1px solid #1E3A8A;
        z-index: 9999;
    }
    .block-container {
        padding-bottom: 60px !important;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# LOGO
# ===============================
logo_path = "logo.png"
if Path(logo_path).exists():
    st.image(logo_path, width=250)
else:
    st.warning("⚠️ Logo não encontrada. Adicione logo.png na pasta.")

st.title("🎓 Time Jorge Nascimento")

# ===============================
# PLANILHAS
# ===============================
efetivo_path = "efetivo.xlsx"
ho_path = "homeoffice.xlsx"
monitores_path = "monitores.xlsx"

df_efetivo = pd.read_excel(efetivo_path)

# Home Office
try:
    df_ho = pd.read_excel(ho_path)
except:
    df_ho = pd.DataFrame(columns=["Data", "Nome", "Líder", "Status", "Observação"])
    df_ho.to_excel(ho_path, index=False)

if df_ho.empty:
    df_ho = pd.DataFrame(columns=["Data", "Nome", "Líder", "Status", "Observação"])

# Monitores
try:
    df_monitores = pd.read_excel(monitores_path)
except:
    df_monitores = pd.DataFrame(columns=["Modelo", "Sala", "Data de instalação", "Data de retirada"])
    df_monitores.to_excel(monitores_path, index=False)

# ===============================
# MENU LATERAL
# ===============================
menu = st.sidebar.radio("📌 Navegação", ["Efetivo", "Home Office", "Monitores"])

# ===============================
# ABA 1 – EFETIVO
# ===============================
if menu == "Efetivo":
    st.header("👥 Consulta de Efetivo")
    colf1, colf2 = st.columns(2)

    filtro_nome = colf1.text_input("Buscar por nome")
    try:
        lista_lideres = ["Todos"] + sorted(df_efetivo.iloc[:, 1].unique())
    except:
        lista_lideres = ["Todos"]

    filtro_lider = colf2.selectbox("Filtrar por líder", lista_lideres)
    df_display = df_efetivo.copy()

    if filtro_nome:
        df_display = df_display[df_display.iloc[:, 0].str.contains(filtro_nome, case=False)]
    if filtro_lider != "Todos":
        df_display = df_display[df_display.iloc[:, 1] == filtro_lider]

    st.subheader(f"Total encontrado: {len(df_display)} colaboradores")
    st.dataframe(df_display, use_container_width=True)

# ===============================
# ABA 2 – HOME OFFICE
# ===============================
elif menu == "Home Office":
    st.header("🏡 Monitoramento de Home Office")
    st.write("📅 Cadastre e visualize os dias de trabalho remoto do time.")

    colaboradores = df_efetivo.iloc[:, 0].unique()

    with st.form("form_ho"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data", datetime.today())
        colaborador = col1.selectbox("Colaborador", colaboradores)
        try:
            lider = df_efetivo.loc[df_efetivo.iloc[:, 0] == colaborador].iloc[:, 1].values[0]
        except:
            lider = "Não encontrado"

        col2.write("**Líder:**")
        col2.info(lider)

        status = col2.selectbox("Situação", ["Home Office", "Presencial", "Folga", "Atividade Externa"])
        observacao = st.text_area("Observação (opcional)")
        salvar = st.form_submit_button("Salvar Registro ✅")

    if salvar:
        novo = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"),
            "Nome": colaborador,
            "Líder": lider,
            "Status": status,
            "Observação": observacao
        }])
        df_ho = pd.concat([df_ho, novo], ignore_index=True)
        df_ho.to_excel(ho_path, index=False)
        st.success("Registro salvo com sucesso!")

    st.subheader("📂 Registros de Home Office")
    colf1, colf2, colf3 = st.columns(3)
    filtro_nome = colf1.selectbox("Filtrar por colaborador", ["Todos"] + list(colaboradores))
    filtro_status = colf2.selectbox("Filtrar por status", ["Todos", "Home Office", "Presencial", "Folga", "Atividade Externa"])
    filtro_data = colf3.text_input("Filtrar por data (DD/MM/AAAA)")

    df_display = df_ho.copy()
    if filtro_nome != "Todos":
        df_display = df_display[df_display["Nome"] == filtro_nome]
    if filtro_status != "Todos":
        df_display = df_display[df_display["Status"] == filtro_status]
    if filtro_data:
        df_display = df_display[df_display["Data"].astype(str) == filtro_data]

    st.dataframe(df_display, use_container_width=True)

    if not df_display.empty:
        st.subheader("📊 Quantitativo de Registros por Status")
        grafico = df_display["Status"].value_counts().reset_index()
        grafico.columns = ["Status", "Quantidade"]
        fig = px.pie(grafico, values="Quantidade", names="Status", title="Distribuição por Status")
        fig.update_layout(title_x=0.3, font_color="white", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado para gerar o gráfico.")

# ===============================
# ABA 3 – MONITORES
# ===============================
elif menu == "Monitores":
    st.header("🖥️ Controle de Monitores")
    st.write("📦 Cadastre e acompanhe o estoque de monitores instalados e retirados.")

    with st.form("form_monitores"):
        col1, col2 = st.columns(2)
        modelo = col1.text_input("Modelo do Monitor")
        sala = col2.text_input("Sala ou Local")
        data_inst = col1.date_input("Data de instalação", datetime.today())
        data_ret = col2.date_input("Data de retirada (opcional)", None)
        salvar_monitor = st.form_submit_button("Salvar Registro ✅")

    if salvar_monitor:
        novo = pd.DataFrame([{
            "Modelo": modelo,
            "Sala": sala,
            "Data de instalação": data_inst.strftime("%d/%m/%Y"),
            "Data de retirada": data_ret.strftime("%d/%m/%Y") if data_ret else ""
        }])
        df_monitores = pd.concat([df_monitores, novo], ignore_index=True)
        df_monitores.to_excel(monitores_path, index=False)
        st.success("Registro de monitor salvo com sucesso!")

    st.subheader("📋 Registros de Monitores")
    filtro_sala = st.selectbox("Filtrar por sala", ["Todas"] + sorted(df_monitores["Sala"].dropna().unique()))
    df_display = df_monitores.copy()
    if filtro_sala != "Todas":
        df_display = df_display[df_display["Sala"] == filtro_sala]
    st.dataframe(df_display, use_container_width=True)

    if not df_display.empty:
        st.subheader("📊 Distribuição de Monitores por Sala")
        grafico = df_display["Sala"].value_counts().reset_index()
        grafico.columns = ["Sala", "Quantidade"]
        fig = px.pie(grafico, values="Quantidade", names="Sala", title="Monitores por Sala")
        fig.update_layout(title_x=0.3, font_color="white", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# RODAPÉ FIXO
# ===============================
st.markdown("""
<div class="footer">
    Desenvolvido por Nathalia Brum © 2025 | Time Jorge Nascimento
</div>
""", unsafe_allow_html=True)
