---
layout: post
title: Visualizing my Winter Commute
disqus: true
---

I moved to New York in January to participate in the Metis data science bootcamp, which meant that I finally could commute by bike! Luckily the winter wasn't too cold and I was able to ride to Metis most days, though I do try to avoid rain and snow. I track almost all my rides using my [Wahoo cycling computer](https://www.wahoofitness.com/devices/bike-computers/gps-elemnt-bolt) and by using [GoldenCheetah](https://www.goldencheetah.org/) I was able to convert the data from the .fit format to .csv for Tableau. [Strava](https://www.strava.com/dashboard) and GoldenCheetah have some good visualizations and analysis built in, but since I'm still learning Tableau I thought I'd do some myself as well.

If this project has taught me anything, it's that I need more sensors to get more data! Still looking for a reasonably priced power meter...

By combining all of my commutes I was able to get my median speed at each point along the route and calculate some cool cumulative statistics. If you click on a given day in one of the following graphs, the map will highlight that day's commute.

 <div>
  	<center>
	<div class='tableauPlaceholder' id='viz1523896653229' style='position: relative'>
		<noscript>
			<a href='#'>
				<img alt='  NYC Winter Bike Commuting ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;NY&#47;NYC_Rides&#47;DashBoard&#47;1_rss.png' style='border: none' />
			</a>
		</noscript>
		<object class='tableauViz'  style='display:none;'>
			<param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> 
			<param name='embed_code_version' value='3' /> <param name='site_root' value='' />
			<param name='name' value='NYC_Rides&#47;DashBoard' /><param name='tabs' value='no' />
			<param name='toolbar' value='yes' />
			<param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;NY&#47;NYC_Rides&#47;DashBoard&#47;1.png' /> 
			<param name='animate_transition' value='yes' />
			<param name='display_static_image' value='yes' />
			<param name='display_spinner' value='yes' />
			<param name='display_overlay' value='yes' />
			<param name='display_count' value='yes' />
			<param name='filter' value='publish=yes' />
		</object>
	</div>                
	<script type='text/javascript'>                    
			var divElement = document.getElementById('viz1523896653229');                    
			var vizElement = divElement.getElementsByTagName('object')[0];                    
			vizElement.style.width='650px';
			vizElement.style.height='2027px';                   
			var scriptElement = document.createElement('script');                    
			scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    
			vizElement.parentNode.insertBefore(scriptElement, vizElement);                
	</script>
	</center>
 </div>
<div><br></div>

There isn't too much to talk about for this post - hopefully the visualizations speak for themselves! The interactions run a bit slowly through the blog, but not locally. I'm guessing Tableau Public isn't offering as much speed as I'd like. My Tableau learning continues...
