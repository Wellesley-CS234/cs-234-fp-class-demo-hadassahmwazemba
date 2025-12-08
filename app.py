import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit page config (must be the first Streamlit call)
st.set_page_config(
    page_title="African Articles Engagement",
    layout="wide",  # <- This makes it use full width
    initial_sidebar_state="expanded"
)


# Load / prepare data
# -----------------
# Option 1: Load from repo
try:
    df = pd.read_csv("data/african_dpdp.csv")
except FileNotFoundError:
    st.warning("Default CSV not found. Please upload your own file.")
    uploaded_file = st.file_uploader("Upload your CSV", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.stop()

st.title("Engagement with Africa-Related Articles on the English Wikipedia")

#st.dataframe(df.head())

########
# Visualization to  see the number of page views per Region
########

#getting the year of the dates

df['year'] = df['date'].apply(lambda x: x.split('-')[0])

st.write("## A sample of what the data looks like")
st.dataframe(df.head())

###########
## Group into regions by country
#######
filtered_df = df.groupby(['region', 'year'])['views'].sum().reset_index()

#st.dataframe(filtered_df)

###########
## Normalize the data per capita
###########

#dropping duplicates (NB : will fix cause some of the countries are not in 2024)
unique_countries = df.drop_duplicates(subset=['country', 'year'])

#getting the total populations first
population_df = unique_countries.groupby(['region','year'])['population'].sum().reset_index()

merged_df = filtered_df.merge(population_df, how='right')

st.dataframe(merged_df)

#calculate the pageviews per capita (1000)
merged_df['views_per_capita']  = merged_df['views'] / df['population'] * 1000000

#zscore
merged_df["views_zscore"] = (
    merged_df["views_per_capita"] - merged_df["views_per_capita"].mean()
) / merged_df["views_per_capita"].std()

st.dataframe(merged_df)


###########
## Visualization
##########

st.header("Analysis of Pageviews Per Capita Per Year")

year = st.selectbox('Choose a year:', ['2023','2024'])

if year:
    year_df = merged_df[merged_df['year'] == year]

regions = st.multiselect('Filter by region:', ['Americas','Asia','Africa','Europe', 'Oceania'], default=['Americas','Asia','Africa','Europe', 'Oceania'])

regions_df = year_df[year_df['region'].isin(regions)]

regions_df = regions_df.sort_values(by="views_per_capita", ascending=False)

st.dataframe(regions_df)


#Plot the barplot


fig = px.bar(regions_df,
             x=regions_df['region'],
             y=regions_df['views_per_capita'],
             color= regions_df['region'],
             title = 'Pageviews Per Capita Per Year')

fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Pageviews per capita",
    )

st.plotly_chart(fig, use_container_width=True)

