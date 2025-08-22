# dashboard.py (FINAL COM BARRAS COLORIDAS)

import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import func, distinct

# --- Importações do seu projeto ---
from repository.CaixaRepository import CaixaRepository
from repository.DocumentoRepository import DocumentoRepository
from repository.UnidadeRepository import UnidadeRepository
from repository.MovimentacaoRepository import MovimentacaoRepository
from repository.UsuarioRepository import UsuarioRepository
from models.models import Caixa, Documento, Unidade, Movimentacao, Usuario

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard - Projeto Arquivo",
    page_icon="📦",
    layout="wide"
)

# --- FUNÇÃO AUXILIAR PARA CONVERSÃO CSV ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig', sep=';')


# --- 2. INICIALIZAÇÃO DOS REPOSITÓRIOS ---
try:
    repo_caixa = CaixaRepository()
    repo_documento = DocumentoRepository()
    repo_unidade = UnidadeRepository()
    repo_movimentacao = MovimentacaoRepository()
    repo_usuario = UsuarioRepository()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    st.info("Verifique se o seu banco de dados Oracle está em execução e as credenciais no ficheiro .env estão corretas.")
    st.stop()


# --- 3. TÍTULO E CABEÇALHO ---
st.title("📦 Dashboard de Gestão de Arquivo")
st.markdown("##")

# --- 4. MÉTRICAS PRINCIPAIS (KPIs) ---
total_caixas = repo_caixa.session.query(func.count(Caixa.id)).scalar()
total_documentos = repo_documento.session.query(func.count(Documento.id)).scalar()
total_unidades = repo_unidade.session.query(func.count(Unidade.id)).scalar()
total_movimentacoes = repo_movimentacao.session.query(func.count(Movimentacao.id)).scalar()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="**Total de Caixas** 📦", value=total_caixas)
with col2:
    st.metric(label="**Total de Documentos** 📄", value=total_documentos)
with col3:
    st.metric(label="**Total de Unidades** 🏢", value=total_unidades)
with col4:
    st.metric(label="**Total de Movimentações** 🚚", value=total_movimentacoes)

st.markdown("---")

