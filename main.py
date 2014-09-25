'''
Created on Aug 19, 2014

@author: MKB
'''
############################################################################################
# Importing
import cv2
import numpy as np
from copy import deepcopy
from random import shuffle
############################################################################################
'''
Function definitions
START
'''
############################################################################################
def loading_scr():
    #For fun
    screen = np.zeros((700,900,3),np.uint8)
    font = cv2.FONT_HERSHEY_COMPLEX
    size = 3
    colour = np.array([255,255,0])
    thickness = 2
    cv2.putText(screen,'Loading ...',(200,400),font,size,colour,thickness,cv2.CV_AA)
    
    cv2.namedWindow('loading',cv2.WINDOW_AUTOSIZE)
    cv2.imshow('loading',screen)
    return

def bg_sub(img):
    #Does the background subtraction and returns the foreground
    fgmask = fgbg.apply(img)
    #cv2.imshow('sub',fgmask)        #TEST
    cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel,dst = fgmask)
    cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,kernel,dst = fgmask)
    
    return fgmask

def define_var():
    #Defines all variables
    global kernel, cap, fgbg, pose, height, width, output_scr,score_bar,bot_bar, out_height
    global out_width, play_area,im_h,im_w,number,data_base,shape_len,normBase,passImg,normValue
    global passmarks,failImg
    
    cap = cv2.VideoCapture(0)
    height = cap.get(4)
    width = cap.get(3)
    
    fgbg = cv2.BackgroundSubtractorMOG2(history = 0,varThreshold=16,bShadowDetection = False)
    
    ker_size = 5
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ker_size,ker_size))
    
    data_base = ['0.jpg','1b.jpg','2.jpg']
    shape_len = len(data_base)
    shuffle(data_base)
    number = 1
    pose = cv2.imread(data_base[number])
    pose = cv2.cvtColor(pose,cv2.COLOR_BGR2GRAY)
    normBase = cv2.norm(np.zeros((height,width),np.uint8),pose)
    print normBase 
    print "NormValue"
    
    passImg = cv2.imread('pass.jpg')        #BGR image
    failImg = cv2.imread('fail.jpg')
    
    
    #The user-end screen
    out_height = 800
    out_width = 1200
    im_h = 768
    im_w = 1024
    output_scr = np.zeros((out_height,out_width,3),np.uint8)
    score_bar = np.ones((im_h,out_width-im_w,3),np.uint8) * 255
    bot_bar = np.zeros((out_height-im_h,out_width,3),np.uint8)
    play_area = np.zeros((im_h,im_w,3),np.uint8)
    output_scr[0:im_h,0:out_width-im_w,:] = score_bar
    output_scr[im_h:out_height,0:out_width,:] = bot_bar
    output_scr[0:im_h,out_width-im_w:out_width,:] = play_area
    cv2.putText(output_scr,'RESET',(1,50),cv2.FONT_HERSHEY_COMPLEX,1,np.array([255,0,0]),2,cv2.CV_AA)
    cv2.putText(output_scr,'PAUSE',(1,100),cv2.FONT_HERSHEY_COMPLEX,1,np.array([255,0,0]),2,cv2.CV_AA)
    cv2.putText(output_scr,'CHANGE',(1,150),cv2.FONT_HERSHEY_COMPLEX,1,np.array([255,0,0]),2,cv2.CV_AA)
    cv2.line(output_scr,(0,im_h-560),(out_width-im_w,im_h-560),(255,0,0),5)
	

def zoomer(img,mul):
    '''
    150 frames = 5 seconds
    100 frames to pass
    20 frames per milestone
    max size 1024x768
    initial size 640x480
    final ratio 1.6 
    '''
    
    global play_area
    temp = np.floor((width*mul,height*mul))
    temp = temp.astype(int)
    img = cv2.resize(img,(temp[0],temp[1]),interpolation = cv2.INTER_LINEAR)
    #top = im_h-np.shape(img)[0]
    #bottom = im_h - top - np.shape(img)[0]
    top = np.int(np.floor((im_h-np.shape(img)[0])/2))
    bottom = im_h - np.shape(img)[0] - top
    right = np.int(np.floor((im_w-np.shape(img)[1])/2))
    left = im_w - right - np.shape(img)[1]
    
    play_area = cv2.copyMakeBorder(img,top,bottom,left,right,cv2.BORDER_CONSTANT,value=[255,0,0] )
    output_scr[0:im_h,out_width-im_w:out_width] = play_area
    #cv2.imshow('play',play_area)
    return
    
def find_area(img):
	#returns the area of the person inside and outside the hole in the wall
	#Incomplete
    img = deepcopy(img)     #Prevent from modifying passed data 
	
    contours, heirarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)       #Modifies img
    area = 0
    if np.shape(contours)[0] > 0 :
        for cnt in contours:
            area = area + cv2.contourArea(cnt)
        
        return area
    
    else :
        return 0

