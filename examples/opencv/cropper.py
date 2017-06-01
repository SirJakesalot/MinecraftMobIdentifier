import cv2
import os
import numpy as np

backgroundMaskRanges = (50, 120), (29, 255), (60, 255)

def readImg(path):
    return cv2.imread(path)

def writeImg(path, img, overwrite=False):
    if not os.path.exists(path) or overwrite:
        cv2.imwrite(path, img)
    else:
        print('[INFO] path already exists', path)

def mask(img, rng1, rng2, rng3):
    '''Apply a mask to image'''
    lowerMask = np.array([rng1[0], rng2[0], rng3[0]])
    upperMask = np.array([rng1[1], rng2[1], rng3[1]])
    return cv2.inRange(img, lowerMask, upperMask)

def rmBackground(img):
    '''Remove the sky and grass from the image'''
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    backgroundMask = mask(hsv, (50, 120), (29, 255), (60, 255))
    bg = cv2.bitwise_and(img, img, mask=backgroundMask)
    return img - bg

def rmNoise(img):
    '''Remove small noise edges'''
    kernel = np.ones((5,5), np.uint8)
    opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    median = cv2.medianBlur(opening, 5)
    return median

def getEdges(img):
    '''Find edges in the image'''
    return cv2.Canny(img, 50, 50)

def resize(img, dim, aspect=False):
    '''Resize the image'''
    oldW, oldH = len(img[0]), len(img)
    if aspect and oldW < oldH:
        ratio = float(dim)/float(oldH)
        w, h = int(oldW * ratio), dim
    elif aspect and oldH > oldW:
        ratio = dim / oldW
        w, h = (dim, int(oldH * ratio))
    else:
        w, h = dim , dim
    return cv2.resize(img, (w, h))

def mergeContours(contours):
    '''Turn all cv2 contours into a large bounding box'''
    xs, ys = [], []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # if cv2.contourArea(c) > 10:
        xs.append(x)
        xs.append(x + w)
        ys.append(y)
        ys.append(y + h)
    if not xs or not ys:
        return None
    xs.sort()
    ys.sort()
    return xs[0], ys[0], xs[-1] - xs[0], ys[-1] - ys[0]

def cropMob(img, show=False):
    '''Return parts of the image that are not the background'''
    # remove grass and sky
    noBackground = rmBackground(img)
    # remove noise
    noNoise = rmNoise(noBackground)
    # edge detection
    edges = getEdges(noNoise)
    _, contours, _ = cv2.findContours(edges,
                                      cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)

    x, y, w, h = mergeContours(contours)
    crop = img[y:y+h, x:x+w]
    if show:
        cv2.imshow('noBackground', noBackground)
        cv2.imshow('noNoise', noNoise)
        cv2.imshow('edges', edges)
        cv2.imshow('crop', crop)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return crop

