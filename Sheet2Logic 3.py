#모듈 불러오기
from os import system, listdir
import sys
system("cls")

#제목 출력
print("-"*19)
print(f"|{'Sheet2Logic 3':^17}|")
print(f"|{'made by jongs':^17}|")
print("-"*19)
print()

#사용할 폴더 묻기
print("변환할 텍스트 파일이 들어 있는 폴더의 이름 또는 경로를 입력하세요.")
print("대소문자 관계없이 입력 가능하고, 경로에는 /와 \\ 모두 사용 가능합니다.")
print("아무것도 입력하지 않으면 현재 프로그램이 위치한 폴더에서 파일을 탐색합니다.")
while True:
    folder=input(70*"-"+"\n").replace("/","\\").split("\\")
    if len(folder) == 1 : #폴더의 경로가 입력되지 않아 기본 경로 추가
        loc_default=__file__.split("\\")
        folder=loc_default[0:-1]+folder

    try:
        files=listdir("\\".join(folder)) #폴더 내부의 파일 탐색
    except: #경로가 잘못됨
        print("해당 경로의 폴더를 찾을 수 없습니다. 다시 입력해 주세요.")
        continue
    else: #경로가 잘못되지 않음

        #폴더 내 txt 파일 개수 세기
        txtcount=0
        for file in files :
            if len(file.split("."))>1 and file.split(".")[1] == "txt" :
                txtcount+=1
        if txtcount==0 : #폴더 내 txt 파일이 없음
            print("해당 경로에 txt 파일이 존재하지 않습니다. 다시 입력해 주세요.")
            continue

        #폴더 이름을 곡의 제목으로 설정(32자 제한)
        title=folder[-1][0:32]
        break

#입력받은 값이 수면 실수로 변환한 값을, 아니면 기본값을 반환하는 함수
#p_only==1이면 음수 불가능, 2이면 0 이하 불가능
def isthisfloat(got, default, p_only=0):
    try:
        got=float(got)
    except:
        return default
    else:
        if (p_only==1 and float(got)<0) or (p_only==2 and float(got)<=0) :
            return default
        else :
            return float(got)
        
folder="\\".join(folder)+"\\"
note_name=['라0', '라#0', '시0', \
'도1', '도#1', '레1', '레#1', '미1', '파1', '파#1', '솔1', '솔#1', '라1', '라#1', '시1', \
'도2', '도#2', '레2', '레#2', '미2', '파2', '파#2', '솔2', '솔#2', '라2', '라#2', '시2', \
'도3', '도#3', '레3', '레#3', '미3', '파3', '파#3', '솔3', '솔#3', '라3', '라#3', '시3', \
'도4', '도#4', '레4', '레#4', '미4', '파4', '파#4', '솔4', '솔#4', '라4', '라#4', '시4', \
'도5', '도#5', '레5', '레#5', '미5', '파5', '파#5', '솔5', '솔#5', '라5', '라#5', '시5', \
'도6', '도#6', '레6', '레#6', '미6', '파6', '파#6', '솔6', '솔#6', '라6', '라#6', '시6', \
'도7', '도#7', '레7', '레#7', '미7', '파7', '파#7', '솔7', '솔#7', '라7', '라#7', '시7', '도8']
note_code=['0.00', '0.01', '0.02', '0.03', '0.04', '0.05', '0.06', '0.07', '0.08', '0.09', '0.10', '0.11', \
'1.00', '1.01', '1.02', '1.03', '1.04', '1.05', '1.06', '1.07', '1.08', '1.09', '1.10', '1.11', \
'2.00', '2.01', '2.02', '2.03', '2.04', '2.05', '2.06', '2.07', '2.08', '2.09', '2.10', '2.11', \
'3.00', '3.01', '3.02', '3.03', '3.04', '3.05', '3.06', '3.07', '3.08', '3.09', '3.10', '3.11', \
'4.00', '4.01', '4.02', '4.03', '4.04', '4.05', '4.06', '4.07', '4.08', '4.09', '4.10', '4.11', \
'5.00', '5.01', '5.02', '5.03', '5.04', '5.05', '5.06', '5.07', '5.08', '5.09', '5.10', '5.11', \
'6.00', '6.01', '6.02', '6.03', '6.04', '6.05', '6.06', '6.07', '6.08', '6.09', '6.10', '6.11']
track=0
sheet=[]
drumtrack=[]

