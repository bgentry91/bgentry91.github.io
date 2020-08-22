---
layout: post
title: Directions
subtitle: How bad are they?
disqus: true
---

Continuing with my [series of mapping NYC road conditions](https://bgentry91.github.io/blog/Bad_Blocks/), I determine a route using GoogleMaps and indentify the associated road conditions.

As I mentioned in my last post, the long term goal of this work is to develop an application that generates better cycling directions in NYC. Before I get to that, I want to continue to refine the data I have by building an intermediate tool. 

### GoogleMaps Directions
Similar to the [Maps Javascript API](https://developers.google.com/maps/documentation/javascript/overview) I've been using, GoogleMaps also offers a [Directions API](https://developers.google.com/maps/documentation/directions/overview). This does exactly what it sounds like - put in two points and it will return three options for a cycling route.

Again you'll need to use your API key - don't forget that if you go beyond the free tier, they will start charging you. Unfortunately [gmplot](https://github.com/gmplot/gmplot/wiki/GoogleMapPlotter.directions) doesn't return 3 route options, so I'll use the [googlemaps](https://github.com/googlemaps/google-maps-services-python) library instead.

As an example, I'll create a quick set of directions between [Prospect Park and McCarren Park](https://www.google.com/maps/dir/Grand+Army+Plaza,+Flatbush+Avenue,+Brooklyn,+NY/40.7197788,-73.9534579/@40.7189569,-73.9537075,17.24z/data=!4m9!4m8!1m5!1m1!1s0x89c25b081e94025d:0x243cd23d852fc32a!2m2!1d-73.9700893!2d40.6738771!1m0!3e1).

~~~python
import googlemaps

gm_api_key = 'YOUR_API_KEY'
gmaps = googlemaps.Client(key=gm_api_key)

directions = gmaps.directions(
    origin = "Grand Army Plaza Brooklyn NY"
    , destination = "201 N 12th St, Brooklyn NY"
    , mode = 'bicycling'
    , alternatives = True
)
~~~

`directions` is a json-formatted response of the three routes provided by Google. Below, I convert this to a tabular format, with each route as a row. Google encodes their line segments, so I use the simple [polyline](https://github.com/hicsail/polyline) library to decode these to coordinates. I then group these decoded segments into one LineString for the entire route using [shapely](https://shapely.readthedocs.io/en/latest/manual.html).

~~~python
from shapely.geometry import LineString
import polyline
import pandas as pd

direction_data = []
for i, direction in enumerate(directions):
    line_data = {}
    line_data['option'] = i
    line_data['line'] = []
    for leg in direction['legs']:
        line_data['distance']  = leg['distance']['text']
        for step in leg['steps']:
            line_data['line'].extend(polyline.decode(step['polyline']['points']))
    line_data['linestr'] = LineString(line_data['line'])
    direction_data.append(line_data)
    
directions_df = pd.DataFrame(direction_data)
~~~

### How bad are they?

Now I need to calculate the length of each route that passes through a "bad block". Shapely comes to the rescue again, but things get a bit complicated here. Because some of the block shapes overlap, if I simply calculate the total distance by which the route crosses a bad block, there is an opportunity to double count certain segments. To handle this, I have to merge overlapping segments prior to calculating the intersection distances.

This may be a bit difficult to conceptualize, so I'll make an example in shapely and use matplotlib to help visualize. I do quite a bit of data manipulation to make shapely happy - I'll gloss over it for now - it's just there to help build the charts.

~~~python
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from itertools import chain
%matplotlib inline

a = Polygon([(0,0),(0,2),(.5,2),(.5,0)])
b = Polygon([(.25,1.5),(.25,2),(3.5,2),(3.5,1.5)])
c = Polygon([(3.55,2),(4.05,2),(4.05,0),(3.55,0)])

route = LineString([(2,.5),(.4,.5),(.4,1.75),(5,1.75)])

shapes = [a,b,c]

def segments(line):
    try:
        line = [list(x.coords) for x in [a for a in line.geoms]]
        line = list(chain(*line))
    except:
        pass
    return [x[0] for x in line.coords],[x[1] for x in line.coords]

fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

shape_colors = ['red','purple','green']

for i, shape in enumerate(shapes):    
    xs, ys = shape.exterior.xy    
    axs.fill(xs, ys, alpha=0.3, fc=shape_colors[i], ec='none')
    
xs,ys = segments(route)
axs.plot(xs, ys, alpha=1)

plt.show();      
~~~

<img src="/images/directions/example_base.png" alt="Base Example" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

I've created three different Polygons and one line segment that runs through each of the polygons. Two of the polygons overlap - this is important! In its current form, I could simply sum up the total length of the line that intersects the polygons.

~~~python
total_intersect = 0
for shape in shapes:
    total_intersect += route.intersection(shape).length
~~~

Using this method, `total_intersect` = 5.3.

To show what's happening here, I can plot each intersection (Just showing one example here, you can replace the variables as needed).

~~~python
fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

shape = a
color = shape_colors[0]

xs, ys = shape.exterior.xy    
axs.fill(xs, ys, alpha=0.3, fc=color, ec='none')
    
xs,ys = segments(route.intersection(shape))
axs.plot(xs, ys, alpha=1)

plt.show();
print(f'Intersection is {route.intersection(shape).length} long.')
~~~

<img src="/images/directions/example_a_bad.png" alt="Example A Bad" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

<img src="/images/directions/example_b_bad.png" alt="Example B Bad" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

<img src="/images/directions/example_c_bad.png" alt="Example C Bad" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

Total from this is 5.3 - but we've counted the overlap between shapes A & B twice.

Shapely has a neat function `unary_union()`, that will take a list of shapes and create one large shape in the form of a "MultiPolygon". This will "dissolve" the overlaps between the `a` and `b` shapes, while retaining the `c` shape as its own entity in the MultiPolygon. When I use `list()` on the MultiPolygon, the non-overlapping shapes split.

~~~python
from shapely.ops import unary_union
multi = unary_union(shapes)

fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

shape_colors = ['red','green']

for i, shape in enumerate(list(multi)):    
    xs, ys = shape.exterior.xy    
    axs.fill(xs, ys, alpha=0.3, fc=shape_colors[i], ec='none')
    
plt.show()
~~~

Now if I calculate the length using the same method as before, it returns 4.95.

~~~python
total_intersect = 0
for shape in multi:
    total_intersect += route.intersection(shape).length
~~~

For comparison, this is what is happening in the correct methodology:

<img src="/images/directions/example_a_good.png" alt="Example A Good" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

<img src="/images/directions/example_b_good.png" alt="Example B Good" style="width:75%; height:75%;max-width:100%;max-height:100%"/>

### Scale it up
Now that I have the tools to manipulate these shapes and properly calculate the lengths needed, I can apply it to the actual block data.

~~~python
from shapely import wkt

def calc_overlap(line, blocks):
    total_length = 0
    for shape in blocks:
        total_length += route.intersection(shape).length
    return total_length

matched_points = pd.read_csv('matched_points.csv')
bad_blocks = matched_points[['physical_id', 'encoded_poly']].drop_duplicates()
combined_blocks = list(unary_union([wkb.loads(ast.literal_eval(x)) for x in bad_blocks['encoded_poly'].tolist()]))

route = direction_data[0]['linestr']

total_length = route.length
bad_length = calc_overlap(route, combined_blocks)
~~~

This results in a route that is considered to be on "bad" roads for 29.7% of it's length. 

If I plot it, maybe I can get a sense for how good the route is (do nearby alternatives have better road conditions?).

~~~python
import gmplot

gmap = gmplot.GoogleMapPlotter(40.645683,-73.94915, 12, apikey=gm_api_key)

for block in combined_blocks:
    path= zip(*block.exterior.coords)
    gmap.polygon(*path, edge_width=4, color='red', alpha=.5)
    
linestr = direction_data[0]['linestr']
path= zip(*linestr.coords)
gmap.plot(*path, edge_width=4, color='blue')


# Draw the map:
gmap.draw('map.html')
~~~

<img src="/images/directions/route_mapped.png" alt="Route_Mapped" style="max-width:100%;max-height:100%"/>

It actually looks pretty good! It's very easy to see where the bad blocks are, and if I zoom and look around, it's relatively easy to find alternative routes.


### Ok, but the earth is round.
In my previous post I addressed some issues with using shapely, as it assumes a Cartesian coordinate system. After some reading I learned about [geopandas](https://geopandas.org/index.html), which is actually built on top of shapely. It has many of the tools that shapely offers, but if given the proper coordinate reference system (CRS), it will more accurately calculate geometries. It also handles shapes from shapely, so it's very easy to plug in to from my current code.

As I mentioned in an earlier post, I converted the [LION dataset](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-lion.page) from [ESPG:2263](https://spatialreference.org/ref/epsg/2263/) to [EPSG:4326](https://spatialreference.org/ref/epsg/4326/). Now that I've learned more, I can explain that EPSG:2263 is a spatial reference system that is commonly used for New York and is calculated in feet. EPSG:4326, also known as WGS 84, is used in GPS systems and is the lat/long system many of us commonly understand. Unfortunately, distances in this system are in degrees - not a very helpful unit.

EPSG:4326 also is a bit confusing as it stores data as `(Lat,Long)` tuples. Because programmers like mathematical standards, they like to store these as `(x,y)` tuples. When I create GeoSeries or GeoPandas objects using my Shapely objects, I need to flip the axes and then initiate them with the EPSG:4326 CRS to ensure it handles this properly.

The geopandas code looks very similar to the shapely code from above. Don't forget to divide by 5280 to convert from feet to miles!

~~~python
import geopandas

route = direction_data[0]['linestr']
flipped_route = shapely.ops.transform(lambda x, y: (y, x), route)
geo_route = geopandas.GeoSeries(flipped_route).set_crs(epsg=4326).to_crs(epsg=2263)
total_length = geo_route.length/5280

bad_length = 0
for block in combined_blocks:
    flipped_block = shapely.ops.transform(lambda x, y: (y, x), block)
    geo_block = geopandas.GeoSeries(flipped_block).set_crs(epsg=4326).to_crs(epsg=2263)
    bad_length += geo_route.intersection(geo_block).length/5280
~~~

This results in a route that is considered to be on "bad" roads for 28.3% of it's length, compared to 29.7% from the original method. The vanilla shapely code runs in about 15 seconds while the geopandas version took around 10 minutes. The geopandas would be fairly parallelizable, so it could be sped up relatively easily.

I'm glad to have learned a bit more about how all this works and added something to the toolbox. For now I may stick with shapely for it's out-of-the-box speed, but it's always good to have a sense of the magnitude of error.

With this in mind, I'll have to go back and adjust some of the road condition calculations from my last two posts. 