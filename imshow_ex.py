import time
from time import sleep


import copy

#open cv 라이브러리
import cv2

font=cv2.FONT_HERSHEY_SIMPLEX



def in_game(maxSpd=160,maxAcc=5,videoPath='test.mp4',trainMaxSpd=160,trainAcc=5,debug=False,w=-1,h=-1):
        print(maxSpd,maxAcc)
        cap = cv2.VideoCapture(videoPath) 
        
        st_cur=0

        fps=cap.get(cv2.CAP_PROP_FPS)
        fpsCount=cap.get(cv2.CAP_PROP_FRAME_COUNT)

        oneFrameTime=1/fps
        ###게임준비
        import scheduler as sc
        s=sc.Scheduler(fps,fpsCount,maxAcc,maxAcc,maxSpd)

        maxSpd=trainMaxSpd
        maxAcc=trainAcc

        f=open("setting.txt",'rt', encoding='UTF8')
        read_data=f.read().split('\n')
        while read_data[0].strip()!="driveData":
            read_data.remove(read_data[0])
        read_data.remove(read_data[0])

        spd,dis_lst,station_Lst=s.scheduling(read_data)
        if debug:
            import matplotlib.pyplot as plt
            plt.plot(spd)
            plt.show()
            plt.plot(dis_lst)
            plt.show()
        train_dis=0

        lever=0

        trainSpd=0       
        
        cur=0
        

        startTime=time.time()

        print("시작",startTime)
        one_frame_time=1/60
        original_frame=None
        wait_time=startTime+1

        print(station_Lst)

        while True:
            #print(trainSpd) 
            if dis_lst[cur]<=train_dis:
                temp=0
                while dis_lst[cur+temp]<train_dis:
                    temp+=1
                if temp==1:
                    ret, frame = cap.read()
                    cur+=1
                else:
                    cur+=temp
                    cap.set(cv2.CAP_PROP_POS_FRAMES,cur)
                    ret, frame = cap.read()
                if w!=-1 and h!=-1:
                    frame=cv2.resize(frame, dsize=(w, h), interpolation=cv2.INTER_AREA)
                original_frame=copy.deepcopy(frame)
            else:
                frame=copy.deepcopy(original_frame)

            if ret:                
                
                dif_dis=station_Lst[st_cur][1]-train_dis
                if dif_dis>0.3:
                    text=station_Lst[st_cur][0]+" "+"%.2f"%(dif_dis)+"km"
                else:
                    text=station_Lst[st_cur][0]+" "+"%.2f"%(dif_dis*1000)+"m"      

                if station_Lst[st_cur][2]==False:
                    text="(no stop)"+text        
                frame=cv2.putText(frame,text,(10,30),font,1,(255,0,0),2)
                frame=cv2.putText(frame,str(int(trainSpd))+"km/h",(70,70),font,1,(0,0,255),2)
                if dif_dis<-0.03:
                    st_cur+=1            
                
                
                
                if lever>0:
                    frame=cv2.putText(frame,"P"+str(lever),(10,70),font,1,(255,0,0),2)
                    
                elif lever==0:
                    frame=cv2.putText(frame,"N",(10,70),font,1,(0,255,0),2)
                else:
                    frame=cv2.putText(frame,"B"+str(-lever),(10,70),font,1,(0,255,0),2)                 


                ##########################################이미지 적용
               
     
                

                cv2.imshow("tvs",frame)
                key=cv2.waitKey(1)
                if key==27:
                    break
                elif key==ord('w'):
                    lever+=1
                    if lever>5:
                        lever=5
                elif key==ord('s'):
                    lever-=1
                    if lever<-8:
                        lever=-8
                elif key==ord('m'):
                    if dif_dis<0:
                        st_cur+=1
                    if len(station_Lst)==st_cur:
                        st_cur-=1
                    else:
                        trainSpd=0
                        cur=station_Lst[st_cur][3]
                        cap.set(cv2.CAP_PROP_POS_FRAMES,cur)
                        train_dis=station_Lst[st_cur][1]
                        

                elif key==ord('n'):
                    st_cur-=1
                    if st_cur<0:
                        st_cur=0
                    else:
                        trainSpd=0
                        cur=station_Lst[st_cur][3]
                        cap.set(cv2.CAP_PROP_POS_FRAMES,cur)
                        train_dis=station_Lst[st_cur][1]

              

                
     
                 
                ###########################
                nowTime=time.time()
                
                deltaTime=nowTime-startTime
        
                startTime=nowTime
                trainSpd+=lever*maxAcc*deltaTime/5
                if trainSpd>maxSpd:
                    trainSpd=maxSpd
                if trainSpd<0:
                    trainSpd=0
                train_dis+=trainSpd/60/60*deltaTime
                            
            else:
                break

        cap.release()
        cv2.destroyAllWindows()


    


    


    


if __name__ == "__main__":
    in_game()

   