import CoolProp.CoolProp as cp
import numpy as np
from .utils import iterable


class Properties(object):

    # Constants
    g = 9.81  # [m/s^2] -> Gravity
    K = 273.15  # [ºC] -> 0ºC in Kelvin

    # Fluid flow properties
    T = 0  # [°C] -> Temperature at the desired point
    P = 0  # [Pa] -> Pressure at the desired point

    v_sg = 0  # [m/s] -> Gas superficial velocity
    v_sl = 0  # [m/s] -> Liquid superficial velocity
    v_m = 0  # [m/s] -> Mixture velocity

    Q_g = 0  # [m^3/s] -> Gas volume rate
    Q_l = 0  # [m^3/s] -> Liquid volume rate

    gvfh = 0  # [-] Gas void fraction in %

    d = 0  # [m] -> Pipe diameter
    l = 0  # [m] -> Pipe length

    theta = 90  # [°] -> Pipe inclination

    # Fluids
    liq = "water"
    gas = "air"

    # Properties functions
    sigma_func = lambda x, y: x + y

    rho_l_func = lambda x, y: x + y
    rho_g_func = lambda x, y: x + y

    mu_l_func = lambda x, y: x + y
    mu_g_func = lambda x, y: x + y

    sigma_default = False

    rho_l_default = False
    rho_g_default = False

    mu_l_default = False
    mu_g_default = False

    # TODO: check what the "prop"_type means and consider removing it
    # FIXING this issue
    # Properties decision functions
    @staticmethod
    def rho(T=None, P=None, foo=None, fluid=None):
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        p = Properties
        #  Check the defined variables
        T = p.T if T is None else T
        P = p.P if P is None else P
        fluid = "liq" if fluid is None else fluid
        # Check which method to use
        if callable(foo):
            # Use the passed function
            rho = foo(T, P)
        elif fluid is "liq":
            if p.rho_l_default:
                # Use custom function
                rho = p.rho_l_func(T, P)
            else:
                # Use coolprop library to get the fluid properties
                rho = cp.PropsSI("D", "T", T + p.K, "P", P, p.liq)
        elif fluid is "gas":
            if p.rho_g_default:
                # Use custom function
                rho = p.rho_l_func(T, P)
            else:
                # Use coolprop library to get the fluid properties
                rho = cp.PropsSI("D", "T", T + p.K, "P", P, p.gas)
        else:
            # Unknown fluid
            # Use coolprop library to get the fluid properties
            rho = cp.PropsSI("D", "T", T + p.K, "P", P, fluid)
        return rho

    @staticmethod
    def mu(T=None, P=None, foo=None, fluid=None):

        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        p = Properties
        #  Check the defined variables
        T = p.T if T is None else T
        P = p.P if P is None else P
        fluid = "liq" if fluid is None else fluid
        # Check which method to use
        if callable(foo):
            # Use the passed function
            mu = foo(T, P)
        elif fluid is "liq":
            if p.mu_l_default:
                # Use custom function
                mu = p.mu_l_func(T, P)
            else:
                # Use coolprop library to get the fluid properties
                mu = cp.PropsSI("V", "T", T + p.K, "P", P, p.liq)
        elif fluid is "gas":
            if p.mu_g_default:
                # Use custom function
                mu = p.mu_l_func(T, P)
            else:
                # Use coolprop library to get the fluid properties
                mu = cp.PropsSI("V", "T", T + p.K, "P", P, p.gas)
        else:
            # Unknown fluid
            # Use coolprop library to get the fluid properties
            mu = cp.PropsSI("V", "T", T + p.K, "P", P, fluid)
        return mu

    @staticmethod
    def sigma(T=None, x=None, foo=None, fluid=None):
        # x = quality
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        p = Properties
        #  Check the defined variables
        T = p.T if T is None else T
        x = 0.0 if x is None else x
        fluid = p.liq if fluid is None else fluid
        # Check which method to use
        if callable(foo):
            # Use the passed function
            sigma = foo(T, x)
        else:
            if p.sigma_default:
                # Use custom function
                sigma = p.sigma_func(T, x)
            else:
                # Use coolprop library to get the fluid properties
                sigma = cp.PropsSI("I", "Q", x, "T", T + p.K, fluid)
        return sigma

    pass


class Convert(object):

    p = Properties

    def __init__(self):
        pass

    # ==================== General convertions ===========================
    def kgmin2m3s(self, m, T=None, P=None, d=None, rho=None, foo=None, fluid=None):
        # m -> [kg/min]
        # t -> [°C]
        # p -> [Pa]
        # d -> [m]
        # Get the specific mass [kg/m^3]
        rho = self.p.rho(rho_type=rho, T=T, P=P, foo=foo, fluid=fluid)
        # Calculate m^3/s
        Q_f = m / (60 * rho)
        return Q_f

    def Qx2Qy(self, Qx, T, P):
        # Static function => Candidate
        # Volume x to volume y using ideal gas equation
        # qx -> m3/s
        # T -> [T_x, T_y] [°C]
        # P -> [P_x, P_y] [Pa]
        p = self.p
        T = [T + p.K, p.T + p.K] if type(T) is not list else T
        P = [P, p.P] if type(P) is not list else P
        # Perform the calculation
        Qy = ((P[0] * T[1]) / (P[1] * T[0])) * Qx
        return Qy

    def m3s2vs(self, Q, d=None):
        # q -> m^3/s
        # d -> m
        p = self.p
        # Check if the variable exists
        d = p.d if not d else d
        # Calculate
        vs = Q / (np.pi * ((d / 2) ** 2))
        return vs

    pass


class PropertyUtil(object):

    p = Properties

    def __init__(self, prop="rho", fluid="liq"):
        self.prop = prop
        self.fluid = fluid

    def __getitem__(self, index):
        # Simpler variable names
        T = self.p.T
        P = self.p.P
        # Get fluid
        fluid = self.p.liq if self.fluid is "liq" else self.p.gas
        # Get property
        if self.prop is "rho":
            return self.p.rho(T=T[index], P=P[index], foo=None, fluid=fluid)
        elif self.prop is "mu":
            return self.p.mu(T=T[index], P=P[index], foo=None, fluid=fluid)
        elif self.prop is "sigma":
            return self.p.sigma(T=T[index], x=0.0, foo=None, fluid=fluid)
