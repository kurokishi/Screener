import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def plot_eps_fcf_chart(years, eps_values, fcf_values):
    df = pd.DataFrame({
        "EPS": eps_values,
        "FCF": fcf_values
    }, index=years)

    fig, ax = plt.subplots()
    df["EPS"].plot(ax=ax, marker='o', label="EPS")
    df["FCF"].plot(ax=ax, marker='s', label="FCF", secondary_y=True)

    ax.set_title("EPS & FCF Trends")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("EPS")
    ax.right_ax.set_ylabel("FCF")
    ax.legend(loc="upper left")
    ax.right_ax.legend(loc="upper right")

    st.pyplot(fig)
