# Tools specific to the notebook analysis

from datascience import *
import matplotlib.pyplot as plots
import numpy as np
import scipy

import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

#import os
import datetime

# Tools for working with timestamps
day_fmt = "%m/%d/%y"

def less_day(day1, day2):
    """Return day1 < day2"""
    return datetime.datetime.strptime(day1, day_fmt) < datetime.datetime.strptime(day2, day_fmt)

def inc_day(day, ndays=1):
    """Return day + ndays"""
    date =  datetime.datetime.strptime(day, day_fmt) + datetime.timedelta(days=ndays)
    return datetime.datetime.strftime(date, day_fmt)

def format_day(day):
    """Return day """
    date =  datetime.datetime.strptime(day, day_fmt)
    return datetime.datetime.strftime(date, day_fmt)

# Computing rates of growth

def wgmean(vals):
    xvals = [x for x in vals if np.isfinite(x)]
    try :
        return scipy.stats.gmean(xvals) if xvals else np.nan
    except :
        return np.nan

def ave_growth(trend, window=4):
    """Average recent growth rate of single trend"""
    return wgmean(trend['rate'][-window:])

def growth_rate(trend, val='rate', window=1):
    """Smooth raw rates"""
    rates = trend[val]
    #vals = np.array((window-1)*[np.nan] + list(rates))
    #return [wgmean(vals[i:i+window]) for i in range(len(rates))]
    return [wgmean(rates[max(0,i-window) : i+window+1]) for i in range(len(rates))]

def plot_rate_trend(trend, val='rate', height=5, width=8):
    with np.errstate(divide='ignore', invalid='ignore'):
        trend = trend.with_column('gm_rate', growth_rate(trend, val))
        trend.extract(['gm_rate']).oplot(height=height, width=width, xlab=20)
        trend.plots[-1].scatter(trend['date'], trend[val])

# Modeling

def get_rates(ts, val='arate'):
    trends = ts.trend()
    rates = trends.extract([x for x in trends.labels if val in x])
    for label in rates.categories :
        rates.relabel(label, label[5:])
    return rates

def exp_rate(days, s, r):
    return [s*r**day for day in days]

def lin_rate(days, s, r):
    return [s + r*day for day in days]

def fit(model, trend, val='arate'):
    """Fit a 2 paramater model to a rate trend"""
    try :
        doffs = list(range(trend.num_rows))
        params, pcov = scipy.optimize.curve_fit(model, doffs, trend[val])
        return params, np.sqrt(np.diag(pcov))
    except :
        return [np.nan, np.nan], [np.nan, np.nan]

def model_rate_trend(trend, val='arate'):
    eparams, epcov = fit(exp_rate, trend, val)
    proj = trend.extract(val)
    doffs = list(range(trend.num_rows))
    proj['exp proj'] = exp_rate(doffs, eparams[0], eparams[1])
    proj['exp+'] = exp_rate(doffs, eparams[0]+epcov[0], eparams[1]+epcov[1])
    proj['exp-'] = exp_rate(doffs, eparams[0]-epcov[0], eparams[1]-epcov[1])
    lparams, lpcov = fit(lin_rate, trend, val)
    proj['lin proj'] = lin_rate(doffs, lparams[0], lparams[1])
    proj['lin+']    = lin_rate(doffs, lparams[0]+lpcov[0], lparams[1]+lpcov[1])
    proj['lin-']    = lin_rate(doffs, lparams[0]-lpcov[0], lparams[1]-lpcov[1])
    return proj, eparams, lparams, epcov, lpcov

