import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import csv  # better library compared to panda for less complicated text files
import matplotlib.pyplot as plt


# Create a class for a Polar H10 person
class PolarUser:
    def __init__(self, name, age, gender, weight):
        self.name = name
        self.gender = gender  # 1=male, 0=female
        self.age = age  # years
        self.weight = weight  # kg

    # Extract Polar Sensor Logger RR data from text file using csv library into list
    def loggertxt_to_rrlist_csv(self, filename):
        rr_intervals = []

        # open the file in read mode
        with open(filename, 'r') as file:
            # create a csv reader object
            reader = csv.DictReader(file, delimiter=';')

            # loop over each row in the file
            for row in reader:
                # append the RR-interval data to the list
                rr_intervals.append(float(row['RR-interval [ms]']))

        return rr_intervals

    # Extract Polar Sensor Logger RR data from text file using pandas library into list
    def loggertxt_to_rrlist_pandas(self, filename):
        # read the file into a pandas DataFrame
        df = pd.read_csv('filename.txt', sep=';')

        # extract the RR-interval data into a list
        rr_intervals = df['RR-interval [ms]'].tolist()
        return rr_intervals

    # Convert RR to HR, up until n-2
    def rrtohr(self, rr):
        heart_rates = []

        # heart rate (beats per minute) = 60,000 / RR interval (in milliseconds)
        # SOURCE: https://www.kubios.com/hrv-analysis-methods/
        for rr_interval in rr:
            heart_rate = 60000 / rr_interval
            heart_rates.append(heart_rate)

        return heart_rates

    # Convert HR to EE
    def hrtoee(self, hr_list):
        ee_list = []

        # Keytel's formula based on:
        # "Prediction of energy expenditure from heart rate monitoring during submaximal exercise"
        # LR Keytel, JH Goedecke, TD Noakes, H Hiiloskorpi, R Laukkanen, L van der Merwe, EV Lambert
        # Source InformationMarch 2005, Volume23(Issue3)Pages, p.289To - 297 - Journal of Sports Sciences
        for hr in hr_list:
            ee = self.gender * (-55.0969 + 0.5309 * hr + 0.1988 * self.weight + 0.2017 * self.age) + (
                        1 - self.gender) * (-20.4022 + 0.4472 * hr - 0.1263 * self.weight + 0.074 * self.age)
            ee_list.append(ee)

        return ee_list

    # Convert text file to EE
    def texttoee(self, filename):
        # Extract rr from text file
        rr = self.loggertxt_to_rrlist_csv(filename)

        # convert RR to HR
        heart_rates = self.rrtohr(rr)

        # convert HR to EE
        return self.hrtoee(heart_rates)


# Create Polar user
ethan = PolarUser("Ethan", 22, 1, 80)  # name, age, gender [male=1], weight [kg]

# Process RR interval data into energy expenditure (EE) using Keytel's formula
ethan_ee1 = ethan.texttoee('Ethan/ethan_BA_60_RR_1.txt')
ethan_ee2 = ethan.texttoee('Ethan/ethan_BA_60_RR_2.txt')
ethan_ee3 = ethan.texttoee('Ethan/ethan_BA_60_RR_3.txt')
ethan_ee4 = ethan.texttoee('Ethan/ethan_BA_60_RR_4.txt')
ethan_ee5 = ethan.texttoee('Ethan/ethan_BA_60_RR_5.txt')

##########################################################
# Visualize data

# create the plot
plt.plot(ethan_ee1, label='EE Baseline 1')
plt.plot(ethan_ee2, label='EE Baseline 2')
plt.plot(ethan_ee3, label='EE Baseline 3')
plt.plot(ethan_ee4, label='EE Baseline 4')
plt.plot(ethan_ee5, label='EE Baseline 5')

# set the axis labels and title
plt.xlabel('Sample Number')
plt.ylabel('Energy Expenditure')
plt.title('Ethan\'s Baseline Energy Expenditure Carrying 60kg Uphill')

# add a legend to the plot
plt.legend()

# display the plot
plt.show()
