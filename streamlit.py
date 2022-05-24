from io import BytesIO

import pandas as pd
import sdmx

import streamlit as st

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


header_text = "OET Portfolio - Data Generation Tool"
home = "Tool Home"

currency_exchange = "FED - Currency Exchange Rates"
industrial_production = "OECD - Industrial Production"
car_production = "OECD - Car Production"


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def render_home():
    st.write("Please select a report using the radio buttons to the left")


def render_exchange():
    st.subheader("Foreign Exchange Rates -- G.5 Monthly")
    st.write("The current foreign exchange data can be seen below:")

    exchange_rates = table25()
    exchange_rates = pd.DataFrame(exchange_rates)

    display = exchange_rates.astype(
        str
    )  # streamlit seems to be struggling with a df bug, casting to string requrired to display df at the time of writing
    st.dataframe(display, 1500, 300)

    st.write("To download the above data, click the button below:")

    exchange_rate_xlsx = to_excel(exchange_rates)

    st.download_button(
        label="Download...",
        data=exchange_rate_xlsx,
        file_name="exchange_rates.xlsx",
        mime="text/csv",
    )


def render_industrial_production():
    st.subheader("Industrial Production -- MEI REAL")
    st.write(
        "As monthly data is not always available, please use the fields below to enter the most relevant month and quarter. Values will default to the most recent published month, previous quarter and full year."
    )
    st.write(
        "Where updates are made to the dates, please use the same format as below, i.e. YYYY-MM"
    )

    industrial_production, month_data, quarter_data, year_data = table26_dates()
    month = st.text_input("Month:", value=str(month_data), max_chars=7)
    quarter = st.text_input("Quarter", value=str(quarter_data), max_chars=7)
    year = st.text_input("Year", value=str(year_data), max_chars=7)

    data = table26_data(industrial_production, month, quarter, year)

    country_dict = {
        "CAN": 0,
        "MEX": 1,
        "USA": 2,
        "AUS": 3,
        "JPN": 4,
        "KOR": 5,
        "NZL": 6,
        "AUT": 7,
        "BEL": 8,
        "CZE": 9,
        "DNK": 10,
        "FIN": 11,
        "FRA": 12,
        "DEU": 13,
        "GRC": 14,
        "HUN": 15,
        "IRL": 16,
        "ITA": 17,
        "LUX": 18,
        "NLD": 19,
        "NOR": 20,
        "POL": 21,
        "PRT": 22,
        "ESP": 23,
        "SWE": 24,
        "CHE": 25,
        "TUR": 26,
        "GBR": 27,
        "OECD": 28,
        "G-7": 29,
        "EU27_2020": 30,
        "EA19": 31,
        "OECDE": 31,
    }

    data = data[data["LOCATION"].isin(country_dict.keys())].set_index("LOCATION")
    all_indexes = pd.DataFrame(country_dict, index=[0]).transpose()
    miss_index = all_indexes.index.difference(data.index)
    add_df = pd.DataFrame(index=miss_index, columns=data.columns).fillna("")
    data = pd.concat([data, add_df], axis=0).reset_index().rename(columns={"index": "LOCATION"})
    data = data.iloc[data.LOCATION.map(country_dict).argsort()].reset_index(drop=True)
    data = inset_blank_row(28, data, ["", "", ""]).transpose()

    display = data.astype(
        str
    )  # streamlit seems to be struggling with a df bug, casting to string requrired to display df at the time of writing
    st.dataframe(display, 1500, 300)
    #    AgGrid(data, theme="streamlit")

    st.write("To download the above data, click the button below:")

    ind_prod_xlsx = to_excel(data)

    st.download_button(
        label="Download...",
        data=ind_prod_xlsx,
        file_name="industrial_production.xlsx",
        mime="text/csv",
    )


def render_car_production():
    st.subheader("New car registrations -- MEI REAL")
    st.write(
        "As monthly data is not always available, please use the fields below to enter the most relevant month and quarter. Values will default to the most recent published month, previous quarter and full year."
    )
    st.write(
        "Where updates are made to the dates, please use the same format as below, i.e. YYYY-MM"
    )

    car_production, month_data, quarter_data, year_data = table27_dates()
    month = st.text_input("Month:", value=str(month_data), max_chars=7)
    quarter = st.text_input("Quarter", value=str(quarter_data), max_chars=7)
    year = st.text_input("Year", value=str(year_data), max_chars=7)

    data = table27_data(car_production, month, quarter, year)

    country_dict = {
        "CAN": 0,
        "USA": 1,
        "AUS": 2,
        "JPN": 3,
        "KOR": 4,
        "NZL": 5,
        "AUT": 6,
        "BEL": 7,
        "CZE": 8,
        "DNK": 9,
        "FIN": 10,
        "FRA": 11,
        "DEU": 12,
        "GRC": 13,
        "HUN": 14,
        "ICE": 15,
        "IRL": 16,
        "ITA": 17,
        "LUX": 18,
        "NLD": 19,
        "NOR": 20,
        "POL": 21,
        "PRT": 22,
        "SVK": 23,
        "ESP": 24,
        "SWE": 25,
        "CHE": 26,
        "TUR": 27,
        "GBR": 28,
        "EA19": 29,
        "OECD": 30,
        "G-7": 31,
        "OECDE": 32,
    }

    data = data[data["LOCATION"].isin(country_dict.keys())].set_index("LOCATION")
    all_indexes = pd.DataFrame(country_dict, index=[0]).transpose()
    miss_index = all_indexes.index.difference(data.index)
    add_df = pd.DataFrame(index=miss_index, columns=data.columns).fillna("")
    data = pd.concat([data, add_df], axis=0).reset_index().rename(columns={"index": "LOCATION"})
    data = data.iloc[data.LOCATION.map(country_dict).argsort()].reset_index(drop=True)
    data = inset_blank_row(30, data, ["", "", ""]).transpose()

    display = data.astype(
        str
    )  # streamlit seems to be struggling with a df bug, casting to string requrired to display df at the time of writing
    st.dataframe(display, 1500, 300)
    #    AgGrid(data, theme="streamlit")

    st.write("To download the above data, click the button below:")

    car_prod_xlsx = to_excel(data)

    st.download_button(
        label="Download...",
        data=car_prod_xlsx,
        file_name="industrial_production.xlsx",
        mime="text/csv",
    )


display_page = st.sidebar.radio(
    "View Page:", (home, currency_exchange, industrial_production, car_production)
)

st.header(header_text)

if display_page == home:
    render_home()
elif display_page == currency_exchange:
    render_exchange()
elif display_page == industrial_production:
    render_industrial_production()
elif display_page == car_production:
    render_car_production()
