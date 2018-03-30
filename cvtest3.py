import cv2
import numpy as np
import operator
import os
from imutils import contours
import imutils

MIN_CONTOUR_AREA = 50

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

class ContourWithData():

    npaContour = None           # contour
    boundingRect = None         # bounding rect for contour
    intRectX = 0                # bounding rect top left corner x location
    intRectY = 0                # bounding rect top left corner y location
    intRectWidth = 0            # bounding rect width
    intRectHeight = 0           # bounding rect height
    fltArea = 0.0               # area of contour

    def calculateRectTopLeftPointAndWidthAndHeight(self):               # calculate bounding rect info
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
        if self.fltArea > MIN_CONTOUR_AREA and self.intRectHeight > 15 and self.intRectHeight <25 and self.intRectWidth<19 and self.intRectHeight>15:
            return True        # much better validity checking would be necessary
        return False

###################################################################################################
#class trainword():
def current_word(x_t):
    allContoursWithData = []                # declare empty lists,
    validContoursWithData = []              # we will fill these shortly

    try:
        npaFlattenedImages = np.loadtxt("es.txt", np.float32)                 # read in training images
    except:
        print ("error unable to open es.txt, exiting program\n")
        os.system("pause")
        return

    try:
        npaClassifications = np.loadtxt("s.txt", np.float32)                  # read in training classifications
    except:
        print ("error, unable to open s.txt, exiting program\n")
        os.system("pause")
        return


    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    imgTestingNumbers = cv2.transpose(x_t)          # read in testing numbers image
    orig = imgTestingNumbers.copy()

    if imgTestingNumbers is None:                           # if image was not read successfully
        print ("error: image not read from file \n\n")        # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                        # and exit function (which exits program)

    imgGray = cv2.cvtColor(imgTestingNumbers[0:35 ,0:288], cv2.COLOR_BGR2GRAY)       # get grayscale image
        #imgGray = cv2.cvtColor(imgTestingNumbers[35:70 ,0:288], cv2.COLOR_BGR2GRAY)
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    # blur

                                                        # filter image from grayscale to black and white
    imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
                                      255,                                  # make pixels that pass the threshold full white
                                      1,       # use gaussian rather than mean, seems to give better results
                                      1,                # invert so foreground will be white, background will be black
                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
                                      2)                                    # constant subtracted from the mean or weighted mean

    imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

    imgContours, npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_LIST,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points


    for (i, c) in enumerate(npaContours):
        orig = contours.label_contour(orig, c, i, color=(240, 0, 159))

    for method in ("left-to-right"):
        # sort the contours
        (npaContours, boundingBoxes) = contours.sort_contours(npaContours, method=method)






    for npaContour in npaContours:                             # for each contour
        contourWithData = ContourWithData()                                             # instantiate a contour with data object
        contourWithData.npaContour = npaContour                                         # assign contour to contour with data
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
        allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data

    for contourWithData in allContoursWithData:                 # for all contours
        if contourWithData.checkIfContourIsValid():             # check if valid
            validContoursWithData.append(contourWithData)       # if so, append to valid contour list
        # end if
    # end for

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right

    strFinalString = ""         # declare final string, this will have the final number sequence by the end of the program

    for contourWithData in validContoursWithData:            # for each contour
                                                # draw a green rect around the current char
        cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                        (contourWithData.intRectX, contourWithData.intRectY),     # upper left corner
                        (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),      # lower right corner
                        (0, 255, 0),              # green
                        2)                        # thickness

        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                           contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

        strCurrentChar = str(chr(int(npaResults[0][0])))                                             # get character from results

        strFinalString = strFinalString + strCurrentChar            # append current char to full string
            # end for

#    print ("\n" + strFinalString + "\n")                  # show the full string

        #cv2.imshow("imgTestingNumbers", imgTestingNumbers)      # show input image with green boxes drawn around found digits
        #cv2.waitKey(0)                                          # wait for user key press

            #cv2.destroyAllWindows()             # remove windows from memory
    word=strFinalString
    return word

def next_word(x_t):
    allContoursWithData = []                # declare empty lists,
    validContoursWithData = []              # we will fill these shortly

    try:
        npaClassifications = np.loadtxt("s.txt", np.float32)                  # read in training classifications
    except:
        print ("error, unable to open s.txt, exiting program\n")
        os.system("pause")
        return

    try:
        npaFlattenedImages = np.loadtxt("es.txt", np.float32)                 # read in training images
    except:
        print ("error, unable to open es.txt, exiting program\n")
        os.system("pause")
        return


    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    imgTestingNumbers = cv2.transpose(x_t)          # read in testing numbers image
    orig = imgTestingNumbers.copy()

    if imgTestingNumbers is None:                           # if image was not read successfully
        print ("error: image not read from file \n\n")        # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                        # and exit function (which exits program)

    imgGray = cv2.cvtColor(imgTestingNumbers[35:71 ,0:288], cv2.COLOR_BGR2GRAY)       # get grayscale image
    #imgGray = cv2.cvtColor(imgTestingNumbers[35:70 ,0:288], cv2.COLOR_BGR2GRAY)
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    # blur

                                                        # filter image from grayscale to black and white
    imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
                                      255,                                  # make pixels that pass the threshold full white
                                      1,       # use gaussian rather than mean, seems to give better results
                                      1,                # invert so foreground will be white, background will be black
                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
                                      2)                                    # constant subtracted from the mean or weighted mean

    imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

    imgContours, npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_LIST,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

#    cv2.imshow('imgBlurred',imgGray)
    cv2.waitKey(0)
    for c in npaContours:
        if cv2.contourArea(c)>100:
            [x,y,w,h] = cv2.boundingRect(c)
            cv2.rectangle(imgGray,(x,y),(x+w,y+h),(100,100,100),2)
#            cv2.imshow('img',imgGray)
            cv2.waitKey(0)
    for (i, c) in enumerate(npaContours):
        orig = contours.label_contour(orig, c, i, color=(240, 0, 159))

#    print("passed enumerate")
    for method in ("left-to-right"):
        # sort the contours
        (npaContours, boundingBoxes) = contours.sort_contours(npaContours, method=method)



    for npaContour in npaContours:                             # for each contour
        contourWithData = ContourWithData()                                             # instantiate a contour with data object
        contourWithData.npaContour = npaContour                                         # assign contour to contour with data
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
        allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data

    for contourWithData in allContoursWithData:                 # for all contours
        if contourWithData.checkIfContourIsValid():             # check if valid
            validContoursWithData.append(contourWithData)       # if so, append to valid contour list
            # end if
        # end for

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right

    strFinalString = ""         # declare final string, this will have the final number sequence by the end of the program

    for contourWithData in validContoursWithData:            # for each contour
                                                # draw a green rect around the current char
        cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                        (contourWithData.intRectX, contourWithData.intRectY+35),     # upper left corner
                        (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight+35),      # lower right corner
                        (0, 255, 0),              # green
                        2)                        # thickness

        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                           contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

        strCurrentChar = str(chr(int(npaResults[0][0])))                                             # get character from results

        strFinalString = strFinalString + strCurrentChar            # append current char to full string
            # end for

#    print ("\n" + strFinalString + "\n")                  # show the full string

    #cv2.imshow("imgTestingNumbers", imgTestingNumbers)      # show input image with green boxes drawn around found digits
    #cv2.waitKey(0)                                          # wait for user key press

     #cv2.destroyAllWindows()             # remove windows from memory
    word=strFinalString
    return word

###################################################################################################
"""__name__ == "__main__":
    current_word()
# end if
"""
