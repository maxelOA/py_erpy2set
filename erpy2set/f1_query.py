# -*- coding: utf-8 -*-
"""f1_query

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rc_1TlCs0FoAnME0JWuSSEegg_05m_9F

# **Paqueterias**
"""

import erpy2set.unravel as un
import requests as r
import json 
import pandas as pd
import numpy as np

"""# **QUERY PACK**


"""

########################################
##### recupera la tabla de laps  ####### v1.1
########################################

def laps_tbl(year):

  data=pd.DataFrame()
  n=num_races(year)

  for j in list(range(1,n+1)):
    k=max_laps(year,j)
    
    for i in list(range(1,k+1)):
        try:
            url=f'http://ergast.com/api/f1/{year}/{j}/laps/{i}.json'
            aux_data=pd.DataFrame(r.get(url).json()['MRData']['RaceTable']['Races'][0]['Laps'][0]['Timings'])
            aux_data[['lap','raceId']]=[i,j]
            data=data.append(aux_data)
        except:
            i+=1
  return data

########################################
#### recupera la tabla de pitstops  #### v1.1
########################################

def pitstops_tbl(year):

  data=pd.DataFrame()
  n=num_races(year)

  for i in list(range(1,n+1)):

    try:
      url=f'http://ergast.com/api/f1/{year}/{i}/pitstops.json'
      aux_data=pd.DataFrame(r.get(url).json()['MRData']['RaceTable']['Races'][0]['PitStops'])
      aux_data['raceId']=i
      data=data.append(aux_data)
    except:
      i+=1
  return data

########################################
# recupera la tabla de constructorResults  v1.1
########################################

def constructorResults_tbl(year):

  data=pd.DataFrame()
  n=num_races(year)

  for i in list(range(1,n+1)):

      url=f'https://ergast.com/api/f1/{year}/{i}/results.json'

      aux_data=pd.DataFrame(r.get(url).json()['MRData']['RaceTable']['Races'][0]['Results'])
      aux_data=aux_data[['Constructor','points','status']]
      un.unravel_noKey(aux_data)

      aux_data['raceId']=i
      data=data.append(aux_data)

  return data

########################################
#calcula en numero de vultas por carrera  v1.1
########################################

def max_laps(year,number_race):

  url=f'https://ergast.com/api/f1/{year}/{number_race}/results.json'
  data=r.get(url).json()
  rslts=pd.DataFrame(data['MRData']['RaceTable']['Races'][0]['Results'])['laps'].astype(int)
  
  return max(rslts)

############################################
#calcula en numero de carreras por temporada  v1.1
############################################

def num_races(year):
  races=pd.DataFrame()

  url=f'https://ergast.com/api/f1/{year}/races.json'
  data=r.get(url).json()
  races=pd.DataFrame(data['MRData']['RaceTable']['Races'])

  return len(races.axes[0])

############################################
# Regresa la cuerda con la primer letra Mayuscula  v1.1
############################################

def firstCap(string_toCap):
  cap=string_toCap[0].capitalize()

  adj_string=cap+string_toCap[1:]

  return adj_string

############################################
#    Ajusta el nombre de las tablas v1.1
############################################

def adj_name(tbl_name):

  if tbl_name == 'qualifyingResults':
    return 'qualifying'
  elif tbl_name == 'sprintResults':
    return 'sprint'
  else:
    return tbl_name

############################################
#   Regrasa la tabla consultada Parent_child v1.1
############################################

def raw_table(table_name,year):
  Df=pd.DataFrame()
  
  dimension_tables={'seasons':'SeasonTable','drivers':'DriverTable','constructors':'ConstructorTable','circuits':'CircuitTable','status':'StatusTable','races':'RaceTable'}
  fact_tables={'driverStandings':['StandingsTable','StandingsLists'],'results':['RaceTable','Races'],'qualifyingResults':['RaceTable','Races'],'constructorStandings':['StandingsTable','StandingsLists'],'sprintResults':['RaceTable','Races']}

  depend_races=['pitstops','laps']
  depend_results=['constructorResults']

  total_races=num_races(year)
  tbl_names= list({**fact_tables,**dimension_tables})+depend_races+depend_results

  if table_name in tbl_names:
    
    
    if table_name in dimension_tables:

     url=f'https://ergast.com/api/f1/{year}/{adj_name(table_name)}.json'
     data=r.get(url).json() 

     locations=dimension_tables[table_name]
     Df=pd.DataFrame(data['MRData'][locations][firstCap(table_name)])

     un.unravel_noKey(Df)

    elif table_name in fact_tables:

      for i in list(range(1,total_races+1)):
        try:
           url=f'https://ergast.com/api/f1/{year}/{i}/{adj_name(table_name)}.json'
           data=r.get(url).json() 

           locations=fact_tables[table_name]
           aux_Df=pd.DataFrame(data['MRData'][locations[0]][locations[1]][0][firstCap(table_name)])
           un.unravel_noKey(aux_Df)
           aux_Df['racesId']=i
           aux_Df['year']=year
        
           Df=Df.append(aux_Df)
        except:
           i+=1

    elif table_name in depend_races:

      if table_name =='pitstops':
           Df=pitstops_tbl(year)

      else:
           Df=laps_tbl(year)
      
    else:
     Df=constructorResults_tbl(year)
   
  else:
     print(f"{table_name} not found in the schema")

  return Df

