import matplotlib.pyplot as plt
import ggps
import numpy as np
import pandas as pd
import glob
import os
from time import gmtime, strftime,mktime, strptime
import datetime
import warnings


class Overview_File_Reader(object):
    """
    reads overview-file that containts all aggregated data.

    returns a pd.DataFrame containing the overview-file

    """
    def __init__(self, file_path=None):
        """
        save given file_path to self, or use default file_path
        :param file_path:
        """
        self.file_path = file_path
        if file_path != None:
            self.file_path = file_path

        elif file_path == None:
            warnings.warn("Standard-path has been chosen by default. Enter path to overviewfile to change this.",stacklevel=1)
            self.file_path = r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon"

    def read_file(self):
        activities = pd.read_csv(os.path.join(self.file_path, "Activities.csv"))
        activities["Datum"] = pd.to_datetime(activities["Datum"])
        return activities

class Activity_Handler(object):
    def __init__(self, activity_data):
        """
        class to make data in overviewfile usable.
        columns in the beginning:
        ['Aktivitätstyp', 'Datum', 'Favorit', 'Titel', 'Distanz', 'Kalorien',
       'Zeit', 'Ø Herzfrequenz', 'Maximale Herzfrequenz', 'Aerober TE',
       'Ø Schrittfrequenz (Laufen)', 'Max. Schrittfrequenz (Laufen)', 'Ø Pace',
       'Beste Pace', 'Positiver Höhenunterschied',
       'Negativer Höhenunterschied', 'Ø Schrittlänge',
       'Durchschnittliches vertikales Verhältnis', 'Ø vertikale Bewegung',
       'Training Stress Score®', 'Ø Leistung', 'Grit', 'Flow',
       'Züge insgesamt', 'Ø Swolf', 'Ø Schlagrate', 'Kletterzeit', 'Grundzeit',
       'Minimale Temperatur', 'Oberflächenpause', 'Dekompression',
       'Beste Rundenzeit', 'Anzahl der Runden', 'Maximale Temperatur']
        :param activity_data: Overview_file of all activities
        """
        self.activity_data = activity_data

        # add datetime_values
        self.activity_data["Year"] = self.activity_data["Datum"].dt.year
        self.activity_data["Month"] = self.activity_data["Datum"].dt.month
        self.activity_data["Week"] = self.activity_data["Datum"].dt.isocalendar().week
        self.activity_data["Week"] = self.activity_data["Week"] - 1
        self.activity_data["Zeit"] = pd.to_datetime(self.activity_data["Zeit"])
        self.activity_data["Minutes"] = self.activity_data["Zeit"].dt.minute

        self.activity_data["Total time in Minutes"] = self.activity_data["Zeit"].dt.hour*60 + self.activity_data["Zeit"].dt.minute

        self.change_swim_activites()

        # only keep swim_bike_run_gym_acitivites
        self.activity_data = self.activity_data[(self.activity_data["Aktivitätstyp"] == "Schwimmen")| (self.activity_data["Aktivitätstyp"] == "Laufen")| (self.activity_data["Aktivitätstyp"] == "Radfahren")| (self.activity_data["Aktivitätstyp"]=="Fitnessstudio und -geräte")]
        test = 0

    def change_swim_activites(self):
        """
        change swim activity types from Freiwasser or Schwimmbad to only Schwimmen, to make grouping easier
        :return:
        """
        for swim in range(len(self.activity_data)):
            if (self.activity_data["Aktivitätstyp"].iloc[swim]== "Freiwasserschwimmen") or (self.activity_data["Aktivitätstyp"].iloc[swim]== "Schwimmbadschwimmen"):
                self.activity_data["Aktivitätstyp"].iloc[swim] = "Schwimmen"
    
    def monthly_minutes_total(self):
        """

        :return: Series with monthly values for activity in sbrg
        """
        
        return  self.activity_data.groupby("Month")["Total time in Minutes"].sum()

    def monthly_minutes_split(self):
        """

        :return: Series with monthly values for activity in sbrg
        """

        return self.activity_data.groupby(["Year", "Month", "Aktivitätstyp"])["Total time in Minutes"].sum().unstack(fill_value=0).stack()
    
    def weekly_minutes_total(self):
        """

        :return: Series with weekly values for activity in sbrg
        """
        weekly_df = self.activity_data.groupby(["Year", "Week"])["Total time in Minutes"].sum()

        date_index = pd.Series(weekly_df.index.get_level_values(0)).astype(str) + "-" + pd.Series(weekly_df.index.get_level_values(1)).astype(str)
        
        
        weekly_df.index = date_index
        
        final_date_index = []
        for date in date_index:
            r = datetime.datetime.strptime(date + '-1', "%Y-%W-%w").date()
            final_date_index.append(r)
        final_date_index = pd.Series(final_date_index)
        weekly_df.index = final_date_index
        
        return weekly_df

    def weekly_minutes_split(self):
        # swim bike run gym activites

        weekly_df = self.activity_data.groupby(["Year", "Week", "Aktivitätstyp"])["Total time in Minutes"].sum()

        date_index = pd.Series(weekly_df.index.get_level_values(0)).astype(str) + "-" + pd.Series(
            weekly_df.index.get_level_values(1)).astype(str)
        acitivity_index = pd.Series(weekly_df.index.get_level_values(2)).astype(str)
        weekly_df.index = date_index

        final_date_index = []
        for date in date_index:
            r = datetime.datetime.strptime(date + '-1', "%Y-%W-%w").date()
            final_date_index.append(r)
        final_date_index = pd.Series(final_date_index).astype(str) + " " + acitivity_index
        weekly_df.index = final_date_index

        return weekly_df

    # filter for bike activities
    def bike_data(self):
        self.bike_data = self.activity_data[self.activity_data["Aktivitätstyp"]== "Radfahren"].reset_index(drop = True)
        return self.bike_data
    
    # filter for running activities
    def run_data(self):
        self.run_data = self.activity_data[self.activity_data["Aktivitätstyp"]== "Laufen"].reset_index(drop = True)
        return self.run_data
    
    # filter for swimming activities
    def swim_data(self):
        swim_styles = ["Freiwasserschwimmen", "Schwimmbadschwimmen"]
        self.swim_data = self.activity_data[self.activity_data["Aktivitätstyp"].isin(swim_styles)].reset_index(drop = True)
        return self.swim_data
    
    
