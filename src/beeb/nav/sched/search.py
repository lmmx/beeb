import re

__all__ = ["ScheduleSieve", "ScheduleSearchMixIn"]


class ScheduleSieve:
    """
    Internal exposed via ScheduleSearchMixIn, reusable for multiple schedules.
    """

    def __init__(self, query, pid_only, multi, regex, uncased, synopsis, throw):
        self.query = query
        self.pid_only = pid_only
        self.multi = multi
        self.regex = regex
        self.uncased = uncased
        self.synopsis = synopsis
        self.throw = throw

    def search(self, schedule):
        if self.regex:
            if self.uncased:
                rc = re.compile(self.query, re.IGNORECASE)
            else:
                rc = re.compile(self.query)
        # re.Match object is truthy, so use for regex searches not the equality operator
        is_match = rc.match if self.regex else self.query.__eq__
        v = [
            b.pid if self.pid_only else b
            for b in schedule.broadcasts
            if any(
                is_match(t)
                for t in (
                    [b.title, b.subtitle, b.synopsis] if self.synopsis else [b.title]
                )
            )
        ]
        if not v:
            if self.throw:
                q_repr = f"matching '{self.query}'" if self.regex else f"'{self.query}'"
                raise ValueError(f"No broadcast {q_repr} on {schedule.date_repr}")
            elif not self.multi:
                v = None
        elif not self.multi:
            v = v[0]
        return v

    def search_listings(self, listings):
        errors = []  # only populated if throwing errors
        result = [] if self.multi else None
        for schedule in listings.schedules:
            try:
                search_result = self.search(schedule)
                if self.multi:
                    # flat list: don't distinguish individual schedules in listings
                    result.extend(search_result)  # does nothing if empty list returned
                elif search_result:
                    # First non-None: break out of for loop ASAP, return result
                    result = search_result
                    break
            except ValueError as e:
                if self.throw:
                    errors.append(e)
                # Ignore all errors until iterating through all schedules
        if errors and not result:
            if len(errors) > 1:
                litany = []
                for e in errors:
                    litany.extend(e.args)
                if all(e.startswith("No broadcast") for e in litany):
                    error_start = " ".join(litany[0].split(" ")[:-2])
                    error_start_date = litany[0].split(" ")[-1]
                    error_end_date = litany[-1].split(" ")[-1]
                    error_date_range = f"{error_start_date} and {error_end_date}"
                    err_str = f"{error_start} between {error_date_range}"
                else:
                    err_str = f"Multiple errors:\n" + "\n".join(litany)
                raise ValueError(err_str)
            raise errors[0]
        return result


class ScheduleSearchMixIn:
    def __init__(
        self,
        title,
        pid_only=False,
        multi=False,
        regex=False,
        case_insensitive=False,
        synopsis=False,
        throw=True,
    ):
        """
        Return the first broadcasts matching the given `title` if `multi` is
        False (default) or a list of all matches if `multi` is True. Return
        only the `pid` string if `pid_only` is True. If `throw` is True (default),
        raise error if not found else return `None` (if not `multi`) or empty list
        (if `multi` is True). Match the `title` as a regular expression if `regex` is
        True (raw strings are recommended for this). Also match against the subtitle
        and synopsis if `synopsis` is True.
        """
        # Either one ChannelSchedule, or a ChannelListings with `.schedules` attr
        from_sched = hasattr(self, "broadcasts")
        # from_listing = hasattr(self, "schedules")
        # if not (from_listing or from_sched):
        #    raise ValueError("Need either schedules nor broadcasts attribute")
        sieve = ScheduleSieve(
            title, pid_only, multi, regex, case_insensitive, synopsis, throw
        )
        return sieve.search(self) if from_sched else sieve.search_listings(self)

    # Bind the init method of a mixin class: common method interface between
    # mixin inheritors without kwarg passing (unlike kwarg passing, keeps
    # informative docstrings), while also clarifying where the filter logic really is
    get_broadcast_by_title = __init__
