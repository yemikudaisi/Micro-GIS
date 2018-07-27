class Scale(object):
    def __init__(self, scale, denominator):
        assert isinstance(scale, float)
        assert isinstance(denominator, float)
        self.numerator = scale
        self.denominator = denominator

    @property
    def representativeFraction(self):
        numerator = int(round(self.numerator/self.numerator))
        denominator = round(self.denominator/self.numerator,2)
        return "{numerator}:{denominator}".format(**locals())

