# LJK
# Date created: 02/04/2025
# Last edited: 02/04/2025

# Co-locating BGC-ARGO floats with AVISO eddies 

import pandas as pd
import xarray as xr
import numpy as np
from itertools import groupby
from matplotlib.path import Path


# Open Argo data
argo_df = pd.read_csv('../BGC_floats_Cornec_20250125.csv')

# Add columns to store eddy data
argo_df["POLARITY"] = 'None'
argo_df["ID"] = np.nan

# Set eddy search bounds based on the Argo location limits
lat_min,lat_max = min(argo_df.LAT),max(argo_df.LAT)
lon_min,lon_max = min(argo_df.LON)+360,max(argo_df.LON)+360

# Open AVISO datasets
anti_ds = xr.open_dataset('../Eddy_trajectory_nrt_3.2exp_anticyclonic_20180101_20241111.nc', engine="netcdf4")
cyc_ds = xr.open_dataset('../Eddy_trajectory_nrt_3.2exp_cyclonic_20180101_20241111.nc', engine="netcdf4")

# Crop AVISO datasets to eddy search bounds
def crop_ds(ds):
    subset_inds = np.where(((ds.latitude >= lat_min) & (ds.latitude <= lat_max)) & 
                            ((ds.longitude >= lon_min) & (ds.longitude <= lon_max)) & 
                            ((ds.time) >= np.datetime64('2024-01-01')))[0]
    return ds.isel(obs=subset_inds)

anti_ds = crop_ds(anti_ds)
cyc_ds = crop_ds(cyc_ds)

# Check if each Argo float is in an eddy

def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

for index, row in argo_df.iterrows():
    if index % 100 == 0:
        print(index)
    
    argo_lon,argo_lat,argo_time = row['LON']+360,row['LAT'],np.datetime64(row['DATE'])
    
    # check each polarity
    for pol in ['ANTI','CYC']:
        if pol == 'ANTI':
            cropped_ds = anti_ds
        else:
            cropped_ds = cyc_ds

        box_size = 2
        subset_inds = np.where(((cropped_ds.latitude >= argo_lat-box_size) & (cropped_ds.latitude <= argo_lat+box_size)) & 
                                ((cropped_ds.longitude >= argo_lon-box_size) & (cropped_ds.longitude <= argo_lon+box_size)) & 
                                ((cropped_ds.time) == argo_time))[0]

        if len(subset_inds) != 0:
            check_ds = cropped_ds.isel(obs=subset_inds)
            
            for obs in np.arange(len(check_ds.obs)):    
                contour_lons = np.array(check_ds.effective_contour_longitude[obs])
                contour_lats = np.array(check_ds.effective_contour_latitude[obs])
        
                if all_equal(contour_lons): # eddy break
                    pass
                else:
                    poly = Path([(contour_lats[j],contour_lons[j]) for j in np.arange(0,len(contour_lats))]) # set up the polygon
                    if poly.contains_points([(argo_lat,argo_lon)]): #find if point is inside the polygon
                        argo_df.at[index,'POLARITY']=pol
                        argo_df.at[index,'ID']=check_ds.track[obs]

# Filter down the argo dataset to in-eddy 
in_eddy_argo = argo_df[argo_df['POLARITY'] != 'None']
in_eddy_argo.to_csv('BGC_floats_Cornec_20250125_in_eddy_LJK.csv', index=False)







