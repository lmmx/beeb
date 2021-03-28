import re

__all__ = ["Sieve"]


class Sieve:
    def __init__(self, query, pid_only, multi, regex, uncased, all_fields, throw):
        self.query = query
        self.pid_only = pid_only
        self.multi = multi
        self.regex = regex
        self.uncased = uncased
        self.all_fields = all_fields
        self.throw = throw

    def is_match(self, target):
        # re.Match object is truthy, so use for regex searches not the equality operator
        match_func = self.rc.match if self.regex else self.query.__eq__
        return match_func(target)

    @property
    def rc(self):
        "Compiled regex: only has a value when self.regex is True"
        if self.regex:
            if self.uncased:
                compiled = re.compile(self.query, re.IGNORECASE)
            else:
                compiled = re.compile(self.query)
            return compiled

    @property
    def _query_repr_(self):
        return f"matching '{self.query}'" if self.regex else f"'{self.query}'"
