import math
import sys
import os
from os import path
import numpy as np
import cv2
import json
import requests

longitude = sys.argv[1] # "-99.1743234"
latitude = sys.argv[2] # "19.3658212"
img_zoom = 19
if len(sys.argv) > 3:
  img_zoom = int(sys.argv[3])

resolution = 0.00

res_ini = 156412
level = 0
while level < 25:
  if level == img_zoom:
    resolution = res_ini
    break
  else:
    res_ini = res_ini / 2
    level += 1
  
url = "https://maps.googleapis.com/maps/api/staticmap?center=" + latitude + "," + longitude + "&zoom=" + str(img_zoom) + "&size=1000x1000&format=png&maptype=roadmap&style=feature:administrative.land_parcel%7Cvisibility:off&style=feature:landscape.man_made%7Celement:geometry.stroke%7Ccolor:0xf50505&style=feature:landscape.natural%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:road%7Cvisibility:off&style=feature:transit%7Cvisibility:off"

base_path = "/tmp/"
file_path = "img_" + str(latitude) + "_" + str(longitude) + "_" + str(img_zoom) + ".png"

try:
  r = requests.get(url, allow_redirects=True)
  open(base_path + file_path, 'wb').write(r.content)

  im = cv2.imread(base_path + file_path)
except:
  print("Error on load image: " + file_path)
  sys.exit(1)

  trans_mask = im[:,:] == [0,0,0]
  im[trans_mask] = 255
 
  trans_mask = im[:,:] == [254, 248, 241]
  im[trans_mask] = 0
  trans_mask = im[:,:] == [240, 240, 240]
  im[trans_mask] = 0
 
  im = im[0:618, 0:640]

  if im.max() == 0:
    print(json.dumps({"successCode": 1, "count": 0, "max_area": 0, "mean_area": 0}))
    sys.exit(0)

  im2 = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY);
  
  try:
    opencv_threshold = 90
    ret,th1 = cv2.threshold(im2, opencv_threshold, 255, cv2.THRESH_BINARY_INV)
    aa,contours,hie = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  except:
    print("Error on threshold")
    sys.exit(1)

  count = 0
  areas = np.array([])
  
  if not hie is None:
    hie = hie[0]

  i = 0
  d_cont = []
  for cont in contours:
    if len(cont) < 3:
      continue
    
    area = cv2.contourArea(cont)
    area_m2 = area*resolution*resolution
    
    if area_m2 < 20:
      continue
      
    i += 1
    areas = np.append(areas, area_m2)
    
    count += 1
    
    d_cont.append(cont)

  #im_res = cv2.drawContours(im, d_cont, -1, (0, 255, 0), 2)
  
  max_area = 0
  mean_area = 0.00

  if len(areas) > 0:
    max_area = areas.max()
    mean_area = areas.mean()
    
  os.remove(base_path + file_path)

  print(json.dumps({"successCode": 1, "count": count, "max_area": max_area, "mean_area": mean_area, "center_area": center_area}))
