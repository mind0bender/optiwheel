import cv2
import numpy as np
import dlib
from math import hypot
from requests import post, get
from time import sleep

predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")

server_url = "http://localhost:8080"


def length(p1, p2):
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def boundingRect(eyeLandmarks):
    xs = list(map(lambda eyeLandmark: eyeLandmark[0], eyeLandmarks))
    ys = list(map(lambda eyeLandmark: eyeLandmark[1], eyeLandmarks))

    return ((min(xs), min(ys)), (max(xs), max(ys)))


def averagePoints(p1, p2):
    return (
        int((p1[0] + p2[0]) / 2),
        int((p1[1] + p2[1]) / 2),
    )


def getEyePoints(gray, face):
    landmarks = predictor(gray, face)

    points = []
    for i in range(36, 48):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        points.append((x, y))

    return points


def getLidRatio(eyeLandmarks):
    cv2.polylines(
        frame,
        [np.array(eyeLandmarks)],
        isClosed=True,
        color=(170, 255, 34),
        thickness=1,
    )

    eyeHorizontalP1, eyeHorizontalP2 = eyeLandmarks[0], eyeLandmarks[3]
    eyeVerticalP1, eyeVerticalP2 = (
        averagePoints(eyeLandmarks[1], eyeLandmarks[2]),
        averagePoints(eyeLandmarks[4], eyeLandmarks[5]),
    )
    eyeRatio = length(eyeHorizontalP1, eyeHorizontalP2) / length(
        eyeVerticalP1, eyeVerticalP2
    )

    cv2.line(frame, eyeHorizontalP1, eyeHorizontalP2, (170, 255, 34), 1)
    cv2.line(frame, eyeVerticalP1, eyeVerticalP2, (170, 255, 34), 1)

    return eyeRatio


def sendDir(direction):
    vector = {
        "x": 0,
        "y": 0,
    }
    match direction:
        case "left":
            vector["x"] = -1
        case "right":
            vector["x"] = 1
        case "forward":
            vector["y"] = 1
        case "neutral":
            pass
    print(vector)

    post("http://localhost:8080", json=vector)


def drawEye(eyePoints):
    leftEye = eyePoints[:6]
    rightEye = eyePoints[6:]

    boundingLeft = boundingRect(leftEye)
    boundingRight = boundingRect(rightEye)

    leftWindow = frame[
        boundingLeft[0][1] : boundingLeft[1][1], boundingLeft[0][0] : boundingLeft[1][0]
    ]
    rightWindow = frame[
        boundingRight[0][1] : boundingRight[1][1],
        boundingRight[0][0] : boundingRight[1][0],
    ]
    cv2.imshow("left", leftWindow)
    cv2.imshow("right", rightWindow)

    cv2.rectangle(frame, *boundingRect(leftEye), (170, 255, 34), 1)
    cv2.rectangle(frame, *boundingRect(rightEye), (170, 255, 34), 1)

    leftEyeRatio = getLidRatio(leftEye)
    rightEyeRatio = getLidRatio(rightEye)

    diff = leftEyeRatio - rightEyeRatio
    avgRatio = (leftEyeRatio + rightEyeRatio) / 2
    dir = "neutral"
    if avgRatio > 4.75:
        print("neutral")
    else:
        if diff > 0.25:
            dir = "left"
            print("left")
        elif diff < -0.25:
            dir = "right"
            print("right")
        else:
            dir = "forward"
            print("forward")

    sendDir(dir)


videoIdx = int(input("Enter video index: "))
cap = cv2.VideoCapture(videoIdx)
detector = dlib.get_frontal_face_detector()

while True:
    _, frame = cap.read()

    if not _:
        print("Could not open camera")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    for face in faces:
        x, y = face.left(), face.top()
        x1, y1 = face.right(), face.bottom()
        cv2.rectangle(frame, (x, y), (x1, y1), (170, 255, 34), 2)

        eyePoints = getEyePoints(gray, face)
        drawEye(eyePoints)
    frame = cv2.flip(frame, 1)
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        cap.release()
        cv2.destroyAllWindows()
