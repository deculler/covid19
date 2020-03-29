# covid19

Contains Notebooks analyzing Covid-19 infection data from Johns Hopkins.  So many thanks to the incredible work of Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE):
https://systems.jhu.edu/.  They provide lots of geospatial visualization.  The notebooks here provide an analytical view. 
They pull data from
[https://github.com/CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19), which is updated
daily.  Various notebooks look at slices through this invaluable data.

Website for this repo: [https://deculler.github.io/covid19/](https://deculler.github.io/covid19/)

Repo for this website: [https://github.com/deculler/covid19](https://github.com/deculler/covid19)

## View and run the notbooks

**Covid19-Worldwide.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/Covid19-Worldwide.ipynb)
examines the growth in confirmed cases worldwide at a country level, showing individual countries contribute to the overall picture
and examining growth rates per country.  Worldwide and per-country projections provide a sense of what the exponential growth
is leading to.  The data is pulled from https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series.

To run the notebooks live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/Covid19-Worldwide.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=Covid19-Worldwide.ipynb)
 
**US-covid19-nytimes.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/US-covid19-nytimes.ipynb)
examines the growth in confirmed cases and deaths in the US at the state level.  

To run live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/US-covid19-nytimes.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=US-covid19-nytimes.ipynb)

**Counties-US-covid19-nytimes.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/Counties-US-covid19-nytimes.ipynb)
examines the growth in confirmed cases and deaths in the US state-by-state at the county level.  

To run live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/Counties-US-covid19-nytimes.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=Counties-US-covid19-nytimes.ipynb)

Cloud infrastuctures for running notebooks

* [https://mybinder.org](https://mybinder.org) - clones the repo and builds an environment.  It takes time, but is
quite general.
      
* [Datahub](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master) -
Is available for members of the UC Berkeley community.  It just clones the repo, as the hub environment is all
set up.  It's fast and retains user state.
Instructions for replicating this environment](http://data8.org/zero-to-data-8/deploy/setup_jupyterhub.html)
