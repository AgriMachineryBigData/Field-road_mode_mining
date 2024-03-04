# -*- coding: gbk -*-

import os
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import numpy as np
cit1=20


def calculate_distance(previous_lat, previous_long, current_lat, current_long):
    previous_lat = float(previous_lat)
    previous_long = float(previous_long)
    current_lat = float(current_lat)
    current_long = float(current_long)
    
    R = 6371000.0
    
    previous_lat_rad = radians(previous_lat)
    previous_long_rad = radians(previous_long)
    current_lat_rad = radians(current_lat)
    current_long_rad = radians(current_long)
    
    dlong = current_long_rad - previous_long_rad
    dlat = current_lat_rad - previous_lat_rad
    
    a = sin(dlat / 2)**2 + cos(previous_lat_rad) * cos(previous_lat_rad) * sin(dlong / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    
    return distance

def moving_average(num, lst):
    ma = [0 for x in range(len(lst))]
    ma[0] = np.mean([lst[0]])
    for i in range(1, len(lst)):
        if i <= num:
            ma[i] = np.mean(lst[:i+1])
        else:
            ma[i] = np.mean(lst[i-num:i+1])
    return ma

input_folder = ''
output_folder = ''

os.makedirs(output_folder, exist_ok=True)

                    
selected_columns = ['timestamp', 'longitude', 'latitude', 'speed', 'bearing', 'type']
date_format = "%H:%M:%S"

for file_name in os.listdir(input_folder):
    if file_name.endswith('.xlsx'):
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)

        df = pd.read_excel(input_file_path)
        
        #delete time repeat point
        time_delete = []
        all_time_point = []
        timestamp = df['timestamp']
        for j in range(len(timestamp)):
            if timestamp[j] in all_time_point:
                time_delete.append(j)
            else:
                all_time_point.append(timestamp[j])

        df = df.drop(time_delete)
        df = df.reset_index(drop=True)
       
        #delete space repeat point
        longitude = df['longitude']
        latitude = df['latitude']
        speed = df['speed']      
        space_delete = []
        all_space_point = []    
        for k in range(len(speed)):
            point = []
            point = [longitude[k], latitude[k], speed[k]]
            if point in all_space_point:
                space_delete.append(k)
            else:
                all_space_point.append(point)

        df = df.drop(space_delete)
        df = df.reset_index(drop=True)
        
        # calculate new distance 
        longitude_list = df['longitude']
        latitude_list = df['latitude']
        speed_list = df['speed']
        distance_list = [0 for x in range(len(speed_list))]
        for p in range(len(list(speed_list))):
            if p == 0:
                distance_list[0] = 0
            else:
                distance_list[p] = round(calculate_distance(latitude_list[p - 1], longitude_list[p - 1], latitude_list[p], longitude_list[p]), 2)          
        df["distance"] = distance_list
        
        distance_average = moving_average(cit1, distance_list)
        for r in range(len(list(distance_list))):
            distance_average[r] = round(distance_average[r], 2) 
        
        #delete Scattered point  
        scattered_delete = []        
        for q in range(len(distance_list)):
            if q>0 and distance_average[q] <= 0.5:
                scattered_delete.append(q)
                continue            
               
        df = df.drop(scattered_delete)
        df = df.reset_index(drop=True) 
        df = df.drop('distance', axis=1)
        
        # calculate new distance 
        new_longitude_list = df['longitude']
        new_latitude_list = df['latitude']
        new_speed_list = df['speed']
        new_distance_list = [0 for x in range(len(new_speed_list))]  
        for t in range(len(list(new_speed_list))):
            if t == 0:
                new_distance_list[0] = 0
            else:
                new_distance_list[t] = round(calculate_distance(new_latitude_list[t - 1], new_longitude_list[t - 1], new_latitude_list[t], new_longitude_list[t]), 2)     
        
        df["distance"] = new_distance_list
        
        #delete drifting point
        new_distance = df["distance"]
        final_speed = df['speed']       
        drifiting_point_delete = []
        for m in range(len(final_speed)):
            if m == 1 and new_distance[m] > 6*new_distance[m+1]:
                drifiting_point_delete.append(m-1)
                continue           
            elif m == len(final_speed)-2 and new_distance[m+1] > 6*new_distance[m]:
                drifiting_point_delete.append(m+1)
                continue         
            elif m>=2 and m<= len(final_speed)-3:               
                if new_distance[m] > 6*new_distance[m-1] and new_distance[m+1] > 6*new_distance[m+2]:
                    drifiting_point_delete.append(m)
                    continue
        df = df.drop(drifiting_point_delete)
        df = df.reset_index(drop=True)                
        df = df.drop('distance', axis=1)
        
        print(f'finished')  
        
        df[selected_columns].to_excel(output_file_path, index=False)