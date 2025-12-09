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
st.write('By Hadassah Mwazemba')

st.write("This analysis examines the interaction of users on the English Wikipedia with African-Related articles. "
         "The data used is from the 2023-2024 Wikipedia DPDP dataset. "
         "The analysis examines articles that had more than 1000 views per day from the mentioned dataset.")

st.divider()

st.subheader("Research Question")
st.write("What is the engagement of African-related Wikipedia articles in the English Wikipedia outside of Africa?")

st.subheader("Hypothesis")
st.write("My hypothesis is that American and European countries have the highest \
         engagement with these articles in terms of pageviews")

st.divider()

st.header("Data Used For The Analysis")
st.write("This dataset was produced by getting Articles from Wikiproject:Africa and extracting their corresponding QIDs. \
         These QIDs were then used to extract the variables needed for this analysis from the DPDP set. \
         A preview of the dataset is provided below ")


is_toggle = st.toggle("View data snippet (first 50 rows) ")

if is_toggle:

    df = df.drop(columns=["Unnamed: 0", "Unnamed: 0.1"], errors="ignore")

    st.dataframe(df.head(50))

st.divider()

########
# Visualization to  see the number of page views per Region
########

#getting the year of the dates

df['year'] = df['date'].apply(lambda x: x.split('-')[0])


###########
## Group into regions by country
#######
filtered_df = df.groupby(['region', 'year'])['views'].sum().reset_index()

###########
## Normalize the data per capita
###########

#dropping duplicates (NB : will fix cause some of the countries are not in 2024)
unique_countries = df.drop_duplicates(subset=['country', 'year'])

#getting the total populations first
population_df = unique_countries.groupby(['region','year'])['population'].sum().reset_index()

merged_df = filtered_df.merge(population_df, how='right')

#calculate the pageviews per capita (1000)
merged_df['views_per_capita']  = merged_df['views'] / df['population'] * 1000000

#zscore
merged_df["views_zscore"] = (
    merged_df["views_per_capita"] - merged_df["views_per_capita"].mean()
) / merged_df["views_per_capita"].std()



###########
## Visualization
##########

st.header("Analysis of Pageviews Per Capita")

year = st.selectbox('Choose a year:', ['2023','2024'])

if year:
    year_df = merged_df[merged_df['year'] == year]

regions = st.multiselect('Filter by region:', ['Americas','Asia','Africa','Europe', 'Oceania'], default=['Americas','Asia','Africa','Europe', 'Oceania'])

regions_df = year_df[year_df['region'].isin(regions)]

regions_df = regions_df.sort_values(by="views_per_capita", ascending=False)

#st.dataframe(regions_df)


#Plot the barplot


fig = px.bar(regions_df,
             x=regions_df['region'],
             y=regions_df['views_per_capita'],
             color= regions_df['region'],
             title = 'Pageviews Per Capita Per Year')

fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Pageviews per capita (1M)",
    )

st.plotly_chart(fig, use_container_width=True)




########
# Visualization to  see the number of page views per Country
########

#getting the year of the dates

df['year'] = df['date'].apply(lambda x: x.split('-')[0])


###########
## Group into regions by country
#######
filtered_df = df.groupby(['country', 'year'])['views'].sum().reset_index()

#dropping duplicates (NB : will fix cause some of the countries are not in 2024)
unique_countries = df.drop_duplicates(subset=['country', 'year'])

#getting the total populations first
# st.dataframe(unique_countries)

st.divider()
st.header("Most Viewed Articles Per Country")

year_select = st.selectbox('Choose a year:', ['2023','2024'], key='year_for_top25')

if year_select:
    df_year = df[df['year'] == year_select]

    country = st.selectbox('Choose a country', sorted(df_year['country'].dropna().unique()), key='country_for_top25')

    country_df = df_year[df_year['country'] == country]

    grouped = (
    country_df.groupby('article', as_index=False)['views'].sum()
    )

    # sorting
    top25 = grouped.sort_values('views', ascending=False).head(25)

    st.write(f"Most Viewed Articles in {country} for {year_select}")
    st.dataframe(top25[['article', 'views']])



