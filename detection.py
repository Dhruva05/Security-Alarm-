import cv2
import face_recognition
from deepface import DeepFace
import threading
from twilio.rest import Client
import keys
import time


cap = cv2.VideoCapture(0)

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0 

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

reference_img = cv2.imread('D:\Python Projects\Alarm\WIN_20240407_15_24_10_Pro.jpg')

face_match = False
unknown_start_time = None
def check_face(frame):
    global face_match
    try: 
        if DeepFace.verify(frame, reference_img.copy())['verified']:
            face_match = True
        else:
            face_match = False  
    except ValueError:
        face_match = False

def message():
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body = "Unrecognized Person At Your Door",
        from_= keys.twilio_number,
        to=keys.target_num,
    )
        

while True:
    ret, frame = cap.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if ret:
        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()#frame --> gray_frame
            except ValueError:
                pass
        counter += 1

        if face_match:
            cv2.putText(frame, 'Face Match', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3,)
            unknown_start_time = None
        else:
            cv2.putText(frame, 'Face Not Match', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(50,50))#frame --> gray_frame
            if len(faces) > 0:
                if unknown_start_time is None:
                    unknown_start_time = time.time()
                else:
                    if time.time() - unknown_start_time > 120:
                        threading.Thread(target=message).start()
                        unknown_start_time = None
                        message()
    

                    
        cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
