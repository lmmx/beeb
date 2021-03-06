import re
from .sieve import Sieve

__all__ = ["ScheduleSieve", "ScheduleSearchMixIn"]


class ScheduleSieve(Sieve):
    """
    Internal exposed via ScheduleSearchMixIn, reusable for multiple schedules.
    """

    def search(self, schedule):
        v = [
            b.pid if self.pid_only else b
            for b in schedule.broadcasts
            if any(
                self.is_match(t)
                for t in (
                    [b.title, b.subtitle, b.synopsis] if self.all_fields else [b.title]
                )
            )
        ]
        if not v:
            if self.throw:
                msg = f"No broadcast {self._query_repr_} on {schedule.date_repr}"
                raise ValueError(msg)
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
            self._handle_errors(errors)
        return result

    def _handle_errors(self, errors):
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


class ScheduleSearchMixIn:
    def get_broadcast_by_title(
        self,
        title,
        pid_only=False,
        multi=False,
        regex=False,
        case_insensitive=False,
        all_fields=False,
        throw=True,
    ):
        """
        Return the first broadcasts matching the given `title` if `multi` is
        False (default) or a list of all matches if `multi` is True. Return
        only the `pid` string if `pid_only` is True. If `throw` is True (default),
        raise error if not found else return `None` (if not `multi`) or empty list
        (if `multi` is True). Match the `title` as a regular expression if `regex` is
        True (raw strings are recommended for this). Also match against the subtitle
        and synopsis if `all_fields` is True.
        """
        # Either one ChannelSchedule, or a ChannelListings with `.schedules` attr
        from_sched = hasattr(self, "broadcasts")
        sieve = ScheduleSieve(
            title, pid_only, multi, regex, case_insensitive, all_fields, throw
        )
        return sieve.search(self) if from_sched else sieve.search_listings(self)
