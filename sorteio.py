import streamlit as st
import random

def run(data_hoje_id, hoje_dt, salvar_dados, SORTEIO_FILE, confirmadas, obter_nome_p):
    st.subheader("🔀 Sorteio de Times")
    tab_oficial, tab_quadra = st.tabs(["🏆 Sorteio Oficial (Pré-Jogo)", "⚡ Ajuste Rápido de Quadra"])

    with tab_oficial:
        sorteio_salvo = st.session_state.sorteio_oficial
        if sorteio_salvo and "times" in sorteio_salvo:
            st.success(f"✅ **Sorteio Oficial Realizado ({sorteio_salvo.get('hora', '')})**")
            cols = st.columns(len(sorteio_salvo["times"]))
            for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
                with cols[idx]:
                    st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                    for item in membros:
                        st.write(f"• **{item}**")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("⏰ O Sorteio Oficial é realizado automaticamente às **Segundas-feiras, às 18:30**.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.write("#### 🛠️ Forçar Novo Sorteio (Admin)")
            confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
            qtd_t = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_oficial")
            if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
                if len(confirmadas_nomes) < qtd_t:
                    st.error("Número insuficiente de confirmadas.")
                else:
                    temp = confirmadas_nomes.copy()
                    random.shuffle(temp)
                    res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
                    for idx, p in enumerate(temp):
                        res_times[f"Time {idx % qtd_t + 1}"].append(p)
                    
                    st.session_state.sorteio_oficial = {
                        "data": data_hoje_id, "hora": f"{hoje_dt.strftime('%H:%M')} (Manual)", "times": res_times
                    }
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                    st.rerun()

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra")
        confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
        if not confirmadas_nomes:
            st.info("Nenhuma jogadora confirmada na lista principal.")
        else:
            presentes = st.multiselect("Marque as jogadoras presentes na quadra:", confirmadas_nomes, default=confirmadas_nomes)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_quadra")
            if st.button("🎲 Sortear Apenas Presentes", use_container_width=True):
                if len(presentes) < qtd_t_q:
                    st.error("Selecione mais jogadoras.")
                else:
                    temp = presentes.copy()
                    random.shuffle(temp)
                    times_q = [[] for _ in range(qtd_t_q)]
                    for idx, p in enumerate(temp):
                        times_q[idx % qtd_t_q].append(p)
                    cols_q = st.columns(qtd_t_q)
                    for i, t in enumerate(times_q):
                        with cols_q[i]:
                            st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1} (Quadra)</h3>", unsafe_allow_html=True)
                            for item in t:
                                st.write(f"• **{item}**")
                            st.markdown("</div>", unsafe_allow_html=True)
