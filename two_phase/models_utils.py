import numpy as np
from .utils import Properties as p
from .models import EBVelocity
from .models import Homogeneous


class EBVelUtil(object):

    def __init__(self):
        # Models
        self.functions = {'nicklin1962': self.nicklin1962,
                          'bendiksen1984': self.bendiksen1984,
                          'theron1989': self.theron1989,
                          'petalasaziz2000': self.petalasaziz2000,
                          'dukler1985': self.dukler1985}

        self.authors = ['Nicklin (1962)',
                        'Bendiksen (1984)',
                        'Theron (1989)',
                        'Petalas and Aziz (2000)',
                        'Dukler (1985)']
        pass

    def ebmodels(self, models=False):
        eb = self.functions
        if models:
            val = np.array([eb[key]() for key in eb.keys()])
            mdl = list(eb.keys())
            return val, mdl
        else:
            return np.array([eb[key]() for key in eb.keys()])

    @staticmethod
    def nicklin1962(v_sg=None, v_sl=None, d=None):
        # Check for default variables
        v_sl = p.v_sl if not v_sl else v_sl
        v_sg = p.v_sg if not v_sg else v_sg
        d = p.d if not d else d
        # Calculate and return the value
        return EBVelocity.nicklin1962(v_sg, v_sl, d, p.g)

    @staticmethod
    def bendiksen1984(v_sg=None, v_sl=None, d=None, theta=None):
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.bendiksen1984(v_sg, v_sl, d, theta, p.g)

    @staticmethod
    def theron1989(v_sg=None, v_sl=None, d=None, theta=None):
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.theron1989(v_sg, v_sl, d, theta, p.g)

    @staticmethod
    def petalasaziz2000(v_sg=None, v_sl=None, rho_l=None, mu_l=None,
                        d=None, theta=None, foo=None, fluid=None):
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        theta = p.theta if not theta else theta
        fluid = 'liq' if not fluid else fluid
        # Calculate the liquid specific mass
        rho_l = p.rho(rho_l, T=None, P=None, foo=foo, fluid=fluid)
        # Calculate the liquid viscosity
        mu_l = p.rho(mu_l, T=None, P=None, foo=foo, fluid=fluid)
        # Calculate and return the value
        return EBVelocity.petalasaziz2000(v_sg, v_sl, rho_l, mu_l, d, theta, p.g)

    @staticmethod
    def dukler1985(v_sg=None, v_sl=None):
        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        return EBVelocity.dukler1985(v_sg, v_sl)

    pass


class HomogeneousUtil(object):

    def __init__(self):
        pass

    # ===================== Homogeneous model utility ========================
    def Rem(self, v_sg=None, v_sl=None, rho_l=None, rho_g=None, mu_l=None,
            mu_g=None, T=None, P=None, d=None, gas=None, liq=None, gvf=None,
            foo=None):

        # Check for default variables
        v_sg = p.v_sg if not v_sg else v_sg
        v_sl = p.v_sl if not v_sl else v_sl
        d = p.d if not d else d
        liq = 'liq' if not liq else liq
        gas = 'gas' if not gas else gas
        foo = [None]*4 if type(foo) is not list else foo

        # Get the fluid properties
        rho_l = p.rho(rho_type=rho_l, T=T, P=P, foo=foo[0], fluid=liq)
        rho_g = p.rho(rho_type=rho_g, T=T, P=P, foo=foo[1], fluid=gas)
        mu_l = p.mu(mu_type=mu_l, T=T, P=P, foo=foo[2], fluid=liq)
        mu_g = p.mu(mu_type=mu_g, T=T, P=P, foo=foo[3], fluid=gas)
        return Homogeneous.Rem(v_sg, v_sl, rho_l, rho_g, mu_l, mu_g, d, gvf)

    pass
