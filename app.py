%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from numerize import numerize
import locale
import babel.numbers
import mysql.connector

# SQL Server Connection
mydb=mysql.connector.connect(  
    host='localhost',
    user='root',
    password='',
)
mycursor=mydb.cursor(buffered=True)
mycursor.execute("USE Phonepe")

st.set_page_config(
    page_title="Phonepe Pulse",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# Title of page
title=st.title("Phonepe")

col1, col2, col3 = st.columns([1,1,1])

    

#Dropdown list State
# from SQL Database unique state list append in State Dropdown
mycursor.execute("SELECT DISTINCT State FROM agg_user")
c=mycursor.fetchall()
state=[]
for i in c:
    
    state.append(*i)
    
with col1 :    
    state_db_1 = st.selectbox('State',(state),key='State_drpdwn-1')    #Dropdown

# dropdown list for Quater
# from SQL Database unique state list append in Quater Dropdown
mycursor.execute("SELECT DISTINCT Quater FROM agg_user")

c=mycursor.fetchall()
quater=[]
for i in c:
    
    quater.append(*i)
with col1 :    
    quater_db_1=st.selectbox('Quater',(quater),key='Quater_drpdwn-1')
    
#dropdown list for Year
# from SQL Database unique state list append in Year Dropdown    
mycursor.execute("SELECT DISTINCT Year FROM agg_user")
c=mycursor.fetchall()
year=[]
for i in c:
    
    year.append(*i)
with col1 :    
    year_db_1=st.selectbox('Year',(year),key='Year_drpdwn-1')    

 
import plotly.express as px
# state_db_1=state_db_1.replace('-',' ')

mycursor.execute(f"SELECT * FROM top_transation WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1} ")

table_rows = mycursor.fetchall()

df = pd.DataFrame(table_rows,columns=['State','Year','Quater','District','District_count','District_amount'])
df['State']=df['State'].str.replace('-',' ')
df['Year']=df['Year'].astype(int)
df['Quater']=df['Quater'].astype(int)
# df['pincode']=df['pincode'].astype(int)
# df['District_count']=df['District_count'].astype(float)
# df['District_amount']=df['District_amount'].astype(float)



#Pincode Map Csv
map_df=pd.read_csv(r'C:\\Users\\91909\\firstprogram\\Phonepe\\zip_to_lat_lon_India_1.csv',low_memory=False)
map_df=map_df[map_df['Country']=='India']
map_df.drop(['state','place','statecode','province_or_countycode','community','communitycode','accuracy','Continent','Country','country code'],axis=1,inplace=True)
map_df.reset_index(drop=True,inplace=True)
map_df.rename(columns = {'province_or_county':'District','postal code':'pincode'}, inplace = True)
# map_df['state']=map_df['state'].apply(str)
# map_df['state']=map_df['state'].apply(str.lower)
map_df['District']=map_df['District'].apply(str)
map_df['District']=map_df['District'].apply(str.lower)
map_df['pincode'] = map_df['pincode'].drop_duplicates(keep='last')

map_df.dropna(axis=0,inplace=True)
map_df['pincode']=map_df['pincode'].astype(int)
map_df.reset_index(drop=True)

chart_data=df.merge(map_df,on='District', how='left')

chart=pd.DataFrame(chart_data)

chart.drop_duplicates(subset=['Year','Quater','District','District_count','District_amount'],keep='last',inplace=True)
chart.reset_index(drop=True,inplace=True)

chart1=chart.groupby(["District","latitude","longitude"])['District_amount'].sum().reset_index()

# st.dataframe(chart)
# with col2:    
#     st.pydeck_chart(pdk.Deck(
#          map_style=None,
#          initial_view_state=pdk.ViewState(
#              latitude=11.820233628491849,
#              longitude=79.27937299999995,
#              zoom=4,      
#              pitch=50,
#           ),
#          layers=[
#               pdk.Layer(
#                    'HexagonLayer',
#                    data=chart1,
#                    get_position=['longitude', 'latitude'],
#                    get_color=[200, 30, 0, 160],
#                    get_radius=200,
#                    auto_highlight=True,
#                    elevation_scale=50,
#                    pickable=True,
#                    elevation_range=[0, 3000],
#                    extruded=True,
#                    coverage=1,
#                 ),
            
#          ],
#      ))
    
# Transaction Details

with st.sidebar:
    

        st.markdown(
        f'''
            <style>
                .sidebar .sidebar-content {{
                    width: 375px;
                }}
            </style>
        ''',
        unsafe_allow_html=True
         )
        st.markdown(f'<div style="font-size: 25px;color:#00FFFF;"><b>Transactions</b></div>', unsafe_allow_html=True)
        mycursor.execute(f"SELECT sum(Transacion_count) FROM agg_trans WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1}")

        for i in mycursor:

            s=babel.numbers.format_currency(int(*i), 'INR', locale="en_IN")   
            st.metric(label="All PhonePe transactions (UPI + Cards + Wallets)",value=s)

        #Total payment value
        mycursor.execute(f"SELECT sum(Transacion_amount) FROM agg_trans WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1}")

        for i in mycursor:

    #         s=babel.numbers.format_currency(int(*i), 'INR', locale="en_IN")  
            i=int(*i)
            value = i / 10000000

            humanized = locale.format('%d', value, grouping=True)
            s = humanized + ' ' + 'Cr'
            st.metric(label="Total payment value",value=s)

            st.markdown(f'<div style="font-size: 25px;color:#00FFFF;"><b>Categories</b></div>', unsafe_allow_html=True)

    
        mycursor.execute(f"""SELECT Transacion_type, sum(Transacion_count) 
             FROM agg_trans WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1} GROUP BY Transacion_type order by count(Transacion_count) """)

        table_rows = mycursor.fetchall()
        st.write(" ")   
        for i,j in table_rows:

            s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 

            st.write(i)
    #         trans_type=st.write(s)
            st.markdown(f'<div style="text-align: right;margin-top:-39px">{s}</div>', unsafe_allow_html=True)
  
        tab1, tab2,= st.tabs(["District", "Pincodes"]) 
        with tab1:
            st.markdown(f'<div style="font-size: 25px;color:#00FFFF;"><b>Top 10 District </b></div>', unsafe_allow_html=True)
            mycursor.execute(f"""SELECT District, sum(District_count) FROM top_transation 
             WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1} GROUP BY District order by count(District_count) """)
            table_rows = mycursor.fetchall()
            st.write(" ")   
            for i,j in table_rows:

        #         s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 
                st.write(i)

                j=int(j)
                s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 

                st.markdown(f'<div style="text-align: right;margin-top:-39px">{s}</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown(f'<div style="font-size: 25px;color:#00FFFF;"><b>Top 10 Pincodes </b></div>', unsafe_allow_html=True)
            mycursor.execute(f"""SELECT pincodes,p_registeredUsers FROM top_users 
             WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1} GROUP BY pincodes order by sum(p_registeredUsers) """)
            table_rows = mycursor.fetchall()
            st.write(" ")   
            for i,j in table_rows:

        #         s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 

        #         s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 
                st.write(i)

                j=int(j)
                s=babel.numbers.format_currency(int(j), 'INR', locale="en_IN") 

                st.markdown(f'<div style="text-align: right;margin-top:-39px">{s}</div>', unsafe_allow_html=True)

mycursor.execute(f"SELECT * FROM top_transation WHERE State='{state_db_1}' AND Year='{year_db_1}' AND Quater={quater_db_1} ")
data=mycursor.fetchall()
result = pd.DataFrame(data,columns=['state','Year','Quater','District','District_count','District_amount'])

label=result.groupby('District')['District_count','District_amount'].sum().reset_index()

    
s=label['District_amount'].apply(lambda x: (babel.numbers.format_currency(float(x), 'INR', locale="en_IN") ))
see=label['District_count'].apply(lambda x: (babel.numbers.format_currency(float(x), 'INR', locale="en_IN") ))

fig=px.bar(label,x='District',y=s,color='District',hover_data=[see],
           labels={'District_count':'All Transaction','y':'Total payment value','hover_data_0':'All Transaction'})  
fig.update_layout(
    yaxis= {'title': 'y-axis',
         'visible': False,
         'showticklabels': False},
)
st.write(fig)
