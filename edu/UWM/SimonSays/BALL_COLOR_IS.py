#Python program for a Nao Robot to ask to see a certain color object (for now balls) and confirm whether teh correct object was shown

#color filtering based on http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html 
#and http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/

#finding contours in images based on http://docs.opencv.org/trunk/d4/d73/tutorial_py_contours_begin.html#gsc.tab=0

#finding contour with largest area and drawing bounding rectangle based on comment to the follwoing stackoverflow question: http://stackoverflow.com/questions/16538774/dealing-with-contours-and-bounding-rectangle-in-opencv-2-4-python-2-7

import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
from naoqi import ALProxy
import vision_definitions

class NaoShowMeGame(object):
    def __init__(self,ip):
        self._IP=ip

        #Get access to Nao's camera
        self._video=ALProxy('ALVideoDevice',self._IP,9559)
        
        #Get access to Nao's text to speech
        self._tts=ALProxy("ALTextToSpeech",self._IP,9559)
        

        #set which camera to use: top camera=0 bottom camera=1
        camera=0 

        #set which resolution to get pictures in: kVGA=640x480 pixels
        resolution=vision_definitions.kVGA 

        #set which colorSpace to get images: kRGB is RGB values
        colorSpace=vision_definitions.kRGBColorSpace

        #set framerate: 1-30
        fps=10

        #subscribe to the camera
        self._cameraClient=self._video.subscribeCamera("detector", camera, resolution,colorSpace,fps)

        #set width and height of images
        self._imageWidth=640
        self._imageHeight=480

        #Set boundaries for colors...ideally there will be a way to automatically calibrate this
        self._GREEN_LOW=[60,70,70]
        self._GREEN_HIGH=[70,255,255]
        self._PINK_LOW=[163,100,120]
        self._PINK_HIGH=[167,255,255]
        self._RED_LOW=[175,150,150]
        self._RED_HIGH=[175,255,255]
        self._PURPLE_LOW=[117,51,50]
        self._PURPLE_HIGH=[128,255,255]
        self._YELLOW_LOW=[15,166,50]
        self._YELLOW_HIGH=[25,255,255]

        #put all the color ranges into a single list   
        self._boundaries=[(self._GREEN_LOW,self._GREEN_HIGH),(self._PINK_LOW,self._PINK_HIGH),(self._PURPLE_LOW,self._PURPLE_HIGH),(self._YELLOW_LOW,self._YELLOW_HIGH)]

    def playLoop(self):
        print "entering game loop"
        print "press ctrl+c to stop the program"
         # green="green"
        #toSay="show me the "+green+" ball"
       # self._tts.say(toSay)
        #try:
            #while true:
        image=None

        #get a picture from Nao
        result = self._video.getImageRemote(self._cameraClient)

        #make sure a picture is received before processing the image
        if result is None:
            print ("cannot get image")
        elif result[6] is None:
            print ("no image data string.")
        else:
            # the image is a bitstring, so reshape it into a multi-dimensional array with the RGB values of pixel with (x,y)
            # location at image[x][y]
            image=np.fromstring(result[6],np.uint8).reshape(480,640,3)

            # release image buffer locked by getImageLocal(). Not mandatory for GetImageRemote(), but recommended
            self._video.releaseImage(self._cameraClient)

            # Convert the image's RGB values to HSV (Hue, Saturation, Value)...at first I used RGB, but read that HSV can work well for filtering
            im=cv2.cvtColor(image,cv2.COLOR_RGB2HSV)

            #TO DO: this is where the main loop of the gam will go: give instruction, wait, check if instruction followed, give feedback

            # this is just for testing...finds all pixels between lower and upper values, finds contours and then draws a
            # square around the contour with the largest area (presumably that is the object we want)
            for(lower,upper) in self._boundaries:

                #convert the HSV values to the correct format
                lower=np.array(lower,dtype="uint8")
                upper=np.array(upper,dtype="uint8")

                #create a mask of the image where pixels that value in the range [lower,upper] are white and everything else is black
                mask=cv2.inRange(im,lower,upper)

                #use dilation and erosion to remove some of the noise in the mask
                kernel = np.ones((5,5),np.uint8)
                mask=cv2.dilate(mask,kernel,iterations=1)
                mask=cv2.erode(mask,kernel,iterations=1)
                
                #find boundaries between the black and white areas of the mask
                im2,contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #get the area of all the regions returned by cv2.findContours
                areas=[cv2.contourArea(c) for c in contours]
                #get the index of the region with the largest area
                if(len(areas)>0):
                    max_index=np.argmax(areas)
                    #get the contour with the largest area
                    cnt=contours[max_index]
                    
                    if (cv2.contourArea(cnt)>150):
                        
                        if np.all(lower==self._GREEN_LOW):
                            self._tts.say("That is green.")
                            print("green")
                        elif np.all(lower==self._PINK_LOW):
                            self._tts.say("That ball is pink.")
                            print("pink")
                        elif np.all(lower==self._PURPLE_LOW):
                            self._tts.say("I think that ball is purple.")
                            print("purple")
                        elif np.all(lower==self._YELLOW_LOW):
                            self._tts.say("That ball is yellow.")
                            print("yellow")
                            
                        #get a rectangle that surrounds the contour with the largest area...presumably this will be the object we are looking for
                        x,y,w,h=cv2.boundingRect(cnt)

                        #draw the rectangle on the original image
                        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
                        
                        #display the image
                        plt.imshow(image,)
                        plt.show()
        #except KeyboardInterrupt:
          #  print
            #print "Interrupted by user"
            #print "Stopping..."
    
    def cleanUp(self):
        #unsubscribe from the camera
        self._video.unsubscribe(self._cameraClient)

game=NaoShowMeGame("192.168.1.114")
game.playLoop()
game.cleanUp()
