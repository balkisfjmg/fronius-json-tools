
"""
Work-in-progress!!!

Reads the logdata-data json files generated by the Fronius Push Service.
Extracts some data and generates a html report
"""

import json
import csv
import collections
import matplotlib.pyplot as plt
from pprint import pprint
import sys, os
from datetime import date
from calendar import monthrange


WP = 4060
YEAR = 2017


PRODUCED = 0
TOTAL_CONSUMED = 1
DIRECT_CONSUMED = 2
SUPPLIED = 3
SPECIFIC_YIELD = 4

WAC_SUB_PRODUCED = 0
WAC_MINUS = 1 # supplied
WAC_PLUS = 2  # purchased

def get_data_from_file(filename):
    """
    returns data for one day from a logdata-data file as a list of:
    [Inverter EnergyReal_WAC_Sum_Produced Wh per day
     Meter EnergyReal_WAC_Minus Wh per day
     Meter EnergyReal_WAC_Plus Wh per day]
    """
    if not os.path.exists(filename):
        print("File {} not found".format(filename))
        return []

    #print("Processing file {}".format(filename))

    with open(filename) as data_file:    
        data = json.load(data_file)

    #pprint(data)

    sum_produced = 0.0

    wac_sum_produced = data['Body']['inverter/1']['Data']['EnergyReal_WAC_Sum_Produced']['Values']
    for key, value in wac_sum_produced.items():
        sum_produced = sum_produced + value

    #print("Sum produced {:.2f} Wh".format(sum_produced))

    meter_minus_data = data['Body']['meter:16220118']['Data']['EnergyReal_WAC_Minus_Absolute']['Values']
    
    if "0" in meter_minus_data:
        meter_minus_start_value = meter_minus_data["0"]
    else:
        meter_minus_start_value = meter_minus_data["1"]
        print("We have the curious case of a missing secound 0 of the day in the data, we used second 1 instead")

    meter_minus_end_value = meter_minus_data["85500"]
    meter_minus = meter_minus_end_value - meter_minus_start_value

    #print("Meter minus {} Wh".format(meter_minus))

    meter_plus_data = data['Body']['meter:16220118']['Data']['EnergyReal_WAC_Plus_Absolute']['Values']

    if "0" in meter_plus_data:
        meter_plus_start_value = meter_plus_data["0"]
    else:
        meter_plus_start_value = meter_plus_data["1"]

    meter_plus_end_value = meter_plus_data["85500"]
    meter_plus = meter_plus_end_value - meter_plus_start_value

    #print("Meter plus {} Wh".format(meter_plus))

    return [sum_produced, meter_minus, meter_plus]

def get_month_data(year, month, start_day, end_day):
    """
    returns a list of day datas with additional computed values
    """
    path = "drosselweg-logdata"

    days = range(start_day, end_day + 1)
    month_data = []

    for day in days:
        filename = "logdata-data" + str(year) + str(month).zfill(2) + str(day).zfill(2) + "235000.json"

        file = os.path.join(path, filename)
        day_data = compute_additional_day_data(get_data_from_file(file))
        month_data.append(day_data)


    sum_produced = 0

    for day in month_data:
        sum_produced = sum_produced + day[0]
        #print("{}/{} Specific yield {}".format(year, month, day[4]))

    print("{}/{} Sum produced {} kWh".format(year, month,sum_produced/1000))

    specific_yield_month = sum_produced / len(days) / WP
    print("{}/{} Specific average yield per day in this month {}".format(year, month, specific_yield_month))

    return month_data



def compute_additional_day_data(day_data):
    """
    Takes day data and  computes additional data based on it, returns it as a list of:
    [produced,         (WAC_Sum_Produced)
     total_consumed,   (WAC_Plus + WAC_Sum_Produced - WAC_Minus)
     direct_consumed,  (WAC_Sum_Produced - WAC_Minus),
     supplied,         (WAC_Minus)
     specific_yield    (WAC_Sum_Produced / Wp)
    ]
    """
    if len(day_data) != 3:
        return [0, 0, 0, 0, 0]

    produced = day_data[WAC_SUB_PRODUCED]
    total_consumed = day_data[WAC_PLUS] + day_data[WAC_SUB_PRODUCED] - day_data[WAC_MINUS]
    direct_consumed = day_data[WAC_SUB_PRODUCED] - day_data[WAC_MINUS]
    supplied = day_data[WAC_MINUS]
    specific_yield = day_data[WAC_SUB_PRODUCED] / WP

    return [produced, total_consumed, direct_consumed, supplied, specific_yield]



def get_year_data(year):

    year_data = []

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    for month in range(start_date.month, end_date.month + 1):
        if month > date.today().month:
            break

        start_day = 1
        weekday, number_of_days = monthrange(start_date.year, month)
        end_day = number_of_days

        if month == date.today().month and end_day >= date.today().day:
            end_day = date.today().day - 1

        year_data.append( get_month_data(start_date.year, month, start_day, end_day) )

    return year_data

