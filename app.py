import streamlit as st

inicio = st.Page("views/inicio.py", title="Inicio", icon=":material/home:", default=True)
dashboard = st.Page("views/dashboard.py", title="Dashboard", icon=":material/dashboard:")
mapas = st.Page("views/mapas.py", title="Mapas", icon=":material/map:")
redes = st.Page("views/redes.py", title="Redes", icon=":material/share:")

pg = st.navigation([inicio, dashboard, mapas, redes])
pg.run()
