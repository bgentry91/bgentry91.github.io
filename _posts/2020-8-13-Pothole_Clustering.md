---
layout: post
title: NYC Road Conditions
subtitle: Clustering with HDBSCAN
disqus: true
---

A few weeks ago I saw a [post on reddit](https://www.reddit.com/r/NYCbike/comments/hr9kd6/is_there_a_map_of_notoriously_poor_roads/) where someone was asking about a map of NYC road conditions. One person had suggested that [311 collects road condition data](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) and that it might be possible to consolidate that data into some sort of useful map. This sort of thing comes up pretty regularly on the subreddit and bad roads annoy me too (especially those [metal plates](https://www.platelocks.com/wp-content/uploads/2012/07/secure-bridge-plates.jpg?x42682)!). That got me thinking - I haven't done a personal project in a while and I love maps, so why not give it a shot! I've even made a 311 [road condition report](https://portal.311.nyc.gov/sr-details/?id=e514b23a-430b-ea11-a811-000d3a8c9145) myself, so I'm relatively familiar with the concept.

### Getting the Data
In my [Rat Inspection](https://bgentry91.github.io/blog/D3_Map_Part3/) project at Metis I downloaded the 311 data as a .CSV, but this time I wanted to plug into the 311 API so that it would be a bit easier to update and maintain the map. With the help of [sodapy](https://github.com/xmunoz/sodapy), writing a quick SoQL query was pretty straightforward. It seemed to require a limit statement, so I just did a little testing to make sure I was selecting enough rows - 100,000 was safe. I also filtered down reports to after January 2020 to keep the data recent (though it may be the case that NYC never actually repairs anything...). 

~~~sql
SELECT
    latitude
    , longitude
    , complaint_type
    , descriptor
    , created_date
    , closed_date
    , resolution_description
    , incident_address
    , street_name
    , borough
WHERE
    complaint_type = 'Street Condition'
    AND created_date > '2020-01-01'
    AND latitude IS NOT NULL
    AND longitude IS NOT NULL
LIMIT 100000
~~~

(To use this SoQL in the below code, just format it as a string and assign it to a `query` variable.)

Hitting the API is relatively straightforward. I was having some issues when I wasn't setting a client timeout for this specific dataset, so there's a line for that. You'll have to get an [app token](https://data.cityofnewyork.us/profile/edit/developer_settings) as well.

~~~python
from sodapy import Socrata
import pandas as pd

client = Socrata('data.cityofnewyork.us', 'YOUR_APP_TOKEN')
dataset_key = 'erm2-nwe9'
client.timeout = 60

results = client.get(dataset_key, query = query)
results_df = pd.DataFrame.from_records(results)
~~~

This returns a simple dataframe that we can use!

### Mapping

The first thing to do is to go ahead and visualize all these potholes. You can do this in the [311 viz tool](https://data.cityofnewyork.us/Social-Services/311-Road-Conditions/kgv6-uxdf/data), but it leaves a bit to be desired and does some funny clustering. I'm sure there are other resources and tools out there, but I wanted to build a framework to start playing around on my own. Luckily, [gmplot](https://github.com/gmplot/gmplot/wiki) makes this pretty easy! I think you can get away without using a [googlemaps javascript API key](https://developers.google.com/maps/documentation/javascript/get-api-key), but it will render your maps in "developer mode." Since Google gives you $200 in monthly credit and only charges $.007/request, you might as well set up an account. For ease of use I just output my map to a simple HTML file and open it in Chrome.

Since I live in Brooklyn and mostly ride around there, I decided to limit my data in this initial step. After some fiddling, I set the middle of the map and the zoom to something that made sense for my testing. Setting an alpha value to .3 made for a nice way to visualize the density of the complaints when the markers overlapped.

I also did a little bit of cleanup because there are a bunch of points over in Pennsylvania. These have street addresses, so at some point I'd like to use [Google's geocoding service](https://developers.google.com/maps/documentation/geocoding/start?utm_source=google&utm_medium=cpc&utm_campaign=FY18-Q2-global-demandgen-paidsearchonnetworkhouseads-cs-maps_contactsal_saf&utm_content=text-ad-none-none-DEV_c-CRE_433476780436-ADGP_Hybrid+%7C+AW+SEM+%7C+SKWS+~+Geocoding+API-KWID_43700039136946657-aud-581578347266:kwd-335278985932-userloc_9004351&utm_term=KW_%2Bgeocoder%20%2Bapi-ST_%2Bgeocoder+%2Bapi&gclid=CjwKCAjwydP5BRBREiwA-qrCGgM5PGwhjxEl-QhUG-hkm2r7G6H0_wjL3pLmLYzzrLokydvgXoEn4RoCjkIQAvD_BwE) to recover these.

~~~python
results_df = results_df[results_df.borough == 'BROOKLYN']
results_df = results_df[(results_df.latitude != '40.1123853') & (results_df.longitude != '-77.5195844')]


import gmplot 

# Create the map
gm_api_key = 'YOUR_API_KEY_GOES_HERE'
gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

gmap.scatter(lats=results_df.latitude
             , lngs=results_df.longitude
             , alpha=.3
             , size=80
             , marker=False)

# Draw the map
gmap.draw('map.html')
~~~

Which results in a pretty good map! I've just taken a screenshot here, but locally you should be able to pan/zoom as you'd like.

<img src="/images//pothole_clusters/Initial_Map.png" alt="Initial Map" style="max-width:100%;max-height:100%" />

The first thing I noticed is that there is definitely some natural clustering. There are also a lot of outlying points that probably indicate an road issue, but aren't problematic enough to avoid riding on a given road.

### Clustering - HDBSCAN

The logical next step was to try out a clustering algorithm on the data and try to identify true problem areas. I've used [DBSCAN](https://www.aaai.org/Papers/KDD/1996/KDD96-037.pdf) in the past and had good luck with it, but I've always been a bit frustrated by it's EPS parameter, which is not very intuitive. This is a complaint I have around unsupervised learning generally - it seems like mostly I just tinker around with parameters on a given dataset until it becomes something that looks good, but it rarely ends up being very generalizable (for me, at least).

I was looking around a bit and came across [HDBSCAN](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html). It solves half of the parameter problem, eliminating the need for EPS though still requiring a set number of minimum samples. Minimum samples is a bit more intuitive, but I do worry that it doesn't generalize to a small time window. In this dataset, I'm looking at all of 2020 to date - what if I switched to last month? Since there are fewer total samples, we might need to decrease the parameter, but by how much? Is it linear? I'll leave that as a problem for another day, but it may come back to haunt me.

Another nice thing about DBSCAN and HDBSCAN is that neither require that every point must be assigned to a cluster. As a mentioned above, we know that some of these complaints are outliers and we should be looking for *patterns* in complaints. This means the algorithm might be able to throw some out for us!

[HDBSCAN's docs](https://hdbscan.readthedocs.io/en/latest/comparing_clustering_algorithms.html#hdbscan) have some good information comparing algorithms, which I thought was very helpful.

HDBSCAN has been implemented in a easy-to-use python library, which makes life easy when trying to play around with it. To start, I just clustered on Lat/Longs, which just felt simple and obvious. I also set `min_samples` to 10, which I somewhat randomly chose for my first pass.

~~~python
from hdbscan import HDBSCAN
clustering = HDBSCAN(min_samples=10).fit(results_df[['latitude','longitude']])
~~~

HDBSCAN returns the cluster numbers via `clustering.labels_` and it assigns non-clustered points a value of -1. I'll exclude those from our output and choose random colors for the labeled points.

~~~python
clean_out = results_df[['latitude','longitude']].copy()
clean_out['cluster'] = clustering.labels_

import random

#set the colors and alpha for mapping
def get_rand_color():
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())

# get distinct colors for each cluster
for val in set(clean_out.cluster):
	cluster_colors[val] = get_rand_color()
        
# map colors to cluster
clean_out['color'] = clean_out['cluster'].map(cluster_colors)
clean_out = clean_out[clean_out.cluster != 1]

gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

gmap.scatter(lats=clean_out.latitude
             , lngs=clean_out.longitude
             , alpha=.3
             , size=80
             , color=list(clean_out.color)
             , marker=False)

gmap.draw('map.html')
~~~

Which gives us something that looks... reasonable!

<img src="/images//pothole_clusters/Initial_Clustering.png" alt="Initial Clustering" style="max-width:100%;max-height:100%"  />

I still don't feel like this is super helpful. It gives blobs to avoid, but when I'm riding my bike I really think more in terms of streets. 

Luckily, the 311 data includes a street name that I can use as an input feature when clustering. The only problem is that street names are strings, and HDBSCAN will only accept numeric input variables. Easy enough - I can just [dummify](https://en.wikipedia.org/wiki/Dummy_variable_(statistics)) them with pandas. Street names can be duplicated across the boroughs, so I concat the borough name with the street name to keep things unique. There are also a bunch of null street names in the dataset, so I exclude those (again, I'd like to do some geocoding to get these back at some point).

~~~python
results_df['street_name_borough'] = results_df.street_name + " " + results_df.borough
results_df.dropna(inplace=True)
results_df.reset_index(inplace=True, drop=True)

cluster_columns = ['latitude','longitude','street_name_borough']
cluster_features = results_df[cluster_columns].copy()
cluster_features = cluster_features.join(pd.get_dummies(cluster_features.street_name_borough))
del cluster_features['street_name_borough']
~~~

Ok, now that that's cleaned up, I'll recluster and map, with the same code as above.

~~~python
clustering = HDBSCAN(min_samples=10).fit(cluster_features)
~~~

Which results in this:

<img src="/images//pothole_clusters/Street_Clusters.png" alt="Street Clustering" style="max-width:100%;max-height:100%" />

It seems to be weighting the street pretty heavily in this version. Paring down and looking at one specific cluster along Henry Street, every single point is along the street, and the cluster is something like 2 miles long! This really isn't particularly helpful - I'd guess that the point in Red Hook really isn't an issue, and I wouldn't avoid all of Henry because there are some bad spots along its length. Maybe I would avoid that cluster around Atlantic Ave.

<img src="/images//pothole_clusters/Henry_Cluster.png" alt="Henry St Cluster" style="max-width:100%;max-height:100%"  />

This one took me a bit. I tried scaling the features between 0-1, thinking that maybe the small scale differences in Lat/Longs were causing problems. The lat/longs in the dataset range from [40.5788013, 40.7355137] and [-73.865758,-74.0341442], so fairly small increments compared to 0/1 for the dummy variables. Still didn't solve much.

Eventually I realized that the model was weighting each feature equally, which meant that my latitude had the exact same weight as any given street name. This presented another problem, since creating ordinal variables (0,1,2,3) would indicate a relationship between the ordinals (i.e street 0 is more similar to street 1 than it is to street 3). To be honest, I couldn't come up with a great way around this, but I did randomize the streets when I created ordinal variables in order to hopefully minimize the issue.

I also decided to continue scaling the variables. I don't think it hurts anything, and could help it to be a bit more generalizable.

~~~python
cluster_columns = ['latitude','longitude','street_name_borough']
cluster_features = results_df[cluster_columns].copy()

street_set = set(cluster_features.street_name_borough)
random.shuffle(list(street_set))
street_map = dict(zip(street_set,range(len(street_set))))
cluster_features['street_num'] = cluster_features.street_name_borough.map(street_map)

from sklearn.preprocessing import MinMaxScaler
scaled = MinMaxScaler((0,1)).fit_transform(cluster_features[['latitude','longitude','street_num']])
~~~

<img src="/images/pothole_clusters/Final_Cluster.png" alt="Final Cluster" style="max-width:100%;max-height:100%"  />

Now there is some continuity to the streets, like Fulton in Downtown Brooklyn/Fort Green and 4th Avenue in Sunset Park. But there is also some good spread in certain areas, such as in Carroll Gardens and Cobble Hill. I think this version really hits a nice middle ground between prioritizing streets and considering lats/longs.

### What's next?
It would be great to set up something to make this a bit more useful for a broad audience. Screenshots aren't super helpful since you can't pan and zoom. I'll be looking into setting up something hosted down the road.

I also think we could use this sort of info to help design and build a tool to generate biking directions. I've been wanting to do some more reinforcement learning work, and I think there are definitely some opportunities to flex that while taking into account this data. More to come!

In doing some research for this post I also came across the DOT's [road milling data](http://www.nycdot.info/), which I will definitely include at some point. Milled up streets are the WORST to ride on.

Also - I might have to change the formatting for this blog. It's 2 years old now, and sort of amazing how fast it looks "ancient" to me. [SpaceJam](https://spacejam.com/)

### Disclaimers
First and foremost, I know this data is flawed. It's super biased to people reporting things to 311, which happens more frequently in certain parts of the city. We do what we can with the info we're given, I suppose.

Clustering is pretty imperfect. There are probably some huge/terrible potholes I excluded. But also check out that map - there are a ton I included! Can Brooklyn streets really be that bad? From personal experience on routes I regularly ride, it seems to hold up to some scrutiny. That being said... please go ride and let me know!  I'd love to keep on improving and tuning this to be the best it can be.

