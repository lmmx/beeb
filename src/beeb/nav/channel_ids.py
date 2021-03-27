from enum import Enum
from collections import namedtuple

__all__ = ["ChannelPicker", "NationalChannel", "RegionalChannel", "LocalChannel"]

channel = namedtuple("Channel", "channel_id title url")

# N.B. some channels have variations (e.g. FM/LW and regional variations), FM variant is
# always last so that `ChannelPicker.by_title` acquires that from the shared title

class NationalChannel(Enum):
    r1x = channel("p00fzl64", "BBC Radio 1Xtra", "1xtra/programmes/schedules")
    r5l = channel("p00fzl7g", "BBC Radio 5 live", "5live/programmes/schedules")
    r5lse = channel("p00fzl7h", "BBC Radio 5 live sports extra", "5livesportsextra/programmes/schedules")
    r6m = channel("p00fzl65", "BBC Radio 6 Music", "6music/programmes/schedules")
    an = channel("p00fzl68", "BBC Asian Network", "asiannetwork/programmes/schedules")
    r1 = channel("p00fzl86", "BBC Radio 1", "radio1/programmes/schedules")
    r2 = channel("p00fzl8v", "BBC Radio 2", "radio2/programmes/schedules")
    r3 = channel("p00fzl8t", "BBC Radio 3", "radio3/programmes/schedules")
    r4lw = channel("p00fzl7k", "BBC Radio 4", "radio4/programmes/schedules/lw")
    r4 = channel("p00fzl7j", "BBC Radio 4", "radio4/programmes/schedules/fm")
    r4x = channel("p00fzl7l", "BBC Radio 4 Extra", "radio4extra/programmes/schedules")
    ws = channel("p02zbmb3", "BBC World Service", "worldserviceradio/programmes/schedules/uk")
    cr = channel("p02jf21y", "CBeebies Radio", "cbeebies_radio/programmes/schedules")


class RegionalChannel(Enum):
    rc = channel("p00fzl7b", "BBC Radio Cymru", "radiocymru/programmes/schedules")
    rf = channel("p00fzl7m", "BBC Radio Foyle", "radiofoyle/programmes/schedules")
    rng = channel("p00fzl81", "BBC Radio Nan Gaidheal", "radionangaidheal/programmes/schedules")
    rss = channel("p00fzl8j", "BBC Radio Scotland", "radioscotland/programmes/schedules/shetland")
    rso = channel("p00fzl8b", "BBC Radio Scotland", "radioscotland/programmes/schedules/orkney")
    rsmw = channel("p00fzl8g", "BBC Radio Scotland", "radioscotland/programmes/schedules/mw")
    rs = channel("p00fzl8d", "BBC Radio Scotland", "radioscotland/programmes/schedules/fm")
    ru = channel("p00fzl8w", "BBC Radio Ulster", "radioulster/programmes/schedules")
    rwmw = channel("p00fzl8x", "BBC Radio Wales", "radiowales/programmes/schedules/mw")
    rw = channel("p00fzl8y", "BBC Radio Wales", "radiowales/programmes/schedules/fm")


