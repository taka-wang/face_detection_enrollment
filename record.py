#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# by Taka Wang

import base64
from imutils.video import VideoStream
import numpy as np
import cv2
import time
import paho.mqtt.client as mqtt

def init_mqtt(broker_address):
    """Return a connected MQTT client"""
    clnt = mqtt.Client("frame-sender")
    clnt.connect(broker_address)
    return clnt

def detection(min_confidence=0.50, client=None):
    """Do face detection and send image to MQTT broker"""
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")

    # initialize the video stream and warmup the camera sensor
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    send_this_frame = True

    while True:
        frame = vs.read()
        # scale down to speed up
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
        # grab the frame dimensions
        (h, w) = small_frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(small_frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    
        # face detection inference
        net.setInput(blob)
        detections = net.forward()

        for i in range(0, detections.shape[2]):
            # check face's confidence
            confidence = detections[0, 0, i, 2]
            if confidence < min_confidence:
                continue

            # compute the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Reset box size for display
            startX *= 4
            startY *= 4
            endX *= 4
            endY *= 4
    
            # draw the bounding box of the face along with the confidence
            text = "{:.2f}%".format(confidence * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 2)
            
            # TODO: save the image to the disk

        # show the output frame
        cv2.imshow("Frame", frame)
        # No matter face or not, send the encoding frame to the MQTT broker
        if client:
            if send_this_frame:
                # Scale down for speed
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                res = bytearray(cv2.imencode(".jpeg", small_frame)[1])
                client.publish("myimage", base64.b64encode(res))  # publish
            send_this_frame = not send_this_frame
        
        # break from the loop
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    # cleanup
    cv2.destroyAllWindows()
    vs.stop()

if __name__ == "__main__":
    print("To exit, press ^C")
    test_client = init_mqtt("127.0.0.1")
    detection(0.95, test_client)
