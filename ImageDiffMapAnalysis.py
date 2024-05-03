import os.path as opath
import chardet


def read_csv_file(path):
    with open(path, "rb") as f:
        datas = f.read()
    datas = datas.decode(encoding=chardet.detect(datas)['encoding'])
    datas = datas.replace("\r\n", "\n")
    if datas.endswith("\n"):
        datas = datas[:-1]
    datas = datas.split("\n")
    out = []
    for l in datas:
        if not l.startswith("#"):
            out.append(l.split(","))
    return out


class ImageDiffMapAnalysis:
    """
    analysis image map data
    file name: imagediffmap.csv
    eg:
    M1:
    ev101aa,ev101a,seton,Aa
    ev101ab,ev101a,seton,Ab:Aa
    ev101ac,ev101a,seton,Ac:Aa
    ev101ad,ev101a,seton,Ad:Aa
    ev101ae,ev101a,seton,Ae:Aa
    ev101af,ev101a,seton,Af:Aa
    ...
    or
    M2:
    EV101AA,EV101A,diff,AA
    EV101AB,EV101A,diff,AB
    EV101AC,EV101A,diff,AC
    EV101AD,EV101A,diff,AD
    EV101AE,EV101A,diff,AE
    EV101AF,EV101A,diff,AF
    EV101BA,EV101A,diff,BA
    EV101BB,EV101A,diff,BB
    EV101BC,EV101A,diff,BC
    EV101BD,EV101A,diff,BD
    EV101BE,EV101A,diff,BE
    EV101BF,EV101A,diff,BF
    EV101BG,EV101A,diff,BG
    EV101AG,EV101A,diff,AG
    EV101CA,EV101A,diff,CA
    EV101CB,EV101A,diff,CB
    EV101CC,EV101A,diff,CC
    EV101CD,EV101A,diff,CD
    EV101CE,EV101A,diff,CE
    EV101CF,EV101A,diff,CF
    EV101CG,EV101A,diff,CG

    EV102AA,EV102A,diff,AA
    EV102AB,EV102A,diff,AB
    EV102AC,EV102A,diff,AC
    EV102AD,EV102A,diff,AD
    EV102AE,EV102A,diff,AE
    EV102AF,EV102A,diff,AF
    EV102BA,EV102A,diff,BA
    EV102BB,EV102A,diff,BB
    EV102BC,EV102A,diff,BC
    EV102BD,EV102A,diff,BD
    EV102BE,EV102A,diff,BE
    EV102BF,EV102A,diff,BF
    """

    def __init__(self, path):
        self.csv_data = read_csv_file(path)
        self.method = self.detect_format()

    def data(self):
        if self.method == "M1":
            data = {}
            for current_data in self.csv_data:
                if data.get(current_data[1]) is None:
                    data[current_data[1]] = []
                if ":" in current_data[3]:
                    data[current_data[1]].append(
                        (current_data[0], current_data[3].split(":")[1], current_data[3].split(":")[0]))
                else:
                    data[current_data[1]].append((current_data[0], current_data[3], None))
            return data

    def detect_format(self):
        assert self.csv_data
        for i in self.csv_data:
            if len(i) == 4:
                if ":" in i[3]:
                    return "M1"
            elif len(i) == 0:
                return "M2"
        return "M3"
