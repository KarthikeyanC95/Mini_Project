import streamlit as st
from streamlit_lottie import st_lottie
import json

st.set_page_config(
    page_title="Bookscape Explorer",
    page_icon=":book:",
)

st.title(":red[Bookscape Explorer] :book: :bar_chart:")
with open("Animation.json") as souce:
    animation = json.load(souce)
    st_lottie(animation, height = 200, width = 200)
    st.markdown("""
            This Bookscape Explorer page allow the user to type the book from  search key and With help of fetch button, it display the data in the dataframe.
             We have provided the slider to limit the view of book data. With help of load to MYSQL Button, it load the data to the mysql workbench
            which has been displayed and finally, the Data visualization page to analysis the book data based on 20 predefined sets of the different query""")
    