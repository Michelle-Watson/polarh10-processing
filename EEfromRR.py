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

        self.baseline_PeakHR = []
        self.baseline2_PeakHR = []
        self.deer_PeakHR = []
        self.DIYbelt_PeakHR = []
        self.butteryfly_PeakHR = []

        self.baseline_AvgEE = []
        self.baseline2_AvgEE = []
        self.deer_AvgEE = []
        self.DIYbelt_AvgEE = []
        self.butteryfly_AvgEE = []

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
        minVal = min(hr)
        startVal = hr[0]
        delta_minmaxHR = maxVal - minVal
        delta_startmaxHR = maxVal - startVal
        i = hr.index(maxVal)
        """
        print(f"i: {i}")
        print(f"t[i]: {t[i]}")
        print(f"hr: {hr}")
        print(f"max: {maxVal}")
        """
        trimHR = hr
        trimt = t
        # All trials took ~30s, so if the maxHR is hit too late or too early, just trim to a standard t=0.7s

        # if time is greater than 0.7, trim to 0.7
        # if t[i] >= 0.7:  # or t[i] < 0.1
        if max(t) > 0.7:
            print(t[i])
            i = next(x for x, val in enumerate(t) if val > 0.7)
            print(i)
            trimHR = hr[0:i]
            trimt = t[0:i]

        return trimt, trimHR, maxVal, delta_minmaxHR, delta_startmaxHR

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
        t_trim, hr_trim, peak_hr, delta_minmaxHR, delta_startmaxHR = self.trim_hr(time, heart_rates)

        # convert HR to EE
        ee = self.hrtoee(hr_trim)
        print(ee)
        avg_ee = mean(ee)

        return t_trim, rr, hr_trim, ee, round(avg_ee), round(peak_hr), round(delta_minmaxHR), round(delta_startmaxHR)

    # def process_files(self, type, filename_base_str, time_base_str, HR_trim_base_str, ee_base_str, eeavg_base_str, hrpeak_base_str):
    def process_files(self, type, filename_base_str, num_files_to_process):
        colour_list = ['red', 'orange', 'yellow', '#90EE90', '#87CEFA']

        # keep track of peak HR and avg EE through trials
        peakHR_list = []
        avgEE_list = []

        # create a 2x2 subplot grid
        fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 10))
        # fig.tight_layout(h_pad=2)
        fig.subplots_adjust(hspace=0.5)

        # flatten the axs array to make it easier to iterate over
        axs = axs.flatten()

        # Keep track of subplots
        ax1 = axs[0]    # HR v time
        ax2 = axs[1]    # EE v time
        ax3 = axs[2]
        ax4 = axs[3]

        for i in range(1, num_files_to_process+1):
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
                t_str, _, hr_str, ee_str, avg_ee_str, peak_hr_str, delta_minmaxHR, delta_startmaxHR = self.texttoee(file_path)
                peakHR_list.append(peak_hr_str)
                avgEE_list.append(avg_ee_str)

                # Plot HR
                ax1.fill_between(t_str, hr_str, color=colour_list[i - 1], alpha=0.5, label=f'HR t{i} peak = {peak_hr_str} bpm, delta_minmaxHR = {delta_minmaxHR}, delta_startmaxHR = {delta_startmaxHR}')

                # Plot EE
                ax2.fill_between(t_str, ee_str, color=colour_list[i - 1], alpha=0.5, label=f'EE t{i}, avg = {avg_ee_str} kJ/m')

            else:
                print(f"File not found: {file_path}")

        # save important vars to object depending on type
        if type == "Baseline":
            self.baseline_PeakHR = peakHR_list
            self.baseline_AvgEE = avgEE_list

        elif type == "Deer":
            self.deer_PeakHR = peakHR_list
            self.deer_AvgEE = avgEE_list

        elif type == "DIYBelt":
            self.DIYbelt_PeakHR = peakHR_list
            self.DIYbelt_AvgEE = avgEE_list

        elif type == "Butterfly":
            self.butteryfly_PeakHR = peakHR_list
            self.butteryfly_AvgEE = avgEE_list


        # Plot peak HR over trials
        ax3.plot(peakHR_list)
        ax3.set_xlabel('Trial')
        ax3.set_ylabel('Heart Rate [beats/minute]', fontsize='small')
        ax3.set_title(f'Peak HR for {type}')  # {filename_base_str}

        # Plot avg EE over trials
        ax4.plot(avgEE_list)
        ax4.set_xlabel('Trial')
        ax4.set_ylabel('Energy Expenditure [kJ/minute]', fontsize='small')
        ax4.set_title(f'Average EE for {type}')

        # set the axis labels and title
        ax1.set_xlabel('Time [minutes]')
        ax1.set_ylabel('Heart Rate [beats/minute]', fontsize='small')
        ax1.set_title(f'{type} HR')  # for {self.name}

        ax2.set_xlabel('Time [minutes]')
        ax2.set_ylabel('Energy Expenditure [kJ/minute]', fontsize='small')
        ax2.set_title(f'{type} EE')

        # add a legend to the plot
        ax1.legend(fontsize='x-small', loc='lower right')
        ax2.legend(fontsize='x-small', loc='lower right')

        # display the plot
        plt.show()

        fig.savefig(f"{filename_base_str}.png")


