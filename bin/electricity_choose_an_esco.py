"""
Generate dataset to help me find the best available ESCO power utility offering

Instructions in case I forget:
1) Navigate here, fill in your zip code.
    http://www.newyorkpowertochoose.com/ptc_choose.cfm
2) Copy and paste the table of providers and costs to a file named ./table.html
3) Run this script
"""
import seaborn as sns
import pandas as pd


def get_data(fp):
    f = open(fp)
    header = "ESCO,RateType,Rate,Green,MinTerm,CancellationFee".split(',')

    rows = []
    nextrow = []
    for line in f:
        if 'Rate History' in line:
            nextrow =  []
            nextrow.append(line.split("Rate History")[0])
        elif "Variable" or "Fixed" in line:
            nr = list(nextrow)
            l = line.strip().split()
            nr.append(l[0])
            nr.append(float(l[1]))
            nr.append("Green Offer checkmark image" in line)
            nr.append(int(l[l.index("Month(s)") - 1]))
            nr.append(('yes' == l[-1] and True) or ('no' != l[-1] and None))
            rows.append(nr)
        else:
            print("line unrecognized: %s" % line)
    df = pd.DataFrame(rows, columns=header)
    return df


def plot(df):
    sns.FacetGrid(df, row='RateType', col='Green')\
        .map_dataframe(lambda data, color: data['Rate'].plot(kind='density'))

    sns.plt.figure()
    df.groupby(['Green', 'RateType'])['Rate'].plot(
        kind='density', legend=True)


def main(fp):
    df = get_data(fp)
    print("\n\nBest Green, Variable Rate ESCOs")
    print(df[
        (df['Green'] == True) & (df['RateType'] == 'Variable')
    ].sort('Rate').head())
    print("\n\nBest Green, Fixed Rate ESCOs")
    print(df[
        (df['Green'] == True) & (df['RateType'] == 'Fixed')
    ].sort('Rate').head())

    plot(df)


if __name__ == '__main__':
    fp = raw_input("Please specify the path to your table.html: ")
    sns.plt.ion()
    main(fp)
    raw_input('hit enter to quit')
