import CoolProp.CoolProp as cp
import numpy as np

# from .utils import Convert
from .flow_utils import Convert
from .flow_utils import Properties
from .flow_utils import PropertyUtil
from .models_utils import *


class TwoPhase(object):

    def __init__(self, d=None, theta=None, l=None, gas="air", liquid="water"):
        # Properties
        self.prop = Properties()
        # Physical properties
        self.prop.d = 0 if d is None else d  # [m] -> Tube diameter
        self.prop.l = 0 if l is None else l  # [m] -> Tube diameter
        self.prop.theta = 90 if theta is None else theta  # [°] -> Tube angle
        # Fluids
        self.prop.liq = liquid
        self.prop.gas = gas
        # Property utils
        self.prop.rho_l = PropertyUtil(self.prop, prop="rho", fluid="liq")
        self.prop.rho_g = PropertyUtil(self.prop, prop="rho", fluid="gas")
        self.prop.mu_l = PropertyUtil(self.prop, prop="mu", fluid="liq")
        self.prop.mu_g = PropertyUtil(self.prop, prop="mu", fluid="gas")
        self.prop.sigma = PropertyUtil(self.prop, prop="sigma", fluid="liq")
        
        # Classes
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
        return self.prop.T

    @T.setter  # T [C] -> Temperature
    def T(self, value):
        self.prop.T = value

    @property  # P [Pa] -> Total pressure
    def P(self):
        return self.prop.P

    @P.setter  # P [Pa] -> Total pressure
    def P(self, value):
        self.prop.P = value

    @property  # v_sg [m/s] -> Gas superficial velocity
    def gvfh(self):
        return self.prop.gvfh

    @property  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self):
        return self.prop.v_sg

    @v_sg.setter  # v_sg [m/s] -> Gas superficial velocity
    def v_sg(self, value):
        p = self.prop
        p.v_sg = value
        p.Q_g = p.v_sg * (np.pi * ((p.d / 4) ** 2))
        # Update dependent variables
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)
        p.v_m = p.v_sl + p.v_sg

    @property  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self):
        return self.prop.v_sl

    @v_sl.setter  # v_sl [m/s] -> Liquid superficial velocity
    def v_sl(self, value):
        p = self.prop
        p.v_sl = value
        # Update dependent variables
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)
        p.v_m = p.v_sl + p.v_sg

    @property  # v_m [m/s] -> Mixture velocity
    def v_m(self):
        return self.prop.v_m

    @property  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self):
        return self.prop.Q_g

    @Q_g.setter  # Q_g [m^3/s] -> Gas volume rate
    def Q_g(self, value):
        p = self.prop
        p.Q_g = value
        p.v_sg = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self):
        return self.prop.v_sg

    @Q_l.setter  # Q_l [m^3/s] -> Liquid volume rate
    def Q_l(self, value):
        p = self.prop
        p.Q_l = value
        p.v_sl = self.m3s2vs(value)
        # Legacy version that check for zero division
        # if (p.v_sg + p.v_sl) != 0:
        p.gvfh = Homogeneous.gvf(p.v_sg, p.v_sl)

    @property  # d [m] -> diameter
    def d(self):
        return self.prop.d

    @d.setter  # d [m] -> diameter
    def d(self, value):
        p = self.prop
        p.d = value
        p.v_sl = Convert.m3s2vs(p.Q_g)
        p.v_sg = Convert.m3s2vs(p.Q_l)

    @property
    def rho_l(self):
        return self.prop.rho_l.value
    
    @rho_l.setter
    def rho_l(self, value):
        self.prop.rho_l.value = value

    @property
    def rho_g(self):
        return self.prop.rho_g.value
    
    @rho_g.setter
    def rho_g(self, value):
        self.prop.rho_g.value = value

    @property
    def mu_l(self):
        return self.prop.mu_l.value
    
    @mu_l.setter
    def mu_l(self, value):
        self.prop.mu_l.value = value

    @property
    def mu_g(self):
        return self.prop.mu_g.value
    
    @mu_g.setter
    def mu_g(self, value):
        self.prop.mu_g.value = value

    @property
    def sigma(self):
        return self.prop.sigma.value
    
    @sigma.setter
    def sigma(self, value):
        self.prop.sigma.value = value

    # ======================== Class Options ================================

    def set_rho_l_func(self, foo, default=True):
        self.prop.rho_l_func = foo
        self.prop.rho_l_default = default

    def set_rho_g_func(self, foo, default=True):
        self.prop.rho_g_func = foo
        self.prop.rho_g_default = default

    def set_mu_l_func(self, foo, default=True):
        self.prop.mu_l_func = foo
        self.prop.mu_l_fdefault = default

    def set_mu_g_func(self, foo, default=True):
        self.prop.mu_g_func = foo
        self.prop.mu_g_fdefault = default
