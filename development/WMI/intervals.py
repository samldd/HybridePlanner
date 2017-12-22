import copy
import re


class Interval(object):
    def __init__(self, bounds, inclusive):
        self.bounds = bounds
        self.inclusive = inclusive

    def combine(self, interval):
        if self.bounds[0] > interval.bounds[0]:
            lower = (self.bounds[0], self.inclusive[0])
        elif self.bounds[0] < interval.bounds[0]:
            lower = (interval.bounds[0], interval.inclusive[0])
        else:
            lower = (self.bounds[0], self.inclusive[0] and interval.inclusive[0])

        if self.bounds[1] < interval.bounds[1]:
            upper = (self.bounds[1], self.inclusive[1])
        elif self.bounds[1] > interval.bounds[1]:
            upper = (interval.bounds[1], interval.inclusive[1])
        else:
            upper = (self.bounds[1], self.inclusive[1] and interval.inclusive[1])

        if lower > upper:
            print("\t\t\t", "INVALID", lower, upper)
            tmp = lower # TODO: aanpassing gemaakt
            lower = upper
            upper = tmp
        return Interval((lower[0], upper[0]), (lower[1], upper[1]))

    def __str__(self):
        left = "[" if self.inclusive[0] else "("
        right = "]" if self.inclusive[1] else ")"
        return left + str(self.bounds[0]) + "," + str(self.bounds[1]) + right

    def is_valid(self):
        return self.bounds[0] < self.bounds[1]


class EmptyInterval(Interval):
    def __init__(self, bounds, inclusive):
        Interval.__init__(self, (0, 0), (False, False))


class Intervals(object):
    def __init__(self, given):
        self.intervals = given

    def times(self, intervals):
        new = copy.copy(self.intervals)
        for v, i in intervals.intervals.items():
            new[v] = new[v].combine(i) if (v in new) else i
        return Intervals(new)

    def __str__(self):
        if len(self.intervals) == 0:
            return "Unbounded"
        return ", ".join(map(lambda t: t[0] + ":" + str(t[1]), self.intervals.items()))

    def keys(self):
        return self.intervals.keys()

    def bounds(self):
        l = []
        for v, i in self.intervals.items():
            l.append(list(i.bounds))
        return l

    def is_valid(self):
        return all(i.is_valid() for i in self.intervals.values())

    @classmethod
    def create(cls, string):
        if string == "boolean":
            return Intervals({})
        pattern = re.compile(r"(\w+)=([+-]?\d+\.?\d+?):([+-]?\d+\.?\d+?)")
        match = pattern.match(string)
        var = match.group(1)
        bounds = float(match.group(2)), float(match.group(3))
        return Intervals({var: Interval(bounds, (True, True))})