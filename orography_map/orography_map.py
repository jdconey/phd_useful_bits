# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 19:19:12 2021

@author: mm16jdc

Script to make a map of the Earth's orography in a given region, using 
cartopy maps and rockhound.

Uses ETOPO data (doi: 10.7289/V5C8276M)
"""
import rockhound as rh
import matplotlib.pyplot as plt
import cmocean

import matplotlib.colors as colors
import numpy as np
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import cartopy


#truncate colormap to just the above the sea ones
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

# Load a version of the topography grid
grid = rh.fetch_etopo1(version="bedrock")

#make colormap
cmap=cmocean.cm.topo
new_cmap = truncate_colormap(cmap, 0.5, 1)
#new_cmap.set_under(color='white')

#bounds of our map
lat_min = 45
lat_max = 62
lon_min = -15
lon_max = 10

# Select a subset that corresponds to our region we're interested in

subset = grid.sel(latitude=slice(45, 75), longitude=slice(-25, 20))

# Plot the age grid.
plt.figure(figsize=(8, 8))
ax = plt.subplot(111,projection=ccrs.TransverseMercator(central_longitude=0))

levels = np.arange(0,2200,200)

subset.bedrock.plot.contourf(
    cmap=new_cmap, cbar_kwargs=dict(pad=0.01, aspect=30,label='Elevation (m)',shrink=0.9), ax=ax,
    vmin=0,vmax=1000,transform=ccrs.PlateCarree(),
    zorder=1,levels=levels
)
ax.set_title("Northern Europe Orography map")
ax.set_extent([lon_min, lon_max, lat_min, lat_max])

ocean_10m = cartopy.feature.NaturalEarthFeature('physical', 'ocean', '10m',
                                        edgecolor='k',
                                        facecolor=cartopy.feature.COLORS['water'])

ax.add_feature(ocean_10m,zorder=2)


# Grid and Labels
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, alpha=1,zorder=6)
gl.xlabels_top = None
gl.ylabels_right = None
#xgrid = np.arange(lon_min-0.5, lon_max+.5, 1.)
xgrid = np.arange(-20,20,10)
#ygrid = np.arange(lat_min, lat_max+1, 1.)
ygrid = np.arange(50,70,10)
gl.xlocator = mticker.FixedLocator(xgrid.tolist())
gl.ylocator = mticker.FixedLocator(ygrid.tolist())
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
print('e')
#gl.xlabel_style = {'size': 14, 'color': 'black'}
gl.xlabel_style={'size':0}
gl.ylabel_style={'size':0}
#gl.ylabel_style = {'size': 14, 'color': 'black'}
plt.tight_layout()
plt.savefig('topo3.pdf',bbox_inches="tight")