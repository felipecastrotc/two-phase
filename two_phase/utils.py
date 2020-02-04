import numpy as np

class Constant(object):
    # Constants
    g = 9.81  # [m/s^2] -> Gravity
    K = 273.15  # [ºC] -> 0ºC in Kelvin

    pass


class Convert(Constant):

    def oi(self):
        return self.g

    pass