def create_files_list():
    os.chdir(r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon\Aktivitaeten")
    act_list = []
    for file in glob.glob("*.*"):
        if str(file).count(".FIT")==1:
            act_list.append(file)
        if str(file).count(".fit")==1:
            act_list.append(file)
    #print(act_list)
    return act_list


def create_activity_csv_files(file_list, of, target_path):
    # create csv file for each activity
    # name will be: "Name of activity" + "Time"
    warnings.warn("Bei der Umwandlung gibt es noch Probleme mit der Uhrzeit. Verdacht auf Probleme bei Zeitumstellung-")

    from fitparse import FitFile
    import pandas as pd
    
    #not working examples
    nwa = []
    
    for file in file_list:
        #create empty df
        df = pd.DataFrame(columns=['enhanced_altitude','enhanced_speed','heart_rate','timestamp','temperature'])
        
        #create lists for target values
        alt_list = []
        speed_list = []
        hr_list = []
        time_list = []
        temp_list = []
        lat_list = []
        lon_list = []
        dist_list = []
        print(file)

        # parse trough file
        for record in FitFile(file).get_messages('record'):
            #print(record)


            # Go through all the data entries in this record
            for record_data in record:


                if record_data.name == "enhanced_altitude":
                    alt_list.append(record_data.value)

                elif record_data.name == "enhanced_speed":
                    speed_list.append(record_data.value)
                elif record_data.name == "heart_rate":
                    hr_list.append(record_data.value)
                elif record_data.name == "timestamp":
                    time_list.append(record_data.value)
                elif record_data.name == "temperature":
                    temp_list.append(record_data.value)
                elif record_data.name == "position_lat":
                    lat_list.append(record_data.value)
                elif record_data.name == "position_long":
                    lon_list.append(record_data.value)
                elif record_data.name == "distance":
                    dist_list.append(record_data.value)

        # create a dataframe to store all activity data
        df = pd.DataFrame([time_list,dist_list,   speed_list, alt_list,  hr_list , temp_list,lat_list,lon_list]).T
        df.columns=['timestamp',"distance", 'enhanced_speed','enhanced_altitude','heart_rate','temperature', "latitude", "longitude"]

        df["timestamp"] = pd.to_datetime(df["timestamp"]) + pd.to_timedelta(2, unit='h')
        
        #change of["Datum"] to datetime for making it searchable
        of["Datum"] = pd.to_datetime(of["Datum"])
        
        #if there is a mutual time in of["Datum"] and the first timestep of the current activity
        # choose activity name like this.
        print(df.head())
        if len(of[of["Datum"]==df["timestamp"][0]]) == 1:
            activity_name = of[of["Datum"]==df["timestamp"][0]]["Aktivitätstyp"].reset_index(drop = True)[0]
            activity_time = of[of["Datum"]==df["timestamp"][0]]["Datum"].reset_index(drop = True)[0]
        
        # if there is no mutual time in of["Datum"] and the first timestep of the current activity
        # make an entrance in nwa list.
        # and see whether there is exactly one activity listed in of that could match, but with a time error of 20 minutes
        # if so, choose this activity_name 
        
        # TODO implement a method that could cope with the problem of there being two possible activites in the timeslot.
        elif len(of[of["Datum"]==df["timestamp"][0]]) == 0 :
            nwa.append(file)
            print(nwa)
        
            if len(of[(of["Datum"]>(df["timestamp"][0]- pd.to_timedelta(20, unit='min')))& (of["Datum"]<(df["timestamp"][0]+ pd.to_timedelta(20, unit='min')))]) == 1:
                del nwa[-1]
                activity_name = of[(of["Datum"]>(df["timestamp"][0]- pd.to_timedelta(20, unit='min')))& (of["Datum"]<(df["timestamp"][0]+ pd.to_timedelta(20, unit='min')))]["Aktivitätstyp"].reset_index(drop = True)[0]
                activity_time = of[(of["Datum"]>(df["timestamp"][0]- pd.to_timedelta(20, unit='min')))& (of["Datum"]<(df["timestamp"][0]+ pd.to_timedelta(20, unit='min')))]["Datum"].reset_index(drop = True)[0]
                print(activity_name)
            




        output = pd.to_datetime(activity_time).strftime("%Y%m%d-%H%M%S")
        df.to_csv(os.path.join(target_path, str(activity_name + "_" + output  + "_"".csv")))
            
            
                
        
    if len(nwa)==0:
        print("keine unhandlebaren Aktivitäten")
    if len(nwa)>0:
        print(str(len(nwa)) + " unhandlebare Aktivitäten")
    return nwa


# adding time in zones to overview_file
def add_zone_to_of(of):
    
    Rzone1 = [95,114]
    Rzone2 = [114,133]
    Rzone3 = [133,152]
    Rzone4 = [152,171]
    Rzone5 = [171,190]

    Lzone1 = [98,117]
    Lzone2 = [117,137]
    Lzone3 = [137,156]
    Lzone4 = [156,176]
    Lzone5 = [176,195]
    
    of["zone0"]= 0
    of["zone1"]= 0
    of["zone2"]= 0
    of["zone3"]= 0
    of["zone4"]= 0
    of["zone5"]= 0
    
    
    
    
    count = 0
    
    for i in range(len(of)):
        activity_name = of["Aktivitätstyp"][50+i]
        activity_time = of["Datum"][50+i]
        try:
            os.chdir(r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon\Aktivitaeten_csv")
            test = activity_name + "_" + activity_time.strftime("%Y%m%d-%H%M%S") +".csv"
            df = pd.read_csv(activity_name + "_" + activity_time.strftime("%Y%m%d-%H%M%S") +".csv" , index_col = 0)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            count +=1
            
            if activity_name =="Radfahren":
                zones= []
                for z in range(len(df)):
                    if df["heart_rate"][z] <Rzone1[0]:
                        zones.append(0)
                    elif (df["heart_rate"][z] >=Rzone1[0]) & (df["heart_rate"][z] <Rzone1[1]):
                        zones.append(1)
                    elif (df["heart_rate"][z] >=Rzone2[0]) & (df["heart_rate"][z] <Rzone2[1]):
                        zones.append(2)
                    elif (df["heart_rate"][z] >=Rzone3[0]) & (df["heart_rate"][z] <Rzone3[1]):
                        zones.append(3)
                    elif (df["heart_rate"][z] >=Rzone4[0]) & (df["heart_rate"][z] <Rzone4[1]):
                        zones.append(4)
                    elif (df["heart_rate"][z] >=Rzone5[0]) & (df["heart_rate"][z] <Rzone5[1]):
                        zones.append(5)
                        
            elif activity_name =="Laufen":
                
                zones= []
                for z in range(len(df)):
                    if df["Herzfrequenz"][z] <Lzone1[0]:
                        zones.append(0)
                        
                    elif (df["heart_rate"][z] >=Lzone1[0]) & (df["heart_rate"][z] <Lzone1[1]):
                        zones.append(1)
                    elif (df["heart_rate"][z] >=Lzone2[0]) & (df["heart_rate"][z] <Lzone2[1]):
                        zones.append(2)
                    elif (df["heart_rate"][z] >=Lzone3[0]) & (df["heart_rate"][z] <Lzone3[1]):
                        zones.append(3)
                    elif (df["heart_rate"][z] >=Lzone4[0]) & (df["heart_rate"][z] <Lzone4[1]):
                        zones.append(4)
                    elif (df["heart_rate"][z] >=Lzone5[0]) & (df["heart_rate"][z] <Lzone5[1]):
                        zones.append(5)
                
                    
            
            
            
            
            
            df["zone"] = zones
            
            
            
            df["dauer_ts_seconds"] = 0
            for j in range(len(df)-1):
                
                df["dauer_ts_seconds"].iat[j] = (df["timestamp"][j+1] - df["timestamp"][j]).seconds
                
            
            zone0 = sum(df[df["zone"]==0]["dauer_ts_seconds"])/60
            zone1 = sum(df[df["zone"]==1]["dauer_ts_seconds"])/60
            zone2 = sum(df[df["zone"]==2]["dauer_ts_seconds"])/60
            zone3 = sum(df[df["zone"]==3]["dauer_ts_seconds"])/60
            zone4 = sum(df[df["zone"]==4]["dauer_ts_seconds"])/60
            zone5 = sum(df[df["zone"]==5]["dauer_ts_seconds"])/60
            
            print((zone1 + zone2 +  zone3 + zone4 + zone5))
            
            
            #update of:
            of["zone0"].iat[i] = zone0
            of["zone1"].iat[i] = zone1
            of["zone2"].iat[i] = zone2
            of["zone3"].iat[i] = zone3
            of["zone4"].iat[i] = zone4
            of["zone5"].iat[i] = zone5
            
            print("worked")
        except:
            print("not worked")
            continue
    return of
        


class activity_finder(object):
    def __init__(self):
        pass
    def list_files(self):
        """create a list containing the files inside the Aktivitaeten-Folder"""
        os.chdir(r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon\Aktivitaeten")
        self.act_list = []
        for file in glob.glob("*.*"):
            if str(file).count(".tcx")==1:
                self.act_list.append(file)
        print(self.act_list)
        return self.act_list
    
    def get_overview_file(self):
        """ Read overview file"""
        self.overview_file = File_Reader().read_file()
        #return self.overview_file
    
    def get_a_time(self):
        """ return time of activity to search for activity file"""
        #activity_time_series:
        self.a_time_ser = pd.to_datetime(self.overview_file["Datum"])
        #return self.a_time_ser 
        
    
    def add_a_file_to_o_file(self):
        #call get_overview_file function to add overview_file to self
        self.list_files()
        self.get_overview_file()
        self.get_a_time()
        
        # add column for activity_file_name
        self.overview_file["activity_dir"] = pd.Series()
        
        #Loop for all activites
        for activity in range(len(self.a_time_ser)):
            #print(self.a_time_ser)
            
            #extract each activity time
            activity_time = self.a_time_ser[activity]
            
            #print(os.getcwd())
            #print(self.act_list)
            
            #loop over each file in folder
            for file in self.act_list:
                #define handler
                handler = ggps.TcxHandler()
                
                #print(os.getcwd())
                #file =  str(os.getcwd()) + str(file)
                os.chdir(r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon\Aktivitaeten")
                #print(self.act_list)
                
                # parse over file
                handler.parse(file)
                
                #extract trackpoints
                trackpoints = handler.trackpoints
                
                #extract time in listed file and add two hours to change timezone
                file_time = (pd.to_datetime(trackpoints[0].values["time"]) + 
                             pd.to_timedelta(2, unit='h')).tz_localize(None)
                
                if file_time == activity_time:
                    #Add activity_dir to overview_file
                    
                    file_dir = pd.to_datetime(self.overview_file["Datum"][activity]).strftime("%Y%m%d-%H%M%S") +"_" +self.overview_file["Aktivitätstyp"][activity]
                    print(str(self.overview_file["Datum"][activity]) )
                    self.overview_file["activity_dir"][activity] = file_dir
                    
                    os.rename(file,str(file_dir) + ".tcx")
                    
        return self.overview_file
                
                
        
    