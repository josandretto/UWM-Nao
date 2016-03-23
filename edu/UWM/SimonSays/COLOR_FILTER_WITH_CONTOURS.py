import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
from naoqi import ALProxy
import vision_definitions

class NaoShowMeGame(object):
    def __init__(ip):
        self._IP=ip

        #Get access to Nao's camera
        self._video=ALProxy('ALVideoDevice',self._IP,9559)
        
        #Get access to Nao's text to speech
        self._tts=ALProxy("ALTextToSpeech",self._IP,9559)

        #set which camera to use: top camera=0 bottom camera=1
        self._camera=0 

        #set which resolution to get pictures in: kVGA=640x480 pixels
        self._resolution=vision_definitions.kVGA 

        #set which colorSpace to get images: kRGB is RGB values
        self._colorSpace=vision_definitions.kRGBColorSpace

        #set framerate: 1-30
        self._fps=10

        #subscribe to the camera
        self._cameraClient=video.subscribeCamera("detector", self._camera, self._resolution,self._colorSpace,self._fps)

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
        self._PURPLE_LOW=[120,50,50]
        self._PURPLE_HIGH=[122,255,255]
        self._YELLOW_LOW=[15,166,50]
        self._YELLOW_HIGH=[25,255,255]

        #put all the color ranges into a single list   
        self._boundaries=[(GREEN_LOW,GREEN_HIGH),(PINK_LOW,PINK_HIGH),(PURPLE_LOW,PURPLE_HIGH),(YELLOW_LOW,YELLOW_HIGH)]

    def playLoop():
        print "entering game loop"
        print "press ctrl+c to stop the program

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
                #kernel=np.ones((3,3),np.uint8)
                #mask=cv2.erode(mask,kernel,iterations=1)
                
                #find boundaries between the black and white areas of the mask
                im2,contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #get the area of all the regions returned by cv2.findContours
                areas=[cv2.contourArea(c) for c in contours]
                #get the index of the region with the largest area
                max_index=np.argmax(areas)
                #get the contour with the largest area
                cnt=contours[max_index]

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
    
    def cleanUp():
        #unsubscribe from the camera
        self._video.unsubscribe(self._cameraClient)

game=NaoShowMeGame("192.168.1.112")
game.playLoop
game.cleanUp()
