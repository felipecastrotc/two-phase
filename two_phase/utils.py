import numpy as np
import CoolProp.CoolProp as cp


class Properties(object):

    # Constants
    g = 9.81  # [m/s^2] -> Gravity
    K = 273.15  # [ºC] -> 0ºC in Kelvin

    # Fluid flow properties
    T = 0  # [°C] -> Temperature at the desired point
    P = 0  # [Pa] -> Pressure at the desired point

    v_sg = 0  # [m/s] -> Gas superficial velocity
    v_sl = 0  # [m/s] -> Liquid superficial velocity

    Q_g = 0  # [m^3/s] -> Gas volume rate
    Q_l = 0  # [m^3/s] -> Liquid volume rate

    gvfh = 0  # [-] Gas void fraction in %

    d = 0  # [m] -> Tube diameter

    theta = 90  # [°] -> Tube inclination

    # Fluids
    liq = 'water'
    gas = 'air'

    # Properties functions
    rho_l_func = (lambda x, y: x + y)
    rho_g_func = (lambda x, y: x + y)

    mu_l_func = (lambda x, y: x + y)
    mu_g_func = (lambda x, y: x + y)

    rho_l_default = False
    rho_g_default = False

    mu_l_default = False
    mu_g_default = False

    # Properties decision functions
    @staticmethod
    def rho(rho_type=None, T=None, P=None, foo=None, fluid=None):
        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        p = Properties
        #  Check the defined variables
        T = p.T if not T else T
        P = p.P if not P else P
        fluid = 'liq' if not fluid else fluid
        # Check if rho_type is already defined
        if not rho_type:
            if callable(foo):
                # Use the passed function
                rho_val = foo(T, P)
            elif fluid is 'liq':
                if p.rho_l_default:
                    # Use custom function
                    rho_val = p.rho_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    rho_val = cp.PropsSI('D', 'T', T + p.K, 'P', P, p.liq)
            elif fluid is 'gas':
                if p.rho_g_default:
                    # Use custom function
                    rho_val = p.rho_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    rho_val = cp.PropsSI('D', 'T', T + p.K, 'P', P, p.gas)
            else:
                # Unknown fluid
                # Use coolprop library to get the fluid properties
                rho_val = cp.PropsSI('D', 'T', T + p.K, 'P', P, fluid)
        return rho_val

    @staticmethod
    def mu(mu_type=None, T=None, P=None, foo=None, fluid=None):

        # In case you want to use custom function saved on the class
        # use the fluid var to specify if you the gas or liquid function.
        p = Properties
        #  Check the defined variables
        T = p.T if not T else T
        P = p.P if not P else P
        fluid = 'liq' if not fluid else fluid
        # Check if mu is already defined
        if not mu:
            if callable(foo):
                # Use the passed function
                mu = foo(T, P)
            elif fluid is 'liq':
                if p.mu_l_default:
                    # Use custom function
                    mu = p.mu_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    mu = cp.PropsSI('V', 'T', T + p.K, 'P', P, p.liq)
            elif fluid is 'gas':
                if p.mu_g_default:
                    # Use custom function
                    mu = p.mu_l_func(T, P)
                else:
                    # Use coolprop library to get the fluid properties
                    mu = cp.PropsSI('V', 'T', T + p.K, 'P', P, p.gas)
            else:
                # Unknown fluid
                # Use coolprop library to get the fluid properties
                mu = cp.PropsSI('V', 'T', T + p.K, 'P', P, fluid)
        return mu

    pass


class Convert(object):

    p = Properties

    def __init__(self):
        pass

     # ==================== General convertions ===========================
    def kgmin2m3s(self, m, T=None, P=None, d=None, rho=None, foo=None,
                  fluid=None):
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
        vs = Q / (np.pi * ((d / 2)**2))
        return vs

    pass
