import numpy as np
import pandas as pd
from astropy.table import Table

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Label, Slider, TextInput, Title, Text
from bokeh.plotting import figure, output_file, show

#read in budget data
default = Table.read('budget-tool/data/slow_ramp.txt', format='ascii')   
df0 = default.to_pandas()
df0['Checksum'] = df0['M1'] + df0['M2'] + df0['M3'] + df0['APD'] + df0['JWST'] + df0['WFIRST']
budget_source = ColumnDataSource(df0)
launch_source = ColumnDataSource(data = {'launch_years': [2042, 2053, 2061], \
    'y_values': [2000,2100,2200], 'color':['#0098FF','#61D836','#F8BA00']}) 
ops_source = ColumnDataSource(data = {'x':[[2042, 2052],[2053, 2063], [2061, 2071]], 
                                      'y':[[2000,2000],[2100,2100], [2200,2200] ], 
                                      'color': ['#0098FF','#61D836','#F8BA00']})
a_source = ColumnDataSource(data = {'x_label':[2040], 'y_label':[2500], 'x_year':[2056], 'y_year':[2500], 
            'label_text':['Years of Simultaneous Operation:'], 'year_text': ['0']})

p0 = figure(x_range=(2020, 2061), y_range=(0, 2800), plot_width=850, plot_height=400)
p0.grid.minor_grid_line_color = '#eeeeee'
p0.xaxis.axis_label = "Year"
p0.yaxis.axis_label = "Budget in Millions"
p0.varea_stack(stackers=['JWST', 'WFIRST', 'M1', 'M2', 'M3', 'APD'], x='Year', 
              color=['#CB297B', '#B51700', '#0098FF','#61D836','#F8BA00', '#DEDEDE'], 
              legend_label=['JWST', 'WFIRST', 'M1','M2','M3', 'APD'], 
              alpha=[ 1., 0.5, 1., 1., 1., 0.5], source=budget_source)
p0.legend.items.reverse()
p0.legend.label_text_font_size = "7pt"
p0.legend.location = "top_left"
p0.legend.orientation = "horizontal"
p0.text(x='x_label', y='y_label', text='label_text', source=a_source)  
p0.text(x='x_year', y='y_year', text='year_text', source=a_source)  
p0.inverted_triangle("launch_years", "y_values", source=launch_source, color="color", alpha=1.0, size=20) 
p0.multi_line("x", "y", color="color", source=ops_source, line_width=5, alpha=0.7) 

# Set up slide control widgets
afwslider = Slider(title="Flagship Wedge ($B)", value=0.6, start=0.5, end=2., step=0.1, width=320)
lifeslider = Slider(title="Mission Lifetimes (Yr)", value=10., start=5., end=30., step=1., width=320)
m1slider = Slider(title="Mission 1 ($B)", value=10.0, start=3.0, end=20.0, step=0.5, width=160)
m2slider = Slider(title="Mission 2 ($B)", value=6.0, start=3.0, end=20.0, step=0.5, width=160)
m3slider = Slider(title="Mission 3 ($B)", value=5.0, start=3.0, end=20.0, step=0.5, width=160)

def mission1_wedge(afw, m1):
    N1 = np.round((m1 - 0.6 * (afw-0.02)) / (afw-0.02)) 
    print()   
    print("M1 budget will run for N1 = ", N1,  " years")   
    df0.iloc[0:50, 1] = 0. 
    df0.iloc[1:7, 1] = (700. - (df0.iloc[1:7, 6] + df0.iloc[1:7, 7])) * 0.5  # M1 gets 1/2 of ($700M - JWST and WFIRST) 
    df0.iloc[7:int(7+N1), 1] = 1000. * afw - 20. 
    df0.iloc[int(7+N1), 1] = 0.3 * (1000. * afw - 20.) 

    print("Total Mission One Cost Right Now = ", df0.iloc[0:40, 1].sum())
    print("      Mission One Launch Year    = ", df0.iloc[int(7+N1), 0])
    print()   

    m1index = int(7+N1)
    budget_source.data = df0
    print("m1index = ", m1index)
    return m1index
     
