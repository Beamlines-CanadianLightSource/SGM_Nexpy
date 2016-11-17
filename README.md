# SGM_Nexpy

### Retrieve XAS c-scans data from a file and assign these data to a new attribute
#### type in filename and range of scan numbers
xas = getMultiXAS(filename = test1, range_start = 0, range_end = 3)

### Plot excitation emission matrix of s specific scan; change the name of intensity
eem(xas, "SDD3")

### Define region of interest and get pfy sdd
xas.getpfy(roi_start = 60, roi_end = 80)

### Plot summary figure
#### Change the name of intensity
xas.summary_plot("PFY_SDD3")

### Remove bad scan data and assign good scan data to a new attribute
#### Type in bad scan numbers between the brackets ex: [2, 5, 9]
good_xas = get_good_scan(xas , [2])

### Calculate (binning & average) and assign the processed data to a new attribute
bin_xas = binned_xas(good_xas, start_energy = 1840, end_energy = 1880, bin_interval = 0.1

### Show all of the processed data in a figure
plot_avg_xas_all(bin_xas)

### Show division figure
plot_division(bin_xas, dividend = "PFY_SDD3", divisor = "I0")