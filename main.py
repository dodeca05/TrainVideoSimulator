import pafy

if __name__=="__main__":
    videoPath="video.mp4"
    maxSpeed=120
    maxAcceleration=5
    mod=""
    trainMaxSpd=160
    trainAcceleration=5
    debug=False
    f=open("setting.txt",'rt', encoding='UTF8')
    read_data=f.read().split('\n')
    while read_data[0].strip()!="driveData":
        cmd=read_data[0].split('=')
        if cmd[0]=="videoPath":
            videoPath=read_data[0][10:]
        elif cmd[0]=="maxSpeed":
            maxSpeed=float(cmd[1])
        elif cmd[0]=="maxAcceleration":
            maxAcceleration=float(cmd[1])
        elif cmd[0]=="mod":
            mod=cmd[1].strip()
        elif cmd[0]=="trainMaxSpeed":
            trainMaxSpd=float(cmd[1])
        elif cmd[0]=="trainAcceleration":
            trainAcceleration=float(cmd[1])
        elif cmd[0]=="debug":
            if cmd[1].strip()=="True":
                debug=True
        read_data.remove(read_data[0])
    if videoPath[:4]=="http":
        print("유튜브 모드")
        video=pafy.new(videoPath)
        best=video.getbest(preftype='mp4')
        videoPath=best.url
    f.close()
    print(videoPath)
    print(maxSpeed)
    print(maxAcceleration)
    print(mod)
    print(read_data)
    if mod=="cv2":
        import imshow_ex as g
        g.in_game(maxSpeed,maxAcceleration,videoPath,trainMaxSpd,trainAcceleration,debug)
    elif mod=="pyqt":
        import pyqt_ex as g
        g.startGame(maxSpeed,maxAcceleration,videoPath,trainMaxSpd,trainAcceleration)
        
