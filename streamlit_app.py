import pandas as pd
import io 
import requests 
import streamlit as st 
import plotly.express as px


header = st.container()
user_input = st.container()
output_graphs = st.container()

with header:
    st.title("USA Covid-19 Dashboard")
    st.markdown("""
    This is an interavtive application to track the number of daily covid-19 cases, death counts and the moving average for every state and county in the United States.
    Select the state and county from the dropdown menu to view its covid-19 statistics. 
    """)

# Fetch Dataset from the New York Times Github Repository
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')), parse_dates=True, index_col='date')

with user_input:
    st.sidebar.header('User Selection') 

    # Generating the list for states
    states_list = []
    counties_list = []

    states_list = df.state.unique()
    states_list.sort()

    select = st.sidebar.selectbox('Choose Bar Chart',['Total Cases','Total Deaths'],key='2')

    state = st.sidebar.selectbox('State:',states_list) # We define the state variable
    
    df_states = df[(df.state == state)].copy()
    counties_list = df_states.county.unique()
    conties_list = counties_list.sort()
    us_state_abbrev = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}
    
    df_total0 = df.groupby(['state', 'county']).max()
    #df_total = df_total.to_frame()
    df_total0.reset_index(level=0, inplace=True)
    df_total = df_total0.groupby('state').sum()
    df_total.reset_index(level=0, inplace=True)
    df_total['state'] = df_total['state'].map(us_state_abbrev).fillna(df_total['state'])
    

    county = st.sidebar.selectbox('County:',counties_list) 

    num_states = st.sidebar.slider('Number of states to be displayed in bar graph. ', min_value = 1, max_value= 50, value= 10, step=1)
    table_days = st.sidebar.slider('Number of days to be displayed in Summary Statistics. ', min_value = 3, max_value= 20, value= 7, step=1)

    moving_average_day = st.sidebar.slider('Number of days for moving average', min_value = 5, max_value = 20, value = 7, step=1)

    # Creating the dataframe for the county
    df_county = df[(df.county == county)& (df.state == state)].copy()

    #Create a new column with new cases
    df_county['New Cases'] = df_county.loc[:, 'cases'].diff()

    #Create a new column for 7-day moving average
    df_county['Moving Average'] = df_county.loc[:,'New Cases'].rolling(window=moving_average_day).mean()
    df_county['deaths'] = df_county['deaths'].astype(int)
    df_county1 = df_county.rename(columns={'cases': 'Total Cases', 'deaths': 'Total Deaths'})

with output_graphs:
    st.subheader(f'Total number of cases vs Total number of deaths for {num_states} states')
    st.markdown("""Select number of states to be displayed from the user selection menu""")
    df_total2 = df_total.sort_values(by=['cases'], ascending=False)
    df_total2 = df_total2.head(num_states)
    plot = px.scatter(data_frame = df_total2, x = 'cases', y = 'deaths', color = 'state', size = 'cases')
    st.plotly_chart(plot)

    st.markdown("""""")
    if select == "Total Cases": 
        st.subheader(f'Top {num_states} states with highest number of covid-19 cases')
        st.markdown("""Choose bar chart type from user selection menu""")
        df_total = df_total.sort_values(by=['cases'], ascending=False)
        fig = px.bar(df_total.head(num_states), y='cases',x='state',color='state',height=400)
        fig.update_layout(xaxis_title='State',yaxis_title='Total Cases',template="plotly_dark")
        st.plotly_chart(fig)
           
           
           
    elif select == "Total Deaths":
        st.subheader(f'Top {num_states} states with highest number of deaths')
        st.markdown("""Choose bar chart type from user selection menu""")
        df_total = df_total.sort_values(by=['deaths'], ascending=False)   
        fig = px.bar(df_total.head(num_states), y='deaths',x='state',color='state',height=400)
        fig.update_layout(title=f'Top {num_states} states highest number of COVID-19 deaths',xaxis_title='Country',yaxis_title='Total deaths',template="plotly_dark")
        st.plotly_chart(fig)

    a = df_county1.iloc[-table_days:, -4:]
    st.header(f'Summary Table for the last {table_days} days for {county} county')
    st.markdown(""" Number of cases, deaths, new cases and moving average for the selected county.""")

    my_table = st.table(a)
    #t1 = st.table(df_total)

    st.header(f'Total Cases for {county}, {state}.')
    
    total_cases_chart = df_county['cases']
    
    st.line_chart(total_cases_chart)

    st.header(f'{moving_average_day} day moving average for {county}, {state}.')
    
    moving_average_chart = df_county['Moving Average']
    
    st.line_chart(moving_average_chart)

    

