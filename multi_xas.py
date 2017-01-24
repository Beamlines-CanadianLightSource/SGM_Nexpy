import numpy as np
import matplotlib.pyplot as plt
from cStringIO import StringIO
import time
from nexpy.gui.plotview import NXPlotView
# from matplotlib.figure import Figure

def getMultiXAS(filename, range_start = None, range_end = None):


   if range_start == None:
      range_start = 0
   if range_end == None:
      range_end = len(filename.NXentry)
   if range_start != 0:
      range_start = range_start - 1

   multi_xas = MultiXAS()

   multi_xas.scan_number = []
   multi_xas.energy = []
   multi_xas.tey = []
   multi_xas.diode = []
   multi_xas.i0 = []
   multi_xas.sdd1 = []
   multi_xas.sdd2 = []
   multi_xas.sdd3 = []
   multi_xas.sdd4 = []

   for i in range (range_start, range_end):
      command = filename.NXentry[i].command
      if str(command).split(" ")[0] == "cscan":
         multi_xas.scan_number.append(str(filename.NXentry[i]).split(":")[1])
         multi_xas.energy.append(filename.NXentry[i].instrument.monochromator.en)
         multi_xas.tey.append(np.array(filename.NXentry[i].instrument.absorbed_beam.tey_r))
         multi_xas.diode.append(np.array(filename.NXentry[i].instrument.absorbed_beam.pd1_r))
         multi_xas.i0.append(np.array(filename.NXentry[i].instrument.incoming_beam.io_r))
         multi_xas.sdd1.append(np.array(filename.NXentry[i].instrument.fluorescence.sdd1))
         multi_xas.sdd2.append(np.array(filename.NXentry[i].instrument.fluorescence.sdd2))
         multi_xas.sdd3.append(np.array(filename.NXentry[i].instrument.fluorescence.sdd3))
         multi_xas.sdd4.append(np.array(filename.NXentry[i].instrument.fluorescence.sdd4))

   return multi_xas


def getSingleXAS(filename, i):

   single_xas = SingleXAS()

   single_xas.energy=np.array(filename.NXentry[i].instrument.monochromator.en)
   single_xas.tey=np.array(filename.NXentry[i].instrument.absorbed_beam.tey_r)
   single_xas.diode=np.array(filename.NXentry[i].instrument.absorbed_beam.pd1_r)
   single_xas.i0 = np.array(filename.NXentry[i].instrument.incoming_beam.io_r)
   single_xas.sdd1 = np.array(filename.NXentry[i].instrument.fluorescence.sdd1)
   single_xas.sdd2 = np.array(filename.NXentry[i].instrument.fluorescence.sdd2)
   single_xas.sdd3 = np.array(filename.NXentry[i].instrument.fluorescence.sdd3)
   single_xas.sdd4 = np.array(filename.NXentry[i].instrument.fluorescence.sdd4)

   return single_xas


class XAS(object):
   def __init__(self):
      self.energy = None
      self.i0 = None
      self.tey = None
      self.diode = None
      self.sdd1 = None
      self.sdd2 = None
      self.sdd3 = None
      self.sdd4 = None
      self.pfy_sdd1 = None
      self.pfy_sdd2 = None
      self.pfy_sdd3 = None
      self.pfy_sdd4 = None

