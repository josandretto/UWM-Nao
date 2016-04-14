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
from copy import deepcopy

class NaoShowMeGame(object):
    def __init__(ip):
        self._IP=ip
        self.animatedSpeechProxy=ALProxy("ALAnimatedSpeechProxy")
        try:
          basicAwarenessProxy=ALProxy("ALBasicAwareness")
          basicAwarenessProxy.stopAwareness()
        except BaseException, err:
            print (err)
            
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
        GREEN_LOW=[60,70,70]
        GREEN_HIGH=[70,255,255]
        PINK_LOW=[163,100,120]
        PINK_HIGH=[167,255,255]
        RED_LOW=[171,143,0]
        RED_HIGH=[179,255,255]
        PURPLE_LOW=[113,51,73]
        PURPLE_HIGH=[169,255,255]
        YELLOW_LOW=[15,166,50]
        YELLOW_HIGH=[25,255,255]
        ORANGE_LOW=[0,147,114]
        ORANGE_HIGH=[179,255,255]
        NEON_YELLOW_LOW=[9,96,103]
        NEON_YELLOW_HIGH=[41,212,255]
        shapes=('circle','square','rectangle','triangle','pentagon')
        #put all the color ranges into a single list   
        #self.objectDict={'green':(GREEN_LOW,GREEN_HIGH,'ball'),
        #           'pink':(PINK_LOW,PINK_HIGH,'ball'),
        #           'purple':(PURPLE_LOW,PURPLE_HIGH,'ball'),
        #           'yellow':(YELLOW_LOW,YELLOW_HIGH,'ball'),
        #           'orange':(ORANGE_LOW,ORANGE_HIGH,'ball'),
        #           'red':(RED_LOW,RED_HIGH,'ball'),
        #           'neon yellow':(NEON_YELLOW_LOW,NEON_YELLOW_HIGH,'ball')}
        self.objectDict={
                    'yellow':(YELLOW_LOW,YELLOW_HIGH)}
    
        self.instructionList.append(('yellow','square',"Show me the yellow square."))
        self.instructionList.append(('yellow','triangle',"Show me the yellow square."))
        self.instructionList.append(('yellow','rectangle',"Show me the yellow square."))
        self.instructionList.append(('yellow','pentagon',"Show me the yellow square."))
def playLoop():
       # print "entering game loop"
       # print "press ctrl+c to stop the program

        try:
            while true:
                i=random.randint(0,len(self.instructionList)-1)
                simon=['','Simon says ']
                doesSimonSay=random.choice(simon)

                toSay=doesSimonSay+self.instructionList[i][1]
                self.animatedSpeechProxy.say(toSay)
                color=(self.instructionList[i][0],True if doesSimonSay=='Simon says ' else False)
 
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
                    lower=self.objectDict[color[0]][0]
                    upper=self.objectDict[color[0]][1]

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
                    cnt=None
                    shape=""
                    response=""
                    if(len(areas)>0):
                        max_index=np.argmax(areas)
                        #get the contour with the largest area
                        cnt=contours[max_index]
                        if (cv2.contourArea(cnt)>1000)
                            shape=self.get_shape(cnt)
                
                            if color[2]:
                                if color[1]==shape:
                                    response='That is correct! That is the '+color[0]+' '+color[1]+"."
                                else:
                                    response='Close! That is a'+color[0]+' '+shape+", but I wanted to see the "+color[0]+' '+color[1]
                            elif shape==color[1]:
                                    response='That is the right shape, but Simon did not say to show me the ' + color[0]+' '+shape+"."
                            else:
                                response='That is a '+color[0]+' '+shape+", but I did not ask to see a " + color[0]+' '+shape+"."

                        #get a rectangle that surrounds the contour with the largest area...presumably this will be the object we are looking for
                        x,y,w,h=cv2.boundingRect(cnt)

                        #draw the rectangle on the original image
                        tmp_image=deepcopy(image)
                        cv2.rectangle(tmp_image,(x,y),(x+w,y+h),(0,255,0),2)
                        #display the image
                        plt.imshow(tmp_image,)
                        plt.show()
                        print(str("LARGEST AREA: "+cv2.contourArea(cnt)))
                    else:
                        seen_color=list()
                        for k in self.objectDict.keys():
                            tmp_cnt=0
                            if not k == color[0]:
                                tmp_cnt=self.get_largest_contour(im,k)
                                if tmp_cnt is not None and cv2.contourArea(tmp_cnt)>2000:
                                    #get a rectangle that surrounds the contour with the largest area...presumably this will be the object we are looking for
                                    x,y,w,h=cv2.boundingRect(cnt)

                                    #draw the rectangle on the original image
                                    tmp_image=deepcopy(image)
                                    cv2.rectangle(tmp_image,(x,y),(x+w,y+h),(0,255,0),2)
                                    
                                    plt.imshow(tmp_image,)
                                    plt.show()
                                    seen_color.append(k)
                        colorStr=""
                        numSeen=len(seen_color)
                        if numSeen==1:
                            colorStr=seen_color[0]
                        elif len(seen_color)>1:
                            for i in range(0,len(seen_color)):
                                colorStr=colorStr+', '+seen_color[i]
                                if i==numSeen-2:
                                    colorStr=colorStr+' and'
                        if color[1] and numSeen<1:
                            response="Simon asked to see the "+color[0]+' '+self.objectDict[color[0]][2]+ " but Simon does't see it. Let's try again."
                            correct=False
                        elif numSeen<1 and not color[1]:
                            response="Great job, I did not say Simon says."
                        else:
                            response="Simon asked to see the "+color[0]+' '+self.objectDict[color[0]][2]+ " but I see "+colorStr+' '+self.objectDict[color[0]][2]+'s.'
                            correct=False
                    ledProxy=ALProxy("ALLeds")
                    sGroup = "FaceLeds"
                    if correct:
                        ledProxy.fadeRGB(sGroup,"green",3.0)
                    else:
                        ledProxy.fadeRGB(sGroup,"red",3.0)
                    self.animatedSpeechProxy.say(response)

            except KeyboardInterrupt:
                print "Interrupted by user"
                print "Stopping..."

            try:
                basicAwarenessProxy=ALProxy("ALBasicAwareness")
                basicAwarenessProxy.startAwareness()
            except BaseException, err:
                print(err)
    
    def get_shape(self, cnt):
        perimeter=cv2.arcLength(cnt,True)
        approximateShape = cv2.approxPolyDP(c,0.07*perimeter,True)
        shape="no idea"
        if len(approximateShape)==3:
            shape="triangle"
        elif len(approximateShape)==4:
            (x,y,w,h) = cv2.boundingRect(approximateShape)
            ar = w/float(h)
            shape = "square" if ar >=.95 or ar<=1.10 else "rectangle"
        elif len(approximateShape)==5:
            shape = "pentagon"

    def cleanUp():
        #unsubscribe from the camera
        self._video.unsubscribe(self._cameraClient)
        

game=NaoShowMeGame()
game.playLoop()
game.cleanUp()
