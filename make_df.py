# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 15:57:41 2022

@author: mm16jdc
"""

#need these two packages to read in the txt file.
from io import StringIO
import pandas as pd

#the following packages are only needed for simple plotting
import matplotlib.pyplot as plt
import cartopy.crs as ccrs



##plan:
#1. Read in the text file and split into separate storms by creating a list of storms,
#   by splitting the string on the word 'start'.

with open('etc-all-traj.txt') as f: #location and filename of our storm txt file.
    file = f.read()

storms = file.split('start')


#2. Loop through these storms and format into a pandas dataframe, which are stored in a list.
#   So we now have a list of dataframes, called 'dfs'.

dfs=[]
for storm in storms:
    if len(storm)>0: #accounting for bad lines (e.g. the first line of the file!).
        storm_io = StringIO(storm)
        df = pd.read_csv(storm_io,skiprows=1,
                         header=None,
                         #added a dummy 'blank' column to account for leading tab in the file.
                         names=['blank','info1','info2','lon','lat','y','m','d','h'], #this is the column names in your data: replace info1,info2 etc with what they actually mean, I couldn't remember and check I didn't get lat and lon the wrong way round!
                         sep='	'
                         )
        
        #this next line to convert some lons >180 to negatives (i.e. west of greenwich is optional)
        df['lon']=df['lon'].where(df['lon']<180,df['lon']-360)
        
        df=df.drop(columns=['blank']) #remove dummy column

        #adding header info to .storm_header in the data [e.g. try print(df.storm_header)]
        storm_header = 'start\t'+storm.split('\n')[0]
        df.storm_header = storm_header
        dfs.append(df)
     
        
#simple plotting using cartopy and matplotlib
def plot_storm(df):
    '''
    plot a storm track
    '''
    lons=df.lon
    lats=df.lat
    
    ax = plt.axes(projection=ccrs.PlateCarree()) #try a few different projections here depending on where the storm is. All on https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html
    ax.plot(lons,lats,transform=ccrs.PlateCarree()) #Plot the storm track
    ax.set_extent([min(lons)-1,max(lons)+1,min(lats)-1,max(lons)+1]) #play around with axes extent
    ax.coastlines() #Add Coastlines
    plt.savefig('example.jpg')
    #plt.show()
    
print(dfs[7].storm_header)
print(dfs[7])


#plot_storm(dfs[7])
    