#파일 하나씩 확인
for file in files : #file: 폴더 내 각 파일의 이름
    try:
        ph=open(folder+file,"r",encoding="UTF-8")
    except:
        try:
            ph=open(folder+file,"r",encoding="cp949")
        except:
            print("파일의 인코딩을 알 수 없어 하나 건너뜁니다.")
            continue
    
    #인코딩 성공한 파일
    filename=file.split(".")[0]
    print(70*"-")

    print(f"'{filename}' 트랙은 몇 번 반복하나요?")
    repeat = input("기본값은 1입니다. 0 이하로 설정하면 해당 파일은 건너뜁니다.\n")
    repeat = isthisfloat(repeat,1)
    repeat = int(repeat) #정수로 설정
    if repeat <= 0 : #0 이하면 다음으로
        continue
    print()

    print(f"'{filename}' 트랙의 음정은 얼마나 조정할까요?")
    pitch = input("기본값은 0입니다. 0.5 단위로 입력해 주세요. 한 옥타브는 6입니다.\n")
    pitch = isthisfloat(pitch,0)
    pitch = int(pitch*2) #2배 해서 정수로
    print()

    print(f"'{filename}' 트랙은 얼마나 빨리 재생되나요?")
    speed = input("기본값은 1입니다. 배속으로 숫자만 입력해 주세요.\n")
    speed = isthisfloat(speed,1,2) #0 이하 안됨
    print()

    print(f"'{filename}' 트랙은 몇 박자 기다렸다가 시작하나요?")
    offset = input("기본값은 0입니다. 배속을 무시합니다.\n")
    offset = isthisfloat(offset,0,1) #0 미만 안됨
    print()

    if repeat > 1 :
        print(f"'{filename}' 트랙의 반복 간 간격은 몇 박자인가요?")
        delay = input("기본값은 0입니다. 시작 오프셋의 영향을 받지 않습니다.\n")
        delay = isthisfloat(delay,0,1) #0 미만 안됨
    else : delay = 0
    print()

    choose=input(f"'{filename}' 트랙의 악기를 드럼으로 고정할까요? (y/n) ")
    if choose.strip().lower()=="y" :
        drumtrack.append(track)
    track+=1

    #박자가 정해져 있지 않을 때 기본값 함수
    def howmanybeats(got, default):
        if len(got)>1 and type(isthisfloat(got[1],"no")) == float :
            return float(got[1])
        else :
            return default

    beat=offset
    raw=ph.readlines()
    for I in range(repeat) : #입력한 수만큼 반복
        for rawline in raw : #파일 한 줄씩 확인
            line=rawline.strip().split() #줄바꿈 제거, 띄어쓰기 기준으로 분리
            if line == [] : continue #빈 줄은 넘김

            if type(isthisfloat(line[0],"no")) == float : #BPM 변경
                sheet.append(( beat,track,float(line[0]) ))
                beat+=howmanybeats(line,0)/speed

            elif line[0] in note_name : #음 연주
                try: #음높이가 범위 안
                    note=note_code[note_name.index(line[0])-3+pitch]
                    sheet.append((beat,track,note))
                finally: 
                    beat+=howmanybeats(line,1)/speed
            
            else : #대기
                beat+=howmanybeats(line,0)/speed

        beat+=delay/speed
    sheet.append((beat,track,0))

    ph.close()

#읽은 값을 로직 코드로 변환
print(70*"-")
sheet.sort(key=lambda x: x[0])

