import streamlit as st

def run(confirmadas, espera, limite, session_state):
    # Banner superior estilo aplicativo moderno
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 16px; border: 1px solid rgba(236, 72, 153, 0.3); margin-bottom: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.3);'>
        <h2 style='color: #f43f5e; margin: 0; font-weight: 800; font-size: 1.8rem;'>⚡ Resenha & Início</h2>
        <p style='color: #94a3b8; margin: 5px 0 0 0; font-size: 0.95rem;'>Peladinha FC — Gestão Inteligente com Toque Feminino</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Cartões de Métricas no estilo moderno
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📱 Acesso Rápido (Cards Interativos)")

    # 2. Grid de Cards 2x3 no estilo do aplicativo de celular
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        with st.container(border=True):
            st.markdown("### 📌")
            st.markdown("#### Presença & Vagas")
            st.write("Confirme ou cancele sua presença na partida da semana.")
            if st.button("Acessar Presença ➔", use_container_width=True, key="card_presenca_btn"):
                session_state.menu_escolhido = "📌 Presença no Jogo"
                st.rerun()

    with col_b:
        with st.container(border=True):
            st.markdown("### 🎂")
            st.markdown("#### Aniversariantes")
            st.write("Veja quem faz aniversário no mês e mande parabéns.")
            if st.button("Ver Elenco ➔", use_container_width=True, key="card_aniv_btn"):
                session_state.menu_escolhido = "📋 Elenco de Jogadoras"
                st.rerun()

    with col_c:
        with st.container(border=True):
            st.markdown("### 🔀")
            st.markdown("#### Sorteio de Times")
            st.write("Confira a divisão dos times para o jogo de hoje.")
            if st.button("Ver Sorteio ➔", use_container_width=True, key="card_sorteio_btn"):
                session_state.menu_escolhido = "🔀 Sorteio de Times"
                st.rerun()

    col_d, col_e, col_f = st.columns(3)

    with col_d:
        with st.container(border=True):
            st.markdown("### 💸")
            st.markdown("#### Pix & Pagamento")
            st.write("Envie seu comprovante e consulte a chave Pix.")
            if st.button("Ir para Pagamento ➔", use_container_width=True, key="card_pix_btn"):
                session_state.menu_escolhido = "💸 Pagamento & Pix"
                st.rerun()

    with col_e:
        with st.container(border=True):
            st.markdown("### 📜")
            st.markdown("#### Regulamento")
            st.write("Consulte as regras e prioridades de vagas do grupo.")
            if st.button("Ler Regras ➔", use_container_width=True, key="card_regra_btn"):
                session_state.menu_escolhido = "📜 Regulamento"
                st.rerun()

    with col_f:
        with st.container(border=True):
            st.markdown("### ⚙️")
            st.markdown("#### Painel Admin")
            st.write("Gerenciamento de avisos, limites e caixa.")
            if st.button("Abrir Admin ➔", use_container_width=True, key="card_admin_btn"):
                session_state.menu_escolhido = "⚙️ Painel Admin"
                st.rerun()

    st.markdown("---")

    # 3. Bloco de Avisos com estilo elegante
    with st.container(border=True):
        st.markdown("#### 📢 Recado do Dia & Avisos")
        recado_atual = session_state.avisos.get('recado', 'Nenhum aviso no momento.')
        vencimento_atual = session_state.avisos.get('vencimento', 'Não informado')
        
        st.info(f"💡 **Aviso Importante:** {recado_atual}")
        st.write(f"📅 **Vencimento das Mensalidades:** {vencimento_atual}")
        st.markdown("🌸 *Lembre-se: Mensalistas têm prioridade na lista até segunda-feira às 17:00.*")
