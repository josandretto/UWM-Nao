import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
from naoqi import ALProxy
import vision_definitions
from naoqi import ALModule

NaoShowMeGame=None
class NaoShowMeGame(ALModule):
    def __init__(self,ip):
        ALModule.__init__(self,name)
        
       # self._IP=ip

        #Get access to Nao's camera
       # self._video=ALProxy('ALVideoDevice',self._IP,9559)
        self._video=ALProxy("ALVideoDevice")
        #Get access to Nao's text to speech
        #self._tts=ALProxy("ALTextToSpeech",self._IP,9559)
        self._tts=ALProxy("ALTextToSpeech")

        self.memory=ALProxy("ALMemory")
        self.memory.subscribeToEvent('FrontTactilTouched','NaoShowMeGame','OnHeadFrontTouched')
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
        GREEN_LOW=[60,70,70]
        GREEN_HIGH=[70,255,255]
        PINK_LOW=[163,100,120]
        PINK_HIGH=[167,255,255]
        RED_LOW=[175,150,150]
        RED_HIGH=[175,255,255]
        PURPLE_LOW=[117,51,50]
        PURPLE_HIGH=[128,255,255]
        YELLOW_LOW=[15,166,50]
        YELLOW_HIGH=[25,255,255]
        self._boundaries={"GREEN":(GREEN_LOW,GREEN_HIGH),"PINK":(PINK_LOW,PINK_HIGH),"RED":(RED_LOW,RED_HIGH),"PURPLE":(PURPLE_LOW,PURPLE_HIGH),"YELLOW":(YELLOW_LOW,YELLOW_HIGH)}
        self.playLoop()
        
    def OnHeadFrontTouched(self,key,value,message):
        self.memory.unsubscribeToEvent('FrontTactilTouched','NaoShowMeGame')
        tts.say("My Head Was Touched")
        self.memory.subscribeToEvent('FrontTactilTouched','NaoShowMeGame','OnHeadFrontTouched')

    def playLoop (self):
        print "entering game loop"
        print "press ctrl+c to stop the program"
        for k,v in self._boundaries:
            target=k
            toSay="show me the "+target+" ball"
            self._tts.say(toSay)
            checkForAction(target)
            toSay="ready for the next one?"

    def checkForAction(self, target)
        try:
            while true:
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

                    lower=self._boundaries[target][0]
                    upper=self._boundaries[target][1]

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
                                self._tts.say("Awesome, that is the green ball.")
                                print("green")
                                break
        except KeyboardInterrupt:
            print
            print "Interrupted by user"
            print "Stopping..."
    
    def cleanUp(self):
        #unsubscribe from the camera
        self._video.unsubscribe(self._cameraClient)
        
def main (ip,port):
    myBroker = ALBroker("myBroker","0.0.0.0",0,ip,port)
    global NaoShowMeGame
    NaoShowMeGame = NaoShowMeGame("192.168.1.114")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main("192.168.1.114", 9559)