def mission2_wedge(afw, m2, m1index):
    
    N2 = np.round((m2 - 0.6 * (afw-0.02)) / (afw-0.02)) 
    print()   
    print("M2 budget will run for N = ", N2,  " years, starting at ", df0.iloc[m1index,0], 'with m1index:', m1index)   
    df0.iloc[1:7, 2] = (700. - (df0.iloc[1:7, 6] + df0.iloc[1:7, 7])) * 0.3333333
    df0.iloc[2:m1index, 2] = 70. 
    df0.iloc[m1index, 2] = 1000. * afw - df0.iloc[m1index, 1] - 70.
    df0.iloc[m1index+1:int(m1index+N2), 2] = 1000. * afw - 20. 
    df0.iloc[int(m1index+N2), 2] = 0.3 * (1000. * afw - 20.) 
    df0.iloc[int(m1index+N2):50, 2] = 0. 


    print("Total Mission Two Cost Right Now = ", df0.iloc[0:40, 2].sum())
    print("      Mission Two Launch Year    = ", df0.iloc[int(m1index+N2), 0])
    print()   

    budget_source.data = df0
    return int(m1index+N2)

def mission3_wedge(afw, m3, m2index):
    
    print()   
    N3 = np.round((m3 - 0.6 * (afw-0.02)) / (afw-0.02)) 
    print("M3 budget will run for N3 = ", N3,  " years, starting at ", df0.iloc[m2index,0], 'with m2index:', m2index)   
    df0.iloc[1:7, 3] = (700. - (df0.iloc[1:7, 6] + df0.iloc[1:7, 7])) * 0.16666667
    df0.iloc[2:m2index, 3] = 50. 
    df0.iloc[m2index, 3] = 1000. * afw - df0.iloc[m2index, 2] - 70.
    df0.iloc[m2index+1:int(m2index+N3), 3] = 1000. * afw - 20. 
    df0.iloc[int(m2index+N3), 3] = 0.3 * (1000. * afw - 20.) 
    df0.iloc[int(m2index+N3):50, 3] = 0. 

    print("Total Mission Three Cost Right Now = ", df0.iloc[0:40, 3].sum())
    print("      Mission Three Launch Year    = ", df0.iloc[int(m2index+N3), 0])
    print()   

    budget_source.data = df0
    return int(m2index+N3)

def update_budget(attrname, old, new):    # master callback function 
    m1index = mission1_wedge(afwslider.value, m1slider.value)
    m2index = mission2_wedge(afwslider.value, m2slider.value, m1index)
    m3index = mission3_wedge(afwslider.value, m3slider.value, m2index)
    print(df0)
    launch_source.data['launch_years'] = [df0.iloc[int(m1index), 0], 
                                          df0.iloc[int(m2index), 0], 
                                          df0.iloc[int(m3index), 0]]
    df0['Total'] = df0['M1'] + df0['M2'] + df0['M3'] + df0['APD']
    ops_source.data['x'] = [[df0.iloc[int(m1index), 0], df0.iloc[int(m1index), 0]+lifeslider.value], [df0.iloc[int(m2index), 0], df0.iloc[int(m2index), 0]+lifeslider.value], [df0.iloc[int(m3index), 0], df0.iloc[int(m3index), 0]+lifeslider.value]]

    print("Mission 1 Last Year of Ops: ", df0.iloc[m1index, 0] + lifeslider.value) 
    print("Mission 3 Launch Year: ", df0.iloc[int(m3index), 0]) 
    years_of_joint_operations = int(np.max([df0.iloc[m1index, 0] + lifeslider.value - df0.iloc[int(m3index), 0], 0]) ) 
    print("Number of Years of Overlapping Operations: ", years_of_joint_operations) 
    a_source.data['year_text'] = [str(years_of_joint_operations)]

def update_lifetime(attrname, old, new):    # master callback function 
    ops_source.data['x'] = [[df0.iloc[int(m1index), 0], df0.iloc[int(m1index), 0]+lifeslider.value], [df0.iloc[int(m2index), 0], df0.iloc[int(m2index), 0]+lifeslider.value], [df0.iloc[int(m3index), 0], df0.iloc[int(m3index), 0]+lifeslider.value]]

m1index = mission1_wedge(afwslider.value, m1slider.value)
m2index = mission2_wedge(afwslider.value, m2slider.value, m1index)
m3index = mission3_wedge(afwslider.value, m3slider.value, m2index)

for e in [afwslider, m1slider, m2slider, m3slider, lifeslider]:
    e.on_change('value', update_budget)

# Set up layouts and add to document
mission_inputs = row(afwslider, lifeslider)
mission_budgets = row(m1slider, m2slider, m3slider)


curdoc().add_root(   column(mission_inputs, mission_budgets, p0)   )
curdoc().title = "Flagship Mission Affordability Calculator"
