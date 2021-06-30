from .models import Homogeneous


class Taitel1980(object):

    num2str = {
        0: "Single-phase",
        1: "Dispersed bubbles",
        2: "Bubbles",
        3: "Slug",
        4: "Churn",
        5: "Annular",
    }

    @staticmethod
    def classify(v_sg, v_sl, rho_g, rho_l, mu_g, mu_l, sigma, g, l, d, text=False):

        # Get homogeneous properties
        gvfh = Homogeneous.gvf(v_sg, v_sl)
        rho_m = Homogeneous.rho_m(gvfh, rho_g, rho_l)
        mu_m = Homogeneous.mu_m(gvfh, mu_g, mu_l)

        # Check the existence of a bubble flow
        chk_bubble = Taitel1980.check_bubble(rho_l, rho_g, sigma, d, g)
        # Bubble flow to Slug flow
        v_sl_e = Taitel1980.e_transition(v_sg, rho_l, rho_g, sigma, g)
        # Dispersed Bubble - transition
        f = Taitel1980.f_transition(v_sl, v_sg, rho_l, rho_g, rho_m, mu_m, sigma, d, g)
        # Churn to Dispersed Bubbles transition
        v_sl_g = Taitel1980.g_transition(v_sg)
        # Slug to Churn transition
        v_sl_h = Taitel1980.h_transition(v_sg, g, d, l)
        # Annular transition
        v_sg_j = Taitel1980.j_transition(rho_l, rho_g, sigma, g)

        # Conditions
        if v_sg > v_sg_j:
            # Annular
            ptt = 5
        elif (f >= 0) and (v_sl > v_sl_g):
            # Dispersed bubbles
            ptt = 1
        elif v_sl > v_sl_e:
            if chk_bubble:
                # Bubbles
                ptt = 2
            else:
                # Slug
                ptt = 3
        elif v_sl > v_sl_h:
            # Churn
            ptt = 4
        else:
            # Slug
            ptt = 3
        
        if text:
            return Taitel1980.num2str[ptt]
        else:
            return ptt

    @staticmethod
    def check_bubble(rho_l, rho_g, sigma, d, g):
        # Check existence of bubble flow - Equation 4.15 of Shoham 2006
        chk_bubble = (
            ((rho_l ** 2.0) * g * (d ** 2.0) / ((rho_l - rho_g) * sigma)) ** 0.25 - 4.36
        ) >= 0
        return chk_bubble

    @staticmethod
    def e_transition(v_sg, rho_l, rho_g, sigma, g):
        # Bubble-Slug - Equation 4.13 of Shoham 2006
        # when v_sg > v_sg_e -> Slug or Churn
        v_sl_e = v_sg * 3.0 - ( 1.15 * ((g * (rho_l - rho_g) * sigma / (rho_l ** 2.0)) ** 0.25)
        )
        return v_sl_e

    @staticmethod
    def f_transition(v_sl, v_sg, rho_l, rho_g, rho_m, mu_m, sigma, d, g):
        # Dispersed Bubble - transition F
        # when f >= 0 or v_sl_g > v_sl -> Dispersed bubble
        # Equation 4.23 of Shoham 2006
        v_m = v_sl + v_sg
        # Left hand side part 1
        f_l1 = (
            2
            * (((0.4 * sigma) / ((rho_l - rho_g) * g)) ** 0.5)
            * ((rho_l / sigma) ** 0.6)
        )
        # Left hand side part 2
        f_l2 = (((2 * 0.046) / d) * ((rho_m * d / mu_m) ** -0.2)) ** 0.4
        # Left hand side part 3
        f_l3 = v_m ** 1.12
        # Right hand side
        f_r = 0.725 + 4.15 * ((v_sg / v_m) ** 0.5)
        # Full equation
        return f_l1 * f_l2 * f_l3 - f_r

    @staticmethod
    def g_transition(v_sg):
        # Dispersed Bubble - transition G
        # Equation 4.24 of Shoham 2006
        return v_sg / 0.52 - v_sg

    @staticmethod
    def h_transition(v_sg, g, d, l):
        # Slug-Churn - Equation 4.31 of Shoham 2006
        # when v_sg > v_sg_h -> Churn flow
        v_sl_h = (l / (d * 40.6) - 0.22) * ((g * d) ** 0.5) - v_sg
        return v_sl_h

    @staticmethod
    def j_transition(rho_l, rho_g, sigma, g):
        # Annular
        # when v_sg > v_sg_j -> Annular
        return (3.1 * (sigma * g * (rho_l - rho_g)) ** 0.25) / (rho_g ** 0.5)