class MultiXAS(XAS):
   def __init__(self):
      XAS.__init__(self)
      self.scan_number = None

   def getpfy(self, roi_start, roi_end):
      self.pfy_sdd1 = [[] for i in range(len(self.sdd1) )]
      self.pfy_sdd2 = [[] for i in range(len(self.sdd2) )]
      self.pfy_sdd3 = [[] for i in range(len(self.sdd3) )]
      self.pfy_sdd4 = [[] for i in range(len(self.sdd4) )]

      for i in range(0, len(self.sdd1)):
         for j in range (len(self.sdd1[i])):
            self.pfy_sdd1[i].append(np.sum(self.sdd1[i][j][roi_start:roi_end]))
            self.pfy_sdd2[i].append(np.sum(self.sdd2[i][j][roi_start:roi_end]))
            self.pfy_sdd3[i].append(np.sum(self.sdd3[i][j][roi_start:roi_end]))
            self.pfy_sdd4[i].append(np.sum(self.sdd4[i][j][roi_start:roi_end]))

   def summary_plot(self, name):
    start_time = time.time()
    # matplotlib.rcParams['figure.figsize'] = (13, 10)

    name = name.upper()
    if name == "TEY":
        intensity = self.tey
    elif name == "I0" or name == "IO":
        intensity = self.i0
    elif name == "DIODE" or name == "PD1":
        intensity = self.diode
    elif name == "PFY_SDD1":
        intensity = self.pfy_sdd1
    elif name == "PFY_SDD2":
        intensity = self.pfy_sdd2
    elif name == "PFY_SDD3":
        intensity = self.pfy_sdd3
    elif name == "PFY_SDD4":
        intensity = self.pfy_sdd4
    else:
        return "Invalid name for the intensity of summary plot"

    total_cscan_num = len(self.energy)
    # print (total_cscan_num)

    # show the plot in Nexpy, similar to figure.show()
    plotview = NXPlotView()

    # setup the size of figure
    plotview.setMinimumHeight(200)
    if total_cscan_num > 10:
        ratio = total_cscan_num / 10
    else:
        ratio = 1
    plotview.resize(700, 280*ratio)
    plotview.figure.clf()

    # setup axis
    ax = plotview.figure.gca()
    ax.axes.get_xaxis().set_visible(True)
    ax.axes.get_yaxis().set_visible(True)
    
    print ("--- %s seconds ---" % (time.time() - start_time))

    energy_tuple = np.array(self.energy[0][:])
    intensity_tuple = np.array(intensity[0][:])
    scan_num_tuple = np.zeros(len(self.energy[0]))
    scan_num_tuple.fill(1)

    for i in range(1, total_cscan_num):
        scan_num_list = np.zeros(len(self.energy[i]))
        scan_num_list.fill(i + 1)
        scan_num_tuple = np.concatenate([scan_num_tuple, scan_num_list])
        energy_tuple = np.concatenate([energy_tuple, np.array(self.energy[i][:])])
        intensity_tuple = np.concatenate([intensity_tuple, np.array(intensity[i][:])])
        #plt.scatter(self.energy[i][:], scan_num_list, c=intensity[i][:], s=140, linewidths=0, marker='s')

    # print("--- %s seconds ---" % (time.time() - start_time))
    ax.scatter(energy_tuple, scan_num_tuple, c=intensity_tuple, s=140, linewidths=0, marker='s')
    # add title of the figure
    ax.set_title("Summary Plot (Intensity: %s)" % (name))
    # add labels for x and y axis
    ax.set_xlabel('Incident Energy(eV)')
    ax.set_ylabel('Scan Index (Scan Number)')
    ax.set_ylim(ymin=0, ymax= total_cscan_num + 1)

    plotview.grid(True)
    plotview.draw()
    print("--- %s seconds ---" % (time.time() - start_time))


class SingleXAS(XAS):
   def __init__(self):
      XAS.__init__(self)
      self.scan_number = None


