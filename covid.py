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
    doffs = list(range(trend.num_rows))
    t1 = trend.with_column('exp pred', exp_rate(doffs, eparams[0], eparams[1]))
    lparams, lpcov = fit(lin_rate, trend)
    t2 = t1.with_column('lin pred', lin_rate(doffs, lparams[0], lparams[1]))
    return t2, eparams, lparams

def show_model_rate_trend(trend, val='arate', height=5, width=8):
    mtrend, eparams, lparams = model_rate_trend(trend, val)
    print(eparams, lparams)
    mtrend.extract(['exp pred', 'lin pred']).oplot(height=height, width=width, xlab=25)
    mtrend.plots[-1].scatter(mtrend['date'], mtrend[val])

def project_progressive_trend(trend, region, num_days, fit_start=None, fit_end=None, distance=14):
    day = trend.last(trend.time_column)
    old_day = inc_day(day, -distance)
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
    
    proj = trend.select([trend.time_column, region, 'new', 'active', 'arate'])
    for i in range(num_days):
        day = inc_day(day)
        old_day = inc_day(old_day)
        arate = growths[i+1]
        new = arate*active
        val = val + new
        active = active + new - proj.get(old_day, 'new')
        proj.append((day, val, new, active, arate))
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