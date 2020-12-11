from Garmin_Handler.Handler import Overview_File_Reader, Activity_Handler, add_zone_to_of, create_activity_csv_files, create_files_list
import matplotlib.pyplot as plt

activities = Overview_File_Reader().read_file()
#print(activities.columns)

file_list = create_files_list()
target_path = r"C:\Users\nicoj\netcase\1-Start-UP\Triathlon\Aktivitaeten_csv"
create_activity_csv_files(file_list, activities,target_path)