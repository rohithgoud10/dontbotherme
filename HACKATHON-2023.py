#!/usr/bin/env python
# coding: utf-8

# In[1]:


import googlemaps
from datetime import datetime, timedelta

gmaps = googlemaps.Client(key='AIzaSyCYjSicJwcb6z9oSdohtoiAHvfA4po847w')


# In[2]:


from k_means_constrained import KMeansConstrained
import csv
import numpy as np
import requests
import pprint,sys
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

api_key = "AIzaSyCYjSicJwcb6z9oSdohtoiAHvfA4po847w"
labels = []
commuters =[]
clusters = []
drivers = []
x_coord = []
y_coord = []
com_cluster_dict = {}
driver_commuter_dict = {}


# In[3]:


clf = KMeansConstrained(
     n_clusters=37,
     size_min=1,
     size_max=3,
     random_state=0
)
commuter_data = np.genfromtxt('final_Commuter_locations.csv',delimiter=',',dtype='float')
#print(data)
clf.fit_predict(commuter_data)
#clf.cluster_centers_.tofile("cluster_centers.csv",sep = ',')
with open("cluster_centers.csv","w") as f:
	mywriter = csv.writer(f, delimiter=',')
	mywriter.writerows(clf.cluster_centers_)

# print(clf.cluster_centers_)


# In[4]:


data = np.genfromtxt("final_Cab_locations.csv",delimiter=',',dtype='float')
for i in data:
    drivers.append(str(str(i[0])+', '+str(i[1])))
for i in clf.cluster_centers_:
    clusters.append(str(str(i[0])+', '+str(i[1])))
for i in commuter_data:
    x_coord.append(i[0])
    y_coord.append(i[1])
    commuters.append(str(str(i[0])+', '+str(i[1])))
index = 0
for i in clf.labels_:
    comm = gmaps.reverse_geocode(commuters[index])[0]['formatted_address']
    #print("comm: " + str(comm))
    index = index + 1
    arr = [comm]
    #arr = [commuters[np.argwhere(clf.labels_ == i)]]
    if clusters[i] in com_cluster_dict:
        com_cluster_dict[clusters[i]] += arr
    else :
        com_cluster_dict[clusters[i]] = arr
clusters = clusters[:15]
drivers = drivers[:15]
url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
cd_dict = {}
for cluster in clusters:
    drivers_string = str('|'.join(drivers))
    #print(cluster)
    #print(drivers_string)
    full_url = url + 'origins=' + cluster + '&destinations=' + drivers_string + '&key=' + api_key
    #print(full_url)
    r = requests.get(full_url)
    x = r.json()
    for elements in x['rows']:
        distanceList = list()
        index = 0
        min_index = 0
        min_distance = sys.maxsize
        for distance in elements['elements']:
            value = distance['distance']['value']
            if (value < min_distance):
                min_distance = value
                min_index = index
            index = index + 1

            cd_dict[cluster] = drivers[min_index]
        del drivers[min_index]


for cluster in cd_dict.keys():
    driver_commuter_dict[cd_dict[cluster]] = com_cluster_dict[cluster]
print("DRIVER ----> COMMUTERS MAPPING : ")
pprint.pprint(driver_commuter_dict)


# In[5]:


fig = plt.figure(figsize=(25,25))
ax = fig.add_subplot(111)
scatter = ax.scatter(x_coord,y_coord,c=clf.labels_,cmap='Accent',s=200)
for i,j in clf.cluster_centers_:
    ax.scatter(i,j,s=300,c='red',marker='+')
ax.set_xlabel('Lattitude',fontsize=22)
ax.set_ylabel('Longitude',fontsize=22)
plt.colorbar(scatter)

fig.show()


# In[6]:


import pprint
waypoints = ['Chicka Hosahalli Bus Stop, Bettakote, Karnataka '
                           '562129, India',
                           '66, Budigere, Budigere Amanikere, Karnataka '
                           '562129, India','4Q76+MC Thimmasandra, Karnataka, India'
                           ]

print(gmaps.reverse_geocode(('12.72955143, 77.86663687'))[0]['formatted_address'])
print(gmaps.reverse_geocode(('12.936785852536188, 77.69089255086674'))[0]['formatted_address'])
results = gmaps.directions(gmaps.reverse_geocode(('13.16971, 77.69980939'))[0]['formatted_address'],
                                     gmaps.reverse_geocode(('12.936785852536188, 77.69089255086674'))[0]['formatted_address'],
                                     waypoints= waypoints)


# In[7]:


from PIL import Image
marker_points = []
waypoints = []
for leg in results[0]["legs"]:
    leg_start_loc = leg["start_location"]
    marker_points.append(f'{leg_start_loc["lat"]},{leg_start_loc["lng"]}')
    for step in leg["steps"]:
        end_loc = step["end_location"]
        waypoints.append(f'{end_loc["lat"]},{end_loc["lng"]}')
last_stop = results[0]["legs"][-1]["end_location"]
marker_points.append(f'{last_stop["lat"]},{last_stop["lng"]}')
#print("WAYPOINT: " + str(waypoints))     
markers = [ "color:blue|size:mid|label:" + chr(65+i) + "|" 
           + r for i, r in enumerate(marker_points)]
result_map = gmaps.static_map(
                 center=waypoints[20],
                 scale=2, 
                 zoom=11,
                 size=[1280, 1280], 
                 format="jpg", 
                 maptype="roadmap",
                 markers=markers,
                 path="color:0x0000ff|weight:2|" + "|".join(waypoints))
with open("driving_route_map_1.jpg", "wb") as img:
    for chunk in result_map:
        img.write(chunk)
im = np.array(Image.open("driving_route_map_1.jpg"))


# In[8]:


plt.figure(figsize = (20,20))
plt.imshow(im, interpolation='nearest', aspect='auto')


# In[ ]:




