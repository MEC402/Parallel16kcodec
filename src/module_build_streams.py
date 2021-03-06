# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:14:45 2018

@author: IkerVazquezlopez
"""

import sys
import pickle
import cv2
import numpy as np

target_h = 8192
target_w = 16384
target_shape = (target_h, target_w, 3)




#%% MAIN METHOD


if len(sys.argv) != 3:
    print(len(sys.argv))
    print("Usage: python module_build_streams.py tracker_path obj_video_dir")
    raise Exception("Stream builder: main --> Input arguments != 3.") 
    
    
tracker_path = sys.argv[1]
obj_video_dir = sys.argv[2]
output_dir = obj_video_dir[:-8]

f = open(tracker_path, 'rb')
tracker = pickle.load(f)
f.close()

output_size = 0

loaded_videos = {}

n_frames = len(tracker.getFrames())

binary = open(output_dir + "output.16kc", 'wb')

output_size += binary.write(target_w.to_bytes(2, byteorder='big'))
output_size += binary.write(target_h.to_bytes(2, byteorder='big'))

target_back = cv2.imread(output_dir + "background.png")
_, target_back = cv2.imencode('.png', target_back)
target_back = target_back.tobytes()

output_size += binary.write(len(target_back).to_bytes(4, byteorder='big'))
output_size += binary.write(target_back)

output_size += binary.write(n_frames.to_bytes(8, byteorder='big'))


for frame in tracker.getFrames():
    n_objects = len(frame.getObjects())
    output_size += binary.write(n_objects.to_bytes(2, byteorder='big'))
    for obj in frame.getObjects():
        if not str(obj.getID()) in loaded_videos:
            obj_cap = cv2.VideoCapture(obj_video_dir + str(obj.getID()) + ".avi")
            loaded_videos[str(obj.getID())] = obj_cap
        ret, v_obj_frame = loaded_videos[str(obj.getID())].read()
       
        if not ret:
            loaded_videos[str(obj.getID())].release()
            continue
        h, w, _ = v_obj_frame.shape
        x, y, _, _ = obj.getBbox()
        
        output_size += binary.write(obj.getID().to_bytes(2, byteorder='big'))
        output_size += binary.write(x.to_bytes(2, byteorder='big'))
        output_size += binary.write(y.to_bytes(2, byteorder='big'))
        output_size += binary.write(w.to_bytes(2, byteorder='big'))
        output_size += binary.write(h.to_bytes(2, byteorder='big'))
        
        _, img = cv2.imencode('.jpg', v_obj_frame)
        img = img.tobytes()
        output_size += binary.write(len(img).to_bytes(4, byteorder='big'))
        output_size += binary.write(img)
        
    
    
print("File size: " + str(output_size))
binary.close()
    

