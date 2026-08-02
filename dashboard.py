import streamlit as st

def run(confirmadas, espera, limite, session_state):
    st.markdown("### 📊 Painel Principal - Acesso Rápido")
    
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
    st.markdown("### ⚡ Cards de Clique Direto")

    # 2. Grid de Cards com Botões de Acesso Rápido
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        with st.container(border=True):
            st.markdown("#### 📌 Presença")
            st.write("Confirme ou cancele sua vaga no jogo.")
            if st.button("Ir para Presença ➔", use_container_width=True, key="btn_card_presenca"):
                session_state.menu_escolhido = "📌 Presença no Jogo"
                st.rerun()
                
    with c2:
        with st.container(border=True):
            st.markdown("#### 💸 Pix & Pagamento")
            st.write("Envie seu comprovante e veja a chave Pix.")
            if st.button("Ir para Pagamento ➔", use_container_width=True, key="btn_card_pix"):
                session_state.menu_escolhido = "💸 Pagamento & Pix"
                st.rerun()
                
    with c3:
        with st.container(border=True):
            st.markdown("#### 🔀 Sorteio")
            st.write("Veja os times sorteados para a partida.")
            if st.button("Ver Sorteio ➔", use_container_width=True, key="btn_card_sorteio"):
                session_state.menu_escolhido = "🔀 Sorteio de Times"
                st.rerun()
                
    with c4:
        with st.container(border=True):
            st.markdown("#### 📋 Elenco")
            st.write("Consulte a lista de jogadoras cadastradas.")
            if st.button("Ver Elenco ➔", use_container_width=True, key="btn_card_elenco"):
                session_state.menu_escolhido = "📋 Elenco de Jogadoras"
                st.rerun()

    st.markdown("---")

    # 3. Bloco de Avisos Moderno
    with st.container(border=True):
        st.markdown("#### 📢 Avisos e Regras Atuais")
        recado_atual = session_state.avisos.get('recado', 'Nenhum aviso no momento.')
        vencimento_atual = session_state.avisos.get('vencimento', 'Não informado')
        
        st.info(f"💡 **Recado do Dia:** {recado_atual}")
        st.write(f"📅 **Vencimento das Mensalidades:** {vencimento_atual}")
        st.markdown("⭐ *Lembre-se: Mensalistas têm prioridade na lista até segunda-feira às 17:00.*")
