# polarh10-processing
Process and Visualize data from the Polar Sensor Logger app (reads data from Polar H10)

[App (android only)](https://play.google.com/store/apps/details?id=com.j_ware.polarsensorlogger&hl=en_CA&gl=US)  

[Polar H10](https://www.polar.com/ca-en/sensors/h10-heart-rate-sensor)

# Use
Create Polar user and input:
```
your_obj_name_here = PolarUser(string "name", int age [years], int gender [male=1, female=0], double weight [kg])
your_obj_name_here.process_files(string 'name_data_type', string 'filename_base_str')
```

`filename_base_str` is the root of your Polar Sensor Logger text files  

Ex) your rr text files may have the names
* Ethan/ethan_BA_60_RR_1
* Ethan/ethan_BA_60_RR_2
* Ethan/ethan_BA_60_RR_3
* Ethan/ethan_BA_60_RR_4  

so you would name 
* `filename_base_str = 'Ethan/ethan_BA_60_RR_'`
