import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
from glob import glob

OUTPUT_DIR = '/Users/hannahrae/data/dan-theory/mcnpx_csv'
INPUT_FILE = '/Users/hannahrae/data/dan-theory/Catalog_full.txt'

class DiscreteSlider(Slider):
    """A matplotlib slider widget with discrete steps."""
    def __init__(self, *args, **kwargs):
        """Identical to Slider.__init__, except for the "increment" kwarg.
        "increment" specifies the step size that the slider will be discritized
        to."""
        self.inc = kwargs.pop('increment', 1.0)
        Slider.__init__(self, *args, **kwargs)

    def set_val(self, val):
        discrete_val = int(val / self.inc) * self.inc # this is the bug
        # We can't just call Slider.set_val(self, discrete_val), because this 
        # will prevent the slider from updating properly (it will get stuck at
        # the first step and not "slide"). Instead, we'll keep track of the
        # the continuous value as self.val and pass in the discrete value to
        # everything else.
        xy = self.poly.xy
        xy[2] = discrete_val, 1
        xy[3] = discrete_val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % discrete_val)
        if self.drawon: 
            self.ax.figure.canvas.draw()
        self.val = val
        if not self.eventson: 
            return
        for cid, func in self.observers.iteritems():
            func(discrete_val)

class Plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def plot(self, obj):
        self.obj = obj
        self.spec = plt.semilogx([x/100. for x in obj.t_bins], obj.spectrum())
        plt.title("DAN Thermal Neutron Count Spectrum with Variable Depth")
        plt.xlabel("time bin")
        plt.ylabel("thermal neutron counts (ctn-cetn)")
        plt.ylim(ymax=0.8)
        _vars = obj.get_variables()
        # add some space for sliders
        plt.subplots_adjust(bottom=0.05*(len(_vars)+2))
        self.sliders = []
        for i, var in enumerate(_vars):
            self.add_slider(i*0.03, var[0], var[1], var[2])
        plt.show()

    def add_slider(self, pos, name, min, max):
        # first parameter to axes() is [left, bottom, width, height]
        fmt = {'depth':'%1.0f', 'cl':'%1.4f', 'h2o_top':'%1.2f', 'h2o_bott':'%1.2f'}
        inc = {'depth':1.0, 'cl':0.0025, 'h2o_top':0.01, 'h2o_bott':0.01}
        ax = plt.axes([0.1, 0.02+pos, 0.8, 0.02], facecolor='lightgoldenrodyellow')
        slider = DiscreteSlider(ax=ax, 
                                label=name, 
                                valmin=min, 
                                valmax=max, 
                                valinit=getattr(self.obj, name), 
                                valfmt=fmt[name], 
                                increment=inc[name])
        self.sliders.append(slider)
        def update(val):
            setattr(self.obj, name, val)
            self.spec[0].set_ydata(self.obj.spectrum())
            print 'Cl: %f, H2Otop: %f, D_top: 1.8, H2Obott: %f, D_bott: 1.8, \
                   Depth: %f, Altitude: 80.0' % (getattr(self.obj, 'cl'), 
                                                 getattr(self.obj, 'h2o_top'), 
                                                 getattr(self.obj, 'h2o_bott'), 
                                                 getattr(self.obj, 'depth'))
            self.fig.canvas.draw_idle()
        slider.on_changed(update)


class DataLookup:
    def __init__(self):
        # Initial values on startup
        self.depth = 4.0
        self.cl = 0.0075
        self.h2o_top = 0.02
        self.d_top = 1.8 # doesn't vary
        self.h2o_bott = 0.03
        self.d_bott = 1.8 # doesn't vary
        self.alt = 80.0 # doesn't vary

        self.t_bins = [0.6989700043360189, 
                       1.0253058652647702, 
                       1.2278867046136734, 
                       1.380211241711606, 
                       1.503790683057181, 
                       1.61066016308988, 
                       1.7058637122839193, 
                       1.7916906490201179, 
                       1.8709888137605752, 
                       1.9464522650130731, 
                       2.0170333392987803, 
                       2.0863598306747484, 
                       2.1492191126553797, 
                       2.214843848047698, 
                       2.2764618041732443, 
                       2.3364597338485296, 
                       2.3961993470957363, 
                       2.45484486000851, 
                       2.5118833609788744, 
                       2.568201724066995, 
                       2.6242820958356683, 
                       2.6794278966121188, 
                       2.733999286538387, 
                       2.788168371141168, 
                       2.8419848045901137, 
                       2.8959747323590648, 
                       2.9489017609702137, 
                       3.0043213737826426, 
                       3.0530784434834195, 
                       3.1072099696478683, 
                       3.1583624920952498, 
                       3.2121876044039577, 
                       3.2624510897304293, 
                       3.315970345456918, 
                       3.367355921026019, 
                       3.419955748489758, 
                       3.4712917110589387, 
                       3.5224442335063197, 
                       3.575187844927661, 
                       3.6263403673750423, 
                       3.677606952720493, 
                       3.72916478969277, 
                       3.7810369386211318, 
                       3.832508912706236, 
                       3.8836614351536176, 
                       3.935003151453655, 
                       3.986323777050765, 
                       4.037426497940624, 
                       4.086359830674748, 
                       4.139879086401237, 
                       4.190331698170292, 
                       4.243038048686294, 
                       4.294466226161593, 
                       4.344392273685111, 
                       4.3979400086720375, 
                       4.447158031342219, 
                       4.498310553789601, 
                       4.549003262025788, 
                       4.600972895686748, 
                       4.652246341003323, 
                       4.703291378118661, 
                       4.754348335711019, 
                       4.8055008581584]

        # Make a dictionary for looking up input values by sim id
        input_lookup = {}
        inputs = np.genfromtxt(INPUT_FILE, skip_header=1)
        for row in inputs:
            input_lookup[row[0]] = row[1:]

        # Make another dictionary to look up spectrum by input
        # where input is a tuple (cl, h2o_top, h2o_bott, depth)
        self.spec_lookup = {}
        for out_file in glob(OUTPUT_DIR + '/*'):
            # grab just the id from the file name and convert to float
            out_id = float(out_file.split('/')[-1][:-4][4:])
            # get the input parameters and convert to tuple (from array)
            param_key = tuple(input_lookup[out_id])
            self.spec_lookup[param_key] = np.load(out_file)

    def spectrum(self):
        params = (self.cl, 
                  self.h2o_top, 
                  self.d_top, 
                  self.h2o_bott, 
                  self.d_bott, 
                  self.depth, 
                  self.alt)
        return (self.spec_lookup[params][:,3]-self.spec_lookup[params][:,1])[:-1]

    def get_variables(self):
        return [
            ('depth', 1.0, 30.0),
            ('cl', 0.0075, 0.02),
            ('h2o_top', 0.01, 0.03),
            ('h2o_bott', 0.01, 0.06)
        ]

k = Plotter()
k.plot(DataLookup())