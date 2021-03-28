import re
from .sieve import Sieve

__all__ = ["CatalogueSieve", "CatalogueSearchMixIn"]


class CatalogueSieve(Sieve):
    """
    Internal exposed via CatalogueSearchMixIn, reusable for multiple catalogues.
    """

    def search(self, catalogue):
        v = [
            pid if self.pid_only else (pid, val)
            for pid, val in catalogue.items()
            if self.is_match(
                val[0] if catalogue.genred else val
            )
        ]
        if not v:
            if self.throw:
                msg = f"No programme {self._query_repr_} in catalogue"
                raise ValueError(msg)
            elif not self.multi:
                v = None
        elif not self.multi:
            v = v[0]
        return v

    def search_guide(self, guide):
        errors = []  # only populated if throwing errors
        result = [] if self.multi else None
        for station_name, catalogue in guide.items():
            try:
                search_result = self.search(catalogue)
                if self.multi:
                    # flat list: don't distinguish individual catalogues in guide
                    result.extend(search_result)  # does nothing if empty list returned
                elif search_result:
                    # First non-None: break out of for loop ASAP, return result
                    result = search_result
                    break
            except ValueError as e:
                if self.throw:
                    errors.append(e)
                # Ignore all errors until iterating through all catalogues
        if errors and not result:
            self._handle_errors(errors)
        return result

    def _handle_errors(self, errors):
        if len(errors) > 1:
            litany = []
            for e in errors:
                litany.extend(e.args)
            if all(e.startswith("No programme") for e in litany):
                error_start = " ".join(litany[0].split(" ")[:-2])
                error_count = f"({len(errors)} errors)"
                err_str = f"{error_start} {error_count}"
            else:
                err_str = f"Multiple errors:\n" + "\n".join(litany)
            raise ValueError(err_str)
        raise errors[0]


class CatalogueSearchMixIn:
    def get_programme_by_title(
        self,
        title,
        pid_only=False,
        multi=False,
        regex=False,
        case_insensitive=False,
        throw=True,
    ):
        """
        Return the first programmes matching the given `title` if `multi` is
        False (default) or a list of all matches if `multi` is True. Return
        only the `pid` string if `pid_only` is True. If `throw` is True (default),
        raise error if not found else return `None` (if not `multi`) or empty list
        (if `multi` is True). Match the `title` as a regular expression if `regex` is
        True (raw strings are recommended for this).
        """
        # Either one ProgrammeCatalogue, or a ProgrammeGuide
        from_cat = hasattr(self, "station_name")
        all_fields = False # not used for catalogues
        sieve = CatalogueSieve(
            title, pid_only, multi, regex, case_insensitive, all_fields, throw
        )
        return sieve.search(self) if from_cat else sieve.search_guide(self)
