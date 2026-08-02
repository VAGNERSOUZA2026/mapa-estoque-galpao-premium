import streamlit as st
import pandas as pd

def run(fuso_br, hoje_dt, salvar_dados, FINANCE_FILE):
    st.subheader("📊 Fluxo de Caixa")
    df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor"])
    
    if not df_fin.empty:
        df_fin["mes_ano"] = df_fin["data"].apply(lambda x: x[3:10] if isinstance(x, str) and len(x) >= 10 else "Geral")
        meses_disp = df_fin["mes_ano"].unique().tolist()
        mes_sel = st.selectbox("📅 Filtrar por Mês/Ano:", ["Todos"] + meses_disp)
        df_fin_filtrado = df_fin[df_fin["mes_ano"] == mes_sel] if mes_sel != "Todos" else df_fin
    else:
        df_fin_filtrado = df_fin

    total_in = df_fin_filtrado[df_fin_filtrado["tipo"] == "Entrada"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
    total_out = df_fin_filtrado[df_fin_filtrado["tipo"] == "Saída"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 Entradas", f"R$ {total_in:.2f}")
    m2.metric("🔴 Saídas", f"R$ {total_out:.2f}")
    m3.metric("💰 Saldo", f"R$ {total_in - total_out:.2f}")

    st.markdown("---")
    tab_list_fin, tab_add_fin, tab_edit_fin = st.tabs(["📜 Extrato", "➕ Novo Registro", "✏️ Editar / Excluir"])

    with tab_list_fin:
        if not df_fin_filtrado.empty:
            cols_to_show = ["data", "descricao", "tipo", "valor"]
            st.dataframe(df_fin_filtrado[cols_to_show], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro para este período.")

    with tab_add_fin:
        with st.form("form_fin", clear_on_submit=True):
            f_data = st.text_input("Data (DD/MM/AAAA)", value=hoje_dt.strftime("%d/%m/%Y"))
            f_desc = st.text_input("Descrição")
            f_tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
            f_valor = st.number_input("Valor (R$)", min_value=0.01, step=5.0)
            if st.form_submit_button("💾 Salvar Registro", use_container_width=True):
                st.session_state.financeiro.append({"data": f_data, "descricao": f_desc, "tipo": f_tipo, "valor": float(f_valor)})
                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                st.success("Lançamento salvo!")
                st.rerun()

    with tab_edit_fin:
        if not st.session_state.financeiro:
            st.info("Nenhum lançamento cadastrado.")
        else:
            opcoes_fin = [f"{i}. {item['data']} - {item['descricao']} (R$ {item['valor']:.2f})" for i, item in enumerate(st.session_state.financeiro)]
            idx_sel = st.selectbox("Escolha o registro para editar/apagar:", range(len(opcoes_fin)), format_func=lambda x: opcoes_fin[x])
            reg_sel = st.session_state.financeiro[idx_sel]

            with st.form("form_edit_fin"):
                ef_data = st.text_input("Data", value=reg_sel.get("data", ""))
                ef_desc = st.text_input("Descrição", value=reg_sel.get("descricao", ""))
                ef_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_sel.get("tipo") == "Entrada" else 1)
                ef_valor = st.number_input("Valor (R$)", value=float(reg_sel.get("valor", 0.0)), min_value=0.01)

                if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    st.session_state.financeiro[idx_sel] = {"data": ef_data, "descricao": ef_desc, "tipo": ef_tipo, "valor": float(ef_valor)}
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Atualizado!")
                    st.rerun()

            if st.button("🗑️ Excluir Lançamento", type="primary", use_container_width=True):
                st.session_state.financeiro.pop(idx_sel)
                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                st.success("Excluído com sucesso!")
                st.rerun()
