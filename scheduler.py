
class Node:
    def __init__(self,line,fps,baseBk,baseAcc,maxSpd):
        self.end_time=-1
        cur=0
        while line[cur]!=' ':
            cur+=1
        self.type=line[:cur]
        line=line[cur:].strip()
        if self.type=="station":
            cur=1
            while line[cur]!='"':
                cur+=1
            self.name=line[1:cur]
            line=line[cur+1:].strip()
            args=line.split(' ')
            if len(args)==1:
                self.start_time=0
                for t in args[0].split(':'):
                    self.start_time*=60
                    self.start_time+=float(t)
                self.start_time*=fps
                self.bk=baseBk
                self.acc=baseAcc
                self.spd=maxSpd
                self.end_time=-1
            elif len(args)>=2:
                self.start_time=0
                for t in args[0].split(':'):
                    self.start_time*=60
                    self.start_time+=float(t)
                self.start_time*=fps
                self.end_time=0
                for t in args[1].split(':'):
                    self.end_time*=60
                    self.end_time+=float(t)
                self.end_time*=fps
                
                if len(args)>2:
                    bk=float(args[2])
                    acc=float(args[3])
                    if bk==0:
                        self.bk=baseBk
                    else:
                        self.bk=bk
                    if acc==0:
                        self.acc=baseAcc
                    else:
                        self.acc=acc
                    if len(args)>=5:
                        self.spd=float(args[4])
                    else:
                        self.spd=maxSpd
                else:
                    self.bk=baseBk
                    self.acc=baseAcc
                    self.spd=maxSpd
            #print(self.start_time,"역 = ",self.name,self.bk,self.acc,self.spd)
        elif self.type=="acceleration":
            args=line.strip().split(' ')
            self.start_time=0
            for t in args[0].split(':'):
                self.start_time*=60
                self.start_time+=float(t)
            self.start_time*=fps
            self.acc=float(args[1])
            if len(args)>=3:
                self.spd=float(args[2])
            else:
                self.spd=maxSpd
            #print(self.start_time,"가속 ",self.acc,self.spd)
        elif self.type=="speed":
            args=line.strip().split(' ')
            self.start_time=0
            for t in args[0].split(':'):
                self.start_time*=60
                self.start_time+=float(t)
            self.start_time*=fps
            self.spd=float(args[1])
            if len(args)>=3:
                self.acc=float(args[2])
                self.bk=self.acc
            else:
                self.acc=baseAcc
                self.bk=baseBk
            #print(self.start_time,"속도 ",self.acc,self.spd)


        
class Scheduler:
    

    def __init__(self,fps,frameCount,baseBk,baseAcc,maxSpd):
        self.baseBk=baseBk
        self.baseAcc=baseAcc
        self.maxSpd=maxSpd
        self.fps=fps
        self.frameCount=frameCount
    def scheduling(self,raw_read_data):
        node_lst=[]
        station_lst=[]
        spd=[0 for i in range(int(self.frameCount))]
        state=[0 for i in range(int(self.frameCount))]

        for n in raw_read_data:
            if n.strip()=="":
                continue

            n=Node(n,self.fps,self.baseBk,self.baseAcc,self.maxSpd)
            if n.start_time!=n.end_time:
                node_lst.append(n)
            if n.type=="station":
                if n.end_time==n.start_time:
                    station_lst.append([n.name,n.start_time,False,0])
                else:
                    station_lst.append([n.name,n.start_time,True,0])
        cur=0
        for i in range(int(self.frameCount)):
            state[i]=cur
            if node_lst[cur].type=="station":
                if (node_lst[cur].start_time<=i and i<node_lst[cur].end_time) or len(node_lst)-1==cur:
                    spd[i]=0
                elif node_lst[cur].end_time<i:
                    spd[i]=spd[i-1]+(node_lst[cur].acc/self.fps)
                    if spd[i]>node_lst[cur].spd:
                        spd[i]=node_lst[cur].spd
            elif node_lst[cur].type=="acceleration":
                spd[i]=spd[i-1]+(node_lst[cur].acc/self.fps)
                if spd[i]>node_lst[cur].spd:
                    spd[i]=node_lst[cur].spd
            elif node_lst[cur].type=="speed":
                spd[i]=node_lst[cur].spd

            if len(node_lst)-1>cur and node_lst[cur+1].start_time<=i:
                cur+=1
                if node_lst[cur].type=="station":
                    if node_lst[cur].start_time==node_lst[cur].end_time:
                        continue
                    else:
                        j=i
                        spd_temp=0
                        while spd[j]>spd_temp:
                            spd[j]=spd_temp
                            j-=1
                            spd_temp+=node_lst[cur].bk/self.fps
                elif node_lst[cur].type=="speed":
                    if spd[i-1]>node_lst[cur].spd:
                        j=i
                        spd_temp=node_lst[cur].spd
                        while spd[j]>spd_temp:
                            spd[j]=spd_temp
                            j-=1
                            spd_temp+=node_lst[cur].bk/self.fps
                    elif spd[i-1]<node_lst[cur].spd:
                        j=i
                        spd_temp=node_lst[cur].spd
                        while spd[j]<spd_temp:
                            spd[j]=spd_temp
                            j-=1
                            spd_temp-=node_lst[cur].acc/self.fps
        dis=[0 for i in range(int(self.frameCount))]

        for i in range(1,int(self.frameCount)):
            dis[i]=dis[i-1]+(spd[i]/60/60/self.fps)
        """
        from matplotlib import pyplot as plt

        plt.plot(spd)
        plt.show()
        plt.plot(dis)
        plt.show()
        print(dis[-1])
        """
        self.spd=spd
        self.dis=dis
        self.node_lst=node_lst
        for i in range(len(station_lst)):
            station_lst[i][3]=int(station_lst[i][1])
            station_lst[i][1]=dis[int(station_lst[i][1])]
        return spd,dis,station_lst

if __name__ == "__main__":
    import cv2
    f=open("setting.txt",'rt', encoding='UTF8')
    read_data=f.read().split('\n')
    while read_data[0].strip()!="driveData":
        read_data.remove(read_data[0])
    read_data.remove(read_data[0])
    cap=cv2.VideoCapture('test.mp4')
    sc=Scheduler(cap.get(cv2.CAP_PROP_FPS),cap.get(cv2.CAP_PROP_FRAME_COUNT),5,5,105)
    a,b,c=sc.scheduling(read_data)
    import matplotlib.pyplot as plt
    plt.plot(a)
    plt.show()
    print(c)
    