# hack: instead of parsing time stamp, I could just use the RR interval as my time stamps
# Create Polar user and Process files

'''
# Prelim Testing (round 1)
# send in number of RR files as well for now
ethan = PolarUser("Ethan", 22, 1, 78)  # name, age, gender [male=1], weight [kg]. Height = 177.8cm (5’10”)
ethan.process_files('Baseline', 'Ethan/ethan_BA_60_RR_', 5)
ethan.process_files('Harness', 'Ethan/ethan_Harness_60_RR_', 3)

hanaan = PolarUser("Hanaan", 22, 0, 86)  # name, age, gender [male=1], weight [kg]. Height = 170cm
hanaan.process_files('Baseline', 'Hanaan/hanaan_BA_40_RR_', 5)
hanaan.process_files('Harness', 'Hanaan/hanaan_Harness_40_RR_', 5)

sydney = PolarUser("Sydney", 22, 0, 86)  # name, age, gender [male=1], weight [kg]. Height = 150cm
sydney.process_files('Baseline', 'Sydney/sydney_BA_20_RR_', 5)
sydney.process_files('Harness', 'Sydney/sydney_Harness_20_RR_', 5)
# sydney_Harness_20_RR_2 -> peak HR at 52s. reached top of hill at ~37s

mich = PolarUser("Michelle", 22, 0, 61.2)  # name, age, gender [male=1], weight [kg]. Height = 161cm
mich.process_files('Baseline', 'Mich/mich_BA_40_RR_', 5)
mich.process_files('Harness', 'Mich/mich_Harness_40_RR_', 5)

# Testing (round 2-3)
# NEW: Baseline, Deer harness, DIY (belt and suspenders) - iteration 1, Butteryfly - iteration 2 that uses straps from deer harness
hanaan = PolarUser("Hanaan", 22, 0, 86)  # name, age, gender [male=1], weight [kg]. Height = 170cm
hanaan.process_files('Baseline', 'Hanaan/hanaan_BA2_40_RR_', 5)
hanaan.process_files('Deer', 'Hanaan/hanaan_Deer_40_RR_', 5)
hanaan.process_files('DIYBelt', 'Hanaan/hanaan_DIYBelt_40_RR_', 5)
hanaan.process_files('Butterfly', 'Hanaan/hanaan_Butterfly_40_RR_', 5)

ethan = PolarUser("Ethan", 22, 1, 78)  # name, age, gender [male=1], weight [kg]. Height = 177.8cm (5’10”)
ethan.process_files('Baseline', 'Ethan/ethan_BA2_60_RR_', 5)
ethan.process_files('Deer', 'Ethan/ethan_Deer_60_RR_', 5)
ethan.process_files('DIYBelt', 'Ethan/ethan_DIYBelt_60_RR_', 5)
ethan.process_files('Butterfly', 'Ethan/ethan_Butterfly_60_RR_', 5)


# NEW: Baseline, Deer harness, DIY (belt and suspenders) - iteration 1, Butteryfly - iteration 2 that uses straps from deer harness
ethan = PolarUser("Ethan", 22, 1, 78)  # name, age, gender [male=1], weight [kg]. Height = 177.8cm (5’10”)
ethan.process_files('DIYBelt', 'Ethan/ethan_DIYBelt_60_RR_', 5)



sydney = PolarUser("Sydney", 22, 0, 86)  # name, age, gender [male=1], weight [kg]. Height = 150cm
sydney.process_files('Deer', 'Sydney/sydney_Deer_20_RR_', 5)
sydney.process_files('Baseline', 'Sydney/sydney_BA2_20_RR_', 5)
'''

mich = PolarUser("Michelle", 22, 0, 61.2)  # name, age, gender [male=1], weight [kg]. Height = 161cm
mich.process_files('Baseline', 'Mich/mich_BA2_40_RR_', 5)
mich.process_files('Deer', 'Mich/mich_Deer_40_RR_', 5)
mich.process_files('DIYBelt', 'Mich/mich_DIYBelt_40_RR_', 5)
mich.process_files('Butterfly', 'Mich/mich_Butterfly_40_RR_', 5)

'''
##########################################################

ethan.process_files('baseline', 'Ethan/ethan_BA_60_RR_', 'time_ethan_ee_', 'ethan_hr_trim_', 'ethan_ee_', 'ethan_avg_ee', 'ethan_peak_hr')
# Process RR interval data into energy expenditure (EE) using Keytel's formula
time_ethan_ee1, _, _, ethan_ee1 = ethan.texttoee('Ethan/ethan_BA_60_RR_1.txt')
time_ethan_ee2, _, _, ethan_ee2 = ethan.texttoee('Ethan/ethan_BA_60_RR_2.txt')
time_ethan_ee3, _, _, ethan_ee3 = ethan.texttoee('Ethan/ethan_BA_60_RR_3.txt')
time_ethan_ee4, _, _, ethan_ee4 = ethan.texttoee('Ethan/ethan_BA_60_RR_4.txt')
time_ethan_ee5, _, _, ethan_ee5 = ethan.texttoee('Ethan/ethan_BA_60_RR_5.txt')


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