def eem(multi_xas, name, scan_num=None):
    start_time = time.time()

    # matplotlib.rcParams['figure.figsize'] = (14, 10)

    if scan_num == None:
      scan_num = 0

    name = name.upper()
    if name == "SDD1":
      intensity = multi_xas.sdd1[scan_num]
      # intensity = np.array(intensity)
    elif name == "SDD2":
      intensity = multi_xas.sdd2[scan_num]
      # intensity = np.array(intensity)
    elif name == "SDD3":
      intensity = multi_xas.sdd3[scan_num]
      # intensity = np.array(intensity)
    elif name == "SDD4":
      intensity = multi_xas.sdd4[scan_num]
      # intensity = np.array(intensity)
    else:
        return "Invalid name for the intensity of EEM"

    energy_array = np.array(multi_xas.energy[scan_num])
    num_of_points = len(energy_array)
    num_of_emission_bins = len(intensity[0])

    bin_num_for_x = np.zeros(shape=(num_of_points, num_of_emission_bins))
    for i in range(num_of_points):
      bin_num_for_x[i].fill(energy_array[i])

    bin_num_for_y = np.zeros(shape=(num_of_points, num_of_emission_bins))
    bin_num_for_y[0:] = np.arange(10, (num_of_emission_bins + 1) * 10, 10)

    v_max = max(intensity[0])
    for i in range(1, num_of_points):
      temp_max = max(intensity[i])
      if temp_max > v_max:
         v_max = temp_max
    # print ("v_max: ", v_max)

    intensity = np.array(intensity)
    plotview = NXPlotView()
    plotview.figure.clf()
    ax = plotview.figure.gca()
    ax.axes.get_xaxis().set_visible(True)
    ax.axes.get_yaxis().set_visible(True)
    # print("--- %s seconds ---" % (time.time() - start_time))
    ax.scatter(bin_num_for_x, bin_num_for_y, c=intensity, s=7, linewidths=0, vmax=v_max, vmin=0)
    print("--- %s seconds ---" % (time.time() - start_time))
    ax.set_xlabel('Incident Energy (eV)')
    ax.set_ylabel('Emission Energy (eV)')
    ax.set_title("Excitation Emission Matrix")
    plotview.grid()
    plotview.draw()
    print("--- %s seconds ---" % (time.time() - start_time))

def get_good_scan(multi_xas, ban_scan_list):
    scan_num_list = multi_xas.scan_number
    length = len(scan_num_list)
    # good_scan_list = []
    good_scan_index = range(0, length, 1)
    good_scan_list = multi_xas.scan_number[:]
    for i in range (length):
        for j in range(len(ban_scan_list)):
            # print ("i: " + str(i))
            # print ("j: " + str(j))
            if scan_num_list[i] == 'entry'+ str(ban_scan_list[j]):
                good_scan_list.remove('entry'+ str(ban_scan_list[j]))
                good_scan_index.remove(i)
    print (good_scan_list)
    print (good_scan_index)
    return get_good_scan_data(multi_xas, good_scan_index, good_scan_list)

def get_good_scan_data(multi_xas, good_scan_index, good_scan_list):

    good_xas = MultiXAS()

    good_xas.scan_number = []
    good_xas.energy = []
    good_xas.tey = []
    good_xas.diode = []
    good_xas.i0 = []
    good_xas.sdd1 = []
    good_xas.sdd2 = []
    good_xas.sdd3 = []
    good_xas.sdd4 = []
    good_xas.pfy_sdd1 = []
    good_xas.pfy_sdd2 = []
    good_xas.pfy_sdd3 = []
    good_xas.pfy_sdd4 = []

    # get all good scan data from original data

    good_xas.scan_number = good_scan_list[:]
    for i in range(0, len(good_scan_index)):
        good_xas.energy.append(np.array(multi_xas.energy[good_scan_index[i]]))
        good_xas.tey.append(np.array(multi_xas.tey[good_scan_index[i]]))
        good_xas.i0.append (np.array(multi_xas.i0[good_scan_index[i]]))
        good_xas.diode.append(np.array(multi_xas.tey[good_scan_index[i]]))
        good_xas.pfy_sdd1.append(np.array(multi_xas.pfy_sdd1[good_scan_index[i]]))
        good_xas.pfy_sdd2.append(np.array(multi_xas.pfy_sdd2[good_scan_index[i]]))
        good_xas.pfy_sdd3.append(np.array(multi_xas.pfy_sdd3[good_scan_index[i]]))
        good_xas.pfy_sdd4.append(np.array(multi_xas.pfy_sdd4[good_scan_index[i]]))

    return good_xas


def binned_xas (xas, start_energy, end_energy, bin_interval):
    edges_array, mean_energy_array, num_of_bins = create_bins(start_energy, end_energy, bin_interval)
    return assign_calculate_data(xas, mean_energy_array, edges_array, num_of_bins)


