import csv

class CellMapperRow:
    def __init__(self, csv_row):
        self.latitude, self.longitude, self.altitude, self.mcc, self.mnc, self.lac, \
            self.cid, self.signal, self.type, self.subtype = csv_row[:10]
        self.arfcn = None
        self.psc_or_pci = None
        if len(csv_row) > 10:
            self.arfcn = csv_row[10]
            if len(csv_row) > 11:
                self.psc_or_pci = csv_row[11]

def parse_signal_csv(filename):
    cellmapper_data = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            row_parsed = [float(row[0]), float(row[1]), int(row[2]), \
                int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]), \
                row[8], row[9]]
            if len(row) > 10:
                row_parsed.append(int(row[10]))
                if len(row) > 11:
                    row_parsed.append(int(row[11]))
            cellmapper_data.append(CellMapperRow(row_parsed))

    return cellmapper_data

def get_rows_diff(row_one, row_two):
    return (row_one.latitude, row_one.longitude, row_two.latitude, row_two.longitude, \
        row_two.altitude - row_one.altitude, row_one.lac, row_two.lac, row_one.cid, row_two.cid, \
        row_two.signal - row_one.signal, row_one.type + "->" + row_two.type, \
        row_one.subtype + "->" +  row_two.subtype, str(row_one.arfcn) + "->" + str(row_two.arfcn))

def find_handovers(cellmapper_data):
    # TODO smarter output file name
    output_file = open("out.csv", mode='w', newline='')
    csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    row_one = cellmapper_data[0]
    for i in range(1, len(cellmapper_data)):
        row_two = cellmapper_data[i]

        # TODO add multi MNC support (dual sim)
        # TODO prune data and recognize situation when data is bullshit (like extremely high RSSI)
        # TODO automatically detect more insteresting facts
        if row_one.cid != row_two.cid:
            csv_writer.writerow(get_rows_diff(row_one, row_two))
        
        row_one = row_two

    output_file.close()
    print("out.csv genereted")

if __name__ == "__main__":
    find_handovers( parse_signal_csv("../signal-2020-09-25_Thomas.csv") )