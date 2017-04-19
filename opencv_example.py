import cv2
import sys

# init cascades
face_cascade_path = '/Users/Macintosh/Desktop/opencv/data/haarcascades/haarcascade_frontalface_default.xml'
eye_cascade_path = '/Users/Macintosh/Desktop/opencv/data/haarcascades/haarcascade_eye.xml'
faceCascade = cv2.CascadeClassifier(face_cascade_path)
eyeCascade = cv2.CascadeClassifier(eye_cascade_path)

# capture video
vid = cv2.VideoCapture(0)

while True:
    # grayscale video capture
    ret, frame = vid.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30,30)
    )

    # draw bounding boxes of faces on frame
    for (x,y,w,h) in faces:
        img = cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eyeCascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0,255,0), 2)
        

    # show image with drawn bounding boxes
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# clean up
vid.release()
cv2.destroyAllWindows()
