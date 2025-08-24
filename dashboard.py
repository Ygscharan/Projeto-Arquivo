import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import func, distinct, cast, Date
import datetime
from PIL import Image
import base64
import os
import signal

from database.db import session
from repository.CaixaRepository import CaixaRepository
from repository.DocumentoRepository import DocumentoRepository
from repository.UnidadeRepository import UnidadeRepository
from repository.MovimentacaoRepository import MovimentacaoRepository
from repository.UsuarioRepository import UsuarioRepository
from models.models import Caixa, Documento, Unidade, Movimentacao, Usuario

st.set_page_config(
    page_title="Dashboard - Projeto Arquivo",
    page_icon="📦",
    layout="wide"
)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig', sep=';')

try:
    repo_caixa = CaixaRepository()
    repo_documento = DocumentoRepository()
    repo_unidade = UnidadeRepository()
    repo_movimentacao = MovimentacaoRepository()
    repo_usuario = UsuarioRepository()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    st.info("Verifique as credenciais no .env e se o banco Oracle está em execução.")
    st.stop()

try:
    banner_image = Image.open('Logo_da_Coamo.svg.png')
    st.image(banner_image, use_column_width=True)
except FileNotFoundError:
    st.warning("Arquivo 'Logo_da_Coamo.svg.png' não encontrado. Por favor, adicione uma imagem com este nome na pasta do projeto.")

st.sidebar.header("Navegação")
if st.sidebar.button("⬅️ Voltar ao Console"):
    st.info("Fechando o dashboard...")
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)

st.title("📦 Dashboard de Gestão de Arquivo")
st.markdown("##")

total_caixas = session.query(func.count(Caixa.id)).scalar()
total_documentos = session.query(func.count(Documento.id)).scalar()
total_unidades = session.query(func.count(Unidade.id)).scalar()
total_movimentacoes = session.query(func.count(Movimentacao.id)).scalar()

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="**Total de Caixas** 📦", value=total_caixas)
with col2: st.metric(label="**Total de Documentos** 📄", value=total_documentos)
with col3: st.metric(label="**Total de Unidades** 🏢", value=total_unidades)
with col4: st.metric(label="**Total de Movimentações** 🚚", value=total_movimentacoes)

