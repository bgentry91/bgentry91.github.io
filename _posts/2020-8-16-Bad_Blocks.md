---
layout: post
title: Bad Blocks
subtitle: Useful Clustering
disqus: true
---

In my [last post](https://bgentry91.github.io/blog/Pothole_Clustering/), I discussed pulling [NYC 311 road condition reports](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/data) from the NYC Open Data API and using [HDBSCAN](https://hdbscan.readthedocs.io/en/latest/) to cluster these reports into problem areas. This led to a somewhat cohesive result, but one that is still not very useful to the casual observer.

<img src="/images/pothole_clusters/Final_Cluster.png" alt="Final Cluster" style="max-width:100%;max-height:100%"/>

A cycling route is ultimately a set of decisions about which turns to make and therefore which streets to ride on. These decisions occur at intersections, and in a grid there are generally 3 options (4, if you want to turn around). Each option leads you down a block to another intersection and so on. Except at the beginning and end of a route, it's fairly rare that a given block would not be completed. Conceptually then, a block is the basic unit of travel, and the sum of the blocks you ride determines the entire route.

In the long term, I'd like to develop an application that would build a set of directions using this mental model, weighting a number of factors (road conditions, bike lanes, direction of travel, etc). To do this, I'll need to transform the data I have into block-based vectors that could then be used to quantify the "value" of a block. 

### Street Data
New York City's Department of City Planning publishes their [LION dataset](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-lion.page), which is a "single line representation of New York City streets containing address ranges and other information." This is a very rich source of data, and it means I can avoid using GoogleMaps or [Open Street Map](https://www.openstreetmap.org/) for now. OSM is a great resource, but I'm not overly familiar with it and the learning curve seems a little steep. OSM is more scalable, but I don't really see myself using this outside of NYC. We'll see - I may regret this decision.

The LION dataset is huge (the [data dictionary](https://www1.nyc.gov/assets/planning/download/pdf/data-maps/open-data/lion_metadata.pdf?r=17a#:~:text=LION%20is%20a%20single%20line,its%20suitability%20for%20any%20purposes.) alone is 49 pages!), so I'm going to use [their REST api](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/LION/FeatureServer/0) to pull what I need. I made a simple function to build the request URL that allows me to pass in which columns to select. I didn't care to dig into the URL encoding and format for this, but if needed I could extend this to accept variable `WHERE` statements, etc. The API also requires a `WHERE` statement, so I just threw in something meaningless.

~~~python
def make_url(select_list, offset):
    url_prefix = 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/LION/FeatureServer/0/query?'
    where_statement = 'where=LZIP+%3C%3E+-1'
    middle_text = '&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&'
    select_statement = f'outFields={"%2C+".join(select_list)}'
    url_suffix = f'&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset={offset}&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=false&quantizationParameters=&sqlFormat=none&f=pjson&token='
    return f'{url_prefix}{where_statement}{middle_text}{select_statement}{url_suffix}'
~~~

The API only returns 2000 rows per request, so I had to set up a simple loop to iterate through requests until all the data has been retrieved. Once I get a request with less than 2000 rows, I know I've hit the end. I also do some data organization to parse through the JSON and format it tabularly (a list of dictionaries). Converting it to a dataframe makes it easy to save as a local .CSV so that I don't have to hit the API every time I spin up the script.

One other tricky bit is that the LION dataset does not store the geographic data into latitudes and longitudes as I am used to reading them. There is a concept called [`ESPG`](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) that allows for different methods of storage and transformation of geographic data. Because graphical representations of a sphere are difficult in 2D, there are a LOT of different coordinate systems used. I'm no GIS expert so I can't provide much background information here, but the LION dataset is currently stored using ESPG:2263 and the commonly understood lat/long data is stored using ESPG:3857. Luckily, [pyproj](https://github.com/pyproj4/pyproj) has a `Transformer` object that will convert between these ESPG codes for us, which I initiate before the loop gets going.

~~~python
from pyproj import Transformer
import requests
import json
import pandas as pd

offset = 0
block_data = []
return_length = 2000
while return_length ==  2000:
    response = requests.get(make_url(select_list, offset))
    json_data = json.loads(response.text)
    return_length = len(json_data['features'])
    if offset == 0:
        transformer = Transformer.from_crs(f"epsg:{json_data['spatialReference']['latestWkid']}", "epsg:4326")
    for block in json_data['features']:
        row = {}
        row['start_coords'] = transformer.transform(block['geometry']['paths'][0][0][0]
                                                    , block['geometry']['paths'][0][0][1])
        row['start_lat'] = row['start_coords'][0]
        row['start_long'] = row['start_coords'][1]
        row['end_coords'] = transformer.transform(block['geometry']['paths'][0][1][0]
                                                  , block['geometry']['paths'][0][1][1])
        row['end_lat'] = row['end_coords'][0]
        row['end_long'] = row['end_coords'][1]
        row['borough'] = block['attributes']['LBoro']
        row['street_name'] = block['attributes']['Street']
        row['id'] = block['attributes']['OBJECTID']
        row['l_block'] = block['attributes']['LCB2010']
        row['r_block'] = block['attributes']['RCB2010']
        row['l_block_suf'] = block['attributes']['LCB2010Suf']
        row['r_block_suf'] = block['attributes']['RCB2010Suf']
        row['seq_num'] = block['attributes']['SeqNum']
        row['face_code'] = block['attributes']['FaceCode']
        row['l_blockface'] = block['attributes']['LBlockFaceID']
        row['r_blockface'] = block['attributes']['RBlockFaceID']
        row['physical_id'] = block['attributes']['PhysicalID']
        block_data.append(row)
    offset = len(block_data)

lion_df = pd.DataFrame(block_data)
lion_df.to_csv('lion.csv', index=False)
~~~

### Bad Blocks

Now that I have some data to work with, I need to identify which blocks have clustered issues. In the future, I may do some work to identify the severity of a block's road conditions, but for now I want a boolean identifier that a block is "bad."

The logical next step was to simply take the coordinates of each issue and see if they intersect with a block from the LION dataset.

As an example, I'll get a specific issue and attempt to find it's associated block. I pick a random record from the issue data and filter down the LION dataset to just the blocks with that street name, since I don't know exactly which block my random coordinate is on.

The LION dataset stores each linear segment of street as its own record. I sort and join those linear segments together to identify a block's LineString (more on this later). First I group each record's physical_id together, which is a representation of a "Physical View of the city's street network." Then I concatenate each segment together to get each block's LineString. Creating the LineStrings is a real pain, but I get there eventually.

~~~python
from shapely.geometry import Point
from shapely.geometry import LineString

issues_df = pd.read_csv('311_road_clusters.csv')

random_rec = issues_df.sample()
issue_point = Point(random_rec.latitude.values[0], random_rec.longitude.values[0])

filtered_street = lion_df[(lion_df.street_name == random_rec.street_name.values[0])].copy()
filtered_street.sort_values(['physical_id','seq_num'], inplace=True)
start_lat_list = filtered_street.groupby(['physical_id'])['start_lat'].apply(list).tolist()
start_long_list = filtered_street.groupby(['physical_id'])['start_long'].apply(list).tolist()
end_lat_list = filtered_street.groupby(['physical_id'])['end_lat'].apply(list).tolist()
end_long_list = filtered_street.groupby(['physical_id'])['end_long'].apply(list).tolist()
formatted_start_block_coords = [list(zip(start_lat_list[i],start_long_list[i])) for i in range(len(start_lat_list))]
formatted_end_block_coords = [list(zip(end_lat_list[i],end_long_list[i])) for i in range(len(start_lat_list))]
final_list = []
for i in range(len(formatted_start_block_coords)):
    x = [val for pair in zip(formatted_start_block_coords[i], formatted_end_block_coords[i]) for val in pair]
    final_list.append(x)
~~~

To get a sense, I'll map out a test point here and the blocks that it may cross.

```python
import gmplot

gm_api_key = 'YOUR_API_KEY'
gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

gmap.scatter(lats=[issue_point.x]
             , lngs=[issue_point.y]
             , alpha=.3
             , size=20
             , marker=False)
    
for block in final_list:
    path= zip(*block)
    gmap.plot(*path, edge_width=4, color='blue')

gmap.draw('map.html')
```
<img src="/images/bad_blocks/bb_line.png" alt="Final Cluster" style="max-width:100%;max-height:100%"/>

Ok - so it looks like these cross!

[Shapely](https://shapely.readthedocs.io/en/latest/) is an amazing library for working with geometries in python, and I highly recommend it - there is a ton of great functionality here. I won't get too in depth with shapely objects right now, but I will store the issue location as a Point, and each block as a LineString. 

~~~python
issue_point = Point(random_rec.latitude.values[0], random_rec.longitude.values[0])
block_linestrings = [LineString(x) for x in final_list]
~~~

Shapely has a `contains` method that returns whether or not a point intersects with a block. 

~~~python
for linestring in block_linestrings:
    if linestring.contains(issue_point):
        print(True)
~~~    

Uh-oh... nothing printed. What happened?

Because lines and points have no (or negligible) width and depth, the likelihood that a point and a line cross is actually relatively low. In the real world, streets have width, meaning that a street itself is actually a rectangle and it isn't accurate to represent it as a line.

To transform these lines into rectangles, Shapely has me covered again. There is a [`buffer`](https://shapely.readthedocs.io/en/latest/manual.html#object.buffer) method that functions very similarly to `offset` in AutoCAD - it turns a line into a polygon with a specified width. At NYC's latitude, .0001 degrees is roughly 30 feet, which is about the same as your average NYC cross street. This isn't perfect because street widths vary, but for now it will work.

Because I'm having a hard time explaining this, I'll transform a line and plot it.

~~~python
block_rectangles = [list(x.buffer(.0001, cap_style=2).exterior.coords) for x in block_linestrings]

gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

gmap.scatter(lats=[issue_point.x]
             , lngs=[issue_point.y]
             , alpha=.3
             , size=20
             , marker=False)

for block in block_rectangles:
    path= zip(*block)
    gmap.polygon(*path, color='blue', edge_width=1)

gmap.draw('map.html')
~~~

<img src="/images/bad_blocks/bb_poly.png" alt="Final Cluster" style="max-width:100%;max-height:100%"/>

Now when zoomed in, the street has a real width.

Using the `contains` method on the point and rectangle, it prints true once, which means the point now has an associated block!

~~~python
block_polygons = [x.buffer(.0001, cap_style=2) for x in block_linestrings]
for polygon in block_polygons:
    if polygon.contains(issue_point):
        print(True)
~~~
~~~python
True
~~~  

### Scale

Now that the problem has been solved theoretically, it needs to be scaled to all of the road condition reports and blocks across the city. Finding these intersections might be possible in pandas, but I think it'll be prohibitively slow. Instead I'll spin up a SQLite DB to handle this join.

SQLite won't handle all these custom objects very well, but Shapely can encode them as strings. In making this adjustment, I rewrote some of the code to be a bit simpler and to apply to the entire dataframe.

~~~python
meta_columns = ['physical_id','borough','street_name']
geo_columns = ['start_lat','start_long','end_lat','end_long']
grouped_ids = lion_df[meta_columns+geo_columns].groupby(meta_columns).agg(list)
grouped_ids['start'] = grouped_ids.apply(lambda x: zip(x['start_lat'],x['start_long']), axis=1)
grouped_ids['end'] = grouped_ids.apply(lambda x: zip(x['end_lat'],x['end_long']), axis=1)
grouped_ids['block_line'] = grouped_ids.apply(lambda x: [val for pair in zip(x['start'],x['end']) for val in pair]
                                              , axis=1)
grouped_ids['encoded_poly'] = grouped_ids.apply(lambda x:LineString(x['block_line']).buffer(.0001
                                                                                               , cap_style=2).wkb
                                                   , axis=1)
block_df = grouped_ids.reset_index()[meta_columns+['encoded_poly']]

issues_df['encoded_point'] = issues_df.apply(lambda x: Point(x['latitude'],x['longitude']).wkb, axis=1)
~~~

Now I'll create the SQLite DB and create tables for both the blocks and issue points. The try/except statements here aren't really necessary, but I included them as I was testing and iterating.

~~~python
import sqlite3

conn = sqlite3.connect('road_conditions.db')
cur = conn.cursor()

try:
    block_df.to_sql('blocks',conn)
except:
    conn.execute('drop table blocks')
    block_df.to_sql('blocks',conn)

try:
    issues_df.to_sql('issues',conn)
except:
    conn.execute('drop table issues')
    issues_df.to_sql('issues',conn)
~~~  

SQLite allows for the creation of [user defined functions](https://www.sqlite.org/appfunc.html), and [SQLite3](https://docs.python.org/3/library/sqlite3.html) has a nice method to pass in python functions with `create_function()`.

With this, I'll create a function that takes in encoded polygons and points, decodes them, then returns the boolean value to determine if the polygon contains a given point using the `contains` function.

~~~python
from shapely import wkb

def check_intersection(encoded_point, encoded_poly):
    return wkb.loads(encoded_poly).contains(wkb.loads(encoded_point))

conn.create_function('check_intersection', 2, check_intersection)
~~~

I can now use this function in a join statement to return all block/report intersections, which will be the "bad" blocks.

I join on `street_name` here because they generally match well between these two datasets - only 264 issues have no match on street name. Without this in the join, the query ran considerably slower.

~~~python
sql = '''
    SELECT
        i.*
        , b.*
    FROM issues i
    INNER JOIN blocks b
        ON check_intersection(i.endcoded_point, b.encoded_linestr)
        AND i.street_name = b.street_name
    '''

matched_points = pd.read_sql_query(sql, conn)

conn.commit()
conn.close()
~~~

There were originally 16400 records in `issues_df`. In the output,`matched_df`, there are 16153 records. Of these, there are 1206 points with more than one matched street and in total there are now only 14871 issues, down about 10%.

A one-to-many relationship between issue and street is to be expected, as the street shapes tend to overlap at intersections. I'm not particularly worried about this.

On the other hand, I am concerned about that loss - I was hoping to see something more in the 5% range. When I checked some of these, three patterns arose:

1. Some points simply don't have very accurate coordinates, mapping in the middle of a block with no discernable street.
2. Some points map near the street, but not within the rectangle. 
3. Some points lie on an incorrectly identified street in the 311 data.

Issue #1 I will mostly ignore - there isn't a lot that can be done with bad data.

Issue #2 can be addressed by widening the street shapes. As a test, I increased the width of the street from .0001 to .0002. This resulted in 15122 distinct issues in `matched_points`, or a loss of 8%. The number of duplicates almost doubled from the original run. Duplicating a "bad block" isn't really problematic since it's a boolean measure, but I wouldn't want to start misidentifying certain blocks when they incorrectly overlap.

Issue #3 can be addressed by removing the `street_name` from the join statement. Unfortunately, 3 hours later this query is still running. In a production version it would be run daily or weekly at best, so the decreased speed might be manageable down the road.

With that testing done, I think I'll keep everything as-is. None of the solutions here result in an vastly improved output with the known issues.

Now that all of the issues are associated with a given block, I'll map out all of the "bad blocks."

~~~python
polygon_gmplot = [wkb.loads(x).exterior.coords for x in matched_points.encoded_poly.unique()]

gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

for block in polygon_gmplot:
    path= zip(*block)
    gmap.polygon(*path, color='red', edge_width=1)

gmap.draw('map.html')
~~~

<img src="/images/bad_blocks/bb_final.png" alt="Final Cluster" style="max-width:100%;max-height:100%"/>

I like this! There are obviously a lot of bad blocks in NYC, but that shouldn't surprise anyone. I'm not going to claim that this is perfect, but it does give a good general sense.

### Disclaimer

I imagine by this point, anyone who has done any experience with GIS will have recognized a number of flaws in my work. Everything I have done relies on the idea that NYC exists on a cartesian plane, which is not true - the earth is round ([or.. I think it is](https://www.nytimes.com/2018/06/08/movies/kyrie-irving-nba-celtics-earth.html)). This quick and dirty method works for a small enough geographic space like New York for now. I definitely need to learn more to have a deeper understanding of geographic concepts and the tools that modern cartographers are using. If you have any good resources or critiques, please send them my way!