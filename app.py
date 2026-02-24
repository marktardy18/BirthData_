!pip install streamlit pandas plotly-express --quiet

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

required_fields = ['state_of_residence', 'month', 'month_code', 'year_code', 'sex_of_infant', 'births']
missing_fields = [field for field in required_fields if field not in df.columns]

if missing_fields:
    st.error(f"Missing logical fields: {missing_fields}")
    st.write(df.columns)
    st.stop()

df['births'] = pd.to_numeric(df['births'], errors='coerce')
df = df.dropna(subset=['births'])

months = ["All"] + sorted(df['month'].astype(str).unique().tolist())
genders = ["All"] + sorted(df['sex_of_infant'].astype(str).unique().tolist())
states = ["All"] + sorted(df['state_of_residence'].astype(str).unique().tolist())

selected_months = st.sidebar.multiselect("Select Month", options=months, default=["All"])
selected_genders = st.sidebar.multiselect("Select Gender", options=genders, default=["All"])
selected_states = st.sidebar.multiselect("Select State", options=states, default=["All"])

filtered_df = df.copy()

if "All" not in selected_months:
    filtered_df = filtered_df[filtered_df['month'].astype(str).isin(selected_months)]

if "All" not in selected_genders:
    filtered_df = filtered_df[filtered_df['sex_of_infant'].astype(str).isin(selected_genders)]

if "All" not in selected_states:
    filtered_df = filtered_df[filtered_df['state_of_residence'].astype(str).isin(selected_states)]

if filtered_df.empty:
    st.warning("Empty filter result.")
else:
    agg_df = filtered_df.groupby(['state_of_residence', 'sex_of_infant'], as_index=False)['births'].sum()
    agg_df = agg_df.sort_values(by='state_of_residence')

    fig = px.bar(
        agg_df,
        x='state_of_residence',
        y='births',
        color='sex_of_infant',
        title="Total Births by State and Gender",
        labels={'sex_of_infant': 'Gender'}
    )
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')

    st.plotly_chart(fig, width="stretch")

    st.dataframe(filtered_df.reset_index(drop=True))
