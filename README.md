# SGM_Nexpy

### Change the filename and type in the scan numbers
xas = getMultiXAS(filename = test1, range_start = 0, range_end = 3)

### plot eem; change the name of intensity
eem(xas, "SDD1")

### define region of interest
xas.getpfy(roi_start = 60, roi_end = 80)

### plot summary figure; change the name of intensity
xas.summary_plot("I0")

### type in bad scan numbers between the brackets
ex: [2, 5, 9]
good_xas = get_good_scan(xas , [2])

### calculate (binning & average) and assign the processed dtaa to a new attribute
bin_xas = binned_xas(good_xas, start_energy = 1840, end_energy = 1880, bin_interval = 0.1

### show all of the processed data in a figure
plot_avg_xas_all(bin_xas)