def create_bins(start_energy, end_energy, bin_interval):
    start_energy = int(start_energy + 1) 
    end_energy = int(end_energy - 1)
    print ("Start creating bins")
    num_of_bins = int ((end_energy-start_energy) / bin_interval)
    print num_of_bins
    num_of_edges = num_of_bins + 1
    # print ("Number of Bins:", num_of_bins)
    # print ("Number of Edges:", num_of_edges)
    print ("Energy range is: ", start_energy, "-", end_energy)
    edges_array = np.linspace(start_energy, end_energy, num_of_edges)

    # generate mean of bins
    mean_energy_array = []
    first_mean = (edges_array[1] + edges_array[0]) / 2
    bin_width = bin_interval
    for i in range(0, num_of_bins):
        mean_energy_array.append(first_mean + bin_width * i)
    mean_energy_array = np.array(mean_energy_array)
    # print ("Mean of energy bins: ", mean_energy_array)
    print ("created bins completed.\n")
    return edges_array, mean_energy_array, num_of_bins


def assign_calculate_data(xas, mean_energy_array, edges_array, num_of_bins):

    start_time = time.time()
    energy_array = xas.energy
    # Initial 3 arrays for each scaler
    tey_bin_array = np.zeros(num_of_bins)
    i0_bin_array = np.zeros(num_of_bins)
    diode_bin_array = np.zeros(num_of_bins)
    pfy_sdd1_bin_array = np.zeros(num_of_bins)
    pfy_sdd2_bin_array = np.zeros(num_of_bins)
    pfy_sdd3_bin_array = np.zeros(num_of_bins)
    pfy_sdd4_bin_array = np.zeros(num_of_bins)

    tey_array = np.array(xas.tey)
    i0_array = np.array(xas.i0)
    diode_array = np.array(xas.diode)

    pfy_sdd1_array = np.array(xas.pfy_sdd1)
    pfy_sdd2_array = np.array(xas.pfy_sdd2)
    pfy_sdd3_array = np.array(xas.pfy_sdd3)
    pfy_sdd4_array = np.array(xas.pfy_sdd4)

    bin_array = [[] for i in range(num_of_bins)]
    bin_width = (edges_array[-1] - edges_array[0]) / num_of_bins
    # print ("The width of a bin is:", bin_width)

    # interation to assign data into bins
    print ("Start assigning data points into bins")
    len_energy_array = len(energy_array)
    print len_energy_array
    print("--- %s seconds ---" % (time.time() - start_time))
    for scan_index in range(0, len_energy_array):
        len_sub_energy_array = len(energy_array[scan_index])
        for datapoint_index in range(0, len_sub_energy_array):
            if energy_array[scan_index][datapoint_index] <= edges_array[-1]:
                x = energy_array[scan_index][datapoint_index] - edges_array[0]
                # get integer part and plus 1
                assign_bin_num = int(x / bin_width) + 1
                #print (assign_bin_num)
                bin_array[assign_bin_num - 1].append([scan_index, datapoint_index])

                # calculate the sum of scaler
                tey_bin_array[assign_bin_num - 1] = tey_bin_array[assign_bin_num - 1] + tey_array[scan_index][datapoint_index]
                i0_bin_array[assign_bin_num - 1] = i0_bin_array[assign_bin_num - 1] + i0_array[scan_index][datapoint_index]
                diode_bin_array[assign_bin_num - 1] = diode_bin_array[assign_bin_num - 1] + diode_array[scan_index][datapoint_index]

                # calculate the sum of pfy sdd
                pfy_sdd1_bin_array[assign_bin_num - 1] = pfy_sdd1_bin_array[assign_bin_num - 1] + pfy_sdd1_array[scan_index][datapoint_index]
                pfy_sdd2_bin_array[assign_bin_num - 1] = pfy_sdd2_bin_array[assign_bin_num - 1] + pfy_sdd2_array[scan_index][datapoint_index]
                pfy_sdd3_bin_array[assign_bin_num - 1] = pfy_sdd3_bin_array[assign_bin_num - 1] + pfy_sdd3_array[scan_index][datapoint_index]
                pfy_sdd4_bin_array[assign_bin_num - 1] = pfy_sdd4_bin_array[assign_bin_num - 1] + pfy_sdd4_array[scan_index][datapoint_index]

    print("--- %s seconds ---" % (time.time() - start_time))

    # Calculate average
    empty_bins = 0
    for index in range(0, num_of_bins):
        # get the total number of data points in a particular bin
        total_data_point = len(bin_array[index])

        # print ("Bin No.", index+1, "; it contains ", total_data_point, "data points")

        if total_data_point == 0:
            empty_bins = empty_bins + 1
            print ("No data point is in Bin No."+ str(index + 1) + ". Average calculation is not necessary")
        else:

            tey_bin_array[index] = tey_bin_array[index] / total_data_point
            i0_bin_array[index] = i0_bin_array[index] / total_data_point
            diode_bin_array[index] = diode_bin_array[index] / total_data_point
            pfy_sdd1_bin_array[index] = pfy_sdd1_bin_array[index] / total_data_point
            pfy_sdd2_bin_array[index] = pfy_sdd2_bin_array[index] / total_data_point
            pfy_sdd3_bin_array[index] = pfy_sdd3_bin_array[index] / total_data_point
            pfy_sdd4_bin_array[index] = pfy_sdd4_bin_array[index] / total_data_point

    # remove empty bins in the front or at the end using slice indices
    if empty_bins != 0:
        index = 0
        while pfy_sdd1_bin_array[index].any() == 0:
            index = index + 1
        empty_bin_front = index
        empty_bin_back = empty_bins - empty_bin_front
        last_non_empty_bin = num_of_bins - empty_bin_back
        # if there are empty bins in the front
        if empty_bin_front != 0 and empty_bin_back == 0:
            bin_xas = MultiXAS()
            bin_xas.energy = mean_energy_array[empty_bin_front:]
            bin_xas.tey = tey_bin_array[empty_bin_front:]
            bin_xas.i0 = i0_bin_array[empty_bin_front:]
            bin_xas.diode = diode_bin_array[empty_bin_front:]
            bin_xas.pfy_sdd1 = pfy_sdd1_bin_array[empty_bin_front:]
            bin_xas.pfy_sdd2 = pfy_sdd2_bin_array[empty_bin_front:]
            bin_xas.pfy_sdd3 = pfy_sdd3_bin_array[empty_bin_front:]
            bin_xas.pfy_sdd4 = pfy_sdd4_bin_array[empty_bin_front:]
        # if there are empty bins in the back
        elif empty_bin_front == 0 and empty_bin_back != 0:
            bin_xas = MultiXAS()
            bin_xas.energy = mean_energy_array[:-empty_bin_back]
            bin_xas.tey = tey_bin_array[:-empty_bin_back]
            bin_xas.i0 = i0_bin_array[:-empty_bin_back]
            bin_xas.diode = diode_bin_array[:-empty_bin_back]
            bin_xas.pfy_sdd1 = pfy_sdd1_bin_array[:-empty_bin_back]
            bin_xas.pfy_sdd2 = pfy_sdd2_bin_array[:-empty_bin_back]
            bin_xas.pfy_sdd3 = pfy_sdd3_bin_array[:-empty_bin_back]
            bin_xas.pfy_sdd4 = pfy_sdd4_bin_array[:-empty_bin_back]
        # if there are empty bin in the front and back
        else:
            bin_xas = MultiXAS()
            bin_xas.energy = mean_energy_array[empty_bin_front:last_non_empty_bin]
            bin_xas.tey = tey_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.i0 = i0_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.diode = diode_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.pfy_sdd1 = pfy_sdd1_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.pfy_sdd2 = pfy_sdd2_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.pfy_sdd3 = pfy_sdd3_bin_array[empty_bin_front:last_non_empty_bin]
            bin_xas.pfy_sdd4 = pfy_sdd4_bin_array[empty_bin_front:last_non_empty_bin]
    # if there is no empty bins
    else:
        bin_xas = MultiXAS()
        bin_xas.energy = mean_energy_array
        bin_xas.tey = tey_bin_array
        bin_xas.i0 = i0_bin_array
        bin_xas.diode = diode_bin_array
        bin_xas.pfy_sdd1 = pfy_sdd1_bin_array
        bin_xas.pfy_sdd2 = pfy_sdd2_bin_array
        bin_xas.pfy_sdd3 = pfy_sdd3_bin_array
        bin_xas.pfy_sdd4 = pfy_sdd4_bin_array

    print ("Assign and calculate data points completed\n")
    print ("--- %s seconds ---" % (time.time() - start_time))
    return bin_xas


