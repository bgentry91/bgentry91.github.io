---
layout: post
title: Red Hook Crit
disqus: true
---

Last week I went to the [Red Hook Crit](https://redhookcrit.com/) in Brooklyn, which definitely one of the best races out there. It's is a bit different than a "traditional" race in that riders must use brakeless fixed gear bikes on short (~1km) laps with very tight corners. It's a mix of semi-pro and amateur riders and makes for a great spectating event - between spectacular crashes, views of Manhattan, and good beer, it's hard to beat.

The week before, my brother had shown me the results from [Mission Crit](http://www.missioncrit.com/), which had a pretty cool [breakdown](http://www.results.crossmgr.com/2018/04-21/2018-04-21-Mission%20Crit%20V-r9-.html?raceCat=Final%20%28Men%29). I figured I could make the same thing for Red Hook!

The data was scraped from the posted [RaceTec Results](http://www.racetecresults.com/Results.aspx?CId=17063&RId=153) using [scrapy](https://scrapy.org/) and a little bit of [selenium](https://www.seleniumhq.org/). Cleaning was done in python and the visualization was built in D3(https://d3js.org/). GPS coordinates for the course were downloaded from the [RHC Strava Segment](https://www.strava.com/segments/17511578).

One BIG caveat - the data is only at the lap level, so exact locations are linearly interpolated. Have to find a way to get all the riders' .fit files from the race...

<iframe src="https://bgentry91.github.io/RHC/" style="border:3px black solid;" width = "730" height="875" scrolling="no"></iframe>