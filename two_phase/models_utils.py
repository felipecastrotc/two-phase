import numpy as np

from .models import EBVelocity, Homogeneous
from .models_flow_pattern_utils import Taitel1980Util
from .utils import get_kwargs


class EBVelUtil(object):
    def __init__(self, p):
        # Properties
        self.p = p
        # Models
        self.functions = {
            "nicklin1962": self.nicklin1962,
            "bendiksen1984": self.bendiksen1984,
            "theron1989": self.theron1989,
            "petalasaziz2000": self.petalasaziz2000,
            "dukler1985": self.dukler1985,
        }

        self.authors = [
            "Nicklin (1962)",
            "Bendiksen (1984)",
            "Theron (1989)",
            "Petalas and Aziz (2000)",
            "Dukler (1985)",
        ]
        pass

    def ebmodels(self, models=False):
        eb = self.functions
        if models:
            val = np.array([eb[key]() for key in eb.keys()])
            mdl = list(eb.keys())
            return val, mdl
        else:
            return np.array([eb[key]() for key in eb.keys()])

    def nicklin1962(self, v_sg=None, v_sl=None, d=None):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sl = p.v_sl if not v_sl else v_sl
        v_sg = p.v_sg if not v_sg else v_sg
        d = p.d if not d else d
        # Calculate and return the value
        return EBVelocity.nicklin1962(v_sg, v_sl, d, p.g)

    def bendiksen1984(self, v_sg=None, v_sl=None, d=None, theta=None):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.bendiksen1984(v_sg, v_sl, d, theta, p.g)

    def theron1989(self, v_sg=None, v_sl=None, d=None, theta=None):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.theron1989(v_sg, v_sl, d, theta, p.g)

    def petalasaziz2000(
        self, v_sg=None, v_sl=None, rho_l=None, mu_l=None, d=None, theta=None,
    ):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        # Calculate the liquid specific mass
        rho_l = p.rho_l.value if rho_l is None else rho_l
        # Calculate the liquid viscosity
        mu_l = p.mu_l.value if mu_l is None else mu_l
        # Calculate and return the value
        return EBVelocity.petalasaziz2000(v_sg, v_sl, rho_l, mu_l, d, theta, p.g)

    def dukler1985(self, v_sg=None, v_sl=None):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        return EBVelocity.dukler1985(v_sg, v_sl)

    pass


class HomogeneousUtil(object):
    def __init__(self, p):
        # Properties
        self.p = p
        pass

    # ===================== Homogeneous model utility ========================
    def Rem(
        self,
        v_sg=None,
        v_sl=None,
        rho_l=None,
        rho_g=None,
        mu_l=None,
        mu_g=None,
        d=None,
        gvf=None,
    ):
        # Simpler name
        p = self.p
        # Check for default variables
        v_sg = p.v_sg if v_sg is None else v_sg
        v_sl = p.v_sl if v_sl is None else v_sl
        d = p.d if d is None else d

        # Get the fluid properties
        rho_l = p.rho_l.value if rho_l is None else rho_l
        rho_g = p.rho_g.value if rho_g is None else rho_g
        mu_l = p.mu_l.value if mu_l is None else mu_l
        mu_g = p.mu_g.value if mu_g is None else mu_g
        return Homogeneous.Rem(v_sg, v_sl, rho_l, rho_g, mu_l, mu_g, d, gvf)

    pass


class PatternUtil(object):
    
    def __init__(self, p):
        self.taitel1980 = Taitel1980Util(p=p)
        pass

    pass