def plot_avg_xas_all(bin_xas):
    """
    Generate all plots (matplotlib figures) for averaged data at once
    :return: None
    """
    print ("Plotting average XAS.")
    # matplotlib.rcParams['figure.figsize'] = (14, 22)

    plotview = NXPlotView()

    plotview.setMinimumHeight(200)
    plotview.resize(1400, 800)
    plotview.figure.clf()

    en = bin_xas.energy
    i0 = bin_xas.i0
    tey  = bin_xas.tey
    diode = bin_xas.diode
    pfy_sdd1 = bin_xas.pfy_sdd1
    pfy_sdd2 = bin_xas.pfy_sdd2
    pfy_sdd3 = bin_xas.pfy_sdd3
    pfy_sdd4 = bin_xas.pfy_sdd4

    plt.subplot(2, 4, 1)
    plt.plot(en, tey)
    # add lable for x and y axis
    plt.xlabel('Energy (eV)')
    plt.ylabel('TEY')
    # add title of the figure
    plt.title('Binned(Averaged) TEY')

    plt.subplot(2, 4, 2)
    plt.plot(en, i0)
    plt.xlabel('Energy (eV)')
    plt.ylabel('I0')
    plt.title('Binned(Averaged) I0')

    plt.subplot(2, 4, 3)
    plt.plot(en, diode)
    plt.xlabel('Energy (eV)')
    plt.ylabel('Diode')
    plt.title('Binned(Averaged) Diode')

    plt.subplot(2, 4, 5)
    plt.plot(en, pfy_sdd1)
    plt.xlabel('Energy (eV)')
    plt.ylabel('PFY_SDD1')
    plt.title('Binned(Averaged) PFY_SDD1')

    plt.subplot(2, 4, 6)
    plt.plot(en, pfy_sdd2)
    plt.xlabel('Energy (eV)')
    plt.ylabel('PFY_SDD2')
    plt.title('Binned(Averaged) PFY_SDD2')

    plt.subplot(2, 4, 7)
    plt.plot(en, pfy_sdd3)
    plt.xlabel('Energy (eV)')
    plt.ylabel('PFY_SDD3')
    plt.title('Binned(Averaged) PFY_SDD3')

    plt.subplot(2, 4, 8)
    plt.plot(en, pfy_sdd4)
    plt.xlabel('Energy (eV)')
    plt.ylabel('PFY_SDD4')
    plt.title('Binned(Averaged) PFY_SDD4')

    plt.tight_layout()
    plotview.figure = plt
    plotview.tab_widget.removeTab(0)
    plotview.tab_widget.removeTab(1)
    plotview.draw()


