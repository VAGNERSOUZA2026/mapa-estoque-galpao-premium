# 8. GERAR QR CODE DO PALLET
elif menu == "🏷️ Gerar QR Code do Pallet":
  st.subheader("🏷️ Etiquetas para Pallet")

  c1, c2 = st.columns(2)
  with c1:
    qr_corr = st.selectbox("Corredor:", LISTA_CORREDORES)
  with c2:
    qr_pal = st.selectbox("Pallet:", LISTA_PALLETS)

  pallet_alvo = f"{qr_corr} - {qr_pal}"

  vinhos_no_pallet = [
      v for v in st.session_state.estoque if v.get("pallet") == pallet_alvo
  ]

  st.markdown("---")

  if vinhos_no_pallet:
    st.success(
        f"📦 **{len(vinhos_no_pallet)} vinho(s)** encontrado(s) em"
        f" **{pallet_alvo}**:"
    )
    for item in vinhos_no_pallet:
      st.markdown(
          f"• **{item.get('nome')}** ({item.get('safra')}) — *Lado:"
          f" {item.get('lado')}*"
      )
  else:
    st.info(f"ℹ️ Nenhum vinho cadastrado em **{pallet_alvo}** no momento.")

  st.markdown("---")

  pallet_encoded = urllib.parse.quote_plus(pallet_alvo)
  link_pallet = (
      f"{URL_APLICATIVO}/?pallet={pallet_encoded}&auth={SENHA_ACESSO}"
  )
  url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(link_pallet)}"

  # Exibição do QR Code centralizado
  col_qr, col_acoes = st.columns([1, 1])

  with col_qr:
    st.image(
        url_qr, caption=f"Etiqueta QR Code — {pallet_alvo}", width=220
    )

  with col_acoes:
    st.markdown("### 🖨️ Opções da Etiqueta")
    st.write(f"**Posição:** {pallet_alvo}")

    # Botão 1: Imprimir a etiqueta diretamente
    btn_html_print = f"""
            <a href="javascript:window.print()" style="
                display: inline-block;
                width: 100%;
                background-color: #581825;
                color: white;
                padding: 12px 0px;
                text-align: center;
                text-decoration: none;
                font-weight: bold;
                border-radius: 8px;
                margin-bottom: 10px;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            ">🖨️ Imprimir Etiqueta</a>
        """
    st.markdown(btn_html_print, unsafe_allow_html=True)

    # Botão 2: Abrir imagem em alta resolução para salvar/imprimir
    st.markdown(
        f"""
            <a href="{url_qr}" target="_blank" style="
                display: inline-block;
                width: 100%;
                background-color: #F1F5F9;
                color: #334155;
                padding: 10px 0px;
                text-align: center;
                text-decoration: none;
                font-weight: 600;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
            ">📥 Abrir Imagem para Baixar</a>
        """,
        unsafe_allow_html=True,
    )
