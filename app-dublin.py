import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import awesome_streamlit as ast
import datetime as dt

import src.pages.ljubljana
import src.pages.about
import src.pages.datacleaning
import src.pages.viz

PAGES = {
    "Data Exploration": src.pages.datacleaning,
    "Ljubljana Example": src.pages.ljubljana,
    "About": src.pages.about,
}


def main():
    st.sidebar.title('Observation Mapping')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    with st.spinner(f"Loading {selection} ..."):
        ast.shared.components.write_page(page)


if __name__ == '__main__':
    main()