def plot_avg_xas_single(bin_xas, detector):

    plotview = NXPlotView()

    if detector == "I0":
        y_array = bin_xas.i0
    elif detector == "TEY":
        y_array = bin_xas.tey
    elif detector == "DIODE" or detector == "PD1":
        y_array = bin_xas.diode
    elif detector == "PFY_SDD1":
        y_array = bin_xas.pfy_sdd1
    elif detector == "PFY_SDD2":
        y_array = bin_xas.pfy_sdd2
    elif detector == "PFY_SDD3":
        y_array = bin_xas.pfy_sdd3
    elif detector == "PFY_SDD4":
        y_array = bin_xas.pfy_sdd4
    else:
        return "Invalid dividend name"

    plotview.figure.clf()
    ax = plotview.figure.gca()
    ax.axes.get_xaxis().set_visible(True)
    ax.axes.get_yaxis().set_visible(True)

    ax.plot(bin_xas.energy, y_array)
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel(detector)
    plotview.draw()


def plot_normalized(xas, dividend, divisor):

    plotview = NXPlotView()

    # convert the string to uppercase
    dividend = dividend.upper()
    divisor = divisor.upper()

    if dividend == "I0":
        dividend_array = xas.i0
    elif dividend == "TEY":
        dividend_array = xas.tey
    elif dividend == "DIODE" or dividend == "PD1":
        dividend_array = xas.diode
    elif dividend == "PFY_SDD1":
        dividend_array = xas.pfy_sdd1
    elif dividend == "PFY_SDD2":
        dividend_array = xas.pfy_sdd2
    elif dividend == "PFY_SDD3":
        dividend_array = xas.pfy_sdd3
    elif dividend == "PFY_SDD4":
        dividend_array = xas.pfy_sdd4
    else:
        return "Invalid dividend name"

    if divisor == "I0":
        divisor_array = xas.i0
    elif divisor == "TEY":
        divisor_array = xas.tey
    elif divisor == "DIODE" or divisor == "PD1":
        divisor_array = xas.diode
    elif divisor == "PFY_SDD1":
        divisor_array = xas.pfy_sdd1
    elif divisor == "PFY_SDD2":
        divisor_array = xas.pfy_sdd2
    elif divisor == "PFY_SDD3":
        divisor_array = xas.pfy_sdd3
    elif divisor == "PFY_SDD4":
        divisor_array = xas.pfy_sdd4
    else:
        return "Invalid divisor name"

    normalized_array = np.array(dividend_array) / np.array(divisor_array)
    # plt.figure()
    # plt.plot(xas.energy, normalized_array)
    # str_y_axis = StringIO()
    # str_y_axis.write(dividend + ' / ' + divisor)
    # plt.ylabel(str_y_axis.getvalue())
    # plt.title("Averaged %s / Averaged %s" % (dividend, divisor))

    plotview.figure.clf()
    ax = plotview.figure.gca()
    ax.axes.get_xaxis().set_visible(True)
    ax.axes.get_yaxis().set_visible(True)

    ax.plot(xas.energy, normalized_array)
    ax.set_xlabel('Energy (eV)')
    str_y_axis = StringIO()
    str_y_axis.write(dividend + ' / ' + divisor)
    ax.set_ylabel(str_y_axis.getvalue())
    ax.set_title("Averaged %s / Averaged %s" % (dividend, divisor))

    plotview.draw()

    return xas.energy, normalized_array


