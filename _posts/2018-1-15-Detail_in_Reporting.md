---
layout: post
title: Detail in Reporting - Missing the Forest for the Trees?
disqus: true
---

### The Problem

For our first project at Metis, we were assigned the task of optimizing the placement of street teams at the entrance of NYC subway stations. These teams were to collect e-mail addresses for those who were interested in attending a gala held by "WomenTechWomenYes" (WYWT). At the conclusion of the project, we were to present our findings and recommendations.

In order to accomplish this, we collected data from the [MTA turnstile dataset](http://web.mta.info/developers/turnstile.html), which is a relatively "dirty" dataset of the entries and exits at each individual turnstile that the MTA manages. The entry and exit data is collected roughly every four hours (with some extra and missing).

Because we had this data at such a granular level, we thought it best to try to report it to WYWT at this level. This meant giving the organization data for each potential four hour time slot. Becuase we felt that week over week changes were minimal, we decided to present to them a weekly "plan" that would allow them to choose the best station(s) for any four hour window during the week. Below is the graph we created to show the busiest stations at each four-hour increment.

<img src="/images/Benson_Graph.png" alt="Benson_Graph" style="width: 600px;"/>

As the other groups presented their data, I was surprised to find that very few others had organized their data in this way - most simply gave recommendations for the top stations and the best times (i.e. Times Square, Weekday Rush Hour). To me it seemed clear that the organization would want as much detail as possible, especially if they wanted to truly optimize their team placement. I asked one of the later groups why they had chosen to report their results in this way, since they clearly had the data in four hour increments. They responded that it was obvious what the best times were, so there was no benefit in adding those details. If 12-4AM on Sunday nights have minimal foot traffic, why clutter their recommendations?

This was an interesting point that I hadn't considered. Even in the project we advised against these "bad" time slots, but still reported them as options. As I thought about it, I was a little disappointed that we had fallen into this over-reporting trap. In order to prevent myself from repeating my mistake, I did some research on detail in reporting and found some general guidelines from [Jennifer Shin's blog on the IBM Big Data & Analytics Hub](http://www.ibmbigdatahub.com/blog/data-visualization-playbook-determining-right-level-detail).

To me, she summed it up as:
1. Visualize it all. If it's too busy, look at summary statistics.
2. Plot what you want to show. Don't crowd your visualization with things that aren't important.
3. Don't overdo it. Too many summary statistics can cause you to lose your message.
4. Try different visualizations. You may notice some "hiding" insights or find a more appealing way to tell your story.

Given these principles, I wanted to get back into the dataset to try to improve my visualization. I decided to start by looking at the data for my local stop, Utica Ave. Since the proposed problem had the gala in June, we pulled in 4 weeks of turnstile data for May 2017. For values that were obviously too large, I simply removed them. Where values were missing or had been removed, I attempted to take the median of the surrounding slots to fill that time slot. 

### Plotting the Data

Using Seaborn, I went ahead and plotted every data point.

<img src="/images/Utica_Graph1.png" alt="Utica 1" style="width: 600px;"/>

As you can see, it's a pretty big mess. The x-axis is unreadable, and there is so much data you really can't pick much out. The only insight that grabs me is that it looks like the data is pretty consistent week over week. This is good - if there aren't different patterns throughout the month, I can probably drill down to just one week.

If I consolidate the data to the daily totals, I get the graph below.

<img src="/images/Utica_Graph2.png" alt="Utica 2" style="width: 600px;"/>

This graph clearly shows that the number of passengers is consistent on any given day of the week - and as a bonus, we see that the all of the weekdays are very consistent as well. I think this would be a helpful graph in an appendix, as most people would probably agree with the assertion that the subway is busiest on weekdays. If someone disagreed, you could pull this out!

One note: Saturdays have some variation at Utica Ave, and the dataset has no data for Utica on the 27th. Not much can be done about missing data, but the discrepancy on the 13th may be worth looking into if we see it across multiple stations.

As I look back at the first Utica graph, I also notice that there seems to be some repetition from time period to time period. If we rearrange the data that way, we get the following set of graphs.

<img src="/images/Utica_Graph3.png" alt="Utica 3" style="width: 600px;"/>
<img src="/images/Utica_Graph4.png" alt="Utica 4" style="width: 600px;"/>
<img src="/images/Utica_Graph5.png" alt="Utica 5" style="width: 600px;"/>
<img src="/images/Utica_Graph6.png" alt="Utica 6" style="width: 600px;"/>
<img src="/images/Utica_Graph7.png" alt="Utica 7" style="width: 600px;"/>
<img src="/images/Utica_Graph8.png" alt="Utica 8" style="width: 600px;"/>


This ends up being a lot of graphs to look at, but I do think it offers some insight. The biggest differences between the weekdays and the weekends seem to happen in the 8-12AM and 4-8PM time slots. 4-8AM and 4-8PM clearly are the best time slots, with the weekday traffic averaging around 7500 passengers. 8AM-12PM and 12PM-4PM show a surprising pattern -  weekdays and weekends have very similar numbers. It may be worth delving into this a little bit further. I suspect that the bins are to blame, since morning rush hour is probably better defined as 6AM-10AM. Regardless, I think these graphs indicate that WYWT should focus on weekday rush hours as they are consistently the highest time slots.

That is a pretty big generalization, but I think as we move through the next visualizations, being able to use that generalization will make our message cleaner and more concise. Again - keep these for the appendix!

Since we've now drawn some insights from a subset of the data, I want to step back and look just at the time periods we indicated.

<img src="/images/All_Graph.png" alt="All_Graph" style="width: 600px;"/>

That didn't help much! Let's try to cut down the number of stations to the top 20. Spoiler: It's actually the top 21.

<img src="/images/Top20_Graph.png" alt="Top20_Graph" style="width: 600px;"/>

I still don't love this - because it's ordered alphabetically, it's hard to see any trends, and it feels a little bit cluttered. We could reduce the number of stations, but I'm not sure that's the problem. Maybe if we try a line graph?

<img src="/images/Top20_LineGraph.png" alt="Top20_LineGraph" style="width: 600px;"/>

This might be even harder to read, and it isn't clear that there is a relationship between the 4-8AM slot and the 4-8PM slot across all the stations. 

If I sort the graph in descending order, maybe a trend will appear?

<img src="/images/Top20_LineGraph_Sorted.png" alt="Top20_LineGraph_Sorted" style="width: 600px;"/>

There does seem to be some correlation between the amount of entries and exits for the two time frames. If we make the assumption that this is the case, we can combine the values for these time ranges and just call it "rush hour" traffic.

<img src="/images/Top20_RushHour_Line.png" alt="Top20_RushHour_Line" style="width: 600px;"/>

That does look simple and clean, but I'm not sure that I love the line graph for displaying this information. I think it would be better for a time series. Let's go back to a bar plot.

<img src="/images/Top20_RushHour_Bar.png" alt="Top20_RushHour_Bar" style="width: 600px;"/>

I think this looks pretty good! It is much more simple than the graph I presented, but it clearly indicates the best recommendations for WYWT. If I were to present this, I'd want to make the following assumptions very clear.
1. Weekday Traffic is very consistent and is much higher than weekend traffic.
2. Traffic during the morning and afternoon rush hours is much higher than during off-peak times.
3. Traffic during the morning and afternoon rush hours are correlated at each station.

### Conclusions

Looking back, I think I wanted to "show off" what our team could do with Seaborn without really thinking about what would be best for the client. Complicated graphs often look interesting but in this case did not do a good job of conveying our message. I will definitely have to think more about this next time!

A few groups overlaid this data on maps, which I really liked. The challenge for them seemed to be identifying which stations were the best. Some tried sizing the points differently (larger = more traffic) or by gradient (darker = more traffic), but it often seemed that the sizes and gradients weren't differentiated enough to easily tell which stations were the busiest. And I'm not sure any group identified the points on the graph - as a non-native of NYC, I had a hard time telling what each station was. 

Hopefully for my next project I can use these lessons to put together an even more effective communication. More to come!

<sub>All of the above data and visualizations can be found on the project's [Github Repository](https://github.com/bgentry91/Benson_Project).</sub>

