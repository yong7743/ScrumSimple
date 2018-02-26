#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import math


class DutySchedule:
    _members = []

    def __init__(self, path, init_data):
        with open(path, "r") as f:
            data = json.load(f)
            self._members = data["names"]
            self._init_date = init_data

    def get_members(self):
        return self._members

    def get_member_onduty(self, target_date):
        duration = (target_date - self._init_date).days
        index = (math.floor(duration / 7)) % len(self._members)
        return self._members[index]


if __name__ == '__main__':
    dutySchedule = DutySchedule("member.json", datetime.date(2018, 2, 19))
    duty_name = dutySchedule.get_member_onduty(datetime.date(2018, 3, 4))
    print(duty_name)



