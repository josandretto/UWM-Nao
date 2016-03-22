import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
from naoqi import ALProxy
import vision_definitions

class NaoShowMeGame(object):
    def __init__(ip):
        self._IP=ip
        self._video=ALProxy('ALVideoDevice',self._IP,9559)
        self._tts=ALProxy("ALTextToSpeech",self._IP,9559)
        self._camera=0 #top camera=0 bottom camera=1
        self._resolution=vision_definitions.kVGA 
        self._colorSpace=vision_definitions.kRGBColorSpace
        self.fps=10
        self._cameraClient=video.subscribeCamera("detector", camera, resolution,colorSpace,fps)
        self.imageWidth=640
        self.imageHeight=480

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
        self._boundaries=[(GREEN_LOW,GREEN_HIGH),(PINK_LOW,PINK_HIGH),(PURPLE_LOW,PURPLE_HIGH),(YELLOW_LOW,YELLOW_HIGH)]
        self._kernel = np.ones((5,5),np.uint8)

    def playLoop():
        print "entering game loop"
        print "press ctrl+c to stop the program
        
        image=None
        result = self._video.getImageRemote(self._cameraClient)
        if result is None:
            print ("cannot get image")
        elif result[6] is None:
            print ("no image data string.")
        else:
            image=np.fromstring(result[6],np.uint8).reshape(480,640,3)
            self._video.releaseImage(self._cameraClient)
                    
            im=cv2.cvtColor(image,cv2.COLOR_RGB2HSV)
                
            for(lower,upper) in self._boundaries:
                lower=np.array(lower,dtype="uint8")
                upper=np.array(upper,dtype="uint8")
                mask=cv2.inRange(im,lower,upper)
                mask=cv2.dilate(mask,self._kernel,iterations=1)
                
                imgray=mask
                ret,thresh=cv2.threshold(imgray,127,255,0)
                im2,contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                areas=[cv2.contourArea(c) for c in contours]
                max_index=np.argmax(areas)
                cnt=contours[max_index]
                            
                x,y,w,h=cv2.boundingRect(cnt)
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
                
                plt.imshow(image,)
                plt.show()
        
    def cleanUp():
        self._video.unsubscribe(self._cameraClient)

game=NaoShowMeGame("192.168.1.112")
game.playLoop
game.cleanUp()