# --- 5. GRÁFICOS DE ANÁLISE GERAL ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Caixas por Tipo de Documento")
    query_caixas_por_tipo_doc = (
        repo_documento.session.query(
            Documento.tipo, func.count(distinct(Caixa.id)).label('quantidade_caixas')
        ).join(Documento.caixas).group_by(Documento.tipo).all()
    )

    if query_caixas_por_tipo_doc:
        df_caixas_por_tipo = pd.DataFrame(query_caixas_por_tipo_doc, columns=['Tipo de Documento', 'Número de Caixas'])
        tipo_grafico1 = st.radio(
            "Selecione o tipo de gráfico:", options=["Gráfico de Pizza", "Gráfico de Barras"],
            key='tipo_grafico_1', horizontal=True
        )
        if tipo_grafico1 == "Gráfico de Pizza":
            formato_label = st.radio(
                "Rótulos:", options=["Porcentagem", "Quantidade"], key='formato_label_1', horizontal=True
            )
            fig1 = px.pie(
                df_caixas_por_tipo, names='Tipo de Documento', values='Número de Caixas', hole=.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            if formato_label == "Porcentagem":
                fig1.update_traces(textinfo='percent', textfont_size=14)
            else:
                fig1.update_traces(textinfo='value', textfont_size=14)
            st.plotly_chart(fig1, use_container_width=True)
        
        elif tipo_grafico1 == "Gráfico de Barras":
            # <--- ALTERAÇÃO AQUI: Adicionado color='Tipo de Documento' ---
            fig1 = px.bar(
                df_caixas_por_tipo, x='Tipo de Documento', y='Número de Caixas', text_auto=True,
                template='plotly_white', color='Tipo de Documento' # Adiciona cores
            )
            fig1.update_layout(showlegend=False) # Esconde a legenda (opcional)
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        csv_caixas_tipo = convert_df_to_csv(df_caixas_por_tipo)
        st.download_button(
            label="Exportar para CSV 📥", data=csv_caixas_tipo, file_name='caixas_por_tipo_documento.csv', mime='text/csv'
        )
    else:
        st.info("Não há documentos associados a caixas para exibir este gráfico.")

with col_graf2:
    st.subheader("Caixas por Unidade")
    query_caixas_unidade = (
        repo_caixa.session.query(Unidade.nome, func.count(Caixa.id).label('quantidade'))
        .join(Unidade, Caixa.unidade_id == Unidade.id).group_by(Unidade.nome).all()
    )
    if query_caixas_unidade:
        df_caixas_unidade = pd.DataFrame(query_caixas_unidade, columns=['Unidade', 'Quantidade de Caixas'])
        tipo_grafico2 = st.radio(
            "Selecione o tipo de gráfico:", options=["Gráfico de Barras", "Gráfico de Pizza"],
            key='tipo_grafico_2', horizontal=True
        )
        if tipo_grafico2 == "Gráfico de Barras":
            # <--- ALTERAÇÃO AQUI: Adicionado color='Unidade' ---
            fig2 = px.bar(
                df_caixas_unidade, x='Unidade', y='Quantidade de Caixas', text_auto=True,
                template='plotly_white', color='Unidade' # Adiciona cores
            )
            fig2.update_layout(showlegend=False) # Esconde a legenda (opcional)
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

        elif tipo_grafico2 == "Gráfico de Pizza":
            fig2 = px.pie(df_caixas_unidade, names='Unidade', values='Quantidade de Caixas', hole=.4)
            fig2.update_traces(textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig2, use_container_width=True)
        csv_caixas_unidade = convert_df_to_csv(df_caixas_unidade)
        st.download_button(
            label="Exportar para CSV 📥", data=csv_caixas_unidade, file_name='caixas_por_unidade.csv', mime='text/csv'
        )
    else:
        st.info("Não há caixas associadas a unidades para exibir este gráfico.")


# --- 6. ANÁLISE DE MOVIMENTAÇÕES (SECÇÃO INTERATIVA) ---
st.markdown("---")
st.subheader("Análise de Atividades por Utilizador")

query_mov_completa = (
    repo_movimentacao.session.query(Movimentacao.tipo, Usuario.nome)
    .join(Usuario, Movimentacao.usuario_id == Usuario.id).all()
)

if query_mov_completa:
    df_mov_completo = pd.DataFrame(query_mov_completa, columns=['Tipo', 'Utilizador'])
    lista_utilizadores = sorted(df_mov_completo['Utilizador'].unique().tolist())
    lista_utilizadores.insert(0, "Todos")

    utilizador_selecionado = st.sidebar.selectbox("Selecione um Utilizador para detalhar:", options=lista_utilizadores)

    if utilizador_selecionado == "Todos":
        df_filtrado = df_mov_completo
        titulo_grafico = "Contagem Geral de Movimentações por Tipo"
    else:
        df_filtrado = df_mov_completo[df_mov_completo['Utilizador'] == utilizador_selecionado]
        titulo_grafico = f"Movimentações de {utilizador_selecionado}"

    contagem_mov_filtrada = df_filtrado['Tipo'].value_counts().reset_index()
    contagem_mov_filtrada.columns = ['Tipo de Movimentação', 'Quantidade']
    
    tipo_grafico_mov = st.radio(
        "Visualizar como:",
        options=["Gráfico de Barras", "Gráfico de Pizza"],
        key='tipo_grafico_mov',
        horizontal=True
    )
    
    if tipo_grafico_mov == "Gráfico de Barras":
        fig_mov = px.bar(
            contagem_mov_filtrada, x='Quantidade', y='Tipo de Movimentação', orientation='h',
            text_auto=True, title=f"<b>{titulo_grafico}</b>", color='Tipo de Movimentação' # Adiciona cores
        )
        fig_mov.update_layout(yaxis_title="", showlegend=False)
        st.plotly_chart(fig_mov, use_container_width=True)
    
    elif tipo_grafico_mov == "Gráfico de Pizza":
        fig_mov = px.pie(
            contagem_mov_filtrada, names='Tipo de Movimentação', values='Quantidade',
            hole=.4, title=f"<b>{titulo_grafico}</b>"
        )
        fig_mov.update_traces(textinfo='percent+label', textfont_size=14)
        st.plotly_chart(fig_mov, use_container_width=True)

    csv_mov_filtrada = convert_df_to_csv(contagem_mov_filtrada)
    st.download_button(
        label="Exportar para CSV 📥", data=csv_mov_filtrada,
        file_name=f'movimentacoes_{utilizador_selecionado.lower().replace(" ", "_")}.csv', mime='text/csv'
    )
else:
    st.info("Não há movimentações registadas para exibir esta análise.")


# --- 7. TABELA DE DADOS DETALHADOS ---
st.markdown("---")
st.subheader("Visão Geral dos Documentos")

documentos_data = repo_documento.get_all()
if 'documentos_data' in locals() and documentos_data:
    lista_para_df = []
    for d in documentos_data:
        data_emissao_obj = getattr(d, 'data_emissao', None)
        data_formatada = data_emissao_obj.strftime('%Y-%m-%d') if data_emissao_obj else 'N/A'
        lista_para_df.append((d.id, d.titulo, d.tipo, data_formatada))

    df_tabela_docs = pd.DataFrame(lista_para_df, columns=['ID', 'Título', 'Tipo', 'Data de Emissão'])
    st.dataframe(df_tabela_docs, use_container_width=True)

    csv_docs_geral = convert_df_to_csv(df_tabela_docs)
    st.download_button(
        label="Exportar para CSV 📥", data=csv_docs_geral, file_name='visao_geral_documentos.csv', mime='text/csv'
    )
else:
    st.warning("Nenhum documento cadastrado.")