class Price(object):
    RATIO_BLUE_TO_MAIN = 4.0
    
    def __init__(self, main, blue=None):
        assert type(main) == float
        self.main = main
        if blue:
            assert type(blue) == float
        self.blue = blue
    
    def __cmp__(self, other):
        m1 = self.main
        m2 = other.main
        b1 = self.blue
        b2 = other.blue
        
        if b1 and b2:
            v1 = m1 + b1 * self.RATIO_BLUE_TO_MAIN
            v2 = m2 + b2 * self.RATIO_BLUE_TO_MAIN
            return cmp(v1, v2)
        elif b1:
            v1 = m1 + b1 * self.RATIO_BLUE_TO_MAIN
            return cmp(v1, m1)
        elif b2:
            v2 = m2 + b2 * self.RATIO_BLUE_TO_MAIN
            return cmp(m1, v2)
        else:
            return cmp(m1, m2)
    
    def __str__(self):
        if self.blue:
            return u"%.2f + %.2f" % (self.main, self.blue)
        else:
            return u"%.2f" % self.main