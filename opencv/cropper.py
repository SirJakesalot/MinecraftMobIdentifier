# Useful Links
# http://www.pyimagesearch.com/2014/01/22/clever-girl-a-guide-to-utilizing-color-histograms-for-computer-vision-and-image-search-engines/

import cv2
import os
import numpy as np
import time
import Queue

backgroundMaskRanges = (50, 120), (29, 255), (60, 255)

def readImg(path):
    '''Read image from disk'''
    return cv2.imread(path)

def convertGray(img):
    '''Convert image to grayscale'''
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def isGrayScale(img):
    '''Simple check to see if image is grayscale'''
    return type(img[0][0]) == np.uint8

def writeImg(path, img, overwrite=False):
    '''Write image to disk'''
    if not os.path.exists(path) or overwrite:
        cv2.imwrite(path, img)
    else:
        print('[CROPPER INFO] path already exists', path)

def getImgHist(img):
    '''Calculate the histogram of values of the image'''
    if isGrayScale(img):
        hist = cv2.calcHist([img], [0], None, [256], [0,256])
    else:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv],
                            [0,1,2],
                            None,
                            (8,8,8),
                            [0,180,0,256,0,256])
    return cv2.normalize(hist, hist)

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
    '''Crop a single bounding box from the image'''
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

def matrixBFS(img, visited, start):
    cropping = []
    q = Queue.Queue()
    q.put(start)

    while q.qsize():
        indx = q.get()
        x, y = indx
        if indx not in visited and any(img[x][y]):
            visited.add(indx)
            additions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            for x,y in additions:
                if 0 <= x <= len(img) - 1 and 0 <= y <= len(img[0]) - 1:
                    q.put((x,y))
            cropping.append(indx)
    return cropping

def cropMobs(img, show=False):
    '''Crop multiple bounding boxes from and image'''
    # remove grass and sky
    noBackground = rmBackground(img)
    # remove noise
    noNoise = rmNoise(noBackground)
    # edge detection
    edges = getEdges(noNoise)
    _, contours, _ = cv2.findContours(edges,
                                      cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)
    cx, cy, cw, ch = mergeContours(contours)
    allMobs = noBackground[cy:cy+ch, cx:cx+cw]
    visited, croppings = set(), []
    for i in range(len(allMobs)):
        for j in range(len(allMobs[0])):
            if any(allMobs[i][j]) and (i,j) not in visited:
                # pixel value is not black and has not been visited yet
                # perform BFS at this pixel
                cropping = matrixBFS(allMobs, visited, (i,j))
                minX, maxX, minY, maxY = float('inf'), -1, float('inf'), -1
                if len(cropping) > 50:
                    for y, x in cropping:
                        if x < minX:
                            minX = x
                        if x > maxX:
                            maxX = x
                        if y < minY:
                            minY = y
                        if y > maxY:
                            maxY = y
                    y, x, h, w = cy + minY, cx + minX, maxY - minY, maxX - minX
                    croppings.append(img[y:y+h, x:x+w])
    if show:
        cv2.imshow('noBackground', noBackground)
        cv2.imshow('noNoise', noNoise)
        cv2.imshow('edges', edges)
        cv2.imshow('allMobs', allMobs)
        for i, crop in enumerate(croppings):
            cv2.imshow(str(i), crop)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return croppings

def segmentCrop(img):
    h, w = img.shape[0], img.shape[1]
    boxW, boxH = int(w/3), int(h/3)
    segments = []
    segments.append(img[:boxH, :boxW])
    segments.append(img[:boxH, boxW:2*boxW])
    segments.append(img[:boxH, 2*boxW:])

    segments.append(img[boxH:2*boxH, :boxW])
    segments.append(img[boxH:2*boxH, boxW:2*boxW])
    segments.append(img[boxH:2*boxH, 2*boxW:])

    segments.append(img[2*boxH:, :boxW])
    segments.append(img[2*boxH:, boxW:2*boxW])
    segments.append(img[2*boxH:, 2*boxW:])
    return segments

def findCentroids(labels, predictions, dim):
    adjacent_segments = {'0': [(1, 'right'), (3, 'down'), (4, 'downright')],
                              '1': [(0, 'left'), (2, 'right'), (3, 'downleft'), (4, 'down'), (5, 'downright')],
                              '2': [(1, 'left'), (4, 'downleft'), (5, 'down')],
                              '3': [(0, 'up'), (1, 'upright'), (4, 'right'), (6, 'down'), (7, 'downright')],
                              '4': [(0, 'upleft'), (1, 'up'), (2, 'upright'), (3, 'left'), (5, 'right'),
                                    (6, 'downleft'), (7, 'down'), (8, 'downright')],
                              '5': [(1, 'upleft'), (2, 'up'), (4, 'left'), (7, 'downleft'), (8, 'down')],
                              '6': [(3, 'up'), (4, 'upright'), (7, 'right')],
                              '7': [(3, 'upleft'), (4, 'up'), (5, 'upright'), (6, 'left'), (8, 'right')],
                              '8': [(4, 'upleft'), (5, 'up'), (7, 'left')]}
    move_value = {'up': (0, 1),
                       'down': (0, -1),
                       'left': (-1, 0),
                       'right': (1, 0),
                       'upleft': (-1, 1),
                       'upright': (1, 1),
                       'downleft': (-1, -1),
                       'downright': (1, -1)}
    centroids = dict()
    confidences = np.sum(predictions, axis=0)
    for i, confidence in enumerate(confidences):
        if confidence >= 1:
            max_indx = np.argmax(predictions[:,i]).item()
            centroidx = 0.5 + (max_indx%3)
            centroidy = 2.5 - (max_indx/3)
            for segment, direction in adjacent_segments[str(max_indx)]:
                direction_tuple = move_value[direction]
                segment_confidence = predictions[segment][i].item() * 0.5
                centroidx += direction_tuple[0] * segment_confidence
                centroidy += direction_tuple[1] * segment_confidence
            centroids[labels[i]] = (int(round(centroidx * dim)), int(round(centroidy * dim)))
    return centroids

if __name__ == '__main__':
    img = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\-mobs\originals\100.jpg')
    #img = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\test.jpg')

    cropMob(img, show=True)
    # start = time.time()
    # croppings = cropMobs(img, show=False)
    # for crop in croppings:
    #     cv2.imshow('cropping', crop)
    #     for i, segment in enumerate(segmentCrop(crop)):
    #         cv2.imshow('c' + str(i), segment)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #
    # print(time.time() - start)