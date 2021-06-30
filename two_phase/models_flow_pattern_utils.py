import numpy as np
import scipy.optimize as opt
from scipy import interpolate

from .models import Homogeneous
from .models_flow_pattern import Taitel1980
from .utils import get_kwargs


class Taitel1980Util(object):
    def __init__(self, p):
        # Properties
        self.p = p
        pass

    def classify(
        self,
        d=None,
        l=None,
        v_sg=None,
        v_sl=None,
        rho_g=None,
        rho_l=None,
        mu_l=None,
        mu_g=None,
        sigma=None,
        text=False,
    ):
        # Simpler name
        p = self.p
        # Return the list of flow patterns

        # Check for default variables
        d = p.d if d is None else d
        l = p.l if l is None else l
        v_sg = p.v_sg if v_sg is None else v_sg
        v_sl = p.v_sl if v_sl is None else v_sl

        # TODO: Consider changing fluid var from gas or liq to the value of coolprop
        # fluid
        # Set properties
        rho_g = p.rho_g.value if rho_g is None else rho_g
        rho_l = p.rho_l.value if rho_l is None else rho_l
        mu_l = p.mu_l.value if mu_l is None else mu_l
        mu_g = p.mu_g.value if mu_g is None else mu_g
        sigma = p.sigma.value if sigma is None else sigma

        # Create a dictionary to pass to the function
        kwargs = {
            "d": d,
            "l": l,
            "v_sg": v_sg,
            "v_sl": v_sl,
            "rho_g": rho_g,
            "rho_l": rho_l,
            "mu_l": mu_l,
            "mu_g": mu_g,
            "sigma": sigma,
            "g": p.g,
            "text": text,
        }

        ptt = []
        for kwarg in get_kwargs(kwargs):
            ptt += [Taitel1980.classify(**kwarg)]
        return np.array(ptt)

    def get_transition_lines(
        self,
        v_sg_list,
        rho_l=None,
        rho_g=None,
        rho_m=None,
        mu_l=None,
        mu_g=None,
        mu_m=None,
        sigma=None,
        d=None,
        l=None,
    ):
        # Simpler name
        p = self.p
        # Return the list of flow patterns

        # Check for default variables
        d = p.d if d is None else d
        l = p.l if l is None else l

        # Set properties
        rho_g = p.rho_g.value if rho_g is None else rho_g
        rho_l = p.rho_l.value if rho_l is None else rho_l
        mu_l = p.mu_l.value if mu_l is None else mu_l
        mu_g = p.mu_g.value if mu_g is None else mu_g
        sigma = p.sigma.value if sigma is None else sigma

        if rho_m is None:
            gvfh = Homogeneous.gvf(self.p.v_sg, self.p.v_sl).mean()
            rho_m = Homogeneous.rho_m(gvfh, rho_g, rho_l)

        if mu_m is None:
            gvfh = Homogeneous.gvf(self.p.v_sg, self.p.v_sl).mean()
            mu_m = Homogeneous.mu_m(gvfh, mu_g, mu_l)

        # Get lines
        # Please refer to Shoham 2006 Figure 4.9 to understand the nomenclature
        e_line = Taitel1980Util.get_e_line(v_sg_list, rho_l, rho_g, sigma, p.g)
        f_line = Taitel1980Util.get_f_line(
            v_sg_list, rho_l, rho_g, rho_m, mu_m, sigma, p.g, d
        )
        g_line = Taitel1980Util.get_g_line(v_sg_list)
        h_line = Taitel1980Util.get_h_line(v_sg_list, p.g, d, l)

        # Create a dictionary with the transition lines
        out = {"E": e_line, "F": f_line, "G": g_line, "H": h_line, "v_sg": v_sg_list}
        return out

    def cut_transition_lines(self, dt):
        out = {}
        x_0 = np.mean(dt["v_sg"])
        # F-G cut

        # Create an interpolating function to find the intersection
        ff = interpolate.interp1d(dt["v_sg"], dt["F"])
        fg = interpolate.interp1d(dt["v_sg"], dt["G"])
        # Find the intersection
        fc = lambda x: ff(x) - fg(x)
        x = opt.fsolve(fc, x_0)[0]
        x_idx = np.where(dt["v_sg"] > x)[0][0]
        # New coordinates
        out["F"] = {
            "x": np.hstack([dt["v_sg"][:x_idx], [x]]),
            "y": np.hstack([dt["F"][:x_idx], [ff(x)]]),
        }
        out["G"] = {
            "x": np.hstack([[x], dt["v_sg"][x_idx:]]),
            "y": np.hstack([[ff(x)], dt["G"][x_idx:]]),
        }

        # E-F cut

        # Create an interpolating function to find the intersection
        fe = interpolate.interp1d(dt["v_sg"], dt["E"])
        # Find the intersection
        fc = lambda x: ff(x) - fe(x)
        x = opt.fsolve(fc, x_0)[0]
        x_idx = np.where(dt["v_sg"] > x)[0][0]
        # New coordinates
        out["E"] = {
            "x": np.hstack([dt["v_sg"][:x_idx], [x]]),
            "y": np.hstack([dt["E"][:x_idx], [fe(x)]]),
        }

        # H cut

        # Create an interpolating function to find the intersection
        fh = interpolate.interp1d(dt["v_sg"], dt["H"])
        # Find the intersection
        fc = lambda x: ff(x) - fh(x)
        try:
            xf = opt.fsolve(fc, x_0)[0]
            xf_idx = np.where(dt["v_sg"] > x)[0][0]
        except:
            xf = dt["v_sg"][0]
            xf_idx = 0
        # Find the intersection
        fc = lambda x: fe(x) - fh(x)
        xe = opt.fsolve(fc, x_0)[0]
        xe_idx = np.where(dt["v_sg"] > x)[0][0]
        # Select the intersection
        x = xf if xf > xe else xe
        x_idx = xf_idx if xf > xe else xe_idx
        # New coordinates
        out["H"] = {
            "x": np.hstack([[x], dt["v_sg"][x_idx:]]),
            "y": np.hstack([[fh(x)], dt["H"][x_idx:]]),
        }

        return out

    @staticmethod
    def get_e_line(v_sg_list, rho_l, rho_g, sigma, g):
        return Taitel1980.e_transition(v_sg_list, rho_l, rho_g, sigma, g)

    @staticmethod
    def get_f_line(v_sg_list, rho_l, rho_g, rho_m, mu_m, sigma, g, d):
        v_sl = []
        for v_sg in v_sg_list:
            f = lambda v_sl: Taitel1980.f_transition(
                v_sl, v_sg, rho_l, rho_g, rho_m, mu_m, sigma, d, g
            )
            v_sl += [opt.fsolve(f, 1)]
        return np.squeeze(np.array(v_sl))

    @staticmethod
    def get_g_line(v_sg_list):
        return Taitel1980.g_transition(v_sg_list)

    @staticmethod
    def get_h_line(v_sg_list, g, d, l):
        return Taitel1980.h_transition(v_sg_list, g, d, l)
