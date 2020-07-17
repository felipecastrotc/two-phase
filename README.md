# Two-phase flow

The `two-phase` flow is a Python library that implements two-phase flows models and make easy to get the flow properties such as flow pattern, elongated bubble velocity, homogenous model properties etc. This library is structured in a way that the user can program using a simple and easy-to-use objects or in a more advanced manner can use the functions of the library directly.

The fluid properties are by default automatically obtained from the [CoolProp](https://github.com/CoolProp/CoolProp). However, you can also pass your own functions, determined experimentally or from any source you want.

The library has also some basic plot utils for some flow pattern maps.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `two-phase` flow package.

```bash
pip install two-phase
```

## Usage

```python
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
```

## Roadmap

- [x] CoolProp integration
- [x] Homogeneous model
- [x] Elongated bubble models
- [x] Taitel 1980 - flow pattern map for vertical flows (being developed)
- [ ] Flow pattern map for horizontal flows
- [ ] Lockhart Martinelli model
- [ ] Alves Anular Flow model
- [ ] Taitel and Barnea model
- [ ] Drift model
- [ ] Beggs and Brill model
- [ ] Hagedorn Brown model
- [ ] Black oil model


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change or add.

When contributing, please use the [black](https://github.com/psf/black) code formatter as it formats the code to looks the  same regardless of the project you are reading.

Please make sure to update tests as appropriate.

## Credits

[@felipecastrotc](https://github.com/felipecastrotc/)

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)