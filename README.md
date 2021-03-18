# beeb

![](beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue.

## Usage

_beeb_ centres around the `ChannelSchedule`, which stores a single day's listings, for a single channel.

- National, local, regional channels can be selected by ID or short name
- The schedule with today's date is loaded by default

To load today's schedule for BBC R4:

```py
from beeb.nav import ChannelSchedule
ChannelSchedule.from_channel_name("r4")
```
⇣
```
ChannelSchedule for BBC Radio 4 on 2021-03-16
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
