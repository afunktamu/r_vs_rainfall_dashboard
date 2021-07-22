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


# In[2]:


# Load Dataframe from CSV
#sipam_df = pd.read_csv('../../csv/sipam_3_hourly_r_and_rainfall.csv')
sipam_df = pd.read_csv('s3://sipam-sband/csv/sipam_3_hourly_r_and_rainfall.csv')
sipam_df


# ## Panel

# In[20]:


def power_law(x, a, b):
    return a*np.power(x, b)

# Fit the power-law data
def get_power_law_params(x_vals, y_vals):
    pars, cov = curve_fit(f=power_law, xdata=x_vals, ydata=y_vals, 
                      p0=[0, 0], bounds=(-np.inf, np.inf))
    return pars

def get_power_law_values(r_vals, rainfall_vals):
    params = get_power_law_params(r_vals, rainfall_vals)
    r_fit_vals = np.arange(0.0, 1.0, 0.01)
    rainfall_fit_vals = params[0]*r_fit_vals**params[1]
    return r_fit_vals, rainfall_fit_vals


# Widgets
rain_type = pn.widgets.Select(name='Rain type', options={'Strat.+Conv.': 'Overall RR', 'Stratiform': 'Stratiform', 'Convective': 'Convective'})
min_rainfall = pn.widgets.FloatSlider(name='Minimum rainfall threshold (mm/hr)', start=0.00, end=0.2, step=0.01, value=0.00)
local_hour = pn.widgets.IntSlider(name='Local hour', start=2, end=23, step=3, value=2)
hide_line_fit = pn.widgets.Checkbox(name='Hide line fit')


# Plot function 
@pn.depends(rain_type.param.value, min_rainfall.param.value, local_hour.param.value, hide_line_fit.param.value)
def get_plot(rain_type, min_rainfall, local_hour, hide_line_fit):
    curr_df = sipam_df.loc[(sipam_df[rain_type] >= min_rainfall) & (sipam_df['local_hour'] == local_hour)]
    sample_pct = 100.0 * ( len(curr_df) / len(sipam_df) )

    # Background scatter plot
    y_max_ceil = np.ceil(sipam_df[rain_type].max())
    ylim = (0,y_max_ceil)
    plot = sipam_df.hvplot.scatter(x='r', y=rain_type, xlim=(0.4,1), ylim=ylim, 
                                  title='SIPAM 3-hourly (' + f'{len(curr_df):.1f}' + ', ' + f'{sample_pct:.2f}' + '%)',
                                  xlabel='Column Saturation Fraction', ylabel='Rainfall (mm/hr)', grid=True, clim=(0,15), alpha=0.25)
    
    # Current scatter plot
    plot *= curr_df.hvplot.scatter(x='r', y=rain_type, color='blue')

    if not hide_line_fit:
        r_fit_vals, rainfall_fit_vals = get_power_law_values(curr_df['r'].values, curr_df[rain_type].values)
        plot *= pd.DataFrame({'r_vals': r_fit_vals, 'rainfall_vals': rainfall_fit_vals}).            hvplot.line(x='r_vals', y='rainfall_vals', color='magenta')
        power_law_params = get_power_law_params(curr_df['r'].values,curr_df[rain_type].values)
        plot *= hv.Text(0.47, y_max_ceil*0.8, 'y = ' + f'{power_law_params[0]:.1f}' + ' * x ^ ' + f'{power_law_params[1]:.1f}')
        
    return plot


widgets = pn.WidgetBox('## r vs. rainfall', rain_type, min_rainfall, local_hour, hide_line_fit)


pn.Row(widgets, get_plot).servable()


# In[ ]:





# In[4]:


# Panel plot