def compute_year_values(year_data):
    
    produced = 0
    total_consumed = 0
    direct_consumed = 0
    supplied = 0

    for month in year_data:
        for day in month:
            produced = produced + day[PRODUCED]
            total_consumed = total_consumed + day[TOTAL_CONSUMED]
            direct_consumed = direct_consumed + day[DIRECT_CONSUMED]
            supplied = supplied + day[SUPPLIED]

    print("Year: Produced:          {:.2f} kWh".format(produced/1000))
    print("Year: Total consumed:    {:.2f} kWh".format(total_consumed/1000))
    print("Year: Direct consumed:   {:.2f} kWh".format(direct_consumed/1000))
    print("Year: Supplied:          {:.2f} kWh".format(supplied/1000))
    print("Year: Autarky %:         {:.1f}%".format(direct_consumed/total_consumed*100))
    print("Year: Direct consumed %: {:.1f}%".format(direct_consumed/produced*100))
    print("Year: Specific yield:    {:.1f}".format( (produced/1000)/(WP/1000)))





def main(argv):
    #get_data_from_file("examples/logdata-data20170304235000.json")
    #get_month_data(2017, 1, 1, 31)
    #get_month_data(2017, 2, 1, 28)

    year_data = get_year_data(YEAR)
    compute_year_values(year_data)




def to_time(seconds):
    seconds = int(seconds) + 7200
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = '{:02d}:{:02d}'.format(h, m)
    #print(time)
    return time


def old():
    with open('examples/logdata-data20160913235000.json') as data_file:    
        data = json.load(data_file)

    #pprint(data)
    #print(data['Body']['inverter/1']['Data']['Current_DC_String_1']['Values'])

    c_dc_1_values = data['Body']['inverter/1']['Data']['Current_DC_String_1']['Values']

    # Dictionaraies, returned by the json reader, have no order.
    # So, convert it to a list of key/value tupels (.items()) and
    # sort it with sorted(), using a lambda function to convert the key/first tupel item to an integer
    # so that the sorting is based on numbers not text
    c_dc_1_values_ordered = sorted(c_dc_1_values.items(), key=lambda x: int(x[0]) )

    # no header text for the time column so that excel treats it as x axis values
    fieldnames = ['', 'Current_DC_String_1']

    with open('examples/c_dc_1.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, dialect='excel-tab')
        writer.writerow(fieldnames)

        for key, value in c_dc_1_values_ordered:
           writer.writerow([key, value])




    wac_plus_abs = data['Body']['meter:16220118']['Data']['EnergyReal_WAC_Plus_Absolute']['Values']
    wac_plus_abs_ordered = sorted(wac_plus_abs.items(), key=lambda x: int(x[0]) )

    wac_plus_diff = []

    previous_value = int(wac_plus_abs_ordered[0][1])
    for key, value in wac_plus_abs_ordered:
        diff = int(value) - previous_value
        wac_plus_diff.append( (to_time(key), float(diff)/1000) )
        previous_value = int(value)

    fieldnames = ['', 'EnergyReal_WAC_Plus_Absolute']

    with open('examples/wac_plus_diff.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, dialect='excel-tab')
        writer.writerow(fieldnames)

        for key, value in wac_plus_diff:
           writer.writerow([key, value])





    wac_minus_abs = data['Body']['meter:16220118']['Data']['EnergyReal_WAC_Minus_Absolute']['Values']
    wac_minus_abs_ordered = sorted(wac_minus_abs.items(), key=lambda x: int(x[0]) )

    wac_minus_diff = []

    previous_value = int(wac_minus_abs_ordered[0][1])
    for key, value in wac_minus_abs_ordered:
        diff = int(value) - previous_value
        wac_minus_diff.append( (to_time(key), float(diff)/1000) )
        previous_value = int(value)


    fieldnames = ['', 'EnergyReal_WAC_Minus_Absolute']

    with open('examples/wac_minus_diff.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, dialect='excel-tab')
        writer.writerow(fieldnames)

        for key, value in wac_minus_diff:
           writer.writerow([key, value])




    plus_keys = []
    plus_values = []

    previous_value = int(wac_plus_abs_ordered[0][1])
    for key, value in wac_plus_abs_ordered:
      diff = int(value) - previous_value
      previous_value = int(value)

      plus_keys.append( int(key) )
      plus_values.append( float(diff) )
      

    print(plus_keys)
    print(plus_values)


    plt.plot(plus_keys, plus_values)
    #plt.show()
    plt.savefig('examples/plot.png', bbox_inches='tight')


if __name__ == "__main__":
    main(sys.argv)