def sub_im(img):
    global normBase,normValue,flag
    #Finds overlapping region
    img = deepcopy(img)
    #img = cv2.resize(img,(640,480))
    #ima = cv2.resize(ima,(640,480))
	#Overlapping region in white and non everlapping in gray
    score = cv2.addWeighted(img,0.5,pose,0.5,0)
    #score = cv2.subtract(ima,img)
    #print cv2.phaseCorrelate(np.float32(img),np.float32(pose))
	#find the area here
	#find_area(score)
	#find_area(img)
    normValue = cv2.norm(img,pose)
    print normValue
    score = cv2.cvtColor(score,cv2.COLOR_GRAY2BGR)
    
    sensitivity = normBase * 0.1
    flag = 0
    #converting overlaping region into green
    retval ,score[:,:,0] = cv2.threshold(score[:,:,0],240,0,cv2.THRESH_TOZERO_INV)
    if normValue < normBase-sensitivity :
        flag = 1
        retval , score[:,:,2] = cv2.threshold(score[:,:,2],240,0,cv2.THRESH_TOZERO_INV)
    
    #score = cv2.subtract(score,neg_green,dst = score,mask =msk)
    cv2.imshow('score',score)
    
    return score

def youpassed():
    global output_scr,mul,count,number,data_base,pose,shape_len,normBase,passmarks
    output_scr[0:im_h,out_width-im_w:out_width] = cv2.resize(passImg,(1024,768),interpolation = cv2.INTER_LINEAR)
    cv2.imshow('output',output_scr) 
    cv2.waitKey(0)
    if number == shape_len-1 :
        number = 0
    else :
        number += 1
	
    pose = cv2.imread(data_base[number])
    pose = cv2.cvtColor(pose,cv2.COLOR_BGR2GRAY)
    normBase = cv2.norm(np.zeros((480,640),np.uint8),pose)
    mul = 0.8
    count = 0
    clearSideBar()
    passmarks = 0

def youfailed():
	global output_scr,mul,count,number,data_base,pose,shape_len,normBase,passmarks
	output_scr[0:im_h,out_width-im_w:out_width] = cv2.resize(failImg,(1024,768),interpolation = cv2.INTER_LINEAR)
	cv2.imshow('output',output_scr)
	cv2.waitKey(0)
	clearSideBar()
	passmarks = 0
	mul=0.8
	count = 0
	if number == shape_len - 1 :
		number = 0
	else:
		number +=1
	pose = cv2.imread(data_base[number])
	pose = cv2.cvtColor(pose,cv2.COLOR_BGR2GRAY)
	normBase = cv2.norm(np.zeros((480,640),np.uint8),pose)
	
def clearSideBar():
	global output_scr,im_h,passmarks,im_w,out_width
	output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,0] = 255*np.ones(np.shape(output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,0]),np.uint8)
	output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,2] = 255*np.ones(np.shape(output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,2]),np.uint8)


def mouse_call(event,x,y,flags,param):
    global mul,count,number,data_base,pose,shape_len,normBase,passmarks
    if event == cv2.EVENT_LBUTTONDOWN:
        if (x < 110) :
            if (y<50) & (y>20) :
                print "RESET"
                mul = 0.8
                count = 0
                clearSideBar()
                passmarks = 0
                print mul,count
            if (y<100) & (y>80):
                print "pause"
                cv2.waitKey(0)
            if (y<150) & (y>130):
                print "Change shape"
                if number == shape_len-1 :
                    number = 0
                else :
                    number = number + 1
                pose = cv2.imread(data_base[number])
                pose = cv2.cvtColor(pose,cv2.COLOR_BGR2GRAY)
                normBase = cv2.norm(np.zeros((480,640),np.uint8),pose)
                mul = 0.8
                count = 0
                clearSideBar()
                passmarks = 0




############################################################################################
'''
Functions definitions 
STOP
'''
############################################################################################
############################################################################################
'''
MAIN Programme
START
'''
############################################################################################
loading_scr()
cv2.waitKey(500)
cv2.namedWindow('output',cv2.WINDOW_NORMAL)
cv2.setMouseCallback('output',mouse_call)
define_var()

mul = 0.8
count = 0
passmarks = 0
cv2.destroyWindow('loading')
while 1:
    _, frame = cap.read()
    frame = cv2.flip(frame,1)   
    bk = bg_sub(frame)                  #bk has the foreground only
    score = sub_im(bk)					#score differentiates between overlapping and non-overlapping region
    #mul = 1
    zoomer(score,mul)
    mul = mul+0.003						#Original 0.0015
    count += 1
    if flag == 1:
        #global output_scr
        passmarks += 1
        output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,0] = np.zeros(np.shape(output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,0]),np.uint8)
        output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,2] = np.zeros(np.shape(output_scr[im_h-passmarks*11-1:im_h,0:out_width-im_w,2]),np.uint8)
        
    
    if (count >200) & (passmarks <50):
        youfailed()
    
    #Checking is player matched the hole in the wall
    if passmarks > 50:
        youpassed()
    
    
    
    
    #cv2.namedWindow('output',cv2.WINDOW_NORMAL) #TEST
    cv2.imshow('output',output_scr)        #TEST
    cv2.namedWindow('frame',cv2.WINDOW_AUTOSIZE)
    cv2.imshow('frame',frame)
    progend = cv2.waitKey(2) & 0xFF    
    if progend == 27:
        break
    
cv2.destroyAllWindows()
cap.release()

