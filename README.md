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

From the ChannelListings you can build `SeriesCatalogue` dictionaries,
by inspecting the parent series IDs of each of the broadcasts in the schedules
within the listings.

<details><summary>❧ Click here for SeriesCatalogue examples</summary>

<p>

To obtain a `SeriesCatalogue` with just series PIDs and titles:

```py
beeb.api.get_series_dict("r4", n_days=1)
```
⇣
```py
{'b00cs19l': 'Midnight News',
 'm000tcbd': 'One Two Three Four - The Beatles In Time by Craig Brown',
 'b006qfvv': 'Shipping Forecast',
 'b006s54y': 'Selection of BBC World Service Programmes',
 'b007rhyn': 'News Briefing',
 'b006qmpj': 'Prayer for the Day',
 'b006qj8q': 'Farming Today',
 'b01s6xyk': 'Tweet of the Day',
 'b006qj9z': 'Today',
 'm000t6qm': 'Lessons On A Crisis',
 'b007qlvb': "Woman's Hour",
 'm000tcbk': 'Meet Me at the Museum',
 'm000t4sz': 'The Real Internet Giants',
 'm000t4t5': "Laura Barton's Notes on Music",
 'b04fc120': 'News Summary',
 'm000tcbx': 'White Fang by Jack London',
 'b006qps9': 'You and Yours',
 'b007rn05': 'Weather',
 'b006qptc': 'World at One',
 'm000tcc6': 'Outsiders',
 'b006qpgr': 'The Archers',
 'b04xxp0g': 'Drama',
 'b01mk3f8': 'Short Cuts',
 'b006r4wn': 'Costing the Earth',
 'b006tgy1': 'Law in Action',
 'b006v8jn': 'A Good Read',
 'b006qskw': 'PM',
 'b006qjxt': "Six O'Clock News",
 'm000ssk8': 'Series 4',
 'b006qsq5': 'Front Row',
 'm000lhkv': 'The Whisperer in Darkness',
 'b006qxww': 'In Touch',
 'b019dl1b': 'Inside Health',
 'b006qtl3': 'The World Tonight',
 'p04x5pd7': 'Fortunately... with Fi and Jane',
 'b006qtqd': 'Today in Parliament'}
```

- Note the bug where some series are named things like "Series 4"! TODO: fix

To obtain a `SeriesCatalogue` with genres:

```py
beeb.api.get_genre_series_dict("r4", n_days=1)
```
⇣
```py
{'News': [('b00cs19l', 'Midnight News'),
          ('b007rhyn', 'News Briefing'),
          ('b006qj9z', 'Today'),
          ('b04fc120', 'News Summary'),
          ('b006qptc', 'World at One'),
          ('b006qskw', 'PM'),
          ('b006qjxt', "Six O'Clock News"),
          ('b006qtl3', 'The World Tonight')],
 'Factual': [('m000tcbd',
              'One Two Three Four - The Beatles In Time by Craig Brown'),
             ('b006s54y', 'Selection of BBC World Service Programmes'),
             ('m000t6qm', 'Lessons On A Crisis'),
             ('b007qlvb', "Woman's Hour"),
             ('m000t4sz', 'The Real Internet Giants'),
             ('m000t4t5', "Laura Barton's Notes on Music"),
             ('m000tcc6', 'Outsiders')],
 'Weather': [('b006qfvv', 'Shipping Forecast'), ('b007rn05', 'Weather')],
 'Religion & Ethics': [('b006qmpj', 'Prayer for the Day')],
 'Nature & Environment': [('b006qj8q', 'Farming Today'),
                          ('b006r4wn', 'Costing the Earth')],
 'Science & Nature': [('b01s6xyk', 'Tweet of the Day')],
 'Drama': [('m000tcbk', 'Meet Me at the Museum'),
           ('m000tcbx', 'White Fang by Jack London'),
           ('b04xxp0g', 'Drama')],
 'Consumer': [('b006qps9', 'You and Yours')],
 'Soaps': [('b006qpgr', 'The Archers')],
 'Life Stories': [('b01mk3f8', 'Short Cuts')],
 'Crime & Justice': [('b006tgy1', 'Law in Action')],
 'Arts': [('b006v8jn', 'A Good Read')],
 'Comedy': [('m000ssk8', 'Series 4')],
 'Arts, Culture & the Media': [('b006qsq5', 'Front Row')],
 'Horror & Supernatural': [('m000lhkv', 'The Whisperer in Darkness')],
 'Disability': [('b006qxww', 'In Touch')],
 'Health & Wellbeing': [('b019dl1b', 'Inside Health')],
 'Chat': [('p04x5pd7', 'Fortunately... with Fi and Jane')],
 'Politics': [('b006qtqd', 'Today in Parliament')]}
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
