# beeb

![](https://raw.githubusercontent.com/lmmx/beeb/master/assets/beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue.

## Motivation

_beeb_ is a light alternative to
[`get_iplayer`](https://github.com/get-iplayer/get_iplayer/)
(10,000 lines of Perl)
and
[`youtube-dl`](https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/bbc.py)
(750+ compatible sites).

These libraries aim to be deep and broad, `beeb` just aims to be specific and quick,
handling common use cases (scheduling and download links) clearly, in nicely
object-oriented Python.

## Requirements

<details><summary>❧ Click here to show requirements</summary>

<p>

- BeautifulSoup
- HTTPX
  - A `requests`-like API with async and HTTP/2 support
- aiostream
  - Asynchronous requests to speed up channel listings retrieval
- tqdm
  - Gives the option to show progress when multiprocessing channel listings
- `more_itertools`

</p>

</details>

## Schedule handling

A `ChannelSchedule` stores a single day's listings, for a single channel.

<details><summary>❧ Click here for basic info on ChannelSchedule</summary>

<p>

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


</p>

</details>

<details><summary>❧ Click here for more complex ChannelSchedule examples</summary>

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

`ChannelListings` are a collection of `ChannelSchedule` objects over a
given time period (from up to 30 days ago).

<details><summary>❧ Click here for basic info on ChannelListings</summary>

<p>

The schedules are loaded asynchronously and then their HTML is parsed on all CPU cores (fast!)

No interface is currently implemented for multiple channels (as I don't particularly need it), but
`beeb.nav.ChannelPicker` gives all available channels if you wanted to iterate over them.

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


</p>

</details>


<details><summary>❧ Click here for examples of ChannelListings queries</summary>

<p>


- There were 26 'Today' episodes aired on BBC R4 in the last 30 days (not aired on Sundays):

```py
>>> for i, b in enumerate(l.get_broadcast_by_title("Today", multi=True)):
...     print(f"{i:2}) {b}")
... 
 0) 06:00 on Wed 17/02/2021 — Today
 1) 06:00 on Thu 18/02/2021 — Today
 2) 06:00 on Fri 19/02/2021 — Today
 3) 07:00 on Sat 20/02/2021 — Today
 4) 06:00 on Mon 22/02/2021 — Today
 5) 06:00 on Tue 23/02/2021 — Today
 6) 06:00 on Wed 24/02/2021 — Today
 7) 06:00 on Thu 25/02/2021 — Today
 8) 06:00 on Fri 26/02/2021 — Today
 9) 07:00 on Sat 27/02/2021 — Today
10) 06:00 on Mon 01/03/2021 — Today
11) 06:00 on Tue 02/03/2021 — Today
12) 06:00 on Wed 03/03/2021 — Today
13) 06:00 on Thu 04/03/2021 — Today
14) 06:00 on Fri 05/03/2021 — Today
15) 07:00 on Sat 06/03/2021 — Today
16) 06:00 on Mon 08/03/2021 — Today
17) 06:00 on Tue 09/03/2021 — Today
18) 06:00 on Wed 10/03/2021 — Today
19) 06:00 on Thu 11/03/2021 — Today
20) 06:00 on Fri 12/03/2021 — Today
21) 07:00 on Sat 13/03/2021 — Today
22) 06:00 on Mon 15/03/2021 — Today
23) 06:00 on Tue 16/03/2021 — Today
24) 06:00 on Wed 17/03/2021 — Today
25) 06:00 on Thu 18/03/2021 — Today
```

- Here's a query of all programmes which mention vaccin(es,ations,inologists) in their
  title/subtitle/synopsis:

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

## Stream handling

<details><summary>❧ Click here for the basics of stream handling</summary>

<p>

Episodes are downloaded from BBC Sounds as M4S (MPEG-DASH streams). There is a header `.dash` file
and then multiple `.dash` files, and if you have all of these you can build a MP4 audio file.

> As far as I know the access to these is geo-fenced, i.e. you must
> be in the UK to download but this may vary between programmes/stations.

The most directly useful functions (which I've needed when interacting with BBC Sounds API) are
those to obtain the M4S links: you only need the final one to construct the full set of URLs
to obtain a complete MP4.

The following functions handle this in `beeb.api`:

- `get_episode_dict`
  - a trivial wrapper to access the `episodes_dict` attribute of `EpisodeListingsHtml`
- `final_m4s_link_from_series_pid`
  - a wrapper to access the `last_m4s_link` attribute of the `MpdXml` class constructed with the `from_episode_pid` class method
- `final_m4s_link_from_episode_pid`
  - a wrapper to access the `last_m4s_link` attribute of the `MpdXml` class constructed with the `from_episode_pid` class method
    after obtaining the episode PID from the episode dict
- `get_series_pid_by_name`
  - a wrapper to access the `filtered` attribute of a `EpisodeMetadataPidJson` object
    constructed with the `get_series_pid` class method.
  - technically it's "by series title and station name" (the arguments are in this order)

You may very well prefer to construct the objects and handle the attributes involved yourself,
these are given as 'recipes' to make it clear how to use beeb's functionality.

</p>

</details>
