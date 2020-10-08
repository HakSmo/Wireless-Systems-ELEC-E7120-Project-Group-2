import sys
import csv
import os

class CellMapperRow:
    def __init__(self, csv_row):
        self.latitude, self.longitude, self.altitude, self.mcc, self.mnc, self.lac, \
            self.cid, self.signal, self.type, self.subtype = csv_row[:10]
        self.arfcn = None
        self.psc_or_pci = None
        if len(csv_row) > 10:
            try:
                self.arfcn = csv_row[10]
                if len(csv_row) > 11:
                    self.psc_or_pci = csv_row[11]
            except ValueError:
                pass

def parse_signal_csv(filename):
    cellmapper_data = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            row_parsed = [float(row[0]), float(row[1]), int(row[2]), \
                int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]), \
                row[8], row[9]]
            if len(row) > 10:
                try:
                    row_parsed.append(int(row[10]))
                    if len(row) > 11:
                        row_parsed.append(int(row[11]))
                except ValueError:
                    pass
            cellmapper_data.append(CellMapperRow(row_parsed))

    return cellmapper_data

def get_rows_diff(row_one, row_two):
    return (row_one.latitude, row_one.longitude, row_two.latitude, row_two.longitude, \
        row_two.altitude - row_one.altitude, row_one.lac, row_two.lac, row_one.cid, row_two.cid, \
        row_two.signal - row_one.signal, row_one.type + "->" + row_two.type, \
        row_one.subtype + "->" +  row_two.subtype, str(row_one.arfcn) + "->" + str(row_two.arfcn))

def find_handovers(cellmapper_data, output_filename="out.csv"):
    output_file = open(output_filename, mode='w', newline='')
    csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    row_one = cellmapper_data[0]
    mnc = row_one.mnc
    for i in range(1, len(cellmapper_data)):
        row_two = cellmapper_data[i]

        # TODO add full multi MNC support (dual sim)
        # TODO automatically detect more insteresting facts
        if row_one.cid != row_two.cid and \
            (row_one.signal < -51 and row_two.signal < -51) and \
            (row_one.mnc == mnc and row_two.mnc == mnc):
            csv_writer.writerow(get_rows_diff(row_one, row_two))
        
        row_one = row_two

    output_file.close()
    print("{} genereted".format(output_filename))

if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_filename = os.path.basename(input_filename).split('.')[0] + '_handovers.csv'
    find_handovers(parse_signal_csv(input_filename), output_filename)