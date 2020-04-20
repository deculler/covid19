# covid19

Contains Notebooks analyzing Covid-19 infection data from Johns Hopkins and NY Times.  So many thanks to the incredible work of Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE):
[https://systems.jhu.edu/](https://systems.jhu.edu/)
and the 
[NY Times](https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html).  They provide wonderful geospatial visualization.  The notebooks here provide a simple analytical view. 
The notebooks pull data from
[https://github.com/CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19) for wordwide data and
for Worldwide data and [https://github.com/nytimes/covid-19-data](https://github.com/nytimes/covid-19-data)
for US data. Both are updated
daily, which takes incredible work.  With that, people can explore and work on the data from a temporal perspective.  Where
might we be in two weeks? (I have stopped maintaining the NY Times notebooks, focusing on the JHU data.)

Website for this repo: [https://deculler.github.io/covid19/](https://deculler.github.io/covid19/)

Repo for this website: [https://github.com/deculler/covid19](https://github.com/deculler/covid19)

## View and run the notbooks

[**Covid19-US-Actions-Matter.ipynb** ](https://htmlpreview.github.io/?https://github.com/deculler/covid19/blob/master/Covid19-US-Actions-Matter.html) [[ View Notebook ] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/Covid19-US-Actions-Matter.ipynb) examines how significantly mitigation measures in the US contained the spread of the virus and how recent undermining of those measures has already changed the projection of whether it ends up contained or grows unchecked.

To run live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/Covid19-US-Actions-Matter.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=Covid19-US-Actions-Matter.ipynb)


**US-County-covid19-JHU.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/US-County-covid19-JHU.ipynb)
County level exploration and projection of confirmed cases and deaths in the US for any state.

To run live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/US-County-covid19-JHU.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=US-County-covid19-JHU.ipynb)

**US-covid19-JHU.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/US-covid19-JHU.ipynb) State level exploration as above.

To run live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/US-covid19-JHU.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=US-covid19-JHU.ipynb)


**World-covid19-JHU.ipynb** [ [View Notebook] ](https://nbviewer.jupyter.org/github/deculler/covid19/blob/master/World-covid19-JHU.ipynb)
examines the growth in confirmed cases worldwide at a country level, showing individual countries contribute to the overall picture
and examining growth rates per country.  Worldwide and per-country projections provide a sense of what the exponential growth
is leading to.  The data is pulled from https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series.

To run the notebooks live:
* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/deculler/covid19/master?filepath=work/World-covid19-JHU.ipynb)
* [datahub.berkeley.edu](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master&path=World-covid19-JHU.ipynb)
 


Cloud infrastuctures for running notebooks

* [https://mybinder.org](https://mybinder.org) - clones the repo and builds an environment.  It takes time, but is
quite general.
      
* [Datahub](http://datahub.berkeley.edu/user-redirect/interact?account=deculler&repo=covid19&branch=master) -
Is available for members of the UC Berkeley community.  It just clones the repo, as the hub environment is all
set up.  It's fast and retains user state.
Instructions for replicating this environment](http://data8.org/zero-to-data-8/deploy/setup_jupyterhub.html)
