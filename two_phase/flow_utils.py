import CoolProp.CoolProp as cp
import numpy as np
from .utils import iterable


class Properties(object):

    # Constants
    g = 9.81  # [m/s^2] -> Gravity
    K = 273.15  # [ºC] -> 0ºC in Kelvin

    def __init__(self):

        # Fluid flow properties
        self.T = 0  # [°C] -> Temperature at the desired point
        self.P = 0  # [Pa] -> Pressure at the desired point

        self.v_sg = 0  # [m/s] -> Gas superficial velocity
        self.v_sl = 0  # [m/s] -> Liquid superficial velocity
        self.v_m = 0  # [m/s] -> Mixture velocity

        self.Q_g = 0  # [m^3/s] -> Gas volume rate
        self.Q_l = 0  # [m^3/s] -> Liquid volume rate

        self.gvfh = 0  # [-] Gas void fraction in %

        self.d = 0  # [m] -> Pipe diameter
        self.l = 0  # [m] -> Pipe length

        self.theta = 90  # [°] -> Pipe inclination

        # Fluids
        self.liq = "water"
        self.gas = "air"

        # Properties
        self.rho_l = 0  # [kg/m³] -> Liquid specific mass
        self.rho_g = 0  # [kg/m³] -> Gas specific mass
        self.mu_l = 0  # [Pa*s] -> Liquid viscosity
        self.mu_g = 0  # [Pa*s] -> Gas viscosity
        self.sigma = 0  # [Pa] -> Surface tension

        # Properties functions
        self.sigma_func = lambda x, y: x + y

        self.rho_l_func = lambda x, y: x + y
        self.rho_g_func = lambda x, y: x + y

        self.mu_l_func = lambda x, y: x + y
        self.mu_g_func = lambda x, y: x + y

        self.sigma_default = False

        self.rho_l_default = False
        self.rho_g_default = False

        self.mu_l_default = False
        self.mu_g_default = False

        # Support variables
        self.curr_hash = 0

    def __len__(self):
        # The length was arbitrarily based on v_sg
        return len(self.v_sg)

    # Update hash value
    def __setattr__(self, key, value):
        super(Properties, self).__setattr__(key, value)
        if key != "curr_hash":
            dct = vars(self)
            del dct["curr_hash"]
            self.curr_hash = hash(frozenset(dct.items()))

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
    def __init__(self, properties, prop="rho", phase="liq"):
        # Quality
        self.x = 0.0
        # Properties class variables
        self.p = properties
        self.p_hash = 0
        # Settings variables
        self.prop = prop
        self.phase = phase

        # Cached value for the property
        self.cached_value = None

        # Value used when the user manually set the property value
        self.manual = False

    # TODO: check what the "prop"_type means and consider removing it
    # FIXING this issue
    # Properties decision functions
    def rho(self, T=None, P=None, foo=None, fluid=None, phase=None):
        # Get fluid
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        phase = phase if phase is not None else self.phase
        if fluid is None:
            fluid = self.p.liq if phase is "liq" else self.p.gas
        # Check if a custom function was passed
        custom_func = self.p.rho_l_default if phase is "liq" else self.p.rho_g_default
        # Check which method to use
        if callable(foo):
            # Use the passed function
            rho = foo(self.p)
        elif custom_func:
            # Use custom function
            if phase is "liq":
                rho = self.p.rho_l_func(self.p)
            else:
                rho = self.p.rho_g_func(self.p)
        else:
            #  Check the defined variables
            T = self.T if T is None else T
            P = self.P if P is None else P
            K = self.p.K
            # Use coolprop library to get the fluid properties
            rho = cp.PropsSI("D", "T", T + K, "P", P, fluid)
        return rho

    def mu(self, T=None, P=None, foo=None, fluid=None, phase=None):
        # Get fluid
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function
        phase = phase if phase is not None else self.phase
        if fluid is None:
            fluid = self.p.liq if phase is "liq" else self.p.gas
        # Check if a custom function was passed
        custom_func = self.p.mu_l_default if phase is "liq" else self.p.mu_g_default
        # Check which method to use
        if callable(foo):
            # Use the passed function
            mu = foo(self.p)
        elif custom_func:
            # Use custom function
            if phase is "liq":
                mu = self.p.mu_l_func(self.p)
            else:
                mu = self.p.mu_g_func(self.p)
        else:
            #  Check the defined variables
            T = self.T if T is None else T
            P = self.P if P is None else P
            K = self.p.K
            # Use coolprop library to get the fluid properties
            mu = cp.PropsSI("V", "T", T + K, "P", P, fluid)
        return mu

    def sigma(self, x, T=None, P=None, foo=None, fluid=None):
        # Get fluid
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        if fluid is None:
            fluid = self.p.liq if self.phase is "liq" else self.p.gas
        # Check if a custom function was passed
        custom_func = self.p.sigma_default
        # Check which method to use
        if callable(foo):
            # Use the passed function
            sigma = foo(x, self.p)
        elif custom_func:
            sigma = self.p.sigma_func(x, self.p)
        else:
            #  Check the defined variables
            T = self.T if T is None else T
            K = self.p.K
            # Use coolprop library to get the fluid properties
            sigma = cp.PropsSI("I", "Q", x, "T", T + K, fluid)
        return sigma

    def update_cache(self):
        # Get property
        if self.prop is "rho":
            self.cached_value = self.rho()
        elif self.prop is "mu":
            self.cached_value = self.mu()
        elif self.prop is "sigma":
            self.cached_value = self.p.sigma(self.x)

    @property
    def value(self):
        if not self.manual:
            if (self.p.curr_hash != self.p_hash) or (self.p_rho_l.value is not None):
                self.p_hash = self.p.curr_hash
                self.update_cache()
        return self.cached_value

    @value.setter
    def value(self, value):
        # if set to None it will disable the manual property settings
        if value is None:
            self.manual = False
        else:
            # Enable the manual value
            self.manual = True
            self.cached_value = value
