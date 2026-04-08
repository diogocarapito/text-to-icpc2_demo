import streamlit as st
import timeit
from utils.utils import (
    device_cuda_mps_cpu,
    load_model,
    prediction_display,
    load_csv_github,
)
import pyperclip
import pandas as pd
import os
import re
import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        dbname=os.environ.get("POSTGRES_DB", "icpc2"),
        user=os.environ.get("POSTGRES_USER", "icpc2user"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
    )


def db_insert(
    text_input, predicted_text, predicted_code, predicted_label, model, feedback, copy
):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions
                (text_input, predicted_text, predicted_code, predicted_label, model, feedback, copy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                text_input,
                predicted_text,
                predicted_code,
                predicted_label,
                model,
                feedback,
                copy,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting into database: {e}")


def demo_new():
    st.header("Demo")

    # st.write(
    #     "O modelo está disponivel em [https://huggingface.co/diogocarapito/text-to-icpc2_bert-base-uncased](https://huggingface.co/diogocarapito/text-to-icpc2)"
    # )

    # get available device
    available_device = device_cuda_mps_cpu(force_cpu=True)

    # choose model
    # model_chosen = "text-to-icpc2_bert-base-uncased"
    # model_chosen = "text-to-icpc2"
    model_chosen = "text-to-icpc2-bert-base-portuguese-cased"

    pipe = load_model(f"diogocarapito/{model_chosen}", available_device)

    # text input
    text = st.text_input("Coloque um diagnóstico para o modelo classificar")

    lables_dataframe = pd.read_csv(
        "https://raw.githubusercontent.com/DiogoCarapito/text-to-icpc2/main/data/icpc2_processed.csv"
    )

    lable_code_dict = pd.read_csv(
        "https://raw.githubusercontent.com/DiogoCarapito/text-to-icpc2/refs/heads/main/data/code_text_label.csv"
    )

    if text == "":
        st.warning("Coloque um diagnóstico para classificar")

    else:
        # check if text corresponds to a letter and 2 algarisms with re
        if bool(re.match(r"[A-Za-z]\d\d", text)):
            # make the text uppercase
            text = text.upper()

            try:
                # get the code
                description = lables_dataframe.loc[
                    lables_dataframe["cod"] == text, "nome"
                ].values[0]

                st.write(f"## {text} - {description}")
            except IndexError:
                st.warning("Código não encontrado")

        else:
            # Record the start time
            start_time = timeit.default_timer()

            # Execute prediction (top 5)
            predictions = pipe(text, top_k=5)

            # Record the end time
            end_time = timeit.default_timer()

            # Calculate the elapsed time
            elapsed_time = end_time - start_time

            # Display the elapsed time
            st.write(
                f"Tempo necessário para classificação: **{elapsed_time:.4f} segundos** com **'{available_device}'**"
            )

            valid_predictions = []
            for each in predictions:
                match_code = lable_code_dict.loc[
                    lable_code_dict["code"] == each["label"], "code"
                ]
                match_text = lable_code_dict.loc[
                    lable_code_dict["code"] == each["label"], "text"
                ]
                if match_code.empty or match_text.empty:
                    continue
                each["code"] = match_code.values[0]
                each["text"] = match_text.values[0]
                valid_predictions.append(each)

            predictions = valid_predictions

            st.subheader("Top 5 Previsões")
            for i, each in enumerate(predictions):
                st.write(
                    f"**{i+1}. {each['code']} — {each['text']}** ({each['score']*100:.1f}%)"
                )

            if not predictions:
                st.warning("Nenhuma previsão encontrada para o texto introduzido.")
                return

            if "copy" not in st.session_state:
                st.session_state["copy"] = False

            if "feedback" not in st.session_state:
                st.session_state["feedback"] = None

            st.write("")
            st.subheader("O modelo portou-se bem?")

            col_1, col_2, col_3 = st.columns([1, 1, 1])

            with col_1:
                if st.button("Copiar código", type="primary"):
                    try:
                        pyperclip.copy(predictions[0]["code"])
                    except Exception:
                        pass
                    st.session_state["copy"] = True
                    st.session_state["feedback"] = 2

            with col_2:
                if st.button("👍", type="primary"):
                    st.session_state["feedback"] = 1

            with col_3:
                if st.button("👎", type="secondary"):
                    st.session_state["feedback"] = -1
            st.write("")
            # text_input, predicted_code, predicted_lable, model
            prediction_display(predictions, lables_dataframe)

            db_insert(
                text,
                predictions[0]["text"],
                predictions[0]["code"],
                predictions[0]["label"],
                model_chosen,
                st.session_state["feedback"],
                st.session_state["copy"],
            )
