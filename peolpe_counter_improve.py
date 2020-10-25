
import numpy as np
import cv2
import Person
import time
import sqlite3
import requests
import threading
import time
import sched, time
import datetime

from datetime import datetime
import random
resource = 0
is_resource_safe = True
cnt_in=0
cnt_out=0
count_in=0
count_out=0
state=0


def printThread(x):
    # upload data thread
    global resource
    global is_resource_safe
    global cnt_in
    global cnt_out
    global count_in
    global count_out
    global state
    while True:
        time.sleep(5)

        def send_backend():
            data = {
                'location': 'ICT',
                'human_in': cnt_in,
                'human_out': cnt_out
            }
            url = 'http://127.0.0.1:8000/api/counting/20/'
            x = requests.put(url, data=data)
            print(x.text, 'this is x ')

        print('call send')
        send_backend()
        print('called send')
        s = sched.scheduler(time.time, time.sleep)

def printThread2(x):
    # camera thread
    global resource
    global is_resource_safe
    global cnt_in
    global cnt_out
    global count_in
    global count_out
    global state
    while True:
                cnt_in=0
                cnt_out=0
                count_in=0
                count_out=0
                state=0

                font = cv2.FONT_HERSHEY_SIMPLEX
                persons = []
                rect_co = []
                max_p_age = 1
                pid = 1
                val = []

                video=cv2.VideoCapture("counting_test.avi")
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

                w = video.get(3)
                h = video.get(4)
                print("ความกว้างเดิมของวิดีโอคือ")
                print(int(w))
                print("ความสูงเดิมของวิดีโอคือ")
                area = h*w
                print(int(h))
                areaTHreshold = area/500
                print('Area Threshold', areaTHreshold)

                #คำนวณตำแหน่งของเส้น
                line_up = int(1*(h/2))
                line_down = int(1*(h/2.1))
                up_limit = int(.5*(h/4))
                down_limit = int(3.2*(h/4))
                print ("red line y:",str(line_down))
                print ("Green line y:", str(line_up))

                line_down_color = (0,0,255)
                line_up_color = (0,255,0)
                pt1 = [0, line_down]
                pt2 = [w, line_down]
                pts_L1 = np.array([pt1,pt2], np.int32)
                pts_L1 = pts_L1.reshape((-1,1,2))
                pt3 = [0, line_up]
                pt4 = [w, line_up]
                pts_L2 = np.array([pt3,pt4], np.int32)
                pts_L2 = pts_L2.reshape((-1,1,2))

                pt5 = [0, up_limit]
                pt6 = [w, up_limit]
                pts_L3 = np.array([pt5,pt6], np.int32)
                pts_L3 = pts_L3.reshape((-1,1,2))
                pt7 =  [0, down_limit]
                pt8 =  [w, down_limit]
                pts_L4 = np.array([pt7,pt8], np.int32)
                pts_L4 = pts_L4.reshape((-1,1,2))

                # fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
                fgbg = cv2.createBackgroundSubtractorKNN()

                kernel = np.ones((3,3),np.uint8)
                kerne2 = np.ones((5,5),np.uint8)
                kerne3 = np.ones((11,11),np.uint8)

                while(video.isOpened()):
                    ret,frame=video.read()
                    if frame is None:
                        break
                    #การคัดแยกพื้นหลังของแอปพลิเคชัน
                    gray = cv2.GaussianBlur(frame, (21, 21), 0)
                    # cv2.imshow('GaussianBlur', frame)
                    # cv2.imshow('GaussianBlur', gray)
                    fgmask = fgbg.apply(gray)
                    fgmask2 = fgbg.apply(gray)

                    try:
                        ret,imBin= cv2.threshold(fgmask,220,250,cv2.THRESH_BINARY)
                        ret,imBin2 = cv2.threshold(fgmask2,220,250,cv2.THRESH_BINARY)
                        cv2.imshow('imBin', imBin2)
                        #เปิดการทำงาน (การกัดกร่อน -> การขยายตัว) เพื่อขจัดเสียงรบกวน
                        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kerne3)
                        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kerne3)
                        #ปิดการทำงาน (การขยายตัว -> การกัดกร่อน) เพื่อเชื่อมต่อพื้นที่
                        mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kerne3)
                        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kerne3)
                        # cv2.imshow('closing_mask', mask2)

                    except:
                        print('EOF')
                        print ('IN:',cnt_in+count_in)
                        print ('OUT:',cnt_in+count_in)
                        break

                    #ค้นหาขอบเขต
                    contours0, hierarchy = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for cnt in contours0:
                        rect = cv2.boundingRect(cnt)
                        area=cv2.contourArea(cnt)
                        if area>areaTHreshold:
                            M=cv2.moments(cnt)
                            cx=int(M['m10']/M['m00'])
                            cy=int(M['m01']/M['m00'])
                            x, y, w, h = cv2.boundingRect(cnt)
                            new=True
                            if cy in range(up_limit,down_limit):
                                for i in persons:
                                    if abs(cx-i.getX())<=w and abs(cy-i.getY())<=h:
                                        new=False
                                        i.updateCoords(cx,cy)
                                        if i.going_UP(line_down,line_up)==True:

                                            if w>80:
                                                count_in=w/40
                                                print("In: /60")
                                            else:
                                                cnt_in+=1
                                                print("In: count+1")
                                            print("ID:", i.getId(), 'crosses the entrance at', time.strftime("%c"))
                                        elif i.going_DOWN(line_down,line_up)==True:

                                            if w>80:
                                                count_out=w/40
                                                print("Out: 60")
                                            else:
                                                cnt_out+=1
                                                print("Out: count+1")
                                            print("ID:", i.getId(), 'crossed the exit at', time.strftime("%c"))
                                        break

                                    if i.getState() == '1':
                                        if i.getDir() == 'down' and i.getY() > down_limit:
                                            i.setDone()
                                        elif i.getDir() == 'up' and i.getY() < up_limit:
                                            i.setDone()
                                    if i.timedOut():

                                        index = persons.index(i)
                                        persons
                                if new == True:
                                    p = Person.MyPerson(pid, cx, cy, max_p_age)
                                    persons.append(p)
                                    pid += 1
                            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                            img = cv2.rectangle(frame, (x, y), (x + w, y + h),line_up_color, 2)
                    for i in persons:
                        cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)
                    str_up = 'IN: ' + str(int(cnt_in))
                    str_down = 'OUT: ' + str(int(cnt_out))

                    frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
                    frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
                    frame = cv2.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
                    frame = cv2.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
                    cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str_down, (10, 90), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                    out.write(frame)
                    cv2.imshow('Frame', frame)

                    k = cv2.waitKey(30) & 0xff
                    if k == 27:
                        break


                print("จำนวนคนเข้าทั้งหมดคือ")
                print(cnt_in)
                print("จำนวนคนเข้าออกทั้งหมดคือ")
                print(cnt_out)
                video.release();
                cv2.destroyAllWindows()



if __name__ == '__main__':


    thread1 = threading.Thread(target=printThread, args=("จำนวนคนทั้งหมด",))
    thread2 = threading.Thread(target=printThread2, args=("คนเข้า- ออก",))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

