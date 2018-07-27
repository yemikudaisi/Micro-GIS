class Scale(object):
    def __init__(self, scale, denominator):
        self.scale = scale
        self.denominator = denominator

    @property
    def representativeFraction(self):
        numerator = int(round(self.scale/self.scale))
        denominator = round(self.denominator/self.scale,2)
        return "{numerator}:{denominator}".format(**locals())