############################################
#  Regrasa la tabla consultada del esquema v1.1
############################################

def clean_table(table_name,year):

  r_table=raw_table(table_name,year)
  #try:
    if table_name=='races':

        table=r_table[['season','round','Circuit_circuitId','raceName','Circuit_circuitName','date','time','url','FirstPractice_date','SecondPractice_date','ThirdPractice_date','Sprint_date']]
        table.columns=['season','round','circuitId','raceName','circuitName','date','time','url','FirstPractice_date','SecondPractice_date','ThirdPractice_date','Sprint_date']
        return table
        
    elif table_name=='results': 

         table=r_table[['racesId','year','Driver_driverId','Constructor_constructorId','number','grid','position','positionText','points','laps','Time_time','Time_millis','FastestLap_lap','FastestLap_rank','FastestLap_Time_time','FastestLap_AverageSpeed_speed','status']]
         table.columns=['raceId','season','driverId','constructorId','number','grid','position','positionText','points','laps','time','milliseconds','fastestLap','rank','fastestLapTime','fastestLapSpeed','status']
         return table
            
    elif table_name=='circuits':

         table=r_table[['circuitId','circuitName','Location_locality','Location_country','Location_lat','Location_long','url']]
         table.columns=['circuitId','circuitName','locality','country','lat','long','url']
         return table

    elif table_name=='constructorStandings':

         table=r_table[['racesId','Constructor_constructorId','points','position','positionText','wins']]
         table.columns=['raceId','constructorId','points','position','positionText','wins']
         return table
  
    elif table_name=='driverStandings':
     
         table=r_table[['racesId','Driver_driverId','points','position','positionText','wins']]
         table.columns=['raceId','driverId','points','position','positionText','wins']
         return table

    elif table_name=='qualifyingResults':

         table=r_table[['racesId','Driver_driverId','Constructor_constructorId','number','position','Q1','Q2','Q3']]
         table.columns=['raceId','driverId','constructorId','number','position','Q1','Q2','Q3']
         return table
    
    elif table_name=='sprintResults':
    
         table=r_table['racesId','Driver_driverId','Constructor_constructorId','number','grid','position',
               'positionText','points','laps','Time_time','Time_millis','FastestLap_lap',
               'FastestLap_Time_time', 'status']
         table.columns=['raceId','driverId','constructorId','number','grid','position',
               'positionText','points','laps','time','millis','fastestLap',
               'fastestLaptime','status']  
         return table
    else:
         return r_table
 # except:
   # return r_table
  

############################################
#  Regrasa la tabla consultada en un rango v1.1
############################################

def query_range(table_name,initial_date,final_date):

  Df=pd.DataFrame()

  for i in list(range(initial_date,final_date+1)):

      aux_Df=clean_table(table_name,i)
      Df=Df.append(aux_Df)

  

  return Df

############################################
#  Regrasa el esquema consultad en un rango v1.1
############################################

def full_schema(initial_date,final_date):
  tables=[]
  Df=pd.DataFrame()

  schema=['seasons','drivers','constructors','circuits','status','races','results','qualifyingResults','constructorResults','constructorStandings','driverStandings','pitstops','laps']

  for table in schema:

      Df=query_range(table,initial_date,final_date)
      tables.append(Df)
      print(f"table {table} is ready")

  print('full success at retrieving the schema')

  return dict(zip(schema, tables))

from datetime import time

def adj_type(table):
    
  print('adj_type still in develop')
  string_type=[]
  date_type=[]
  time_type=[]
  int_type=[]
  float_type=[]

