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

From the ChannelListings you can build `ProgrammeCatalogue` dictionaries,
by inspecting the parent programme IDs of each of the broadcasts in the schedules
within the listings.

<details><summary>❧ Click here for ProgrammeCatalogue examples</summary>

<p>

To obtain a `ProgrammeCatalogue` with just programme PIDs and titles:

```py
beeb.api.get_programme_dict("r4", n_days=1)
```
⇣
```py
{'b00cs19l': 'Midnight News',
 'b006qfvv': 'Shipping Forecast',
 'b006s54y': 'Selection of BBC World Service Programmes',
 'b007rhyn': 'News Briefing',
 'b006qmpj': 'Prayer for the Day',
 'b006qj8q': 'Farming Today',
 'b01s6xyk': 'Tweet of the Day',
 'b006qj9z': 'Today',
 'b09zgd6y': 'Chinese Characters',
 'b007qlvb': "Woman's Hour",
 'm0002rjm': "Alexei Sayle's The Absence of Normal",
 'b04fc120': 'News Summary',
 'b006qps9': 'You and Yours',
 'b007rn05': 'Weather',
 'b006qptc': 'World at One',
 'b006qpgr': 'The Archers',
 'b04xxp0g': 'Drama',
 'b006qjnv': 'Money Box',
 'b019dl1b': 'Inside Health',
 'm000s2kt': 'Sideways',
 'b00dv9hq': 'The Media Show',
 'b006qskw': 'PM',
 'b006qjxt': "Six O'Clock News",
 'b006qsq5': 'Front Row',
 'b006qk11': 'Moral Maze',
 'b006xp1x': 'Lent Talks',
 'b006r4wn': 'Costing the Earth',
 'b006qtl3': 'The World Tonight',
 'm000czyb': 'The Skewer',
 'b006qtqd': 'Today in Parliament'}
```

To obtain a `ProgrammeCatalogue` with genres (be warned — for the last 30 days this takes 60 seconds):

