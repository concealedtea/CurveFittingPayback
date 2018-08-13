import pyodbc
import sys, csv, os, json, math
import pandas as pd
from io import StringIO
from pandas import DataFrame
from pandas.tools.plotting import table
from scipy.stats import linregress
from numpy import *
from sympy import Eq, var, solve
from scipy.optimize import leastsq
from scipy.optimize import fsolve
from scipy.integrate import quad
from scipy.integrate import simps
from pylab import *
import pylab
import random
import itertools as IT
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import asciitable

pd.set_option('display.max_columns', None)
leftSide120 = 0
def exec_query(query_text,driver= "{ODBC Driver 13 for SQL Server};",server= "REMOVED",
               database= "REMOVED",UID= "REMOVED",PWD= "REMOVED",return_value= True):
    conn= pyodbc.connect(
        r'DRIVER='+driver+
        r'SERVER='+server+
        r'DATABASE='+database+
        r'UID='+UID+
        r'PWD='+PWD
        )
    return conn

def decaySolver120(x):
    return (np.log(15)*(x**119)) - (np.log(119)*(x**15)) - leftSide120

def main():
    query = ("""select
                	age,
                	imp,
                	SUM(revenue)/ NULLIF(SUM(uc_spend),0) as percentile
                from Reports.dbo.TemporaryData
                where
                    age Between 1 and 14
                	and uc_spend > 0
                	and imp = 'horoscope_microsite'
                	--and platform = 'Desktop'
                	--and platform = 'Mobile'
                GROUP BY
                	age,
                	imp
                ORDER BY
                	age""")
    msql_db = exec_query(query)
    df = pd.read_sql(query, msql_db)
    k = 0
    xdata = df.age.tolist()
    # df['percentile'] = df['percentile'].apply(lambda x: x)
    ydata = df.percentile.tolist()

    # Functions
    powerFit = lambda x, amp, index: amp * np.power(x,index)
    fitfunc = lambda p, x: p[0]*np.power(x,p[1])
    errfunc = lambda p, x, y: (y - fitfunc(p,x))
    pinit = [1,-1, 0.]
    out = leastsq(errfunc, pinit, args=(xdata, ydata), full_output=1)
    pfinal = out[0]
    covar = out[1]
    index = pfinal[1]
    amp = pfinal[0]

    #Plot the functions
    clf()
    subplot(1,1,1)
    # amp = 0.02657103828367992
    # index = -0.3644474196495383
    absolute = 0.0168315406923035
    amp = float(amp)
    index = float(index)
    plot(range(1,365), powerFit(range(1,365),amp,index)) # Fitting
    plot(xdata, ydata, 'k') #DATA
    xlabel('$age$')
    ylabel('$payback$')
    text(0,0,'$fit = %5.6fx^{%5.6f}$' % (amp, index), color = 'b')
    print('Best Fit Equation: ' + str(amp) +'x^' + str(index))
    print('On day 14 we will payback ' + str((simps(powerFit(range(1,15),amp,index)) + absolute) * 100) + '%')
    print('On day 120 we will payback ' + str((simps(powerFit(range(1,121),amp,index)) + absolute) * 100) + '%')
    print('On day 365 we will payback ' + str((simps(powerFit(range(1,366),amp,index)) + absolute) * 100) + '%')
    area = []
    for x in range(2,365):
        area.append(simps(powerFit(range(1,x + 1),amp,index)))
    for count in range(0,len(area)):
        if (area[count] > 1):
            print ('Based on the first 14 days, we will payback 100% on day ' + str(count))
            break
    # show()
    # averageDecay = (1 - simps(powerFit(range(1,14),amp,index))) / 106
    # # print('Average Decay Per Day starting day 15 till 120 is: ' + str(100 * averageDecay) + '%')
    print()
    print('In order to hit 100% Payback by day 120: ')
    leftSide120 = (1 - simps(powerFit(range(1,15), amp, index)) - absolute)/(amp * np.power(14,index))
    leftSide120 = leftSide120 * np.log(15) * np.log(119)
    print(solve(((np.log(15)*(x**119)) - (np.log(119)*(x**15)) - leftSide120), x))
    print('Starting on Day 14, we need to decay at: ' + str((1. - decaySum) * 100) + '%')
    print('In order to have a 35% net profit by day 365: ')
    decayRate = 0.35 ** (1./244.)
    print('Starting on Day 120, we need to decay at: ' + str(100 * decayRate) + '%')

if __name__ == '__main__':
    main()
    # input('Finished, program will now exit')
    os._exit(1)
