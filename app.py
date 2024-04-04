import streamlit as st

view = [100,150,30]
st.write('# View')
st.write('## raw')
view

st.bar_chart(view)
st.write('## bar chart')

import pandas as pd
sview = pd.Series(view)
