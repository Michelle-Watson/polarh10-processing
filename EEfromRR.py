import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import csv  # better library compared to panda for less complicated text files
import matplotlib.pyplot as plt
from statistics import mean

import os


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

    # Convert RR-interval into time stamp (x-axis of graph)
    # It's easier than parsing the time from the text file directly, but can only be used with RR-interval data
    def rrtotime(self, rr):
        time = []
        running_t_ms = 0

        # the running sum of rr-intervals is the same as the time value
        for rr_interval in rr:
            running_t_ms += rr_interval
            running_t_min = round(running_t_ms / 60000.0, 2)
            time.append(running_t_min)

        return time

    # trim HR at peak
    def trim_hr(self, t, hr):
        maxVal = max(hr)
        i = hr.index(maxVal)
        # All trials took ~30s, so if the maxHR is hit too late or too early, just trim to a standard t=0.7s
        if t[i] >= 0.7 or t[i] < 0.1:
            print(t[i])
            i = next(x for x, val in enumerate(t) if val > 0.7)
            print(i)
        trimHR = hr[0:i]
        trimt = t[0:i]
        return trimt, trimHR, maxVal

    # trim HR ~30s

    # Convert text file to EE
    def texttoee(self, filename):
        # Extract rr from text file
        rr = self.loggertxt_to_rrlist_csv(filename)

        time = self.rrtotime(rr)

        # convert RR to HR
        heart_rates = self.rrtohr(rr)

        if filename == 'Ethan/ethan_BA_60_RR_2.txt':
            with open('HR.txt', 'w') as f:
                write = csv.writer(f)
                # using csv.writer method from CSV package
                write.writerow(heart_rates)

        # trim HR when it peaks, need to trim time as well since they're plotted together
        t_trim, hr_trim, peak_hr = self.trim_hr(time, heart_rates)

        # convert HR to EE
        ee = self.hrtoee(hr_trim)
        print(ee)
        avg_ee = mean(ee)

        return t_trim, rr, hr_trim, ee, round(avg_ee), round(peak_hr)

    # def process_files(self, type, filename_base_str, time_base_str, HR_trim_base_str, ee_base_str, eeavg_base_str, hrpeak_base_str):
    def process_files(self, type, filename_base_str):
        base_string = 'Ethan/ethan_BA_60_RR_'
        colour_list = ['red', 'orange', 'yellow', '#90EE90', '#87CEFA']

        # keep track of peak HR and avg EE through trials
        peakHR_list = []
        avgEE_list = []

        # create a 2x2 subplot grid
        fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 10))
        fig.tight_layout(h_pad=2)

        # flatten the axs array to make it easier to iterate over
        axs = axs.flatten()

        # Keep track of subplots
        ax1 = axs[0]    # HR v time
        ax2 = axs[1]    # EE v time
        ax3 = axs[2]
        ax4 = axs[3]

        for i in range(1, 6):
            file_path = f"{filename_base_str}{i}.txt"
            # t_str = f"{time_base_str}{i}"
            # hr_str = f"{HR_trim_base_str}{i}"
            # ee_str = f"{ee_base_str}{i}"
            # avg_ee_str = f"{eeavg_base_str}{i}"
            # peak_hr_str = f"{hrpeak_base_str}{i}"

            if os.path.isfile(file_path):
                # Perform some action on the file
                print(f"Processing file: {file_path}")

                # Process RR interval data into energy expenditure (EE) using Keytel's formula
                t_str, _, hr_str, ee_str, avg_ee_str, peak_hr_str = self.texttoee(file_path)
                peakHR_list.append(peak_hr_str)
                avgEE_list.append(avg_ee_str)

                # Plot HR
                ax1.fill_between(t_str, hr_str, color=colour_list[i - 1], alpha=0.5, label=f'HR {type} {i} peak = {peak_hr_str} bpm')

                # Plot EE
                ax2.fill_between(t_str, ee_str, color=colour_list[i - 1], alpha=0.5, label=f'EE {type} {i}, avg = {avg_ee_str} kJ/min')

            else:
                print(f"File not found: {file_path}")

        # Plot peak HR over trials
        ax3.plot(peakHR_list)
        ax3.set_xlabel('Trial')
        ax3.set_ylabel('Heart Rate [beats/minute]')
        ax3.set_title(f'Peak HR for {type} {base_string}')

        # Plot avg EE over trials
        ax4.plot(avgEE_list)
        ax4.set_xlabel('Trial')
        ax4.set_ylabel('Energy Expenditure [kJ/minute]')
        ax4.set_title(f'Average EE for {type} {base_string}')

        # set the axis labels and title
        ax1.set_xlabel('Time [minutes]')
        ax1.set_ylabel('Heart Rate [beats/minute]')
        ax1.set_title(f'{type} HR for {base_string}')

        ax2.set_xlabel('Time [minutes]')
        ax2.set_ylabel('Energy Expenditure [kJ/minute]')
        ax2.set_title(f'{type} EE for {base_string}')

        # add a legend to the plot
        ax1.legend()
        ax2.legend()

        # display the plot
        plt.show()

        fig.savefig(f"{filename_base_str}.png")


# hack: instead of parsing time stamp, I could just use the RR interval as my time stamps
# Create Polar user and Process files
ethan = PolarUser("Ethan", 22, 1, 80)  # name, age, gender [male=1], weight [kg]
ethan.process_files('baseline', 'Ethan/ethan_BA_60_RR_')


'''
ethan.process_files('baseline', 'Ethan/ethan_BA_60_RR_', 'time_ethan_ee_', 'ethan_hr_trim_', 'ethan_ee_', 'ethan_avg_ee', 'ethan_peak_hr')
# Process RR interval data into energy expenditure (EE) using Keytel's formula
time_ethan_ee1, _, _, ethan_ee1 = ethan.texttoee('Ethan/ethan_BA_60_RR_1.txt')
time_ethan_ee2, _, _, ethan_ee2 = ethan.texttoee('Ethan/ethan_BA_60_RR_2.txt')
time_ethan_ee3, _, _, ethan_ee3 = ethan.texttoee('Ethan/ethan_BA_60_RR_3.txt')
time_ethan_ee4, _, _, ethan_ee4 = ethan.texttoee('Ethan/ethan_BA_60_RR_4.txt')
time_ethan_ee5, _, _, ethan_ee5 = ethan.texttoee('Ethan/ethan_BA_60_RR_5.txt')

##########################################################
print(time_ethan_ee1)
# Visualize data
colour_list = ['red', 'orange', 'yellow', '#90EE90', '#87CEFA']

# create the plot
plt.fill_between(time_ethan_ee1, ethan_ee1, color='red', alpha=0.5, label='EE Baseline 1')
plt.fill_between(time_ethan_ee2, ethan_ee2, color='orange', alpha=0.5, label='EE Baseline 2')
plt.fill_between(time_ethan_ee3, ethan_ee3, color='yellow', alpha=0.5, label='EE Baseline 3')
plt.fill_between(time_ethan_ee4, ethan_ee4, color='#90EE90', alpha=0.5, label='EE Baseline 4')
plt.fill_between(time_ethan_ee5, ethan_ee5, color='#87CEFA', alpha=0.5, label='EE Baseline 5')

# set the axis labels and title
plt.xlabel('Time [minutes]')
plt.ylabel('Energy Expenditure [kJ/minute]')
plt.title('Ethan\'s Baseline Energy Expenditure Carrying 60kg Uphill')

# add a legend to the plot
plt.legend()

# display the plot
plt.show()
'''
