pip install sdmx

import pandas as pd
import sdmx

pd.set_option("display.float_format", "{:.4f}".format)


def table25():
    def exchange_rates():
        url = "https://www.federalreserve.gov/releases/g5/current/"
        table = pd.DataFrame(pd.read_html(url)[0])
        rates = table.iloc[0:23, [0, 2, 3, 4, 5]]
        broad = table.iloc[23, [0, 2, 3, 4, 5]]
        return rates, broad

    def gen_excel():
        exchange, broad = exchange_rates()
        exchange = pd.DataFrame(exchange).transpose()
        exchange["23"] = ""
        broad = pd.DataFrame(broad)
        output = pd.concat([exchange, broad], axis=1)
        return output

    df = gen_excel().reset_index()
    dic = {
        "January": "Jan",
        "February": "Feb",
        "March": "Mar",
        "April": "Apr",
        "June": "Jun",
        "July": "Jul",
        "August": "Aug",
        "September": "Sep",
        "October": "Oct",
        "November": "Nov",
        "December": "Dec",
    }
    df["index"] = df["index"].replace(dic, regex=True)
    df["index"] = df["index"].str.replace(" 20", "-")

    output = df.iloc[1:5, :]
    output.columns = df.iloc[0, :]
    return output


def table26_dates():
    OECD = sdmx.Client("OECD")
    message = OECD.data("MEI_REAL")
    MEI_DATA = pd.DataFrame(sdmx.to_pandas(message.data[0])).reset_index()

    subject = "PRINTO01"
    cols = ["LOCATION", "TIME_PERIOD", "value"]

    ind_prod = MEI_DATA[cols][MEI_DATA["SUBJECT"] == subject]

    month = ind_prod["TIME_PERIOD"][
        ind_prod["TIME_PERIOD"].str.contains("-") & ~ind_prod["TIME_PERIOD"].str.contains("Q")
    ].max()
    quarter = ind_prod["TIME_PERIOD"][ind_prod["TIME_PERIOD"].str.contains("Q")].max()
    year = ind_prod["TIME_PERIOD"][~ind_prod["TIME_PERIOD"].str.contains("-")].max()
    return ind_prod, month, quarter, year


def table26_data(df, month, quarter, year):
    ind_prod_month = df[df["TIME_PERIOD"] == month]
    ind_prod_quarter = df[df["TIME_PERIOD"] == quarter]
    ind_prod_year = df[df["TIME_PERIOD"] == year]

    outfile = ind_prod_year
    outfile = pd.concat([outfile, ind_prod_quarter], axis=0).drop_duplicates(
        subset=["LOCATION"], keep="last"
    )
    outfile = pd.concat([outfile, ind_prod_month], axis=0).drop_duplicates(
        subset=["LOCATION"], keep="last"
    )
    return outfile


def table27_dates():
    OECD = sdmx.Client("OECD")
    message = OECD.data("MEI_REAL")
    MEI_DATA = pd.DataFrame(sdmx.to_pandas(message.data[0])).reset_index()

    subject = "SLRTCR03"
    cols = ["LOCATION", "TIME_PERIOD", "value"]

    car_prod = MEI_DATA[cols][MEI_DATA["SUBJECT"] == subject]

    month = car_prod["TIME_PERIOD"][
        car_prod["TIME_PERIOD"].str.contains("-") & ~car_prod["TIME_PERIOD"].str.contains("Q")
    ].max()
    quarter = car_prod["TIME_PERIOD"][car_prod["TIME_PERIOD"].str.contains("Q")].max()
    year = car_prod["TIME_PERIOD"][~car_prod["TIME_PERIOD"].str.contains("-")].max()
    return car_prod, month, quarter, year


def table27_data(df, month, quarter, year):
    car_prod_month = df[df["TIME_PERIOD"] == month]
    car_prod_quarter = df[df["TIME_PERIOD"] == quarter]
    car_prod_year = df[df["TIME_PERIOD"] == year]

    outfile = car_prod_year
    outfile = pd.concat([outfile, car_prod_quarter], axis=0).drop_duplicates(
        subset=["LOCATION"], keep="last"
    )
    outfile = pd.concat([outfile, car_prod_month], axis=0).drop_duplicates(
        subset=["LOCATION"], keep="last"
    )
    return outfile


def inset_blank_row(row_number, df, row_value):
    start_upper = 0
    end_upper = row_number
    start_lower = row_number
    end_lower = df.shape[0]
    upper_half = [*range(start_upper, end_upper, 1)]
    lower_half = [*range(start_lower, end_lower, 1)]
    lower_half = [x.__add__(1) for x in lower_half]
    index_ = upper_half + lower_half
    df.index = index_
    df.loc[row_number] = row_value
    df = df.sort_index()
    return df
