import argparse
import datetime
import os
import re
import textwrap


def icalentry(cols):
    day = re.sub(r'\(.+\)', '', cols[3])
    ko = "{}/{} {}".format(cols[0], day, cols[4] or '00:00')
    if '未定' in ko:
        return None
    ko = datetime.datetime.strptime(ko, '%Y/%m/%d %H:%M')
    ko = ko.strftime('%Y%m%dT%H%M00')
    league, match = cols[1], re.sub(r'第.日', '', cols[2])
    home, _, away, stadium = cols[5:]
    return home, away, textwrap.dedent(f"""
        BEGIN:VEVENT
        DTSTART;TZID=Asia/Tokyo:{ko}
        DTEND;TZID=Asia/Tokyo:{ko}
        SUMMARY:{league}{match} {home}vs{away}({stadium})
        END:VEVENT
    """)[1:-1]


def to_han(s):
    tn = {chr(ord('０') + i): chr(ord('0') + i) for i in range(10)}
    tc = {chr(ord('Ａ') + i): chr(ord('A') + i) for i in range(26)}
    return s.translate(str.maketrans({**tn, **tc}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('out')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    lines = [to_han(line).split(',') for line in
             open(args.csv, 'r').read().splitlines()]

    cals = dict()
    all_cals = []
    for cols in lines:
        ret = icalentry(cols)
        if not ret:
            continue
        home, away, ical = ret
        if home not in cals:
            cals[home] = []
        if away not in cals:
            cals[away] = []
        cals[home].append(ical)
        cals[away].append(ical)
        all_cals.append(ical)

    headers = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//@sakanazensen//J-League 2022 calendar (as of 2022/1/21)//EN",   # NOQA
    ]

    league = lines[0][1]
    if 'YLC' in league:
        league = 'YLC'
    cals = {**cals, league: all_cals}
    for team, cal in cals.items():
        print(team)
        with open(os.path.join(args.out, f'{team}.ics'), 'wt') as f:
            f.write("\n".join(headers + cal + ["END:VCALENDAR"]))


if __name__ == "__main__":
    main()
