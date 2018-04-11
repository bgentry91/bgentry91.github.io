---
layout: post
title: A Shallow Analysis of the Cobbled Classics
disqus: true
---

### Cobbled Classics
In the past year or so I've started to watch quite a bit of pro cycling. Like many, I started with the Tour de France but have since branched out, especially to the one-day races. They generally have a good bit of drama without the weeks-long time commitment. The ["Cobbled Classics"](https://en.wikipedia.org/wiki/Cobbled_classics) are four early season one-day races that feature numerous sections of pavé (cobblestones). The length of these races (250km+) combined with the pave sections make for some great racing.

This year, everyone has been talking about the domination of [Quick-Step Floors](http://www.quickstepfloorscycling.com/) in the early season races. Since I had the opportunity this week to learn [Tableau](https://www.tableau.com/) and we're in a bit of a lull after [Paris-Roubaix](https://en.wikipedia.org/wiki/Paris%E2%80%93Roubaix), I thought I'd explore the results.

### Analysis
I called this a shallow analysis because I was just trying to learn Tableau without doing a ton of data wrangling. I simply pulled the results of the four races from [CyclingNews](http://www.cyclingnews.com/) and combined them. I had to do a little cleanup in pandas because CyclingNews doesn't report rider names consistently, but everything else was straightforward.

As an aside - Tableau does a pretty good job of allowing you to share your visualizations. Embedding is relatively easy (looking at you, D3/bl.ocks). The graphic is interactive, so play around with it!

<div>
	<div class='tableauPlaceholder' id='viz1523479019489' style='position: relative'><noscript><a href='#'><img alt='Cobbled_Classics ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Co&#47;Cobbled_Classics&#47;Cobbled_Classics&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='Cobbled_Classics&#47;Cobbled_Classics' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Co&#47;Cobbled_Classics&#47;Cobbled_Classics&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1523479019489');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height='1577px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                
	</script>
	</div>
<div><br></div>
As you can see, Quick-Step controlled these races. They were on the podium in every race and had at least 4 riders in the top 30 of each. The last diagram sends the point home - no other team even comes close to Quick-Step's number of top 20 finishers (15! next is BMC with 7). Having that many racers up front makes a huge difference when supporting their leader. It's also impressive to see the consistency of the Quick-Step racers. Stybar never missed a top-10 and Gilbert never fell outside the top 20. Aside from his bad race in Gent-Wevelgem, Terpstra was consistently in the top 3.

It's clear the the Belgians love these races. They couldn't pull out a win, but the top 20 in each race was at least 35% Belgian! Granted, the number of Belgian racers is almost double that of any other nationality (71, second is France at 39). Below is a map showing the breakdown of racer nationalities. If you're feeling less Euro-centric, feel free to zoom out.


<div>
<div class='tableauPlaceholder' id='viz1523478112909' style='position: relative'><noscript><a href='#'><img alt='Dashboard 1 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;CC&#47;CC_Map_1&#47;Dashboard1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='CC_Map_1&#47;Dashboard1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;CC&#47;CC_Map_1&#47;Dashboard1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1523478112909');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height='827px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
</div>
<div><br></div>

### Tableau
Being that this was my first foray into Tableau and this is technically a data science blog, I feel like I should give my first impressions. Since my other experience is with D3 and Excel, most of my comparisons will start there.

First, I love open source software. Tableau isn't too bad ($35/month), but outside a professional setting it is not cheap. If I'm paying, I'm going to go with D3 every time.

As far as visualization options go, if I'm creating package-standard graphs it performs well. Outside of that it starts to feel very hacky. People create some interesting and crazy stuff, but the thought and effort behind it is a bit ridiculous. I tried my hand at a [Sankey diagram](https://en.wikipedia.org/wiki/Sankey_diagram) using SuperDataScience's [YouTube tutorial](https://www.youtube.com/watch?v=1HwCzlA9hI4&t=984s). While I was able to get something to pop out, I could never get it to look polished.

The dashboard UI is terrible. Just terrible. I struggled with the tiled geometry and opted mostly for floating. There is no object snap and no grid, so you do a lot of manual shifting of the objects (either by inputting pixel locations or mouse-dropping). As far as I can tell, you can't even use the arrows keys to move them around. The worst part of the dashboard is sizing it. There are a bunch of predefined sizes that were helpful, but I hope you choose the right one the first time. If you change the size, the software automatically resizes all of your objects... and not in a sensible way. I spent more time than I'd like to admit resizing objects to get everything perfect(ish). As a program made for ease of use, this is unacceptable. I'd rather build my dashboards in Microsoft Visio, and that's saying something.

Formatting the graphs in the UI wasn't terrible once I got the hang of it. It's pretty tedious (I must be missing some keyboard shortcuts), but it generally gets the job done. I don't love the automatic formatting, and occasionally I would change something and the software would overwrite my custom formatting. This could be pretty annoying if I didn't do things in the right order. I am still not sure what the columns/rows mean and after about 20 hours I'd say I only get it right about 50% of the time.

The calculated fields are great, and I think as I get more experience they will come in handy. The functions are very similar to Excel which makes for an easy transition. The size, shape, and label parameters are wonderful. I only imported data from a .csv, but that was very easy. I have heard that Tableau struggles with direct database connections that are constantly updating, but I didn't get a chance to test that out.

Because markdown formatting is fun, I thought I'd build a table comparing the three visualization options. I ranked them on a 1-5 scale (5 is best), but my reasoning is pretty off the cuff - don't read too much into it.

|Feature|D3|Tableau|Excel|
|:---:|:---:|:---:|:---:|
|Learning Curve|1|3|5|
|Cost|5|1|3|
|Simple Graphs/Shapes|1|5|4|
|Complex Graphs/Shapes|5|3|1|
|Graph Customization|5|4|2|
|Mapping|4|5|0|
|Data Manipulation|4|3|4|
|Data Structure|3|3|4|
|Community/Resources|5|4|5|
|Sharing|3|5|5|
|Marketing Department Ranking|4|5|0|






