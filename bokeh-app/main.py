#!/usr/bin/env python
# coding: utf-8

# # r vs. rainfall Panel dashboard
# 
# Testing!

# In[1]:


import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

import hvplot.pandas
import panel as pn
import panel.widgets as pnw
import colorcet as cc

import holoviews as hv
from holoviews import opts


# In[4]:


# Load Dataframe from CSV
#sipam_df = pd.read_csv('../../csv/sipam_3_hourly_r_and_rainfall.csv')
sipam_df = pd.read_csv('s3://sipam-sband/csv/sipam_3_hourly_r_and_rainfall.csv')
sipam_df


# ## Panel

# In[5]:


def power_law(x, a, b):
    return a*np.power(x, b)

# Fit the power-law data
def get_power_law_params(df):
    pars, cov = curve_fit(f=power_law, xdata=df['r'].values, ydata=df['Overall RR'].values, 
                      p0=[0, 0], bounds=(-np.inf, np.inf))
    return pars

def get_power_law_values(df):
    params = get_power_law_params(df)
    r_vals = np.arange(0.0, 1.0, 0.01)
    rainfall_vals = params[0]*r_vals**params[1]
    return r_vals, rainfall_vals

# Widgets
rain_type = pn.widgets.Select(name='Rain type', options={'Strat.+Conv.': 'Overall RR', 'Stratiform': 'Stratiform', 'Convective': 'Convective'})
min_rainfall = pn.widgets.FloatSlider(name='Minimum rainfall threshold (mm/hr)', start=0.00, end=0.2, step=0.01, value=0.00)
local_hour = pn.widgets.IntSlider(name='Local hour', start=2, end=23, step=3, value=2)
line_fit = pn.widgets.Checkbox(name='Show line fit')

# Plot function 
@pn.depends(rain_type.param.value, min_rainfall.param.value, local_hour.param.value, line_fit.param.value)
def get_plot(rain_type, min_rainfall, local_hour, line_fit):
    curr_df = sipam_df.loc[(sipam_df[rain_type] >= min_rainfall) & (sipam_df['local_hour'] == local_hour)]
    sample_pct = 100.0 * ( len(curr_df) / len(sipam_df) )
    plot = curr_df.hvplot.scatter(x='r', y=rain_type, xlim=(0.4,1), ylim=(0,5), 
                                  title='SIPAM 3-hourly (' + f'{len(curr_df):.1f}' + ', ' + f'{sample_pct:.2f}' + '%)',
                                  xlabel='Column Saturation Fraction', ylabel='Rainfall (mm/hr)', grid=True, clim=(0,15))
    if line_fit:
        r_vals, rainfall_vals = get_power_law_values(curr_df)
        plot *= pd.DataFrame({'r_vals': r_vals, 'rainfall_vals': rainfall_vals}).            hvplot.line(x='r_vals', y='rainfall_vals', color='magenta')
        
    return plot

widgets = pn.WidgetBox('## r vs. rainfall', rain_type, min_rainfall, local_hour, line_fit)

pn.Row(widgets, get_plot).servable()


# In[ ]:


# Panel plot

