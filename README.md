# beeb

![](https://raw.githubusercontent.com/lmmx/beeb/master/beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue.

## Usage

- Create a schedule for BBC R4, defaulting to today's date:

```py
from beeb.nav import Schedule
Schedule.from_channel_name("r4")
```
⇣
```
Schedule for BBC Radio 4 on 2021-03-16
```

## Description

_beeb_ centres around the `Schedule`, which is not limited to a single day's listings:

- ≥1 channels (national, local, regional; indicate by ID or name)
- ≥1 dates (only today by default, or past N days, or from particular date to another date)
- ≥1 times of day ('early', 'morning', 'afternoon', 'evening', 'late')
