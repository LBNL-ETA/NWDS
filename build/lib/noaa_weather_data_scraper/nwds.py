# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:41:59 2018

@author: benoi
"""
# version with quality check and save by zip
import numpy as np
import pandas as pd
import datetime as dt
import time
import requests
import pytz
import os
from math import radians, cos, sin, asin, sqrt, floor
import geocoder
import argparse

ddf = {}
memory_df = {}
memory_NS_DO = {}
accurate_quality = 1
quality_rule = 85
temp_format = 'F'
df = pd.read_csv("ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv", sep=",", usecols=['USAF','WBAN', 'STATION NAME', 'CTRY', 'STATE', 'LAT', 'LON'])



def Set_dict_DF(FD, LD):
    """ Set up a memory dictionnary for each year of the instance
        This method protect the data from the difference between years
        Some weather  stations are bad for some years but good for someothers.
        Thus if we delete the bad weather station for the instance year we win on the computer time
            - FD : first date
            - LD : last date
    """
    global ddf
    global df
    for d in range(FD.year-1, (LD.year + 2)):
        #if year isn't already in the key list of the dictionnary
        if(d not in ddf.keys()):
            #Generate a new instance of df in the dictionnary with a link year key
            ddf[d] = df
    
def Date_calibration(DD, s, TZ):
    
    """ Adjust the time difference for the parameter timezone
            - DD : Datetime
            - s : switch mode
            - TZ : timezone
            
        The weather data from NOAA is based on UTC time
    """
    
    dif_hour_tz = dt.datetime.now(tz=pytz.timezone(str(TZ))).hour - dt.datetime.now(tz=pytz.utc).hour
    #If s = 1 = True
    if(s):
        #Change the datetime to UTC
        DD = DD - dt.timedelta(hours=dif_hour_tz)
    else:
        #Change the datetime to the original time
        DD = DD + dt.timedelta(hours=dif_hour_tz)
        
    return DD

def Distance_orthonormique(lon1, lat1, lon2, lat2):
    
    """ Calcute the distance between to location point by longitude and latitude
            - lon1 : longitude location 1
            - lat1 : latitude location 1
            - lon2 : longitude location 2
            - lon2 : longitude location 2
    """
    
    #Convert position in radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    #rvmT = Earth radius [km]
    rvmT = 6371 
    #Project the position on
    a = sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
    c = 2 * asin(sqrt(a)) 
    
    d = c *  rvmT
    return d

def GeoLocZip(zip_code, cntry):

   """ Geo locate "zip_code" with specific country (cntry)
           - zip_code : zip code
           - cntry : country
       (GeoLocZip use OpenStreetMap API via geocoder (geocoder.osm)
   """
   nb_error = 0
   #Try connection with OSM server
   while(nb_error < 100):
       try :
           #connection succeed
           time.sleep(1)
           g = geocoder.osm(str(zip_code)+' '+str(cntry))
           break
       except:
           #connection failed
           #try again
           nb_error += 1
           print("error req - nb_error : "+str(nb_error))
           continue
    #g.osm['x'] = longitude
    #g.osm['y'] = latitude
   return g.osm['x'], g.osm['y']


def Fetch_station(long, lat, y):
    
    """ Fetch the weather station with the smaller distance from the zip code location
            - long : longitude
            - lat : latitude
            - y : year
    """
    global ddf
    dmin = 1000000
    rs = 0
    i=0
    for i in range(len(ddf[y])):
        #Calculate the distance between zip code location and weather station location
        dnew = Distance_orthonormique(ddf[y]['LON'][i], ddf[y]['LAT'][i], long, lat)

        if(dmin > dnew):
            #If the last smaller distance is superior than the current distance :
                #the new smaller distance is the current distance
            dmin = dnew
            rs = i

    #rs = index dataframe weather station
    #ddf[y]['STATION NAME'][rs] = Weather station name
    #round(dmin, 2) = Distance between weather station and zip code
    
    return rs, ddf[y]['STATION NAME'][rs], round(dmin,2)

def Data_formatting(dz, y, timestep, TZ):
    
    """ Clean and format the data
            - dz : original data
            - y : specified year
            - timestemp : specified timestemp
            - TZ : specified timezone
    """
    
    #reindex data by datetime
    dz.index = pd.to_datetime(dz['DATE'])
    
    #Isolate temperature data
    dz = dz[['TMP']]
    
    #Delete data mistake
    dz = dz[dz['TMP'] != "+9999,9"]
    
    #Format data
    dz['TMP'] = dz['TMP'].str.replace(',', '.')
    dz['TMP'] = pd.to_numeric(dz['TMP'], errors='coerce')
    
    #Delete NaN data
    dz = dz.dropna()
    
    #Convert temperature
    dz['TMP'] = dz['TMP'] / 10
    dz['TMP'] = dz['TMP'] * (9/5) + 32
        
    #Convert datetime index utc to specified timezone
    dz.index = dz.index.tz_localize(pytz.utc).tz_convert(pytz.timezone(str(TZ))).strftime("%Y-%m-%d %H:%M:%S")
    dz.index = pd.to_datetime(dz.index)
    
    #Resample data by average on timestep
    dz = dz.resample(rule = str(timestep)).mean()
    
    #Define the first date of the instance year
    fdy = dt.datetime.strptime("01/01/"+str(y)+" 00:00", '%m/%d/%Y %H:%M')
    #Convert first date of the year to timezone
    fdy = Date_calibration(fdy, 0, TZ)
    
    #If we collect the date from the current year we limit the collect from 2days before now
    
    #Define the datetime 2 days before now
    dbeyest = dt.datetime.now(tz=pytz.timezone(str(TZ))) - dt.timedelta(days=2)
    
    #If the instance year is the current year
    if(y == dbeyest.year):
        #We limit the collect 2 days before now
        ldy = dt.datetime.strptime(str(dbeyest.month)+"/"+str(dbeyest.day)+"/"+str(y)+" 23:59", '%m/%d/%Y %H:%M')
    else:
        #Else, we collect the full year
        ldy = dt.datetime.strptime("12/31/"+str(y)+" 23:59", '%m/%d/%Y %H:%M')
    
    #Convert the last date of the year to specified timezone
    ldy = Date_calibration(ldy, 0, TZ)
    
    #Set up dataframe for the specified datetime index and timestep
    ph = pd.DataFrame(index=pd.DatetimeIndex(start=fdy, end=ldy, freq=str(timestep)))
    
    #Past original data temperature in the time fitted dataframe (with the datetimeindex position)
    ph['TMP'] = dz['TMP']
    
    #Calculate the quality of the instance data
    nb_nan = ph['TMP'].isnull().sum()
    qual = (1 - (nb_nan) / len(ph)) * 100
 
    return dz, qual
    


def Collect_data(clo, cla, FD, LD, ZC, idx_time, cntry, TZ):
    
    """ Collect the weather data (main function)
        - clo : longitude
        - cla : latitude
        - FD : first date
        - LD : last date
        - ZC : zip code
        - idx : index time (if specified)
        - cntry : country
        - TZ : timezone (pytz)
    """
    #initiate the console response
    rep = ""
    global ddf
    
    #define the noaa server access
    server_noaa = "https://www.ncei.noaa.gov/data/global-hourly/access/"
    
    #Initate dateframe
    data = pd.DataFrame()
    
    #Convert date from specified timezone to UTC
    FDc = Date_calibration(FD, 1, TZ)
    LDc = Date_calibration(LD, 1, TZ)
    
    #define timestep
    timestep = "1 H"
    
    #Loop on the range time by each year
    for y in range(FDc.year, (LDc.year + 1)):
        rep += '--- Collect Year ['+str(y) + '] --- \n' 
        
        #Loop on each weather station while the ouput data is good
        #weather station in the year instancied dataframe  
        for i in range(len(ddf[y])) :
              
            #Define the memory key : year_zipcode
            key_d_z = str(y)+'_'+str(ZC)
            
            #Verify if the data is already in the memory
            if(key_d_z in memory_df.keys()) :
                #The data is already in the memory :
                #Collect the data and go next (save compute time and server solicitation)
                ext_data = memory_df[key_d_z]
                NS, DO = memory_NS_DO[key_d_z].split('_')[0], memory_NS_DO[key_d_z].split('_')[1]
                break
            else:
                
                #The data isn't in the memory :
                
                #Collect information about the nearest weather station from the zip code
                rs, NS, DO = Fetch_station(clo, cla, y)
                
                #Generate the ftp key weather station
                code_station = str(ddf[y]['USAF'][rs])+str(ddf[y]['WBAN'][rs])
                
                #Define the server access
                url = server_noaa+str(y)+'/'+code_station+'.csv'
                
                #Get the data
                req = requests.get(url)
                
                #The server answer
                if(req.status_code == 200):
                    
                    #Extract the data (only date and temperature)
                    ext_data = pd.read_csv(url, usecols=['DATE','TMP'])
                    
                    #Check if the data isn't empty (1000 is arbitrary)
                    if(len(ext_data) > 1000):
                        
                        #Format data
                        ext_data, qual = Data_formatting(ext_data, y, timestep, TZ)
                        
                        #Check if the data quality respect the quality rule
                        if(qual > quality_rule):
                            
                            #Save the date in the memory
                            memory_df[key_d_z] = ext_data
                            memory_NS_DO[key_d_z] = str(NS)+'_'+str(DO)
                            
                            #Response for the GUI
                            rep += "# Station ["+str(NS)+"] valid : \n"
                            rep += "- Quality density data : "+str(round(qual, 2))+"% \n"
                            rep += "- Great circle distance : "+str(round(DO,2))+"km \n"
                            break
                        else:
                            #The data quality is too bad
                            #Response for the GUI
                            rep += "# Station ["+str(NS)+"] invalid : \n"
                            rep += "- Quality density data : "+str(round(qual,2))+"% \n"
                            rep += "> Quality criterion unsatisfied \n"
                            
                            #Delete the weather station in the dataframe (instancied by year)
                            ddf[y] = ddf[y].drop(rs).reset_index(drop=True)
                            continue
    
                    else:
                        #The data density is too low
                        
                        #Response for the GUI
                        rep += "# Station ["+str(NS)+"] invalid : \n"
                        rep += "> Low data volume \n"
                        
                        #Delete the weather station in the dataframe (instancied by year)
                        ddf[y] = ddf[y].drop(rs).reset_index(drop=True)

                        continue
                else:
                    #The NOAA doesn't answer for the code station
                    rep += "# Station ["+str(NS)+"] invalid : \n"
                    rep += "> Server doesn't answer\n"
                    
                    #Delete the weather station in the dataframe (instancied by year)
                    ddf[y] = ddf[y].drop(rs).reset_index(drop=True)

                    continue
        #Add data in the Dataframe
        data = data.append(ext_data)
    
    #Define a new dataframe mark out by the specified time range
    range_time = pd.DataFrame(index=pd.DatetimeIndex(start=FD, end=LD, freq=timestep))
    
    #Paste data in the time marked out Dataframe
    range_time['Temp'] = data['TMP']
    
    #Calculate the amount of NaN (global)
    nb_nan = range_time['Temp'].isnull().sum()
    
    #Calculate the global quality
    quality = (1 - (nb_nan) / len(range_time)) * 100
    
    #Fill the gap data by temporal interpolation
    data = range_time.interpolate(method='time')
    data = data.ffill().bfill()
    data['Temp'] = round(data['Temp'], 2)
    
    
    #If specified index time, cut the data for it
    if(len(idx_time)> 2):
        final_data = pd.DataFrame(index = pd.to_datetime(idx_time))
        final_data['Temp'] = round(data['Temp'], 2)
        #final_data = final_data.resample(rule = str(timestep)).mean()
        #final_data = final_data.dropna()
    else:
        final_data = data
    
    return final_data, quality, NS, DO, rep



# ### CONSOLE MODE ###
if __name__ == "__main__":
    
    """ Define input argument :
        -m : mode (zip / rmv2.0)
        -fd : first date (%m/%d/%y %H:%M)
        -ld: last date (%m/%d/%y %H:%M)
        -tz : pytz timezone
        -cty : country (United states, US, USA)
        -zip : zip code
        -of : output folder (C:/...)
        -if : input_folder (C:/...)
        
        Mode "zip"  :: Neccessary's arguments :
            -m
            -fd
            -ld
            -tz
            -cty
            -zip
            -of
        Mode "rmv2.0 :: Neccessary's arguments :
            -m
            -tz
            -of
            -if
        
    """
    parser = argparse.ArgumentParser(prog='./scrape_ftp_noaa.py')
    parser.add_argument('-m', '--mode', nargs='+', type=str)
    parser.add_argument('-fd', '--first_date', nargs='+', type=str)
    parser.add_argument('-ld', '--last_date', nargs='+', type=str)
    parser.add_argument('-tz', '--time_zone', nargs='+', type=str)
    parser.add_argument('-cty', '--country', nargs='+', type=str)
    parser.add_argument('-zip', '--zip', nargs='+', type=str)
    parser.add_argument('-of', '--output_folder', nargs='+', type=str)
    parser.add_argument('-if', '--input_folder', nargs='+', type=str)
    args = parser.parse_args()
    
    
    if(args.mode[0] == "zip"):
        
        #Format date (%m/%d/%y + %H:%M)
        a_fd = str(args.first_date[0])+" "+str(args.first_date[1])
        a_ld = str(args.last_date[0])+" "+str(args.last_date[1])

        #Check error        
        nb_error = 0
        msg_error = ""
        try:
            first_date = dt.datetime.strptime(str(a_fd), '%m/%d/%y %H:%M')
        except:
            nb_error += 1
            msg_error += "First Date format invalid (use : -fd  %m/%d/%y %H:%M) \n"
        try:
            last_date = dt.datetime.strptime(str(a_ld), '%m/%d/%y %H:%M')
        except:
            nb_error += 1
            msg_error += "Last Date format invalid (use : -ld  %m/%d/%y %H:%M) \n"
        if(args.time_zone[0] == ""):
            nb_error += 1
            msg_error += "Time zone unspecified (use : -tz timezone ) \n"
        if(args.country[0] == ""):
            nb_error +=1
            msg_error += "Country unspecified (use : -cty country) \n"
        if(len(args.zip[0]) < 5):
            nb_error += 1
            msg_error += "Invalid zip code (use : -zip 00000) \n"
        if(args.output_folder[0] == ""):
            nb_error +=1
            msg_error += "Unspecified output folder (use : -of C:/...) \n"
        if(nb_error == 0):
            
            #Collect longitude and latitude from the zip code
            zlo, zla = GeoLocZip(args.zip[0], args.country[0])
            
            #Set up the dataframe dictionnary
            Set_dict_DF(first_date, last_date)
            
            #Collect the data and some informations 
                #data = weather data
                #NS = Name station
                #DO = Great circle distance
                #rep = Response for the GUI/Console
            data, quality, NS, DO, rep = Collect_data(zlo, zla, first_date, last_date, args.zip[0], "", args.country[0], args.time_zone[0])
            final_data = pd.DataFrame()
            final_data['time'] = data.index.strftime('%m/%d/%y %H:%M')
            final_data['Temp'] = data.Temp.values
            #Save the in the output folder
            final_data.to_csv(str(args.output_folder[0])+"/"+str(args.zip[0])+".csv")
            print("Collect finish : Global quality = "+str(quality))
        else:
            print("Error ("+str(nb_error)+") : ")
            print(msg_error)
            
    elif(args.mode[0] == "rmv2.0"):
        
        #Check error
        nb_error = 0
        msg_error = ""
        if(args.time_zone[0] == ""):
            nb_error += 1
            msg_error += "Time zone unspecified (use : -tz timezone ) \n"
        if(args.output_folder[0] == ""):
            nb_error +=1
            msg_error += "Unspecified output folder (use : -of C:/...) \n"
        if(args.input_folder[0] == ""):
            nb_error +=1
            msg_error += "Unspecified input folder (use : -if C:/...) \n"
        if(nb_error == 0):
            try : 
                in_fold = os.listdir(str(args.input_folder[0]))
            except:
                print("Error : Invalid input folder")
                
            if(len(in_fold) >= 1):
                for f in in_fold:
                    if('.csv' in f):
                        print('### Input File = '+str(f)+' ### \n')
                        if('.csv' in f):
                            
                            #Collect the input data
                            db = pd.read_csv(str(args.input_folder[0]+'/'+f))
                            
                            #Collect data informations
                            zip_code = db.iloc[0, 1]
                            cntry = db.iloc[0, 2]
                            
                            #Collect longitude and latitude from the zip code
                            zlo, zla = GeoLocZip(zip_code, cntry)
                            
                            #Collect date
                            first_date = dt.datetime.strptime(db.iloc[2,0], '%m/%d/%y %H:%M')
                            last_date = dt.datetime.strptime(db.iloc[-1,0], '%m/%d/%y %H:%M')
                            
                            #Set up the dataframe dictionnary
                            Set_dict_DF(first_date, last_date)
                            
                            print('## Collect weather data = [zip code: '+str(zip_code)+']['+str(cntry)+'] ##\n')
                            print('# Got Location = [lon : '+str(round(zlo,3))+'][lat : '+str(round(zla,3))+']\n')
                                  
                            #Collect the data and some informations 
                                #data = weather data
                                #NS = Name station
                                #DO = Great circle distance
                                #rep = Response for the GUI/Console
                            data, quality, NS, DO, rep = Collect_data(zlo, zla, first_date, last_date, zip_code, db['buildingID'][2:].values,cntry, args.time_zone[0])
                            print(rep)
                            
                            #Format the output data (put temperature and set up the rmv2.0 model)
                            df_fil = pd.DataFrame()
                            df_fil['time'] = data.index.strftime('%m/%d/%y %H:%M')
                            df_fil['eload'] = db['zip'][2:].values
                            df_fil['Temp'] = data['Temp'].values
                            
                            #Save data in the output folder
                            df_fil.to_csv(str(args.output_folder[0])+'/'+f, index=False)
                            print('# Global quality = '+str(round(quality, 2))+'% \n')
                            print('### Output File = '+str(f)+' ### \n \n')
                            time.sleep(1)
            else:
                print("Invalid or empty input folder")
    else:
        print('Invalid mode. (mode = "zip" or "rmv2.0")')