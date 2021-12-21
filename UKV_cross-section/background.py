from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import cartopy.feature as cfeature
import cartopy.crs as ccrs

import iris
import xarray
import pandas as pd

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    """Return a truncated colormap for plotting land"""
    
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def get_proj(fname):
    """Return the cartopy projection of a UKV netCDF file."""
    cubes = iris.load_cube(fname)
    cubes_crs = cubes.coord_system().as_cartopy_crs()
    return cubes_crs

def sliceplot2(fname,y_coord,xmin,xmax):
    """(deprecated) Plot a cross section using iris."""
    cubes = iris.load_cube(fname)
    c2 = iris.load_cube('20211120T1200Z-PT0027H00M-height_of_orography.nc')
    slice1 = cubes.extract(iris.Constraint(projection_y_coordinate=y_coord))
    slice2 = c2.extract(iris.Constraint(projection_y_coordinate=y_coord))
    #return slice1
    #x1=450
    #x2=609
    y1=y_coord
    y2=y_coord
    slice1=slice1[:20,xmin:xmax]
    slice2=slice2[xmin:xmax]
    #print(slice1)
    
    xs=[cubes[12,509,xmin].coord('projection_x_coordinate').points,cubes[12,509,xmax].coord('projection_x_coordinate').points]
    
    #xs = [xmin,xmax]
    ys=[y1,y2]
   # print(slice1)
   # plt.gca().gridlines(draw_labels=True)
    
    # Plot #1: contourf with axes longitude from -180 to 180
    fig = plt.figure(figsize=(12, 16))
    plt.subplot(211)
    qplt.plot(slice2,c='k')
    levels=np.arange(0,1.2,0.2)
    qplt.contourf(slice1, coords=['projection_x_coordinate', 'height'],cmap='Blues_r',levels=levels)
    # Plot #2: contourf with axes longitude from 0 to 360
    proj = get_proj(fname)
    
    ax = plt.subplot(212, projection=proj)
    cmap = plt.get_cmap('gist_earth')
    new_cmap = truncate_colormap(cmap, 0.3, 1)    
   # new_cmap.set_under('white')
    qplt.contourf(c2, 15,cmap=new_cmap)
    ax.plot(xs, ys,c='white')
    ax.set_xlim(xs[0]-1,xs[1]+1)
    ax.set_ylim(y1-5000,y2+5000)
    print(xs[0],xs[1],y1,y2)
    plt.gca().coastlines()
    plt.gca().add_feature(cfeature.OCEAN,zorder=100,edgecolor='k')
    
    fig.show()
   # plt.tight_layout()
   
def get_index_x(x):
    """UKV specific conversion from model projection to index of x coords"""
    f = int((x+1158000)/2000)
    return f 
 
def get_index_y(y):
    """UKV specific conversion from model projection to index of y coords"""
    f = int((y+1036000.0)/2000)
    return f
    
def get_vars(filename,verbose=False):
    """Return list of variables within a given netCDF file"""
    data = xarray.open_dataset(filename)
    if verbose==True:
        print(list(data.variables))
    return list(data.variables)
    
def x_sliceplot(filename,var_name,orog_fname,proj,lat,lon,cmap='viridis',add_towns=True,save=False):
    """
    Plot a cross section
    
    KEYWORD ARGUMENTS
        filename;   string;         location of the file you wish to plot
        var_name;   string;         the variable to be plotted
        orog_fname; string;         location of the orography file
        proj;       cartopy object; the projection of the netCDF file.
        lat;        float;          the desired latitude to plot
        lon;        float;          the desired longitude to plot
        cmap;       string;         the colormap to use on the data, e.g. "Blues_r", "seismic"
        add_towns;  BOOLEAN;        whether to plot towns on the map (default True)
        save;       BOOLEAN;        whether to save the produced figure (default False)
    
    """
    fig = plt.figure(figsize=(6,12))
    earthcmap = plt.get_cmap('gist_earth')
    orog_cmap = truncate_colormap(earthcmap, 0.3, 1)  
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212,projection=proj)

    #ax1.imshow(b.values,cmap='Greys',transform=proj)
    x,y = proj.transform_point(lon,lat,  ccrs.PlateCarree())
    x1 = get_index_x(x-50000)
    x2 = get_index_x(x+50000)
    y1 = get_index_y(y)
    
    
    data = xarray.load_dataset(filename)
    orog = xarray.load_dataset(orog_fname)['surface_altitude']
    data[var_name][:20,y1,x1:x2].plot(cmap=cmap,ax=ax1,cbar_kwargs={'label':var_name,'shrink':0.7})
    orog[y1,x1:x2].plot(ax=ax1,c='k')
    
    orog[y1-50:y1+50,x1-30:x2+30].plot.contourf(ax=ax2,cmap=orog_cmap,cbar_kwargs={'label':'surface_altitude','shrink':0.7})
    
    x1_t = orog['projection_x_coordinate'][x1]
    x2_t = orog['projection_x_coordinate'][x2]
    y1_t = orog['projection_y_coordinate'][y1]
    
    ax2.plot([x1_t,x2_t],[y1_t,y1_t],transform=proj,c='white',lw=3)

    ax2.coastlines(resolution='10m',alpha=1)
    
    ax2.set_ylim(orog['projection_y_coordinate'][y1-50],orog['projection_y_coordinate'][y1+50])
    ax2.set_xlim(orog['projection_x_coordinate'][x1-30],orog['projection_x_coordinate'][x2+30])
    #plt.savefig('leewaves2.pdf')
    
    ax1.set_title('Cross Section Plot')
    ax2.set_title('Cross section location')
    fig.suptitle('UKV '+var_name+' Forecast \n Forecast Time: '+str(data['forecast_reference_time'].values)[:19]+' \n Valid at:'+str(data['time'].values)[:19])
    
    for axes in [ax2]:

        gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=2, color='grey', alpha=0.5, linestyle='--')

        gl.xlines = True
        gl.top_labels = False
        gl.right_labels = False
 
    if add_towns==True:
        locs = pd.read_csv('gb2.csv')
        xs_towns = list(locs['lng'])
        ys_towns = list(locs['lat'])
        labels = list(locs['city'])
        i=0
        ax2.scatter(xs_towns,ys_towns,transform=ccrs.PlateCarree(),zorder=8,c='k')
        while i<len(labels):
            temp_x,temp_y = proj.transform_point(xs_towns[i],ys_towns[i],  ccrs.PlateCarree())
            if temp_x > x - 50000 - 60000 and temp_x < x+ 50000 + 60000:
                if temp_y>y-100000 and temp_y<y+100000:
                    ax2.text(xs_towns[i],ys_towns[i],labels[i],transform=ccrs.PlateCarree(),zorder=20)
            i=i+1
    
    if save==True:
        plt.savefig('UKV_'+var_name+'_'+str(data['forecast_reference_time'].values)[:19].replace(':','')+'_'+str(data['time'].values)[:19].replace(':','')+'.pdf',bbox_inches='tight')
        
 