def show_model_rate_trend(trend, val='arate', height=5, width=8, 
                          alpha=0.2, lincolor='lightcoral', expcolor='aqua'):
    mtrend, eparams, lparams, epcov, lpcov = model_rate_trend(trend, val)
    #print(eparams, epcov, lparams, lpcov)
    mt = mtrend.extract(['exp proj', 'lin proj'])
    mt.oplot(height=height, width=width, xlab=25)
    mt.plots[-1].fill_between(mtrend['date'], mtrend['lin-'], mtrend['lin+'], facecolor=lincolor, alpha=alpha)    
    mt.plots[-1].plot(mtrend['date'], mtrend['lin+'], ':', color=lincolor)
    mt.plots[-1].plot(mtrend['date'], mtrend['lin-'], ':', color=lincolor)
    mt.plots[-1].fill_between(mtrend['date'], mtrend['exp-'], mtrend['exp+'], facecolor=expcolor, alpha=alpha)
    mt.plots[-1].plot(mtrend['date'], mtrend['exp+'], ':', color=expcolor)
    mt.plots[-1].plot(mtrend['date'], mtrend['exp-'], ':', color=expcolor)
    mt.plots[-1].scatter(mtrend['date'], mtrend[val])
    
def project_progressive_trend(trend, region, num_days, 
                              fit_start=None, fit_end=None, act_dist=14):
    """ project progressive arate modeled in [fit_start, fit_end] for num_days
    where active is given by window of length act_dist, matching trend
    """
    day = trend.last(trend.time_column)
    old_day = inc_day(day, -act_dist)
    val = trend.last(region)
    new = trend.last('new')
    active = trend.last('active')
    arate = trend.last('arate')
    if fit_start :
        if fit_end is None :
            fit_end = day 
        params, pcov = fit(exp_rate, trend.between(fit_start, fit_end), 'arate')
    else :
        params, pcov = fit(exp_rate, trend, 'arate')
    growths = exp_rate(range(num_days+1), arate, params[1])
    growths_hi = exp_rate(range(num_days+1), arate, params[1]+pcov[1])
    growths_lo = exp_rate(range(num_days+1), arate, params[1]-pcov[1])
    
    proj = trend.select([trend.time_column, region, 'new', 'active', 'arate'])
    proj[region+'-'] = proj[region]
    proj[region+'+'] = proj[region]
    proj['new-'] = proj['new']
    proj['new+'] = proj['new']
    proj['active-'] = proj['new']
    proj['active+'] = proj['new']
    active_lo = active_hi = active
    val_lo = val_hi = val
    for i in range(num_days):
        day = inc_day(day)
        old_day = inc_day(old_day)
        arate = growths[i+1]
        new = arate*active
        new_lo = growths_lo[i+1]*active_lo
        new_hi = growths_hi[i+1]*active_hi
        val = val + new
        val_lo = val_lo + new_lo
        val_hi = val_hi + new_hi
        active = active + new - proj.get(old_day, 'new')
        active_lo = active_lo + new_lo - proj.get(old_day, 'new-')
        active_hi = active_hi + new_hi - proj.get(old_day, 'new+')
        proj.append((day, val, new, active, arate, val_lo, val_hi, new_lo, new_hi, active_lo, active_hi))
    return proj

def proj_prog(trend, region, dist=14, fit_start=None, fit_end=None):
    proj = project_progressive_trend(trend, region, dist, fit_start, fit_end)
    pproj = proj.extract([region, 'active', 'new'])
    pproj.oplot(width = 8, xlab=25)
    end = trend.last(trend.time_column)
    plots.plot([end, end], [0, trend.last(region)])
    if fit_start:
        plots.plot([fit_start, fit_start], [0, trend.get(fit_start, region)], ':')
    if fit_end:
        plots.plot([fit_end, fit_end], [0, trend.get(fit_end, region)], ':')
    plots.text(end, trend.last(region), "{:,}".format(trend.last(region)))
    plots.text(pproj.last('date'), pproj.last(region), "{:,}".format(int(pproj.last(region))))
    pproj.plots[-1].fill_between(proj['date'], proj[region+'-'], proj[region+'+'], alpha=0.2)
    pproj.plots[-1].fill_between(proj['date'], proj['active-'], proj['active+'], alpha=0.2) 
    pproj.plots[-1].fill_between(proj['date'], proj['new-'], proj['new+'], alpha=0.2) 
    