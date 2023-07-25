#!/usr/bin/env python3
import cv2
import optparse


def getArguments():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--destination", dest="destination")
    parser.add_option("-f", "--filename", dest="filename")
    (option, args) = parser.parse_args()
    if not option.destination:
        option.destination = "temp"
    if not option.filename:
        option.filename = "temp"
    return option


def captureImage(folder, name):
    vid = cv2.VideoCapture(0)
    while vid.isOpened():
        ret, frame = vid.read()
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Press 'C' to Close Camera", (10, 440), font, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Press 'SpaceBar' to Capture Image", (10, 470), font, 0.7, (0, 255, 255), 2)
        k = cv2.waitKey(1)
        if k == ord('c'):
            break
        elif k % 256 == 32:
            imgName = "." + folder + "/" + name + ".jpg"
            cv2.imwrite(imgName, frame)
            break
        cv2.imshow("Capture Image", frame)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    options = getArguments()
    captureImage(options.destination, options.filename)
