#SGM_Nexpy Plugin

### Plugin Installation
#### Extract the SGMPy.zip file into $HOME\.nexpy\plugins on windows, or ~/.nexpy for Unix machines.
#### Alternatively you can use the graphical install within NeXpy by going to `File->Install Plugin` in nexpy and selecting the extracted folder.  Select "Install Locally" if you do not want to, (or don't have permissions to) install the plugin system wide, and press OK. 

# SGM_Nexpy

### Retrieve XAS c-scans data from a file and assign these data to a new attribute
#### Type in filename and range of scan numbers
xas = getMultiXAS(filename = test, range_start = 0, range_end = 3)

### Plot excitation emission matrix of a specific scan
#### Change the name of intensity (SDD1, SDD2, SDD3, SDD4)
eem(xas, "SDD3")

### Define region of interest and get pfy_sdd
xas.getpfy(roi_start = 60, roi_end = 80)

### Plot summary figure
#### Change the name of intensity (I0, TEY, Diode, PFY_SDD1, PFY_SDD2, PFY_SDD3, PFY_SDD4)
xas.summary_plot("PFY_SDD3")

### Remove bad scan data and assign good scan data to a new attribute
#### Type in bad scan numbers between the brackets ex: [2, 5, 9]
good_xas = get_good_scan(xas , ban_scan_list = [])

### Calculate (binning & average) and assign the processed data to a new attribute
bin_xas = binned_xas(good_xas, start_energy = 1840, end_energy = 1880, bin_interval = 0.1)

### Show all of the processed data in a figure
#### Including I0, TEY, Diode, PFY_SDD1, PFY_SDD2, PFY_SDD3, PFY_SDD4
plot_avg_xas_all(bin_xas)

### Export binned and averaged data
export_xas(bin_xas, filename = "test")

### Show normalized(division) figure and pass normalized data to a new attribute
export_data = plot_normalized(bin_xas, dividend = "PFY_SDD3", divisor = "I0")

### Export normalized data
#### Save the processed data as plain text in the directory where people start their NeXpy
export_normalized_data(export_data, filename = "test")


