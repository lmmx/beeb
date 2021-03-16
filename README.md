# beeb

![](https://raw.githubusercontent.com/lmmx/beeb/master/beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue

## Usage

- Create a schedule for BBC radio 4 dated today:

```py
from beeb.nav import Schedule
Schedule.from_channel_name("r4")
```
⇣
```
Schedule for BBC Radio 4 on 2021-03-16
```
