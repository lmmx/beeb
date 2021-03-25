from xml.etree import ElementTree as ET
from json import loads
from functools import reduce
from ..share.http_utils import GET
from bs4 import BeautifulSoup as BS

__all__ = ["XmlHandler", "JsonHandler", "HtmlHandler"]


class PullMixIn:
    def pull(self):
        resp = GET(self.url, raise_for_status=True)
        data = self.reader_func(resp.content.decode())
        self.handle(data)


class SerialisedHandler(PullMixIn, dict):
    """
    Serialisation helper providing a common interface for XML and JSON.
    Subclasses must provide `reader_func` to parse the decoded contents
    of GET request to `self.url`,
    """

    clear_on_filter = False  # override in subclass to add self-unloading behaviour

    def filter(self, filter_key_path=None, force_preserve=False):
        if self.filter_key_path and filter_key_path is None:
            filter_key_path = self.filter_key_path
        if filter_key_path and type(filter_key_path) is tuple:
            # Input is tuple of multiple key paths so output a tuple of multiple values
            filtered = tuple(
                reduce(dict.__getitem__, kp, self)
                for kp in filter_key_path
            )
        else:
            filtered = reduce(dict.__getitem__, filter_key_path, self)
        # Only clear the dict after successfully filtering. This enables
        # higher level error handling to check the data without re-pulling
        if self.clear_on_filter and not force_preserve:
            self.clear()  # The JSON dict will be empty if filter succeeded
        return filtered


class XmlHandler(SerialisedHandler):
    "XML handler base class."

    def __init__(self, url, defer_pull=False, filter_key_path=None):
        self.url = url
        self.filter_key_path = filter_key_path
        if not defer_pull:
            self.pull()

    def handle(self, data):
        self.root = data  # root ET.Element
        self.update(data.attrib)  # load ET.Element.attrib dict

    @staticmethod
    def reader_func(data):
        return ET.fromstring(data)


class JsonHandler(SerialisedHandler):
    """
    JSON handler base class. Subclasses must set `pid_property_name`
    (to clearly distinguish the different PIDs) and a property `url`.
    """

    clear_on_filter = True  # override in subclass to remove self-unloading behaviour

    def __init__(self, pid, defer_pull=False, filter_key_path=None):
        setattr(self, self.pid_property_name, pid)
        self.filter_key_path = filter_key_path
        if not defer_pull:
            self.pull()

    def handle(self, data):
        self.update(data)
        if self.filter_key_path:
            self.filtered = self.filter()

    @staticmethod
    def reader_func(data):
        return loads(data)

    @classmethod
    def from_json(cls, json, pid, filter_key_path=None, load_string=False):
        if load_string:
            json = loads(json)
        j = cls(pid=pid, filter_key_path=filter_key_path, defer_pull=True)
        j.handle(json)
        return j

class HtmlHandler(PullMixIn):
    """
    Subclasses must provide `reader_func` to parse the decoded contents
    of GET request to `self.url`,
    """

    def pull(self):
        resp = GET(self.url, raise_for_status=True)
        data = self.reader_func(resp.content.decode())
        self.handle(data)

    def handle(self, data):
        self.page = data  # store BeautifulSoup document

    @staticmethod
    def reader_func(data):
        return BS(data, features="html5lib")
