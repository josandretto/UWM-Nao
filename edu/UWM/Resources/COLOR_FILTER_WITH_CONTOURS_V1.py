import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
from naoqi import ALProxy
import vision_definitions

def main(port,ip):
    IP=ip
    PORT=port
    proxy=ALProxy('ALVideoDevice','192.168.1.112',9559)
    camera=0 #top camera=0 bottom camera=1
    resolution=vision_definitions.kVGA 
    colorSpace=vision_definitions.kRGBColorSpace
    fps=10
    client=proxy.subscribeCamera("detector", camera, resolution,colorSpace,fps)
    width=640
    height=480
    #image = np.zeros((height,width,3),np.uint8)
    image=None
    result = proxy.getImageRemote(client)
    if result is None:
        print ("cannot get image")
    elif result[6] is None:
        print ("no image data string.")
    else:
        image=np.fromstring(result[6],np.uint8).reshape(480,640,3)
        proxy.releaseImage(client)
        proxy.unsubscribe(client)
        cv2.imwrite('C:\Users\Joanna SanDretto\Downloads\calibration.png',cv2.cvtColor(image,cv2.COLOR_RGB2BGR))
    
    plt.imshow(image,)
    plt.show()
    im=cv2.cvtColor(image,cv2.COLOR_RGB2HSV)
    GREEN_LOW=[60,70,70]
    GREEN_HIGH=[70,255,255]
    PINK_LOW=[163,100,120]
    PINK_HIGH=[167,255,255]
    RED_LOW=[175,150,150]
    RED_HIGH=[175,255,255]
    PURPLE_LOW=[120,50,50]
    PURPLE_HIGH=[122,255,255]
    YELLOW_LOW=[15,166,50]
    YELLOW_HIGH=[25,255,255]
    boundaries=[(GREEN_LOW,GREEN_HIGH),(PINK_LOW,PINK_HIGH),(PURPLE_LOW,PURPLE_HIGH),(YELLOW_LOW,YELLOW_HIGH)]
    kernel = np.ones((5,5),np.uint8)

    for(lower,upper) in boundaries:
        lower=np.array(lower,dtype="uint8")
        upper=np.array(upper,dtype="uint8")
        mask=cv2.inRange(im,lower,upper)
        mask=cv2.dilate(mask,kernel,iterations=1)
       
        plt.imshow(mask,)
        plt.show()
        
        imgray=mask
        ret,thresh=cv2.threshold(imgray,127,255,0)
        im2,contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        areas=[cv2.contourArea(c) for c in contours]
        max_index=np.argmax(areas)
        cnt=contours[max_index]
                
        x,y,w,h=cv2.boundingRect(cnt)
        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
       # img=cv2.drawContours(image,contours,-1,(0,255,0),3)

        plt.imshow(image,)
        plt.show()

if __name__ == "__main__" :
    main("192.168.1.112",9559)
