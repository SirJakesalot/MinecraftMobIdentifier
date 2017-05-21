# import the necessary packages
import cv2
import numpy as np

hh = 'Hue High'
hl = 'Hue Low'
sh = 'Saturation High'
sl = 'Saturation Low'
vh = 'Value High'
vl = 'Value Low'
wnd = 'Colorbars'

def nothing(x):
    pass

img = cv2.imread(r'C:\Users\armentrout\Documents\PyCharm\MinecraftObjectRecognition\agents\imgs\mobs\70.jpg')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.namedWindow('Colorbars')

def update(x):
    #read trackbar positions for each trackbar
    hul=cv2.getTrackbarPos(hl, wnd)
    huh=cv2.getTrackbarPos(hh, wnd)
    sal=cv2.getTrackbarPos(sl, wnd)
    sah=cv2.getTrackbarPos(sh, wnd)
    val=cv2.getTrackbarPos(vl, wnd)
    vah=cv2.getTrackbarPos(vh, wnd)

    #make array for final values
    HSVLOW=np.array([hul,sal,val])
    HSVHIGH=np.array([huh,sah,vah])

    #create a mask for that range
    mask = cv2.inRange(hsv, HSVLOW, HSVHIGH)
    res = cv2.bitwise_and(img, img, mask=mask)
    cv2.imshow(wnd, res)

# Begin Creating trackbars for each
cv2.createTrackbar(hl, wnd, 0, 179, update)
cv2.createTrackbar(hh, wnd, 0, 179, update)
cv2.createTrackbar(sl, wnd, 0, 255, update)
cv2.createTrackbar(sh, wnd, 0, 255, update)
cv2.createTrackbar(vl, wnd, 0, 255, update)
cv2.createTrackbar(vh, wnd, 0, 255, update)

update(None)
while (1):
    k = cv2.waitKey(0)
    if k == ord('q'):
        break

cv2.destroyAllWindows()