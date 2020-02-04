import numpy as np
import CoolProp.CoolProp as cp
import sklearn.metrics as mtr
from .models import EBVelocity, Homogeneous
from .utils import Convert, Constant

class TwoPhase(EBVelocity, Constant):

    # Fluid flow properties
    T = 0  # [°C] -> Temperature at the desired point
    P = 0  # [Pa] -> Pressure at the desired point

    _v_sg = 0  # [m/s] -> Gas superficial velocity
    _v_sl = 0  # [m/s] -> Liquid superficial velocity

    _Q_g = 0  # [m^3/s] -> Gas volume rate
    _Q_l = 0  # [m^3/s] -> Liquid volume rate

    _gvfh = 0  # [-] Gas void fraction in %

    _d = 0  # [m] -> Tube diameter

    theta = 90  # [°] -> Tube inclination

    # Properties functions
    rho_l_func = (lambda self, x, y: x + y)
    rho_g_func = (lambda self, x, y: x + y)

    mu_l_func = (lambda self, x, y: x + y)
    mu_g_func = (lambda self, x, y: x + y)

    rho_l_default = False
    rho_g_default = False

    mu_l_default = False
    mu_g_default = False

    test = Convert()

    def __init__(self, d=None, theta=None, gas='air', liquid='water'):
        # Physical properties
        self._d = 0 if not d else d  # [m] -> Tube diameter
        self.theta = 90 if not theta else theta  # [°] -> Tube angle

        # Fluids
        self.liq = liquid
        self.gas = gas
 
        pass

    # ======================== Utilities ================================

    # Properties decision functions
    def __rho__(self, rho=None, T=None, P=None, foo=None, fluid=None):
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        #  Check the defined variables
        T = self.T if not T else T
        P = self.P if not P else P
        fluid = 'liq' if not fluid else fluid
        # Check if rho is already defined
        if not rho:
            if callable(foo):
                # Use the passed function
                rho = foo(T, P)
            elif fluid is 'liq':
                if self.rho_l_default:
                    # Use custom function
                    rho = self.rho_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    rho = cp.PropsSI('D', 'T', T + self.K, 'P', P, self.liq)
            elif fluid is 'gas':
                if self.rho_g_default:
                    # Use custom function
                    rho = self.rho_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    rho = cp.PropsSI('D', 'T', T + self.K, 'P', P, self.gas)
            else:
                # Unknown fluid
                # Use coolprop library to get the fluid properties
                rho = cp.PropsSI('D', 'T', T + self.K, 'P', P, fluid)
        return rho

    def __mu__(self, mu=None, T=None, P=None, foo=None, fluid=None):
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.

        #  Check the defined variables
        T = self.T if not T else T
        P = self.P if not P else P
        fluid = 'liq' if not fluid else fluid
        # Check if mu is already defined
        if not mu:
            if callable(foo):
                # Use the passed function
                mu = foo(T, P)
            elif fluid is 'liq':
                if self.mu_l_default:
                    # Use custom function
                    mu = self.mu_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    mu = cp.PropsSI('V', 'T', T + self.K, 'P', P, self.liq)
            elif fluid is 'gas':
                if self.mu_g_default:
                    # Use custom function
                    mu = self.mu_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    mu = cp.PropsSI('V', 'T', T + self.K, 'P', P, self.gas)
            else:
                # Unknown fluid
                # Use coolprop library to get the fluid properties
                mu = cp.PropsSI('V', 'T', T + self.K, 'P', P, fluid)
        return mu

    # ======================== Specific ================================

    def lflow_elm(self, P):
        # Static function => Candidate
        # P -> Pa
        # It converts from Pa -> inH2O
        P = P * 0.0040146309
        # inH2O == ft^3/min -> m^3/s
        q = 0.0004719474 * P
        return q

    # ==================== General convertions ===========================

    def kgmin2m3s(self, m, T=None, P=None, d=None, rho=None, foo=None,
                  fluid=None):
        # m -> [kg/min]
        # t -> [°C]
        # p -> [Pa]
        # d -> [m]
        # Get the specific mass [kg/m^3]
        rho = self.__rho__(rho=rho, T=T, P=P, foo=foo, fluid=fluid)
        # Calculate m^3/s
        Q_f = m / (60 * rho)
        return Q_f

    def Qx2Qy(self, Qx, T, P):
        # Static function => Candidate
        # Volume x to volume y using ideal gas equation
        # qx -> m3/s
        # T -> [T_x, T_y] [°C]
        # P -> [P_x, P_y] [Pa]
        T = [T + self.K, self.T + self.K] if type(T) is not list else T
        P = [P, self.P] if type(P) is not list else P
        # Perform the calculation
        Qy = ((P[0] * T[1]) / (P[1] * T[0])) * Qx
        return Qy

    def m3s2vs(self, Q, d=None):
        # q -> m^3/s
        # d -> m
        # Check if the variable exists
        d = self.d if not d else d
        # Calculate
        vs = Q / (np.pi * ((d / 2)**2))
        return vs

    # ===================== Homogeneous model utility ==========================

    def Rem(self, v_sg=None, v_sl=None, rho_l=None, rho_g=None, mu_l=None,
               mu_g=None, T=None, P=None, d=None, gas=None, liq=None, gvf=None,
               foo=None):
        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        d = self.d if not d else d
        liq = 'liq' if not liq else liq
        gas = 'gas' if not gas else gas
        foo = [None]*4 if type(foo) is not list else foo
        # Get the fluid properties
        rho_l = self.__rho__(rho=rho_l, T=T, P=P, foo=foo[0], fluid=liq)
        rho_g = self.__rho__(rho=rho_g, T=T, P=P, foo=foo[1], fluid=gas)
        mu_l = self.__mu__(mu=mu_l, T=T, P=P, foo=foo[2], fluid=liq)
        mu_g = self.__mu__(mu=mu_g, T=T, P=P, foo=foo[3], fluid=gas)
        return Homogeneous.Rem(v_sg, v_sl, rho_l, rho_g, mu_l, mu_g, d, gvf)

    # ============ Experimental C0 e C1 ========================================
    def c0_c1(self, gvf, v_sg=None, v_sl=None, v_m=None):

        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        if not v_m:
            v_m = v_sg + v_sl
        v_sg = v_sg.astype(float)
        v_m = v_m.astype(float)
        gvf = gvf.astype(float)
        # Calculate and return the value
        return TwoPhase.c0_c1_s(v_sg, v_m, gvf)

    # ======================== EB models utility =============================

    def nicklin1962(self, v_sg=None, v_sl=None, d=None):
        # Check for default variables
        v_sl = self.v_sl if not v_sl else v_sl
        v_sg = self.v_sg if not v_sg else v_sg
        d = self.d if not d else d
        # Calculate and return the value
        return EBVelocity.nicklin1962(v_sg, v_sl, d, self.g)

    def bendiksen1984(self, v_sg=None, v_sl=None, d=None, theta=None):
        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        d = self.d if not d else d
        theta = self.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.bendiksen1984(v_sg, v_sl, d, theta, self.g)

    def theron1989(self, v_sg=None, v_sl=None, d=None, theta=None):
        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        d = self.d if not d else d
        theta = self.theta if not theta else theta
        # Calculate and return the value
        return EBVelocity.theron1989(v_sg, v_sl, d, theta, self.g)

    def petalasaziz2000(self, v_sg=None, v_sl=None, rho_l=None, mu_l=None,
                        d=None, theta=None, foo=None, fluid=None):
        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        d = self.d if not d else d
        theta = self.theta if not theta else theta
        fluid = 'liq' if not fluid else fluid
        # Calculate the liquid specific mass
        rho_l = self.__rho__(rho_l, T=None, P=None, foo=foo, fluid=fluid)
        # Calculate the liquid viscosity
        mu_l = self.__mu__(mu_l, T=None, P=None, foo=foo, fluid=fluid)
        # Calculate and return the value
        return EBVelocity.petalasaziz2000(v_sg, v_sl, rho_l, mu_l, d, theta, self.g)
        
    def dukler1985(self, v_sg=None, v_sl=None):
        # Check for default variables
        v_sg = self.v_sg if not v_sg else v_sg
        v_sl = self.v_sl if not v_sl else v_sl
        return EBVelocity.dukler1985(v_sg, v_sl)

    def ebmodels(self, models=False):
        eb = self.ebvel_dict
        if models:
            val = np.array([eb[key]() for key in eb.keys()])
            mdl = list(eb.keys())
            return val, mdl
        else:
            return np.array([eb[key]() for key in eb.keys()])

    # ============ Experimental C0 e C1 ========================================

    @staticmethod
    def c0_c1_s(v_sg, v_m, gvf):
        # Get the Y and X to fit a 1 order polynomial
        y_fit = v_sg/gvf
        x_fit = v_m
        # Fit using Least squares
        coef = np.polyfit(x_fit, y_fit, 1)
        # Get the predictions
        y_pred = np.polyval(coef, x_fit)
        # Calculate the R²
        r2 = mtr.r2_score(y_fit, y_pred)
        return coef, r2

    # ======================== Callbacks ================================

    @property  # v_sg [m/s] -> Gas superficial velocity
    def gvfh(self):
        return self._gvfh

    @property  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self):
        return self._v_sg

    @v_sg.setter  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self, value):
        self._v_sg = value
        self._Q_g = self._v_sg * (np.pi * ((self._d / 4)**2))
        # Legacy version that check for zero division
        # if (self._v_sg + self._v_sl) != 0:
        self._gvfh = Homogeneous.gvf(self._v_sg, self._v_sl)

    @property  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self):
        return self._v_sl

    @v_sl.setter  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self, value):
        self._v_sl = value
        self._Q_l = self._v_sl * (np.pi * ((self._d / 4)**2))
        # Legacy version that check for zero division
        # if (self._v_sg + self._v_sl) != 0:
        self._gvfh = Homogeneous.gvf(self._v_sg, self._v_sl)

    @property  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self):
        return self._Q_g

    @Q_g.setter  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self, value):
        self._Q_g = value
        self._v_sg = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (self._v_sg + self._v_sl) != 0:
        self._gvfh = Homogeneous.gvf(self._v_sg, self._v_sl)

    @property  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self):
        return self._v_sg

    @Q_l.setter  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self, value):
        self._Q_l = value
        self._v_sl = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (self._v_sg + self._v_sl) != 0:
        self._gvfh = Homogeneous.gvf(self._v_sg, self._v_sl)

    @property  # d [m] -> diameter
    def d(self):
        return self._d

    @d.setter  # d [m] -> diameter
    def d(self, value):
        self._d = value
        self._v_sl = self.m3s2vs(self._Q_g)
        self._v_sg = self.m3s2vs(self._Q_l)

    # ======================== Class Options ================================

    def set_rho_l_func(self, foo, default=True):
        self.rho_l_func = foo
        self.rho_l_default = default

    def set_rho_g_func(self, foo, default=True):
        self.rho_g_func = foo
        self.rho_g_default = default

    def set_mu_l_func(self, foo, default=True):
        self.mu_l_func = foo
        self.mu_l_fdefault = default

    def set_mu_g_func(self, foo, default=True):
        self.mu_g_func = foo
        self.mu_g_fdefault = default
