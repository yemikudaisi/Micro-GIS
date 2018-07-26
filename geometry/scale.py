class Scale(object):
    def __init__(self, scale, denominator):
        self.scale = scale
        self.denominator = denominator

    @property
    def representativeFraction(self):
        numerator = self.scale/self.scale
        denominator = self.denominator/self.scale
        return "{numerator},{denominator}".format(**locals())

