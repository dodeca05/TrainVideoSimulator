from PyQt5 import QtCore, QtGui, QtWidgets,QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QTime
#import threading
from PyQt5.QtCore import QThread


import sys

#open cv 라이브러리
import cv2

font=cv2.FONT_HERSHEY_SIMPLEX

class QtWindow(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.n = 0
        self.main = parent
        self.isRun = False
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_W:
            self.lever+=1
            if self.lever>5:
                self.lever=5
        elif e.key()==Qt.Key_S:
            self.lever-=1
            if self.lever<-8:
                self.lever=-8

    def setupUi(self, MainWindow):
        self.targetFPS=30
        self.offset=0
        MainWindow.setObjectName("ForSign")
        MainWindow.resize(1600, 800)

        MainWindow.keyPressEvent=self.keyPressEvent
 
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.video_viewer_label = QtWidgets.QLabel(self.centralwidget)
        self.video_viewer_label.setGeometry(QtCore.QRect(10, 10, 1290, 730))

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 720))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.speedLabel=QtWidgets.QLabel("spd",MainWindow)
        font1 = self.speedLabel.font()
        font1.setBold(True)
        font1.setPointSize(20)
        self.speedLabel.setFont(font1)
        self.speedLabel.move(1300,500)

        self.stationLabel=QtWidgets.QLabel("station",MainWindow)
        self.stationLabel.setGeometry(QtCore.QRect(0, 0, 1000, 200))
        font1 = self.stationLabel.font()
        font1.setBold(True)
        font1.setPointSize(20)
        self.stationLabel.setFont(font1)
        self.stationLabel.move(1300,000)

        self.disLabel=QtWidgets.QLabel("dis",MainWindow)
        self.disLabel.setGeometry(QtCore.QRect(0, 0, 1000, 200))
        font1 = self.disLabel.font()
        font1.setBold(True)
        font1.setPointSize(20)
        self.disLabel.setFont(font1)
        self.disLabel.move(1300,100)

        self.gearLabel=QtWidgets.QLabel("gear",MainWindow)
        font2 = self.speedLabel.font()
        font2.setBold(True)
        font2.setPointSize(20)
        self.gearLabel.setFont(font2)
        self.gearLabel.move(1300,300)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.MainWindow=MainWindow

    def in_game(self, MainWindow,videoPath='test.mp4'):
        videoPath=self.videoPath
        cap = cv2.VideoCapture(videoPath) 
        
        st_cur=0

        fps=cap.get(cv2.CAP_PROP_FPS)
        fpsCount=cap.get(cv2.CAP_PROP_FRAME_COUNT)

        oneFrameTime=1/fps
        ###게임준비
        import scheduler as sc
        s=sc.Scheduler(fps,fpsCount,self.maxAcc,self.maxAcc,self.maxSpeed)

        f=open("setting.txt",'rt', encoding='UTF8')
        read_data=f.read().split('\n')
        while read_data[0].strip()!="driveData":
            read_data.remove(read_data[0])
        read_data.remove(read_data[0])

        spd,dis_lst,station_Lst=s.scheduling(read_data)

        train_dis=0

        self.lever=0

        self.maxSpd=self.trainMaxSpd
        self.maxAcc=self.trainAcceleration

        trainSpd=0       
        
        acceleration=2
        maxSpd=105
   
        acceleration/=fps
        cur=0
        

        #startTime=time.time()
        #startTime=QTime.currentTime().msec()
        startTime=QTime.currentTime().msec()
        print("시작",startTime)
        one_frame_time=1/60
        original_frame=None
        wait_time=startTime+1

        print(station_Lst)
        #self.p = self.pixmap.scaled(1280, 720, QtCore.Qt.IgnoreAspectRatio)
        while True:
            QtWidgets.QApplication.processEvents()
            print(trainSpd) 
            if dis_lst[cur]<=train_dis:
                temp=0
                while dis_lst[cur+temp]<train_dis:
                    temp+=1
                if temp==1:
                    self.ret, self.frame = cap.read()
                    cur+=1
                else:
                    cur+=temp
                    cap.set(cv2.CAP_PROP_POS_FRAMES,cur)
                    self.ret, self.frame = cap.read()
                original_frame=self.frame[:]
            else:
                self.frame=original_frame[:]
            if self.ret:
                
                
                dif_dis=station_Lst[st_cur][1]-train_dis
                if dif_dis>1.0:
                    text=station_Lst[st_cur][0]+"\n"+"%.2f"%(dif_dis)+"km"
                else:
                    text=station_Lst[st_cur][0]+"\n"+"%.2f"%(dif_dis*1000)+"m"              
                self.stationLabel.setText(text)
                #self.stationLabel.update()
                #QtWidgets.QApplication.processEvents() 
                if dif_dis<-0.05:
                    st_cur+=1            
                
                
                
                if self.lever>0:
                    self.gearLabel.setText("P"+str(self.lever))
                    self.gearLabel.setStyleSheet("Color : blue")
                elif self.lever==0:
                    self.gearLabel.setText("N0")
                    self.gearLabel.setStyleSheet("Color : green")
                else:
                    self.gearLabel.setText("B"+str(self.lever*-1))
                    self.gearLabel.setStyleSheet("Color : black")
                #self.gearLabel.update()
                #QtWidgets.QApplication.processEvents() 


                ##########################################이미지 적용
                self.rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.convertToQtFormat = QImage(self.rgbImage.data, self.rgbImage.shape[1], self.rgbImage.shape[0],
                                                QImage.Format_RGB888)
                self.pixmap = QPixmap(self.convertToQtFormat)
                self.p = self.pixmap.scaled(1280, 720, QtCore.Qt.IgnoreAspectRatio)
                text=str(int(trainSpd))+"km/h"
                self.speedLabel.setText(text)
                #self.speedLabel.update()
                #QtWidgets.QApplication.processEvents() 

                self.video_viewer_label.setPixmap(self.p)
                self.video_viewer_label.update() #프레임 띄우기


                for i in range(5):#DONT freeze!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    QtWidgets.QApplication.processEvents()
                

                #sleep(0.01)
                QtTest.QTest.qWait(10)
                #pyqtSleep(0.01)
                 
                ###########################
                #nowTime=time.time()
                nowTime=QTime.currentTime().msec()
                deltaTime=nowTime-startTime
                if deltaTime<0:
                    deltaTime=nowTime+(1000-startTime)
                deltaTime/=1000
                
                startTime=nowTime
                trainSpd+=self.lever*self.maxAcc*deltaTime/5
                if trainSpd>self.maxSpd:
                    trainSpd=self.maxSpd
                if trainSpd<0:
                    trainSpd=0
                train_dis+=trainSpd/60/60*deltaTime
                            
            else:
                break

        cap.release()
        cv2.destroyAllWindows()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("vts", "vts"))


    def video_thread(self, MainWindow):
        
        thread = threading.Thread(target=self.in_game, args=(self,))
        thread.daemon = True
        thread.start()
    def run(self):
        self.in_game(self.MainWindow)
        pass
    def setArgs(self,maxSpeed,maxAcceleration,videoPath,trainMaxSpd,trainAcceleration):
        self.maxSpeed=maxSpeed
        self.maxAcc=maxAcceleration
        self.videoPath=videoPath
        self.trainMaxSpd=trainMaxSpd
        self.trainAcceleration=trainAcceleration

def startGame(maxSpeed,maxAcceleration,videoPath,trainMaxSpd,trainAcceleration):
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = QtWindow()
    ui.setupUi(MainWindow)
    ui.setArgs(maxSpeed,maxAcceleration,videoPath,trainMaxSpd,trainAcceleration)
    
    
    MainWindow.show()
    ui.start()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = QtWindow()
    ui.setupUi(MainWindow)

    #ui.video_thread(MainWindow)

    MainWindow.show()
    ui.start()
    app.exec_()

    #sys.exit(app.exec_())