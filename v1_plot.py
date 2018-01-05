
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from glob import glob
from Tkinter import *
from math import log10

output_dir = '/Users/hannahrae/data/dan-theory/mcnpx_csv'
input_file = '/Users/hannahrae/data/dan-theory/Catalog_full.txt'

### THIS IS WHERE I'M TRYING TO MAKE A SLIDER ###
# class Plotter:
#     def __init__(self):
#         self.fig, self.ax = plt.subplots()

#     def plot(self, obj):
#         self.obj = obj
#         self.l = plt.plot(obj.xvals/100,obj.series())
#         _vars = obj.get_variables()
#         plt.subplots_adjust(bottom=0.03*(len(_vars)+2))
#         self.sliders = []
#         for i,var in enumerate(_vars):
#             self.add_slider(i*0.03, var[0], var[1], var[2])
#         plt.show()

#     def add_slider(self, pos, name, min, max):
#         ax = plt.axes([0.1, 0.02+pos, 0.8, 0.02], axisbg='lightgoldenrodyellow')
#         slider = Slider(ax, name, min, max, valinit=getattr(self.obj, name))
#         self.sliders.append(slider)
#         def update(val):
#             setattr(self.obj, name, val)
#             self.l[0].set_ydata(self.obj.series())
#             self.fig.canvas.draw_idle()
#         slider.on_changed(update)

# class PlotFinder:
#     def __init__(self, param_to_vary='Depth', spec_lookup):
#         self.spec_lookup = spec_lookup
#         if param_to_vary == 'Depth':
#             self.cl = 0.0075
#             self.h2o_top = 0.01
#             self.d_top = 1.8
#             self.h2o_bott = 0.02
#             self.d_bott = 1.8
#             self.alt = 80.0
#             self.xvals = range(1, 11) + [12, 15, 20, 25, 30]

#     def series(self):
#         return self.amp*np.sin(2*np.pi*self.freq*self.t)

#     def get_variables(self):
#         return [
#             ('freq', 0.1, 10),
#             ('amp', 0.1, 1)
#         ]

def plot_spectra():
    plot_dir = '/Users/hannahrae/data/dan-theory/spectra_plots'
    for output in glob(output_dir + '/*'):
        plot_name = output.split('/')[-1][:-4] + '.png'
        print 'plotting', plot_name
        out_arr = np.load(output)
        fig = plt.figure()
        plt.semilogx(out_arr[:,0]/100, out_arr[:,3]-out_arr[:,1])
        plt.ylabel('thermal neutron counts (ctn-cetn)')
        plt.xlabel('time bin')
        fig.savefig(plot_dir + '/' + plot_name)

def plot_vary_h2o_bott(spec_lookup, 
                        cl=0.0075, 
                        d_top=1.8,
                        h2o_top=0.01,
                        d_bott=1.8,
                        depth=1.0, 
                        alt=80.0):

    h2o_vals = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for val in h2o_vals:
        z = val
        params = (cl, h2o_top, d_top, val, d_bott, depth, alt)
        xs = spec_lookup[params][:,0]/100
        xlog = [log10(x) for x in xs[:-1]] # last value is 0
        ax.plot(xlog, (spec_lookup[params][:,3]-spec_lookup[params][:,1])[:-1], z, 'b-')
        ax.set_xlabel('time bin (s)')
        ax.set_ylabel('thermal neutron counts (ctn-cetn)')
        ax.set_zlabel('h2o_bott (wt %)')
        
    plt.show()

def plot_vary_h2o_top(spec_lookup, 
                        cl=0.0075, 
                        d_top=1.8,
                        h2o_bott=0.04,
                        d_bott=1.8,
                        depth=1.0, 
                        alt=80.0):

    h2o_vals = [0.01, 0.02, 0.03]

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for val in h2o_vals:
        z = val
        params = (cl, val, d_top, h2o_bott, d_bott, depth, alt)
        xs = spec_lookup[params][:,0]/100
        xlog = [log10(x) for x in xs[:-1]] # last value is 0
        ax.plot(xlog, (spec_lookup[params][:,3]-spec_lookup[params][:,1])[:-1], z, 'b-')
        ax.set_xlabel('time bin (s)')
        ax.set_ylabel('thermal neutron counts (ctn-cetn)')
        ax.set_zlabel('h2o_top (wt %)')
        
    plt.show()

def plot_vary_depth(spec_lookup, 
                    cl=0.0075, 
                    h2o_top=0.01, 
                    d_top=1.8,
                    h2o_bott=0.02,
                    d_bott=1.8,
                    alt=80.0):

    depth_vals = range(1, 11) + [12, 15, 20, 25, 30] # Y

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for val in depth_vals:
        z = val
        params = (cl, h2o_top, d_top, h2o_bott, d_bott, val, alt)
        xs = spec_lookup[params][:,0]/100
        xlog = [log10(x) for x in xs[:-1]] # last value is 0
        ax.plot(xlog, (spec_lookup[params][:,3]-spec_lookup[params][:,1])[:-1], z, 'b-')
        ax.set_xlabel('time bin (s)')
        ax.set_ylabel('thermal neutron counts (ctn-cetn)')
        ax.set_zlabel('depth (m)')
        
    plt.show()

def main():
    # Make a dictionary for looking up input values by sim id
    input_lookup = {}
    inputs = np.genfromtxt(input_file, skip_header=1)
    for row in inputs:
        input_lookup[row[0]] = row[1:]

    # Make another dictionary to look up spectrum by input
    # where input is a tuple (cl, h2o_top, h2o_bott, depth)
    spec_lookup = {}
    for out_file in glob(output_dir + '/*'):
        # grab just the id from the file name and convert to float
        out_id = float(out_file.split('/')[-1][:-4][4:])
        # get the input parameters and convert to tuple (from array)
        param_key = tuple(input_lookup[out_id])
        spec_lookup[param_key] = np.load(out_file)
    
    plot_vary_depth(spec_lookup)
    #plot_vary_h2o_top(spec_lookup)
    #plot_vary_h2o_bott(spec_lookup)

if __name__ == '__main__':
    main()