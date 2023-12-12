# todo: specify borrowed capital, eir and duration
# todo: show amortization table
# todo: editable dataframe for partials https://blog.streamlit.io/editable-dataframes-are-here/
# todo: show new amortization table with partials
# todo: show total interest vs with partials
import streamlit as st
import pandas as pd
from service import LoanService
from definitions import PartialAmortization


def partials_serializer(partials: pd.DataFrame) -> list[PartialAmortization]:
    return [
        PartialAmortization(int(p["Year"]), int(p["Capital"]))
        for p in partials.to_dict("records")
        if p["Year"] and p["Capital"]
    ]


def gui():
    st.set_page_config(
        page_title="Finances Analysis",
        page_icon="📈",
        layout="wide",
    )

    st.title("French Loan")

    with st.container():
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.subheader("Loan parameters")
            borrowed_capital = st.number_input(
                "Borrowed Capital",
                min_value=1_000,
                max_value=10_000_000,
                value=100_000,
                step=10_000,
            )
            eir_100 = st.number_input(
                "Effective Interest Rate %",
                min_value=0.5,
                max_value=10.0,
                value=3.0,
                step=0.01,
            )
            duration = st.number_input(
                "duration",
                min_value=3,
                max_value=40,
                value=30,
            )
            loan = LoanService(
                borrowed_capital,
                eir_100 / 100.0,
                duration,
            )

            btn_basic_loan = st.button("Compute", key="basic_loan")

            st.divider()
            st.subheader("Partial Amortizations")

            init_df = pd.DataFrame([{"Year": None, "Capital": None}])
            partials_df = st.data_editor(init_df, num_rows="dynamic")

            btn_partials = st.button("Compute", key="loan_with_partials")

        with col2:
            st.subheader("Amortization Table")
            if btn_basic_loan or btn_partials:
                df_basic_loan = loan.get_amortization_table()
                st.dataframe(df_basic_loan[df_basic_loan.outstanding_capital > 0])

                df_basic_loan = df_basic_loan.fillna(0)
                total = sum(df_basic_loan["interest"] + df_basic_loan["amortized_capital"])
                interests = sum(df_basic_loan["interest"])
                st.markdown(f"Total {round(total, 2):,} €")
                st.markdown(f"Interests {round(interests, 2):,} €")

            st.divider()

            st.subheader("Amortization Table - with partials")
            if btn_partials:
                partials = partials_serializer(partials_df)
                df_with_partials = loan.get_amortization_table_with_partials(partials)
                st.dataframe(df_with_partials[df_with_partials.outstanding_capital > 0])

                df_with_partials = df_with_partials.fillna(0)
                total = sum(df_with_partials["interest"] + df_with_partials["amortized_capital"])
                interests = sum(df_with_partials["interest"])
                st.markdown(f"Total {round(total, 2):,} €")
                st.markdown(f"Interests {round(interests, 2):,} €")


if __name__ == "__main__":
    gui()
