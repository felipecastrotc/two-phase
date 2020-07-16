from two_phase import Properties as p
import pandas as pd
import numpy as np
from two_phase import TwoPhase


df = pd.read_excel("table_exp_points.xlsx")

df["V_sl (m/s)"]

tp = TwoPhase(d=0.0525, gas="air", liquid="water")

tp.v_sl = df["V_sl (m/s)"].values
tp.v_sg = df["V_sg (m/s)"].values

tp.P = df["PT-301 (kPa)"].values * 1e3 + 101.325 * 1e3
tp.T = df["TT-301 (ºC)"].values