#페이지 0 내용 생성
logic=[f"""setrate 100
read x cell1 0
jump 10 notEqual x 0
sensor a switch1 @enabled
jump 9 notEqual a 1
set t1 @time
write t1 cell1 2
write 1 cell1 0
jump 11 always
print "{title}\\n"
jump 20 equal x 0
control enabled switch1 0
read t1 cell1 2
set t2 @time
op sub t t2 t1
op div t t 10
op idiv t t 1
op div t t 100
print t
print "\\n"
sensor a switch2 @enabled
jump 26 notEqual a 1
control enabled switch2 0
read i cell1 1
op add i i 11
jump 31 always
sensor a switch3 @enabled
jump {34+min(963,track)} notEqual a 1
control enabled switch3 0
read i cell1 1
op add i i 19
op sub i i 10
jump 31 greaterThan i 9
write i cell1 1"""]

for I in range(min(963,track)):
    if I in drumtrack :
        logic[0]+=f"""
control color block{I+1} 10"""
    else :
        logic[0]+=f"""
control color block{I+1} i"""

logic[0]+="""
print "[#2030D0]Made with"
print "[#FFFF00] Sheet2Logic 3"
printflush message1"""

#페이지 1과 이후 내용 생성
BPM=120
beat=0
play=[]

#sheet을 구성하는 튜플에는 {a}현재 박자, {b}노트 블록 번호,
#{c}바꿀 BPM(float) 또는 연주할 음높이(string) 순서대로 저장되어 있음
for a,b,c in sheet :
    if a>beat : #시간이 달라지면
        play.append(f"wait {60*(a-beat)/BPM}")
        beat=a
  
    if type(c)==str : #음 연주
        play.append(f"control config block{b} {c}")
    else : #BPM 변경
        if c>0 : BPM=c

#생성한 내용을 페이지에 붙여넣기
for I in range(len(play)//996 + 1):
    logic.append(f"setrate 100\nread x cell1 0\njump 1 notEqual x {I+1}") #시작 부분
    for J in range(min( 996, len(play)-(I*996) )): #음 연주 부분
        logic[I+1]+="\n"
        logic[I+1]+=play[996*I + J]
    
    if I == len(play)//996 : #마지막 부분
        logic[I+1]+=f"\nwrite 0 cell1 0"
    else :
        logic[I+1]+=f"\nwrite {I+2} cell1 0"

#각 페이지를 파일로 저장하기
print("로직 코드가 작성된 텍스트 파일을 저장할 폴더의 이름 또는 경로를 입력하세요.")
print("주의: 입력한 폴더 내에 이름이 같은 파일이 이미 존재할 경우, 기존 파일은 삭제됩니다!")
while True:
    folder=input(70*"-"+"\n").replace("/","\\").split("\\")
    if len(folder) == 1 : #폴더의 경로가 입력되지 않아 기본 경로 추가
        loc_default=__file__.split("\\")
        folder=loc_default[0:-1]+folder
    folder="\\".join(folder)
    
    try:
        files=listdir(folder) #폴더 내부의 파일 탐색
    except: #없는 폴더
        print("해당 이름의 폴더가 존재하지 않습니다.")
        print("폴더를 새로 만들어 다시 시도하거나 이미 존재하는 폴더의 이름을 입력하세요.")
    else: #있는 폴더
        alrexist=[]
        for I in range(len(logic)) :
            if f"page {I}.txt" in files :
                alrexist.append(f"page {I}")
        if len(alrexist)>0 :
            print(f"{', '.join(alrexist)} 파일이 이미 존재합니다. 그래도 계속하시겠습니까?",end=" ")
            choose=input("(y/n) ")
            if choose!="y" :
                print("폴더 이름이나 경로를 다시 입력해 주세요.")
                continue
        for I in range(len(logic)) :
            with open(f"{folder}\\page {I}.txt","w",encoding="utf8") as ph :
                ph.write(logic[I])
        break

print("\n성공적으로 저장되었습니다!")
input("Enter를 눌러 종료합니다...")
system("cls")
sys.exit(0)