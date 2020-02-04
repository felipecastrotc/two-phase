import pandas as pd
import numpy as np
from two_phase import TwoPhase


df = pd.read_excel('table_exp_points.xlsx')

df['V_sl (m/s)']

tp = TwoPhase(d=0.0525, gas='air', liquid='water')

tp.v_sl = df['V_sl (m/s)']
tp.v_sg = df['V_sg (m/s)']


tp.g = 1
tp.g
tp.test.g


class mytest:
    name = "test1"
    tricks = list()

    def __init__(self, name):
        self.name = name
        self.tricks = [name]
        self.tricks.append(name)


t1 = mytest("hello world")
t2 = mytest("bye world")


print(t1.name, t2.name)
print(t1.tricks, t2.tricks)


class a(object):
    test = 1

    def test


class mytest:
    name = "test1"
    tricks = list()

    def __init__(self, name):
        self.name = name
        #self.tricks=[name]
        self.tricks.append(name)


t1 = mytest("hello world")
t2 = mytest("bye world")
print(t1.name, t2.name)
print(t1.tricks, t2.tricks)