```py
beeb.api.get_genre_programme_dict("r4", n_days=30)
```
⇣
```py
{'Arts': [('b006v8jn', 'A Good Read')],
 'Arts, Culture & the Media': [('b01875r3', 'One to One'),
                               ('b006qsq5', 'Front Row'),
                               ('b00dv9hq', 'The Media Show'),
                               ('b006qp6p', 'Open Book'),
                               ('b006r5jt', 'The Film Programme'),
                               ('b006slnx', 'Feedback'),
                               ('m00055q2', 'Rewinder'),
                               ('b006qjym', 'Loose Ends'),
                               ('b06p0p0g', 'The Why Factor'),
                               ('b006qpdd', 'Pick of the Week'),
                               ('b006r9xr', 'Start the Week'),
                               ('b006s5sf', 'Bookclub'),
                               ('b09w07c4', 'Art of Now')],
 'Biographical': [('b0721qqk', 'Riot Girls')],
 'Chat': [('p04x5pd7', 'Fortunately... with Fi and Jane'),
          ('m000s9s1', 'Between Ourselves with Marian Keyes'),
          ('b00snr0w', 'The Infinite Monkey Cage')],
 'Classic & Period': [('m000j0t9', 'Electric Decade')],
 'Comedy': [('b00x8dq1', 'My Teenage Diary'),
            ('b08mj1wj', 'Reluctant Persuaders'),
            ('m0002rjm', "Alexei Sayle's The Absence of Normal")],
 'Consumer': [('b006qps9', 'You and Yours')],
 'Crime & Justice': [('b006tgy1', 'Law in Action'), ('m0000nfh', 'Intrigue')],
 'Disability': [('b006qxww', 'In Touch')],
 'Drama': [('b04xxp0g', 'Drama'),
           ('b08lw2hh', 'Short Works'),
           ('m000s855', "Hardy's Women")],
 'Entertainment': [('b060cdyj', 'Bunk Bed')],
 'Factual': [('b006s54y', 'Selection of BBC World Service Programmes'),
             ('b007qlvb', "Woman's Hour"),
             ('m0001kbd', 'Born in Bradford'),
             ('b006th08', 'File on 4'),
             ('m000s2kt', 'Sideways'),
             ('b006qk11', 'Moral Maze'),
             ('b006qjlq', 'From Our Own Correspondent'),
             ('b006qnc7', 'Radio 4 Appeal'),
             ('b07cblx9', 'The Briefing Room'),
             ('b006qng8', 'A Point of View'),
             ('b006qnj3', 'Broadcasting House'),
             ('m0003r3t', 'My Name Is...'),
             ('m00019hp', 'Archive on 4'),
             ('b007qxpr', 'Round Britain Quiz'),
             ('b03w7bwg', 'Out of the Ordinary'),
             ('b09zgd6y', 'Chinese Characters')],
 'Families & Relationships': [('b006qgj4', 'Saturday Live')],
 'Food & Drink': [('b006qnx3', 'The Food Programme')],
 'Gardens': [('b006qp2f', "Gardeners' Question Time")],
 'Health & Wellbeing': [('b019dl1b', 'Inside Health')],
 'Historical': [('m000sqkk', 'Gudrun')],
 'History': [('b006qykl', 'In Our Time'),
             ('b00nrtd2', 'A History of the World in 100 Objects')],
 'Life Stories': [('b01mk3f8', 'Short Cuts'),
                  ('b006qnmr', 'Desert Island Discs'),
                  ('b006qpmv', 'Last Word'),
                  ('b006qjz5', 'Profile'),
                  ('b03cdpww', 'Meeting Myself Coming Back'),
                  ('b01cqx3b', 'The Listening Project')],
 'Money': [('b006qjnv', 'Money Box'), ('b006sz6t', 'The Bottom Line')],
 'Music': [('b00704s1', 'Counterpoint')],
 'Nature & Environment': [('b006qj8q', 'Farming Today'),
                          ('b006xrr2', 'Ramblings'),
                          ('b05w99gb', 'Natural Histories'),
                          ('b006r4wn', 'Costing the Earth')],
 'News': [('b00cs19l', 'Midnight News'),
          ('b007rhyn', 'News Briefing'),
          ('b006qj9z', 'Today'),
          ('b04fc120', 'News Summary'),
          ('b006qptc', 'World at One'),
          ('b006qskw', 'PM'),
          ('b006qjxt', "Six O'Clock News"),
          ('b006qtl3', 'The World Tonight'),
          ('b007rhyy', 'News and Papers'),
          ('b00g3j4x', 'News'),
          ('b006qnz4', 'The World This Weekend')],
 'Panel Shows': [('b006s5dp', 'Just a Minute')],
 'Politics': [('b006qtqd', 'Today in Parliament'),
              ('b006qgvj', 'Any Questions?'),
              ('b006qjfq', 'The Week in Westminster'),
              ('b006qmmy', 'Any Answers?'),
              ('m0001xq1', 'The Battles That Won Our Freedoms'),
              ('b006r4vz', 'Analysis'),
              ('b006s624', 'Westminster Hour')],
 'Religion & Ethics': [('b006qmpj', 'Prayer for the Day'),
                       ('b006xp1x', 'Lent Talks'),
                       ('b006sgsh', 'Bells on Sunday'),
                       ('b006qn7f', 'Something Understood'),
                       ('b006qnbd', 'Sunday'),
                       ('b006qnds', 'Sunday Worship')],
 'Satire': [('b09rwvwt', 'Henry Normal: A Normal...'),
            ('m000czyb', 'The Skewer'),
            ('b006qgt7', 'The Now Show')],
 'Science & Nature': [('b01s6xyk', 'Tweet of the Day'),
                      ('b07dx75g', 'The Curious Cases of Rutherford & Fry'),
                      ('b036f7w2', 'BBC Inside Science'),
                      ('b06vy2jd', 'Science Stories')],
 'Science & Technology': [('b01n7094', 'The Digital Human')],
 'Sitcoms': [('b0b2nh1n', 'Ability')],
 'Sketch': [('b00kvs8r', 'Newsjack')],
 'Soaps': [('b006qpgr', 'The Archers'), ('b006qnkc', 'The Archers Omnibus')],
 'Standup': [('b0b22qhr', 'Stand-Up Specials'),
             ('b011tzjy', 'Meet David Sedaris')],
 'Weather': [('b006qfvv', 'Shipping Forecast'), ('b007rn05', 'Weather')]}
```

This is equivalent to constructing the class directly and accessing its `.keyed_by_genre` property.

```py
beeb.nav.sched.ProgrammeCatalogue("r4", n_days=30, with_genre=True)
```

- This takes about 7 or 8 seconds (fast given the number of requests it's making!)
- Note that these requests occasionally fail (async sessions are prone to rare connection errors),
  and are silently retried up to 3 times (one seems to be enough in my experience).

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
- `final_m4s_link_from_programme_pid`
  - a wrapper to access the `last_m4s_link` attribute of the `MpdXml` class constructed with the `from_episode_pid` class method
- `final_m4s_link_from_episode_pid`
  - a wrapper to access the `last_m4s_link` attribute of the `MpdXml` class constructed with the `from_episode_pid` class method
    after obtaining the episode PID from the episode dict
- `get_programme_pid_by_name`
  - a wrapper to access the `filtered` attribute of a `EpisodeMetadataPidJson` object
    constructed with the `get_programme_pid` class method.
  - technically it's "by programme title and station name" (the arguments are in this order)

You may very well prefer to construct the objects and handle the attributes involved yourself,
these are given as 'recipes' to make it clear how to use beeb's functionality.

</p>

</details>
