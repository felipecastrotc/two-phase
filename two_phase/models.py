import numpy as np
from .utils import Constant as ct

class EBVelocity(object):
    
    def __init__(self):
        # Models
        self.ebvel_dict = {'nicklin1962': self.nicklin1962,
                              'bendiksen1984': self.bendiksen1984,
                              'theron1989': self.theron1989,
                              'petalasaziz2000': self.petalasaziz2000,
                              'dukler1985': self.dukler1985}

        self.ebvel_title = ['Nicklin (1962)',
                               'Bendiksen (1984)',
                               'Theron (1989)',
                               'Petalas and Aziz (2000)',
                               'Dukler (1985)']
        pass

    # ============ Models - Elongated bubble translational velocity =========

    #  The models implemented follows the paper by Rodrigues et al. 20017
    # A COMPARITIVE STUDY OF CLOSURE EQUATIONS FOR GAS - LIQUID SLUG FLOW

    @staticmethod
    def nicklin1962(v_sg, v_sl, d, g):
        # The following equation is the number 15 of Taitel et al. 1980
        # The model is basically given by
        # V_TB = C_0*v_m + C_1*sqrt(g*d)
        c_0 = 1.2
        c_1 = 0.351
        # Mixture superficial velocity
        v_m = v_sg + v_sl
        # Finally calculate the Taylor bubble velocity
        v_tb = c_0 * v_m + c_1 * np.sqrt(g * d)
        return v_tb

    @staticmethod
    def bendiksen1984(v_sg, v_sl, d, theta, g):
        # The model is basically given by
        # V_TB = C_0*v_m + C_1*sqrt(g*d)
        # Convert the angle to radians
        theta = np.deg2rad(theta)
        # Mixture velocity
        v_m = v_sg + v_sl
        # Froude number
        Fr_v = v_sl / np.sqrt(g * d)
        # Critical Froude number
        Fr_crit = 3.5
        # Get the c_0
        c_0 = (Fr_v >= Fr_crit) * 1.2
        c_0 += (Fr_v < Fr_crit) * (1.05 + 0.15 * np.power(np.sin(theta), 2))
        # Get the c_1
        c_1 = (Fr_v >= Fr_crit) * (0.35 * np.sin(theta))
        c_1 += (Fr_v < Fr_crit) * (0.54 * np.cos(theta) + 0.35 * np.sin(theta))
        # Finally calculate the Taylor bubble velocity
        v_tb = c_0 * v_m + c_1 * np.sqrt(g * d)
        return v_tb

    @staticmethod
    def theron1989(v_sg, v_sl, d, theta, g):
        # The model is basically given by
        # V_TB = C_0*v_m + C_1*sqrt(g*d)
        # Convert the angle to radians
        theta = np.deg2rad(theta)
        # Mixture velocity
        v_m = v_sg + v_sl
        # Froude number
        Fr_v = v_sl / np.sqrt(g * d)
        # Critical Froude number
        Fr_crit = 3.5
        # TT constant
        TT = 1 + (Fr_v / Fr_crit) * np.cos(theta)
        # C_0 constant
        c_0 = 1.3 - 0.23 / TT + 0.13 * np.power(np.sin(theta), 2)
        # C_1 constant
        c_1 = (-0.5 + 0.8 / TT) * np.cos(theta) + 0.35 * np.sin(theta)
        # Finally calculate the Taylor bubble velocity
        v_tb = c_0 * v_m + c_1 * np.sqrt(g * d)
        return v_tb

    @staticmethod
    def petalasaziz2000(v_sg, v_sl, rho_l, mu_l, d, theta, g):
        # The model is basically given by
        # V_TB = C_0*v_m
        theta = np.deg2rad(theta)  # Convert the angle to radians
        # Reynolds number
        Re_v = (rho_l * (v_sg + v_sl) * d) / mu_l
        # C_0 constant
        c_0 = (1.64 + 0.12 * np.sin(theta)) / (np.power(Re_v, 0.031))
        # Finally calculate the Taylor bubble velocity
        v_tb = c_0 * (v_sl + v_sg)
        return v_tb

    @staticmethod
    def dukler1985(v_sg, v_sl):
        # The model is basically given by
        # V_TB = C_0*v_m
        c_0 = 1.225
        # Finally calculate the Taylor bubble velocity
        v_tb = c_0 * (v_sl + v_sg)
        return v_tb

    pass


class Homogeneous(object):

    # ====================== Homogeneous model ==========================

    @staticmethod
    def gvf(v_sg, v_sl):
        return v_sg / (v_sg + v_sl)

    @staticmethod
    def Rem(v_sg, v_sl, rho_l, rho_g, mu_l, mu_g, d, gvf=None):
        K = ct.K
        # Calculate the liquid properties
        if not gvf:
            # Get the homogeneous GVF
            gvf = Homogeneous.gvf(v_sg, v_sl)
        # Mixture properties
        rho_m = ((1 - gvf) * rho_l + gvf * rho_g)
        mu_m = ((1 - gvf) * mu_l + gvf * mu_g)
        # Get the mixture velocity
        Re = (rho_m * (v_sg + v_sl) * d) / mu_m
        return Re

    pass
