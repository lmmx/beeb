# beeb

![](https://raw.githubusercontent.com/lmmx/beeb/master/assets/beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue.

## Usage

A `ChannelSchedule` stores a single day's listings, for a single channel.

- National, local, regional channels can be selected by ID or short name
- The schedule with today's date is loaded by default

To load today's schedule for BBC R4:

```py
from beeb.nav import ChannelSchedule
ChannelSchedule.from_channel_name("r4")
```
⇣
```
ChannelSchedule for BBC Radio 4 on 2021-03-17
```

These ChannelSchedule objects can be used to find programmes:

```py
>>> from beeb.nav import ChannelSchedule
>>> s = ChannelSchedule.from_channel_name("r4")
>>> s.get_broadcast_by_title("Today", pid_only=True)
'm000t476'
>>> s.get_broadcast_by_title("Midnight News")
00:00 on 17/03/2021 — Midnight News
>>> for b in s.get_broadcast_by_title("Shipping Forecast", multi=True): b
00:48 on 17/03/2021 — Shipping Forecast
05:20 on 17/03/2021 — Shipping Forecast
12:03 on 17/03/2021 — Shipping Forecast
```


<details><summary>Click here for more complex examples</summary>

<p>

```py
>>> for b in s.get_broadcast_by_title(r".*\bNews\b", regex=True, multi=True): b
... 
00:00 on 17/03/2021 — Midnight News
05:30 on 17/03/2021 — News Briefing
12:00 on 17/03/2021 — News Summary
18:00 on 17/03/2021 — Six O'Clock News
>>> for b in s.get_broadcast_by_title(r".*\bnews\b", multi=True,
... case_insensitive=True, regex=True, synopsis=True): print(b)
... 
00:00 on 17/03/2021 — Midnight News
05:30 on 17/03/2021 — News Briefing
06:00 on 17/03/2021 — Today
12:00 on 17/03/2021 — News Summary
13:00 on 17/03/2021 — World at One
17:00 on 17/03/2021 — PM
18:00 on 17/03/2021 — Six O'Clock News
20:00 on 17/03/2021 — Moral Maze
22:00 on 17/03/2021 — The World Tonight
23:30 on 17/03/2021 — Today in Parliament
>>> for b in s.get_broadcast_by_title(
... r".*\b(pandemic|virus|coronavirus|Covid|vaccines?|vaccinations?|health|healthcare|NHS)\b",
... multi=True, case_insensitive=True, regex=True, synopsis=True): print(b)
... 
10:00 on 17/03/2021 — Woman's Hour
15:00 on 17/03/2021 — Money Box
15:30 on 17/03/2021 — Inside Health
```

</p>

</details>

As well as schedules for a single day, _beeb_ has `ChannelListings`, a collection of `ChannelSchedule` objects over a
given time period (from up to 30 days ago).

```py
>>> from beeb.nav import ChannelListings
>>> ChannelListings.from_channel_name("r4")
ChannelListings for BBC Radio 4 from 2021-02-17 to 2021-03-18 (30 days)
```

The schedules are stored as a chronological list in the `ChannelListings.schedules` attribute

```py
>>> from beeb.nav import ChannelListings
>>> l = ChannelListings.from_channel_name("r4")
ChannelListings for BBC Radio 4 from 2021-02-17 to 2021-03-18 (30 days)
>>> l.schedules[0]
ChannelSchedule for BBC Radio 4 on 2021-02-17
```

ChannelListings follows the same interface as ChannelSchedule (they share a commonly bound method,
to avoid too much parameter passing).


<details><summary>Click here for examples of listings queries</summary>

<p>


```py
>>> for i, b in enumerate(l.get_broadcast_by_title("Today", multi=True)):
...     print(f"{i:2}: {b}")
... 
 0: 06:00 on Wed 17/02/2021 — Today
 1: 06:00 on Thu 18/02/2021 — Today
 2: 06:00 on Fri 19/02/2021 — Today
 3: 07:00 on Sat 20/02/2021 — Today
 4: 06:00 on Mon 22/02/2021 — Today
 5: 06:00 on Tue 23/02/2021 — Today
 6: 06:00 on Wed 24/02/2021 — Today
 7: 06:00 on Thu 25/02/2021 — Today
 8: 06:00 on Fri 26/02/2021 — Today
 9: 07:00 on Sat 27/02/2021 — Today
10: 06:00 on Mon 01/03/2021 — Today
11: 06:00 on Tue 02/03/2021 — Today
12: 06:00 on Wed 03/03/2021 — Today
13: 06:00 on Thu 04/03/2021 — Today
14: 06:00 on Fri 05/03/2021 — Today
15: 07:00 on Sat 06/03/2021 — Today
16: 06:00 on Mon 08/03/2021 — Today
17: 06:00 on Tue 09/03/2021 — Today
18: 06:00 on Wed 10/03/2021 — Today
19: 06:00 on Thu 11/03/2021 — Today
20: 06:00 on Fri 12/03/2021 — Today
21: 07:00 on Sat 13/03/2021 — Today
22: 06:00 on Mon 15/03/2021 — Today
23: 06:00 on Tue 16/03/2021 — Today
24: 06:00 on Wed 17/03/2021 — Today
25: 06:00 on Thu 18/03/2021 — Today
```

- There were 26 'Today' episodes aired on BBC R4 in the last 30 days (not aired on Sundays)

```py
>>> for b in l.get_broadcast_by_title(r".*\b(vaccin.+?)\b", multi=True, case_insensitive=True,
... regex=True, synopsis=True): print(b)
... 
15:30 on Wed 17/02/2021 — Inside Health
18:00 on Wed 17/02/2021 — Six O'Clock News
11:30 on Mon 22/02/2021 — How to Vaccinate the World
14:00 on Sat 27/02/2021 — Any Answers?
07:10 on Sun 28/02/2021 — Sunday
11:30 on Mon 01/03/2021 — How to Vaccinate the World
20:00 on Wed 03/03/2021 — Moral Maze
22:15 on Sat 06/03/2021 — Moral Maze
11:30 on Mon 08/03/2021 — How to Vaccinate the World
11:30 on Mon 15/03/2021 — How to Vaccinate the World
18:00 on Mon 15/03/2021 — Six O'Clock News
22:00 on Mon 15/03/2021 — The World Tonight
21:00 on Tue 16/03/2021 — Inside Health
15:30 on Wed 17/03/2021 — Inside Health
18:00 on Wed 17/03/2021 — Six O'Clock News
```

</p>

</details>
