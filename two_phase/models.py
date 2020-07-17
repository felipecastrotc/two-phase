import numpy as np

from .flow_utils import Properties as p


class EBVelocity(object):

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
    def Rem(rho_g, rho_l, mu_g, mu_l, d, v_sg=None, v_sl=None, v_m=None, gvf=None):
        # Check if it was passed the mixture velocity or it is possible
        # to calculate the mixture velocity.
        if not v_m:
            if not v_sl or not v_sg:
                txt = (
                    "Please pass the mixture velocity or the"
                    + " superficial velocities!"
                )
                raise ValueError(txt)
            else:
                v_m = v_sg + v_sl
        # Check if it was passed the GVF or it is possible to calculate it.
        if not gvf:
            if not v_sl or not v_sg:
                txt = (
                    "Please pass the GVF explicitly or pass the"
                    + "superficial velocities!"
                )
                raise ValueError(txt)
            else:
                # Get the homogeneous GVF
                gvf = Homogeneous.gvf(v_sg, v_sl)

        # Calculate mixture the properties
        rho_m = Homogeneous.rho_m(gvf, rho_g, rho_l)
        mu_m = Homogeneous.mu_m(gvf, mu_g, mu_l)
        # Get the mixture velocity
        return (rho_m * (v_m) * d) / mu_m

    @staticmethod
    def rho_m(gvf, rho_g, rho_l):
        # gvf [0, 1]
        return gvf * rho_g + (1 - gvf) * rho_l

    @staticmethod
    def mu_m(gvf, mu_g, mu_l):
        # gvf [0, 1]
        return gvf * mu_g + (1 - gvf) * mu_l

    @staticmethod
    def dp_g(rho_m, g, theta):
        return rho_m * g * np.sin(np.deg2rad(theta))

    @staticmethod
    def dp_f(f_f, rho_m, v_m, d):
        return (f_f * rho_m * (v_m) ** 2) / (2 * d)

    pass


class Pattern(object):

    taitel1980_ptt = {
        0: "Single-phase",
        1: "Dispersed bubbles",
        2: "Bubbles",
        3: "Slug",
        4: "Churn",
        5: "Annular",
    }

    @staticmethod
    def taitel1980(v_sg, v_sl, rho_g, rho_l, mu_l, sigma, g, l, d, text=False):
        # TODO: documentation and references

        if v_sg == 0:
            ptt = 0
        else:
            # Annular
            # when v_sg > v_sg_j -> Annular
            v_sg_j = (3.1 * (sigma * g * (rho_l - rho_g)) ** 0.25) / (rho_g ** 0.5)

            # Dispersed Bubble
            # when f >= 0 or v_sl_g > v_sl -> Dispersed bubble
            # Euqation 4.23 of Shoham 2006
            v_m = v_sl + v_sg
            f_l1 = (
                2
                * (((0.4 * sigma) / ((rho_l - rho_g) * g)) ** 0.5)
                * ((rho_l / sigma) ** 0.6)
            )
            f_l2 = ((((2 * 0.046) / d) * ((rho_l * d / mu_l) ** -0.2)) ** 0.4) * (
                v_m ** 1.12
            )
            f_r = 0.725 + 4.15 * ((v_sg / v_m) ** 0.5)
            f = f_l1 * f_l2 - f_r
            # Equation 4.24 of Shoham 2006
            v_sl_g = (v_sg - v_sg * 0.52) / 0.52

            # Bubble-Slug - Equation 4.13 of Shoham 2006
            # when v_sg > v_sg_e -> Slug or Churn
            v_sg_e = (
                v_sl + 1.15 * ((g * (rho_l - rho_g) * sigma / (rho_l ** 2.0)) ** 0.25)
            ) / 3.0
            # Check existence of bubble flow - Equation 4.15 of Shoham 2006
            chk_bubble = (
                ((rho_l ** 2.0) * g * (d ** 2.0) / ((rho_l - rho_g) * sigma)) ** 0.25
                - 4.36
            ) >= 0

            # Slug-Churn - Equation 4.31 of Shoham 2006
            # when v_sg > v_sg_h -> Churn flow
            v_sg_h = (l / (d * 40.6) - 0.22) * ((g * d) ** 0.5) - v_sl

            # Conditions
            if v_sg > v_sg_j:
                ptt = 5
            elif (f >= 0) and (v_sl > v_sl_g):
                ptt = 1
            elif v_sg < v_sg_e:
                if chk_bubble:
                    ptt = 2
                else:
                    ptt = 3
            elif (v_sg > v_sg_e) and (v_sg < v_sg_h):
                ptt = 3
            else:
                ptt = 4

        if text:
            return Pattern.taitel1980_ptt[ptt]
        else:
            return ptt

    pass


class Friction(object):
    @staticmethod
    def blasius_fanning(Re, lmt=2300):
        # Shoham 2006 - Pag. 19 -> "For all practical purposes, the
        # correlation covering the widest range of the Reynolds number
        #  is n = 0.2, C F = 0.046 for the Fanning friction factor, and
        #  C M = 0.184 for the Moody friction factor."
        if Re < lmt:
            f = 16 * Re ** (-1)
        else:
            f = 0.046 * Re ** (-0.2)

        return f

    @staticmethod
    def blasius_moody(Re, lmt=2300):
        # Shoham 2006 - Pag. 19 -> "For all practical purposes, the
        # correlation covering the widest range of the Reynolds number
        #  is n = 0.2, C F = 0.046 for the Fanning friction factor, and
        #  C M = 0.184 for the Moody friction factor."
        if Re < lmt:
            f = 64 * Re ** (-1)
        else:
            f = 0.184 * Re ** (-0.2)

        return f

    @staticmethod
    def moody(Re, e):
        return 0.0055 * (1 + (2e4 * e + 1e6 / Re) ** (1 / 3))

    @staticmethod
    def fanning_normalized(Re, lambda_l):
        # TODO: Check if it base 10 or natural
        # y = -np.log(lambda_L)
        # s = 1 + y/(1.281 - 0.478*y + 0.444*y ^ 2 -
        #             0.094*y ^ 3 - 0.00843*y ^ 4);
        # f = s*f_n;
        raise NotImplementedError

    @staticmethod
    def moody_normalized(Re, e, H_l, lambda_l):
        # TODO: Check the formulas
        # Caclulate the friction factor
        # f_n = 0.0055*(1 + ((2*1e4)*(e) + ((1e6)/Re))**(1/3))
        # y = lambda_l/(H_l ^ 2)
        # # the function s becomes unbounded in the interval 1 < y < 1.2. For this interval, s is calculated from
        # if y > 1 & y < 1.2:
        #     # TODO: Check if it base 10 or natural
        #     s = np.log(2.2*y - 1.2)
        # else:
        #     s = np.log(y)/(-0.0523 + 3.182*np.log(y) - 0.875 *
        #             (np.log(y)**2) + 0.01853*(np.log(y)**4))

        # f_ = np.exp(s)*f_n
        raise NotImplementedError

    pass
