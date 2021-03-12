from datetime import timedelta

__all__ = ["parse_isoduration_as_timedelta", "total_seconds_in_isoduration"]


def parse_isoduration_as_timedelta(isostring):
    """
    Parse the ISO8601 duration string as a `datetime.timedelta` object.
    For example, "PT3H2M59.989333S" indicates 3 hours, 2 minutes and
    59.989 seconds.
    """
    separators = {
        "PT": None,
        "H": "hours",
        "M": "minutes",
        "S": "seconds",
    }
    duration_vals = {}
    for sep, unit in separators.items():
        partitioned = isostring.partition(sep)
        if partitioned[1] == sep:
            # Matched this unit
            isostring = partitioned[2]
            if sep == "PT":
                continue  # Successful prefix match
            dur_str = partitioned[0]
            dur_val = float(dur_str) if "." in dur_str else int(dur_str)
            duration_vals.update({unit: dur_val})
        else:
            if sep == "PT":
                raise ValueError("Missing PT prefix")
            else:
                # No match for this unit: it's absent
                duration_vals.update({unit: 0})
    td = timedelta(**duration_vals)
    return td


def total_seconds_in_isoduration(isostring):
    td = parse_isoduration_as_timedelta(isostring)
    s = td.total_seconds()
    return s
