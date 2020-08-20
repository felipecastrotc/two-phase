from two_phase import TwoPhase
import pandas as pd

# Load your experimental data
df = pd.read_excel("table_exp_points.xlsx")

# Configure your experimental setup in SI units
tp = TwoPhase(d=0.0525, l=8.1, theta=90, gas="air", liquid="water")

# Set the liquid and gas superficial velocities
tp.v_sl = df["V_sl (m/s)"].values
tp.v_sg = df["V_sg (m/s)"].values

# Set the pressure and temperature
tp.P = df["PT-101 (kPa)"].values * 1e3 + 101.325 * 1e3
tp.T = df["TT-101 (C)"].values

# Get flow Pattern of each experimental point
ptt = tp.ptt.taitel1980(text=True)

# Get the elongated bubble velocity for each experimental point
v_tb = tp.eb_vel.ebmodels()
v_tb_nicklin = tp.eb_vel.nicklin1962()

# Get volumetric flow-rate
q_l = tp.Q_l
q_g = tp.Q_g

# Get experimental properties
P_0 = tp.P[0]  # Pressure
T_0 = tp.T[0]  # Temperature
q_g0 = tp.Q_g[0]  # Gas flow rate
v_sg0 = tp.v_sg[0]  # Gas superficial velocity