# def plot_normalized_carbon(dividend_xas, dividend, divisor_xas, divisor):
#
#     if dividend == "I0" or dividend == "IO":
#         dividend_array = dividend_xas.i0
#     elif dividend == "TEY":
#         dividend_array = dividend_xas.tey
#     elif dividend == "DIODE" or dividend == "PD1":
#         dividend_array = dividend_xas.diode
#     elif dividend == "PFY_SDD1":
#         dividend_array = dividend_xas.pfy_sdd1
#     elif dividend == "PFY_SDD2":
#         dividend_array = dividend_xas.pfy_sdd2
#     elif dividend == "PFY_SDD3":
#         dividend_array = dividend_xas.pfy_sdd3
#     elif dividend == "PFY_SDD4":
#         dividend_array = dividend_xas.pfy_sdd4
#     else:
#         return "Invalid dividend name"
#
#     if divisor == "I0" or divisor == "IO":
#         divisor_array = divisor_xas.i0
#     elif divisor == "TEY":
#         divisor_array = divisor_xas.tey
#     elif divisor == "DIODE" or divisor == "PD1":
#         divisor_array = divisor_xas.diode
#     elif divisor == "PFY_SDD1":
#         divisor_array = divisor_xas.pfy_sdd1
#     elif divisor == "PFY_SDD2":
#         divisor_array = divisor_xas.pfy_sdd2
#     elif divisor == "PFY_SDD3":
#         divisor_array = divisor_xas.pfy_sdd3
#     elif divisor == "PFY_SDD4":
#         divisor_array = divisor_xas.pfy_sdd4
#     else:
#         return "Invalid divisor name"
#
#     normalized_array = np.array(dividend_array / divisor_array)
#     plt.figure()
#     plt.plot(dividend_xas.energy, normalized_array)
#     plt.title("Averaged %s / Blank Averaged %s" % (dividend, divisor))
#     plt.show()
#
#     export_data = ExportData()
#     export_data.dividend = dividend
#     export_data.divisor = divisor
#     export_data.mean_energy_array = dividend_xas.energy
#     export_data.normalized_array = normalized_array
#     return export_data
