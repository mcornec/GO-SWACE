#LJK
# Date created: 02/04/25
# Last edited: 02/04/25

#Marin subsetted the BGC-Argo floats located in the Gulf Stream region 

# --------60--------
#|		   | 
#-10  Gulf Stream -76
#|		   |
# --------30--------
# 
# Cropping AVISO datasets to the same bounds

import numpy as np
import pandas as pd
import xarray as xr

argo_df = pd.read_csv('../BGC_floats_Cornec_20250125.csv')
anti_ds = xr.open_dataset('../Eddy_trajectory_nrt_3.2exp_anticyclonic_20180101_20241111.nc', engine="netcdf4")
#cyc_ds = xr.open_dataset('../Eddy_trajectory_nrt_3.2exp_cyclonic_20180101_20241111.nc', engine="netcdf4")

def crop_ds(ds):
    lat_min,lat_max = min(argo_df.LAT),max(argo_df.LAT)
    lon_min,lon_max = min(argo_df.LON)+360,max(argo_df.LON)+360

    subset_inds = np.where(((ds.latitude >= lat_min) & (ds.latitude <= lat_max)) & 
                            ((ds.longitude >= lon_min) & (ds.longitude <= lon_max)) & 
                            ((ds.time) >= np.datetime64('2024-02-01')))[0]
    
    return ds.isel(obs=subset_inds)

print('Cropping datasets...')
anti_ds = crop_ds(anti_ds)
#cyc_ds = crop_ds(cyc_ds)

print('Loading datasets into memory...') 
anti_ds.load() 
#cyc_ds.load()

print('Saving datasets...')
anti_ds.to_netcdf('../Eddy_trajectory_nrt_3.2exp_anticyclonic_20180101_20241111_GS_2024.nc',format='NETCDF4')
#cyc_ds.to_netcdf('../Eddy_trajectory_nrt_3.2exp_cyclonic_20180101_20241111_GS_2024.nc',format='NETCDF4')