class LocalChannel(Enum):
    cov = channel("p00fzl78", "BBC Coventry & Warwickshire", "bbccoventryandwarwickshire/programmes/schedules")
    ess = channel("p00fzl7f", "BBC Essex", "bbcessex/programmes/schedules")
    her = channel("p00fzl7q", "BBC Hereford & Worcester", "bbcherefordandworcester/programmes/schedules")
    new = channel("p00fzl82", "BBC Newcastle", "bbcnewcastle/programmes/schedules")
    som = channel("p00fzl8m", "BBC Somerset", "bbcsomerset/programmes/schedules")
    sur = channel("p00fzl8q", "BBC Surrey", "bbcsurrey/programmes/schedules")
    sus = channel("p00fzl8r", "BBC Sussex", "bbcsussex/programmes/schedules")
    tee = channel("p00fzl93", "BBC Tees", "bbctees/programmes/schedules")
    wil = channel("p00fzl8z", "BBC Wiltshire", "bbcwiltshire/programmes/schedules")
    ber = channel("p00fzl74", "BBC Radio Berkshire", "radioberkshire/programmes/schedules")
    bri = channel("p00fzl75", "BBC Radio Bristol", "radiobristol/programmes/schedules")
    cam = channel("p00fzl76", "BBC Radio Cambridgeshire", "radiocambridgeshire/programmes/schedules")
    cor = channel("p00fzl77", "BBC Radio Cornwall", "radiocornwall/programmes/schedules")
    cum = channel("p00fzl79", "BBC Radio Cumbria", "radiocumbria/programmes/schedules")
    der = channel("p00fzl7c", "BBC Radio Derby", "radioderby/programmes/schedules")
    dev = channel("p00fzl7d", "BBC Radio Devon", "radiodevon/programmes/schedules")
    glo = channel("p00fzl7n", "BBC Radio Gloucestershire", "radiogloucestershire/programmes/schedules")
    gue = channel("p00fzl7p", "BBC Radio Guernsey", "radioguernsey/programmes/schedules")
    hum = channel("p00fzl7r", "BBC Radio Humberside", "radiohumberside/programmes/schedules")
    jer = channel("p00fzl7s", "BBC Radio Jersey", "radiojersey/programmes/schedules")
    ken = channel("p00fzl7t", "BBC Radio Kent", "radiokent/programmes/schedules")
    lan = channel("p00fzl7v", "BBC Radio Lancashire", "radiolancashire/programmes/schedules")
    lee = channel("p00fzl7w", "BBC Radio Leeds", "radioleeds/programmes/schedules")
    lei = channel("p00fzl7x", "BBC Radio Leicester", "radioleicester/programmes/schedules")
    lin = channel("p00fzl7y", "BBC Radio Lincolnshire", "radiolincolnshire/programmes/schedules")
    lon = channel("p00fzl6f", "BBC Radio London", "radiolondon/programmes/schedules")
    man = channel("p00fzl7z", "BBC Radio Manchester", "radiomanchester/programmes/schedules")
    mer = channel("p00fzl80", "BBC Radio Merseyside", "radiomerseyside/programmes/schedules")
    nfk = channel("p00fzl83", "BBC Radio Norfolk", "radionorfolk/programmes/schedules")
    nth = channel("p00fzl84", "BBC Radio Northampton", "radionorthampton/programmes/schedules")
    ntt = channel("p00fzl85", "BBC Radio Nottingham", "radionottingham/programmes/schedules")
    oxf = channel("p00fzl8c", "BBC Radio Oxford", "radiooxford/programmes/schedules")
    she = channel("p00fzl8h", "BBC Radio Sheffield", "radiosheffield/programmes/schedules")
    shr = channel("p00fzl8k", "BBC Radio Shropshire", "radioshropshire/programmes/schedules")
    sol = channel("p00fzl8l", "BBC Radio Solent", "radiosolent/programmes/schedules")
    sto = channel("p00fzl8n", "BBC Radio Stoke", "radiostoke/programmes/schedules")
    suf = channel("p00fzl8p", "BBC Radio Suffolk", "radiosuffolk/programmes/schedules")
    yor = channel("p00fzl90", "BBC Radio York", "radioyork/programmes/schedules")
    tcr = channel("p00fzl96", "BBC Three Counties Radio", "threecountiesradio/programmes/schedules")
    wm = channel("p00fzl9f", "BBC WM 95.6", "wm/programmes/schedules")

class SearchableEnum:
    @classmethod
    def by_name(cls, name, must_exist=False):
        matches = [
            y.value[name].value for y in cls.__members__.values()
            if name in y.value.__members__
        ]
        if len(matches) > 1:
            raise ValueError(f"Enums are not unique: {matches=}")
        if must_exist and not matches:
            raise ValueError(f"No channel named {name}")
        return matches[0] if matches else None

    @classmethod
    def by_id(cls, channel_id, must_exist=True, return_value=True):
        matches = [
            {
                v.value.channel_id: (v.value if return_value else v.name)
                for v in y.value.__members__.values()
            }.get(channel_id)
            for y in ChannelPicker.__members__.values()
            if channel_id in [
                x.value.channel_id
                for x in y.value
            ]
        ]
        if len(matches) > 1:
            raise ValueError(f"Enum IDs are not unique: {matches=}")
        if must_exist and not matches:
            raise ValueError(f"No channel named {name}")
        return matches[0] if matches else None

    @classmethod
    def by_title(cls, title, must_exist=True, return_value=True):
        matches = [
            {
                v.value.title: (v.value if return_value else v.name)
                for v in y.value.__members__.values()
            }.get(title)
            for y in ChannelPicker.__members__.values()
            if title in [
                x.value.title
                for x in y.value
            ]
        ]
        if len(matches) > 1:
            raise ValueError(f"Enum IDs are not unique: {matches=}")
        if must_exist and not matches:
            raise ValueError(f"No channel named {name}")
        return matches[0] if matches else None

    @classmethod
    def keys_by_category(cls, category, remove_variants=False, remove_cbeebies=True):
        """
        Either pass name or enum itself, e.g `"local"` or `ChannelPicker.local`,
        or a list of one or more of those, e.g. `["national", "local"]`. If
        `remove_variants` is True, only keep the canonical form (the last)
        where there are multiple entries with the same title.

        Exclude the children's channel "CBeebies" (does not parse to catalogue for
        some reason and is not the same type as the other national channels anyway).
        """
        keys = []
        if isinstance(category, list):
            for c in category:
                keys.extend(cls.keys_by_category(c, remove_variants=remove_variants))
            remove_variants = False # ensure not to re-remove at the end
        else:
            if isinstance(category, str): # name e.g. "local"
                category = cls[category]
            keys.extend(sorted([*category.value.__members__]))
        if remove_variants:
            keys = cls.remove_variants(keys, sort=True)
        if remove_cbeebies:
            if "cr" in keys:
                keys.remove("cr")
        return keys

    @classmethod
    def remove_variants(cls, station_names, sort=False):
        station_names = {
            cls.by_title(f.title, return_value=False)
            for f in map(cls.by_name, station_names)
        }
        return sorted(station_names) if sort else station_names

class ChannelPicker(SearchableEnum, Enum):
    local = LocalChannel
    regional = RegionalChannel
    national = NationalChannel
