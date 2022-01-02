#!/usr/bin/env python3

from enum import Enum, IntEnum
from sys import argv, stdout, stderr
from os import path, makedirs
from urllib.parse import urlencode
from urllib.request import urlopen
from shutil import copyfileobj
from datetime import date

URL = "https://eventor.orienteering.asn.au/Events/ExportICalendarEvents"


def main(args):
    out_dir = args[1]

    start = date(date.today().year, 1, 1)
    end = date(start.year, 12, 31)

    for org, classes, disciplines in combinations(stdout):
        name = filename(org, classes, disciplines)
        query = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "organisations": int(org),
            "classifications": ','.join(map(str, classes)),
        }
        if len(disciplines) > 0:
            query["disciplines"] = ','.join(map(str, disciplines))

        file_path = path.join(out_dir, name)
        makedirs(path.dirname(file_path), exist_ok=True)

        query = urlencode(query)
        stderr.write(f'Fetching {name}\n')
        copyfileobj(urlopen(f'{URL}?{query}'), open(file_path, "wb"))


def combinations(page):
    "All combinations to generate"

    for org in Organisation.iter():
        a = anchor(org)
        page.write(f'<a id="{a}" href="#{a}">\n')
        page.write(f'  <h1>{org.desc()}</h1>\n')
        page.write('</a>\n')
        for classes in Classification.combinations():
            a = anchor(org, classes)
            page.write(f'<a id="{a}" href="#{a}">\n')
            page.write(f'  <h2>{text_list(map(str, classes))}</h2>\n')
            page.write('</a>\n')
            page.write('<ul>\n')
            for disciplines in Discipline.combinations():
                p = filename(org, classes, disciplines)
                t = text_list(map(desc, disciplines))
                page.write('  <li>')
                page.write(f'<a href="./{p}">{t}</a>')
                page.write('</li>\n')
                yield (org, classes, disciplines)
            page.write('</ul>\n')


def desc(value):
    return value.desc()


def text_list(items):
    items = list(items)
    text = ""

    if len(items) == 0:
        return text

    text = items.pop()

    sep = " and "
    if len(items) == 0:
        return text
    elif len(items) > 1:
        sep = ", and "

    text = items.pop() + sep + text
    sep = ", "

    while len(items) > 0:
        text = items.pop() + sep + text

    return text


def name(join, org, classes=None, disciplines=None):
    name = str(org)
    if classes is not None and len(classes) > 0:
        name = join(name, '-'.join(map(str, classes)))
    if disciplines is not None:
        if len(disciplines) > 0:
            name = join(name, '-'.join(map(str, disciplines)))
        else:
            name = join(name, "All")
    return name


def anchor(*args):
    "Generate an anchor name"
    return name(lambda *parts: '.'.join(parts), *args)


def filename(*args):
    "Generate a file name"
    return name(path.join, *args) + '.ics'


class Classification(Enum):
    "Eventor classifications of events"

    INTERNATIONAL = 0
    CHAMPIONSHIP = 1
    NATIONAL = 2
    REGIONAL = 3
    LOCAL = 4
    CLUB = 5

    def __str__(self):
        return {
            Classification.INTERNATIONAL: "International",
            Classification.CHAMPIONSHIP: "Championship",
            Classification.NATIONAL: "National",
            Classification.REGIONAL: "Regional",
            Classification.LOCAL: "Local",
            Classification.CLUB: "Club"
        }[self]

    @staticmethod
    def combinations():
        yield [
            Classification.INTERNATIONAL,
            Classification.CHAMPIONSHIP,
            Classification.NATIONAL,
            Classification.REGIONAL,
            Classification.LOCAL,
            Classification.CLUB,
        ]

        yield [
            Classification.INTERNATIONAL,
            Classification.CHAMPIONSHIP,
            Classification.NATIONAL,
            Classification.REGIONAL,
        ]

        yield [
            Classification.CHAMPIONSHIP,
            Classification.REGIONAL,
            Classification.LOCAL,
        ]

        yield [
            Classification.LOCAL,
            Classification.CLUB,
        ]


class Organisation(IntEnum):
    "State groups of organisation"

    ALL = 2
    ACT = 4
    NSW = 5
    QLD = 6
    SA = 7
    TAS = 8
    VIC = 9
    WA = 10

    @staticmethod
    def iter():
        all_orgs = [
            Organisation.ALL,
            Organisation.ACT,
            Organisation.NSW,
            Organisation.QLD,
            Organisation.SA,
            Organisation.TAS,
            Organisation.VIC,
            Organisation.WA,
        ]

        for org in all_orgs:
            yield org

    def __str__(self):
        return {
            Organisation.ALL: "All",
            Organisation.ACT: "ACT",
            Organisation.NSW: "NSW",
            Organisation.QLD: "Qld",
            Organisation.SA: "SA",
            Organisation.TAS: "Tas",
            Organisation.VIC: "Vic",
            Organisation.WA: "WA",
        }[self]

    def desc(self):
        return {
            Organisation.ALL: "All Organisations",
            Organisation.ACT: "Australian Capital Territory (ACT)",
            Organisation.NSW: "New South Wales (NSW)",
            Organisation.QLD: "Queensland",
            Organisation.SA: "South Australia (SA)",
            Organisation.TAS: "Tasmania",
            Organisation.VIC: "Victoria",
            Organisation.WA: "Western Australia (WA)",
        }[self]


class Discipline(Enum):
    FOOT = 0
    PARK_AND_STREET = 1
    MOUNTAIN_BIKE = 2
    RADIO = 3
    SKI = 4

    def __str__(self):
        return {
            Discipline.FOOT: "Foot",
            Discipline.PARK_AND_STREET: "ParkAndStreet",
            Discipline.MOUNTAIN_BIKE: "MountainBike",
            Discipline.RADIO: "Radio",
            Discipline.SKI: "Ski",
        }[self]

    def desc(self):
        return {
            Discipline.FOOT: "Foot",
            Discipline.PARK_AND_STREET: "Urban",
            Discipline.MOUNTAIN_BIKE: "Mountain Bike",
            Discipline.RADIO: "Radio",
            Discipline.SKI: "Ski",
        }[self]

    @staticmethod
    def combinations():
        all_disciplines = [
            Discipline.FOOT,
            Discipline.PARK_AND_STREET,
            Discipline.MOUNTAIN_BIKE,
            Discipline.RADIO,
            Discipline.SKI,
        ]

        yield []

        for discipline in all_disciplines:
            yield [discipline]

        yield [
            Discipline.FOOT,
            Discipline.PARK_AND_STREET,
        ]


if __name__ == "__main__":
    main(argv)
