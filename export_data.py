import os


def export_xas (xas, filename, **kwargs):
    cwd = os.getcwd()
    export_file_path = filename
    print ("export to: " , export_file_path[0])

    with open(export_file_path[0], "w") as out_file:
        for key in kwargs:
            out_file.write("# %s : %s \n" % (key, kwargs[key]))
        out_file.write("# Energy\tTEY\tI0\tDiode\tPFY_SDD1\tPFY_SDD2\tPFY_SDD3\tPFY_SDD4\n")
        for i in range(0, len(xas.energy)):
            out_string = ""
            # print energy_array[i]
            out_string += str(xas.energy[i])
            out_string += "\t"
            out_string += str(xas.tey[i])
            out_string += "\t"
            out_string += str(xas.i0[i])
            out_string += "\t"
            out_string += str(xas.diode[i])
            out_string += "\t"
            out_string += str(xas.pfy_sdd1[i])
            out_string += "\t"
            out_string += str(xas.pfy_sdd2[i])
            out_string += "\t"
            out_string += str(xas.pfy_sdd3[i])
            out_string += "\t"
            out_string += str(xas.pfy_sdd4[i])
            out_string += "\n"
            out_file.write(out_string)

    print ("Export data complete")


def export_normalized_data(export_data, filename):
    cwd = os.getcwd()
    export_file_path = cwd+"/"+filename[0]+".xas"
    print ("export to: " + export_file_path)

    with open(export_file_path, "w") as out_file:
        out_file.write("# Beamline.file-content: Normalized " + export_data.dividend + "\n")
        string_table_header = "# " + export_data.dividend + "\t" + export_data.divisor + "\n"
        out_file.write(string_table_header)
        for i in range(0, len(export_data.mean_energy_array)):
            out_string = ""
            out_string += str(export_data.mean_energy_array[i])
            out_string += "\t"
            out_string += str(export_data.normalized_array[i])
            out_string += "\n"
            out_file.write(out_string)
    print ("Export data complete.")


class ExportData(object):
    def __init__(self):

        self.dividend = None
        self.divisor = None
        self.mean_energy_array = None
        self.normalized_array = None
