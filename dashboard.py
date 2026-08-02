import streamlit as st

def run(confirmadas, espera, limite, session_state):
    st.markdown("### 📊 Visão Geral do Sistema")
    
    # 1. Cartões de Métricas (Estilo Dashboard Profissional)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Vagas Confirmadas", value=f"{len(confirmadas)} / {limite}", delta="Lista Principal")
    with col2:
        st.metric(label="Fila de Espera", value=f"{len(espera)}", delta="Aguardando Vaga" if len(espera) > 0 else "Sem fila")
    with col3:
        total_cad = len(session_state.jogadoras)
        st.metric(label="Elenco Total", value=f"{total_cad}", delta="Cadastradas")
    with col4:
        mensalistas_ativas = len([j for j in session_state.jogadoras if j.get("tipo") == "Mensalista"])
        st.metric(label="Mensalistas", value=f"{mensalistas_ativas}", delta="Fixas")

    st.markdown("---")

    # 2. Cards Modernos com Bordas Nativas
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        with st.container(border=True):
            st.markdown("#### 📢 Avisos e Regras Atuais")
            recado_atual = session_state.avisos.get('recado', 'Nenhum aviso no momento.')
            vencimento_atual = session_state.avisos.get('vencimento', 'Não informado')
            
            st.info(f"💡 **Recado do Dia:** {recado_atual}")
            st.write(f"📅 **Vencimento das Mensalidades:** {vencimento_atual}")
            st.markdown("⭐ *Lembre-se: Mensalistas têm prioridade na lista até segunda-feira às 17:00.*")

    with col_dir:
        with st.container(border=True):
            st.markdown("#### ⚡ Atalhos e Status de Acesso")
            
            usuario = session_state.usuario_logado
            if usuario:
                st.success(f"👤 Você está logada como: **{usuario}**")
                st.write("Vá até a aba **📌 Presença no Jogo** para confirmar sua vaga ou gerenciar sua participação.")
            else:
                st.warning("⚠️ **Você não está logada.** Faça login na barra lateral esquerda para interagir com o sistema.")
            
            st.markdown("---")
            st.markdown("🚀 *Use o menu lateral esquerdo para navegar entre as funções de Sorteio, Pix e Elenco.*")
