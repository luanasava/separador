import streamlit as st
import pandas as pd
import io
import zipfile
from collections import defaultdict

st.title("Agrupador de CSV por CEP")

uploaded_file = st.file_uploader("Envie um arquivo CSV", type=["csv"])

if uploaded_file:
    try:
        # Lê o CSV
        df = pd.read_csv(uploaded_file, dtype=str, sep=';', engine='python', on_bad_lines='skip')
        df.columns = [col.strip() for col in df.columns]

        # Verificação de colunas necessárias
        if 'CEP_INICIAL' not in df.columns or 'CEP_FINAL' not in df.columns:
            st.error("O arquivo precisa conter as colunas 'CEP_INICIAL' e 'CEP_FINAL'.")
        else:
            # Agrupa pela combinação de CEP
            df['__group_key__'] = df['CEP_INICIAL'].str.strip() + '|' + df['CEP_FINAL'].str.strip()
            group_counts = df['__group_key__'].value_counts()

            # Cria um dicionário com os grupos
            buckets = defaultdict(list)
            for key, count in group_counts.items():
                group_rows = df[df['__group_key__'] == key].drop(columns='__group_key__')
                buckets[count].append(group_rows)

            # Gera os arquivos CSV e compacta em um ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for count, group_list in buckets.items():
                    result = pd.concat(group_list, ignore_index=True)
                    csv_bytes = result.to_csv(index=False, sep=';', encoding='utf-8-sig')
                    zip_file.writestr(f"{count}.csv", csv_bytes)

            zip_buffer.seek(0)

            # Botão para download do ZIP
            st.success("Arquivos agrupados com sucesso!")
            st.download_button(
                label="Baixar arquivos agrupados (.zip)",
                data=zip_buffer,
                file_name="conjuntos_exportados.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
