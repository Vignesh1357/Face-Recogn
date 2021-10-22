import os
from os import listdir
from os.path import isfile, join

from django.shortcuts import render, redirect
from matplotlib import pyplot as plt

from .forms import UserRegisterForm, UserUpdateForm
from django.contrib import messages
from .models import Person, Img
import pyttsx3
import cv2
import numpy as np
from django.contrib.auth.decorators import login_required
from django_facematch import settings
import boto3
from botocore.exceptions import NoCredentialsError



@login_required
def home(request):
    person_obj = Person.objects.get(user=request.user)
    if request.method == 'POST':
        usn_form = UserUpdateForm(request.POST, instance=request.user.person)

        if request.POST.get('usn'):
            if usn_form.is_valid():
                usn_form.save()
                messages.success(request, 'Saved')
                return redirect('app-home')

        if request.POST.get('analyze'):

            usn_form = UserUpdateForm(request.POST, instance=request.user.person)

            face_classifier = cv2.CascadeClassifier(
                str(settings.BASE_DIR) + '/django_facematch/haarcascade_frontalface_default.xml')

            def face_extractor(img):

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                if faces is ():
                    return None
                for (x, y, w, h) in faces:
                    cropped_face = img[y:y + h, x:x + w]
                return cropped_face

            # Update the link to the folder inside bucket
            print(request.user.person.usn)
            cap = cv2.VideoCapture(
                'https://django-facedetect.s3.ap-south-1.amazonaws.com/videos/' + request.user.person.usn)
            count = 0

            while True:

                ret, frame = cap.read()
                if frame is None:
                    messages.error(request, "Coudn't analyze, Please make sure your face is clearly visible")
                    break
                elif face_extractor(frame) is not None:
                    count += 1
                    face = cv2.resize(face_extractor(frame), (200, 200))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                    file_name_path = str(settings.BASE_DIR) + '\\media\\' + person_obj.usn + str(count) + '.jpg'

                    cv2.imwrite(file_name_path, face)
                    img_obj = Img()
                    img_obj.img = person_obj.usn + str(count) + '.jpg'
                    img_obj.save()

                    def upload_to_aws(local_file, bucket, s3_file):
                        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID ,
                                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

                        try:
                            s3.upload_file(local_file, bucket, s3_file)
                            print("Upload Successful")
                            return True
                        except FileNotFoundError:
                            print("The file was not found")
                            return False
                        except NoCredentialsError:
                            print("Credentials not available")
                            return False

                    uploaded = upload_to_aws(file_name_path,settings.AWS_STORAGE_BUCKET_NAME,
                                             'pictures/' + person_obj.usn + '/' + person_obj.usn + str(count) + '.jpg')
                    cv2.putText(face, str(count), (200, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("face cropper", face)

                else:
                    pass

                if cv2.waitKey(1) == 13 or count == 15:
                    messages.success(request, 'Collecting samples complete')
                    break

            cap.release()
            cv2.destroyAllWindows()



    else:
        usn_form = UserUpdateForm(instance=request.user.person)

    context = {
        'usn_form': usn_form,
        'person_obj': person_obj,
        'user': request.user,
        'user_usn': request.user.person.usn
    }

    return render(request, 'facedetect/home.html', context)


def mainHome(request):
    if request.method == 'POST':
        if request.POST.get('home'):
            return redirect('app-home')

        elif request.POST.get('recognize'):
            return redirect('recognize')
    return render(request, 'facedetect/mainHome.html')


def recognize(request):
    if request.method == 'POST':
        usn = request.POST.get('usn')
        if usn == '':
            messages.error(request, 'Please Enter USN to proceed ')
        if request.POST.get('usn'):
            try:
                Person.objects.get(usn=usn)
            except:
                messages.error(request, "This USN/Video of this user doen't exist in database")
                return redirect('home')

        if usn:
            context = {
                'usn': usn,
            }
            return render(request, 'facedetect/recognize.html', context)

        if request.POST.get('detect_face'):

            q = 1
            x = 0
            c = 0
            m = 0
            d = 0
            while q <= 2:
                usn = request.POST.get('detect_face')

                data_path = "https://django-facedetect.s3.ap-south-1.amazonaws.com/pictures/" + usn + '/'

                Training_data, Lebels = [], []

                for i in range(1, 15):
                    path = data_path + usn + str(i) + '.jpg'

                    images = plt.imread(path, cv2.IMREAD_GRAYSCALE)
                    Training_data.append(np.asarray(images, dtype=np.uint8))
                    Lebels.append(i)

                Lebels = np.asarray(Lebels, dtype=np.int32)

                model = cv2.face.LBPHFaceRecognizer_create()
                model.train(np.asarray(Training_data), np.asarray(Lebels))

                q += 1

            face_classifier = cv2.CascadeClassifier(
                str(settings.BASE_DIR) + '/django_facematch/haarcascade_frontalface_default.xml')

            model.save('model.h5')
            model.save('model.tflite')

            def speak(audio):
                engine.say(audio)
                engine.runAndWait()

            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            engine.setProperty("voice", voices[0].id)
            engine.setProperty("rate", 140)
            engine.setProperty("volume", 1000)

            def face_detector(img, size=0.5):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)

                if faces is ():
                    return img, []
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    roi = img[y:y + h, x:x + w]
                    roi = cv2.resize(roi, (200, 200))

                return img, roi

            # Update the link to the folder inside bucket

            cap = cv2.VideoCapture(
                'https://django-facedetect.s3.ap-south-1.amazonaws.com/detect_vids/' + usn)
            g=0
            while True:
                print(g)
                g+=1
                ret, frame = cap.read()
                image, face = face_detector(frame)

                try:
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                    id, result = model.predict(face)

                    if result < 500:
                        confidence = int((1 - (result) / 300) * 100)
                        display_string = str(confidence)
                        cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 0))
                        print(confidence)
                    if confidence >= 80:
                        cv2.putText(image, "on", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
                       
                        x += 1
                    else:
                        cv2.putText(image, "off", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
                     
                        c += 1
                except:
                    cv2.putText(image, "Face not found", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
                  
                    d += 1
                    pass

                if cv2.waitKey(1) == 13 or x == 10 or c == 30 or d == 20:
                    print(x,c,d)
                    break
            cap.release()
            cv2.destroyAllWindows()

            if x >= 5:
                messages.success(request, "Your face is matching with database :)")

            else:
                messages.error(request, "Your face is not matching...please retry")
            return redirect('home')

    return render(request, 'facedetect/recognize.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to login')
            return redirect('app-home')
    else:
        form = UserRegisterForm()
    return render(request, 'facedetect/registerform.html', {'form': form})