st.markdown("---")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Caixas por Tipo de Documento")
    with st.expander("Filtrar por Período"):
        start_date_c1 = st.date_input("Data de Início", value=datetime.date(2015, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="c1_start")
        end_date_c1 = st.date_input("Data de Fim", value=datetime.date.today(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="c1_end")

    if start_date_c1 > end_date_c1:
        st.error("Erro: A data de início não pode ser posterior à data de fim.")
    else:
        end_date_c1_adj = datetime.datetime.combine(end_date_c1, datetime.time.max)
        query_c1 = (
            session.query(Documento.tipo, func.count(distinct(Caixa.id)).label('quantidade'))
            .join(Documento.caixas).filter(Caixa.data_criacao.between(start_date_c1, end_date_c1_adj))
            .group_by(Documento.tipo).all()
        )
        if query_c1:
            df_c1 = pd.DataFrame(query_c1, columns=['Tipo de Documento', 'Número de Caixas'])
            tipo_grafico_c1 = st.radio("Tipo de gráfico:", options=["Gráfico de Pizza", "Gráfico de Barras"], key='tipo_grafico_c1', horizontal=True)
            if tipo_grafico_c1 == "Gráfico de Pizza":
                fig1 = px.pie(df_c1, names='Tipo de Documento', values='Número de Caixas', hole=.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig1.update_traces(textinfo='percent+label', textfont_size=14); st.plotly_chart(fig1, use_container_width=True)
            else:
                fig1 = px.bar(df_c1, x='Tipo de Documento', y='Número de Caixas', text_auto=True, template='plotly_white', color='Tipo de Documento')
                fig1.update_layout(showlegend=False); fig1.update_traces(textposition='outside'); st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado para o período selecionado.")

with col_graf2:
    st.subheader("Caixas por Unidade")
    with st.expander("Filtrar por Período"):
        start_date_c2 = st.date_input("Data de Início", value=datetime.date(2015, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="c2_start")
        end_date_c2 = st.date_input("Data de Fim", value=datetime.date.today(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="c2_end")

    if start_date_c2 > end_date_c2:
        st.error("Erro: A data de início não pode ser posterior à data de fim.")
    else:
        end_date_c2_adj = datetime.datetime.combine(end_date_c2, datetime.time.max)
        query_c2 = (
            session.query(Unidade.nome, func.count(Caixa.id).label('quantidade'))
            .join(Unidade, Caixa.unidade_id == Unidade.id)
            .filter(Caixa.data_criacao.between(start_date_c2, end_date_c2_adj))
            .group_by(Unidade.nome).all()
        )
        if query_c2:
            df_c2 = pd.DataFrame(query_c2, columns=['Unidade', 'Quantidade de Caixas'])
            tipo_grafico_c2 = st.radio("Tipo de gráfico:", options=["Gráfico de Barras", "Gráfico de Pizza"], key='tipo_grafico_c2', horizontal=True)
            if tipo_grafico_c2 == "Gráfico de Barras":
                fig2 = px.bar(df_c2, x='Unidade', y='Quantidade de Caixas', text_auto=True, template='plotly_white', color='Unidade')
                fig2.update_layout(showlegend=False); fig2.update_traces(textposition='outside'); st.plotly_chart(fig2, use_container_width=True)
            else:
                fig2 = px.pie(df_c2, names='Unidade', values='Quantidade de Caixas', hole=.4)
                fig2.update_traces(textinfo='percent+label', textfont_size=14); st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado para o período selecionado.")

st.markdown("---")
st.subheader("Análise de Atividades")

filtros_col1, filtros_col2 = st.columns(2)
with filtros_col1:
    with st.expander("Filtrar por Período"):
        start_date_mov = st.date_input("Data de Início", value=datetime.date(2015, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="mov_start")
        end_date_mov = st.date_input("Data de Fim", value=datetime.date.today(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), key="mov_end")

with filtros_col2:
    with st.expander("Filtrar por Usuário e Documento"):
        lista_tipos_doc = [tipo[0] for tipo in session.query(Documento.tipo).distinct().order_by(Documento.tipo).all()]
        lista_tipos_doc.insert(0, "Todos")
        tipo_doc_selecionado = st.selectbox("Filtrar por Tipo de Documento:", options=lista_tipos_doc, key="doc_type_filter")

        lista_utilizadores = [user[0] for user in session.query(Usuario.nome).distinct().order_by(Usuario.nome).all()]
        lista_utilizadores.insert(0, "Todos")
        utilizador_selecionado = st.selectbox("Filtrar por Utilizador:", options=lista_utilizadores, key="user_filter")

if start_date_mov > end_date_mov:
    st.error("Erro: A data de início não pode ser posterior à data de fim.")
else:
    end_date_mov_adj = datetime.datetime.combine(end_date_mov, datetime.time.max)
    
    query_mov = (
        session.query(Movimentacao.tipo, Usuario.nome, Documento.tipo.label("doc_tipo"))
        .join(Usuario, Movimentacao.usuario_id == Usuario.id)
        .join(Caixa, Movimentacao.caixa_id == Caixa.id)
        .join(Caixa.documentos)
        .filter(Movimentacao.data.between(start_date_mov, end_date_mov_adj))
    )

    if tipo_doc_selecionado != "Todos":
        query_mov = query_mov.filter(Documento.tipo == tipo_doc_selecionado)
    
    if utilizador_selecionado != "Todos":
        query_mov = query_mov.filter(Usuario.nome == utilizador_selecionado)
    
    resultados_mov = query_mov.all()

    if resultados_mov:
        df_mov = pd.DataFrame(resultados_mov, columns=['Tipo de Movimentação', 'Utilizador', 'Tipo de Documento'])
        
        titulo_grafico = "Contagem Geral de Movimentações"
        if utilizador_selecionado != "Todos":
            titulo_grafico = f"Movimentações de {utilizador_selecionado}"
        if tipo_doc_selecionado != "Todos":
            titulo_grafico += f" (Docs: {tipo_doc_selecionado})"

        contagem_mov_filtrada = df_mov['Tipo de Movimentação'].value_counts().reset_index()
        contagem_mov_filtrada.columns = ['Tipo de Movimentação', 'Quantidade']
        
        tipo_grafico_mov = st.radio("Visualizar como:", options=["Gráfico de Barras", "Gráfico de Pizza"], key='tipo_grafico_mov', horizontal=True)
        if tipo_grafico_mov == "Gráfico de Barras":
            fig_mov = px.bar(contagem_mov_filtrada, x='Quantidade', y='Tipo de Movimentação', orientation='h', text_auto=True, title=f"<b>{titulo_grafico}</b>", color='Tipo de Movimentação')
            fig_mov.update_layout(yaxis_title="", showlegend=False); st.plotly_chart(fig_mov, use_container_width=True)
        else:
            fig_mov = px.pie(contagem_mov_filtrada, names='Tipo de Movimentação', values='Quantidade', hole=.4, title=f"<b>{titulo_grafico}</b>")
            fig_mov.update_traces(textinfo='percent+label', textfont_size=14); st.plotly_chart(fig_mov, use_container_width=True)
    else:
        st.info("Nenhuma movimentação encontrada para os filtros selecionados.")

st.markdown("---")
st.subheader("Visão Geral de Todos os Documentos")
documentos_data = repo_documento.get_all()
if documentos_data:
    lista_para_df = [(d.id, d.titulo, d.tipo, d.data_emissao.strftime('%Y-%m-%d') if d.data_emissao else 'N/A') for d in documentos_data]
    df_tabela_docs = pd.DataFrame(lista_para_df, columns=['ID', 'Título', 'Tipo', 'Data de Emissão'])
    st.dataframe(df_tabela_docs, use_container_width=True)
    st.download_button(label="Exportar CSV de Documentos 📥", data=convert_df_to_csv(df_tabela_docs), file_name='visao_geral_documentos.csv', mime='text/csv')
else:
    st.warning("Nenhum documento cadastrado.")