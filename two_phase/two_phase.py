import CoolProp.CoolProp as cp
import numpy as np

# from .utils import Convert
from .flow_utils import Convert
from .flow_utils import Properties as p
from .models_utils import *


class TwoPhase(object):
    def __init__(self, d=None, theta=None, l=None, gas="air", liquid="water"):
        # Physical properties
        p.d = 0 if d is None else d  # [m] -> Tube diameter
        p.l = 0 if l is None else l  # [m] -> Tube diameter
        self.theta = 90 if theta is None else theta  # [°] -> Tube angle
        # Fluids
        p.liq = liquid
        p.gas = gas
        # Classes
        # Properties
        self.prop = p
        # Utils for the Elongated bubble velocity
        self.eb_vel = EBVelUtil()
        # Utils for the Homogeneous model
        self.hg = HomogeneousUtil

        # Utils for flow pattern
        self.ptt = PatternUtil
        # Convert utils
        self.convert = Convert

        pass

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

    # ============ Experimental C0 e C1 ========================================

    @staticmethod
    def c0_c1_s(v_sg, v_m, gvf):
        # Get the Y and X to fit a 1 order polynomial
        y_fit = v_sg / gvf
        x_fit = v_m
        # Fit using Least squares
        coef = np.polyfit(x_fit, y_fit, 1)
        # Get the predictions
        y_pred = np.polyval(coef, x_fit)
        # Calculate the R²
        # TODO: add r2 score manually
        # r2 = mtr.r2_score(y_fit, y_pred)
        return coef, r2

    # ======================== Callbacks ================================

    @property  # T [C] -> Temperature
    def T(self):
        return p.T

    @T.setter  # T [C] -> Temperature
    def T(self, value):
        p.T = value

    @property  # P [Pa] -> Total pressure
    def P(self):
        return p.P

    @P.setter  # P [Pa] -> Total pressure
    def P(self, value):
        p.P = value

    @property  # v_sg [m/s] -> Gas superficial velocity
    def gvfh(self):
        return p.gvfh

    @property  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self):
        return p.v_sg

    @v_sg.setter  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self, value):
        p.v_sg = value
        p.Q_g = p.v_sg * (np.pi * ((p.d / 4) ** 2))
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self):
        return p.v_sl

    @v_sl.setter  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self, value):
        p.v_sl = value
        p.Q_l = p.v_sl * (np.pi * ((p.d / 4) ** 2))
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # v_m [m/s] -> Mixture velocity
    def v_m(self):
        return p.v_mr

    @property  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self):
        return p.Q_g

    @Q_g.setter  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self, value):
        p.Q_g = value
        p.v_sg = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self):
        return p.v_sg

    @Q_l.setter  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self, value):
        p.Q_l = value
        p.v_sl = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # d [m] -> diameter
    def d(self):
        return p.d

    @d.setter  # d [m] -> diameter
    def d(self, value):
        p.d = value
        p.v_sl = Convert.m3s2vs(p.Q_g)
        p.v_sg = Convert.m3s2vs(p.Q_l)

    # ======================== Class Options ================================

    def set_rho_l_func(self, foo, default=True):
        p.rho_l_func = foo
        p.rho_l_default = default

    def set_rho_g_func(self, foo, default=True):
        p.rho_g_func = foo
        p.rho_g_default = default

    def set_mu_l_func(self, foo, default=True):
        p.mu_l_func = foo
        p.mu_l_fdefault = default

    def set_mu_g_func(self, foo, default=True):
        p.mu_g_func = foo
        p.mu_g_fdefault = default
