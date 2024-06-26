import streamlit as st
from ReportGenerator import getSymbolReport, getTechnicalAnalysis, benchmarksAndCompetitorAnalysis #Importing report Generator Functions
from PIL import Image
import base64
# import warnings
# warnings.filterwarnings("ignore")

st.set_page_config(page_title="Stock Analysis Dashboard v2", page_icon="📈", layout="wide")


def get_base64_of_image(image_filename):
    """
    Converts an image file to a Base64 encoded data URI.
    """
    with open(image_filename, "rb") as f:
        image_data = f.read()
    encoded_data = base64.b64encode(image_data).decode()
    return f"data:image/png;base64,{encoded_data}"

image_path = "./Streamlit_App/header.gif"  # Replace with actual path
base64_data = get_base64_of_image(image_path)

st.markdown(f"![My Image]({base64_data})")

st.title('Stock Analysis Dashboard')
ticker_symbol = st.text_input("Enter US S&P 500 Ticker:")

if st.button("Generate Report"):
    report = getSymbolReport(ticker_symbol)
    fig1 = getTechnicalAnalysis(ticker_symbol)
    fig2 = benchmarksAndCompetitorAnalysis(ticker_symbol)
    st.markdown(report)
    st.markdown('### Technical Analysis')
    st.plotly_chart(fig1)
    st.markdown('### Benchmark and Competitor Analysis')
    st.plotly_chart(fig2)