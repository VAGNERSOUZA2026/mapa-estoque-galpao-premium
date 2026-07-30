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
  url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={urllib.parse.quote(link_pallet)}"

  col_qr, col_acoes = st.columns([1, 1])

  with col_qr:
    st.image(
        url_qr, caption=f"Etiqueta QR Code — {pallet_alvo}", width=220
    )

  with col_acoes:
    st.markdown("### 🖨️ Opções da Etiqueta")
    st.write(f"**Posição:** {pallet_alvo}")

    # Script JS inteligente que abre uma janela limpa só com a imagem e chama o menu de impressoras imediatamente
    btn_html_print = f"""
            <script>
            function imprimirEtiquetaDireto() {{
                var printWindow = window.open('', '_blank');
                printWindow.document.write('<html><head><title>Imprimir Etiqueta - {pallet_alvo}</title>');
                printWindow.document.write('<style>body{{text-align:center; font-family:sans-serif; padding:20px;}} img{{width:280px; height:280px;}} h2{{margin-bottom:5px; color:#581825;}}</style>');
                printWindow.document.write('</head><body>');
                printWindow.document.write('<h2>GALPÃO PREMIUM</h2>');
                printWindow.document.write('<h3>{pallet_alvo}</h3>');
                printWindow.document.write('<img src="{url_qr}" onload="window.print(); window.close();" />');
                printWindow.document.write('</body></html>');
                printWindow.document.close();
            }}
            </script>
            <button onclick="imprimirEtiquetaDireto()" style="
                width: 100%;
                background-color: #581825;
                color: white;
                padding: 14px 0px;
                text-align: center;
                font-weight: bold;
                font-size: 1rem;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                margin-bottom: 12px;
                box-shadow: 0px 4px 8px rgba(0,0,0,0.15);
            ">🖨️ Imprimir Etiqueta Agora</button>
        """
    st.markdown(btn_html_print, unsafe_allow_html=True)

    st.markdown(
        f"""
            <a href="{url_qr}" target="_blank" style="
                display: inline-block;
                width: 100%;
                background-color: #F1F5F9;
                color: #334155;
                padding: 12px 0px;
                text-align: center;
                text-decoration: none;
                font-weight: 600;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
            ">📥 Baixar Imagem do QR Code</a>
        """,
        unsafe_allow_html=True,
    )
