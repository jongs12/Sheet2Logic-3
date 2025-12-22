#모듈 불러오기
from os import system, listdir
import sys
system("cls")

#입력받은 값이 범위 내의 실수이면 해당 수 반환, 아니면 기본값 반환
def is_float(value, default = 0, no_negative = 0) :
    try:
        value = float(value) #실수인지 확인
    except:
        return default #실수가 아님, 기본값 반환
    else:
        #no_negative == 1이면 음수 불가능, no_negative == 2면 0도 불가능
        if (no_negative == 1 and value < 0) or (no_negative == 2 and value <= 0) :
            return default #불가능한 값이 들어옴, 기본값 반환
        else :
            return value #조건 만족
        
#파일 확장자 제거 함수
def cut_extension(file, by=".", no_space=True) :
    if file.count(by)>0 : #확장자 분리 기호가 있으면
        cut_file = by.join(file.split(by)[0:-1]) #확장자 이후 제거
    else: cut_file = file #없으면 그대로 둠

    if no_space == True : #공백 제거 활성화 시
        return cut_file.strip() #양 옆의 공백 제거
    else : return cut_file #아니면 그대로 반환

#파일이 확장자가 있고 그게 txt인지 확인
def is_txt(file):
    return (len(file.split(".")) > 1 and file.split(".")[-1] == "txt")

#제목 출력
print("-"*19)
print(f"|{'Sheet2Logic':^17}|")
print(f"|{'version 3.5':^17}|")
print(f"|{'made by jongs':^17}|")
print("-"*19)
print()

#사용할 폴더 묻기
print("변환할 텍스트 파일이 들어 있는 폴더의 경로를 입력하세요.")
print("경로 없이 폴더의 이름만 입력하면 현재 프로그램이 위치한 폴더에서 탐색합니다.")
print("대소문자 관계없이 입력 가능하고, 경로에는 /와 \\ 모두 사용 가능합니다.")

while True: #제대로 된 입력이 들어올 때까지 반복
    folder = input(70*"-"+"\n").replace("/","\\").rstrip("\\").split("\\") #입력 받기

    if len(folder) == 1 : #슬래시가 없음
        folder_full = __file__.split("\\")[0:-1]+folder #파일 경로 추가
    else : #슬래시가 있음
        folder_full = folder #입력한 그대로

    folder = folder_full[-1] #폴더 이름만 남김
    folder_full = "\\".join(folder_full).rstrip("\\") #폴더 경로를 문자열로

    try:
        files = sorted(listdir(folder_full)) #폴더 내부의 파일 탐색
    except: #경로가 잘못됨
        print("해당 경로의 폴더를 찾을 수 없습니다. 다시 입력해 주세요.")
        continue

    else: #경로가 잘못되지 않음
        txtcount = 0 #폴더 내 txt 파일 개수 세기
        for file in files : #각각의 파일에 대해
            if is_txt(file) : txtcount += 1 #txt면 값 증가

        if txtcount == 0 : #폴더 내 txt 파일이 없음
            print("해당 경로에 txt 파일이 존재하지 않습니다. 다시 입력해 주세요.")
            continue

        #이상 없음
        folder = folder[0:32] #폴더 이름을 곡의 제목으로 설정(32자 제한)
        break
        
note_name = ["도", "레", "미", "파", "솔", "라", "시"] #계이름 리스트
note_code = [0, 2, 4, 5, 7, 9, 11] #계이름에 대응하는 값
inst_list = ["piano","bells","square","saw","bass","organ","synth","chime","violin","harp","drum"]
block_num = 0 #블록 번호(midi track)
prev_name = "<없음>" #직전에 인식한 파일 이름
total_sheet = [] #변환에 필요한 리스트 통합본

#txt 파일 하나씩 확인
for file in files :
    if is_txt(file) : #txt 파일일 경우
        try: #인코딩 방식이 UTF-8인지 확인
            with open(folder_full + "\\" + file, "r", encoding="UTF-8") as sheet :
                if sheet.read().strip() == "" :
                    print(f"폴더 내 {file} 파일은 비어 있어 건너뜁니다.")
                    continue

        except: #UTF-8이 아님
            try: #인코딩 방식이 ANSI인지 확인
                with open(folder_full + "\\" + file, "r", encoding="cp949") as sheet :
                    if sheet.read().strip() == "" :
                        print(f"폴더 내 {file} 파일은 비어 있어 건너뜁니다.")
                        continue

            except: #ANSI가 아님
                print(f"폴더 내 {file} 파일은 인코딩을 알 수 없어 건너뜁니다.")
                print("파일 저장 시 UTF-8(권장) 또는 ANSI 인코딩을 사용하세요.\n")
                continue

            else: #ANSI가 맞음 - 파일 열기
                sheet = open(folder_full + "\\" + file, "r", encoding="cp949")
        else: #UTF-8이 맞음 - 파일 열기
            sheet = open(folder_full + "\\" + file, "r", encoding="UTF-8")

        #블록 번호 증가 여부 판단
        file = cut_extension(file) #.txt 제거
        file_name = cut_extension(file, by = "-") #마지막 "-" 앞부분만
        if file_name != prev_name : #직전에 남긴 이름과 같음
            block_num += 1 #블록 번호 1 증가
            prev_name = file_name #이름 저장
        
        beat = 0 #현재까지 진행한 박자
        intro = [] #반복 활성화 이전
        loop = [] #반복 활성화 이후
        is_looping = False #반복 활성화 여부
        loop_count = 0 #반복 횟수
        pitch_modifier = 0 #피치 조절 정도
        speed_modifier = 1 #속도 조절 배수

        for line in sheet : #한 줄씩 읽기
            line = line.strip().split() #단어 단위로 분리
            if line == [] : continue #빈 줄 건너뛰기

            elif line[0][0] in note_name : #첫 번째 글자가 note_name에 포함되면
                act = ["play_note", "0.00", beat, block_num] #음 연주
                note_pitch = note_code[note_name.index(line[0][0])] #음높이 설정
                note_octave = 0 #옥타브 설정
                
                try: #두 번째 글자가 # 또는 b면 반음만큼 변경
                    if line[0][1] == "#" :
                        note_pitch += 1
                    elif line[0][1] == "b" :
                        note_pitch -= 1
                except: pass
                note_pitch += pitch_modifier #피치 조절
                
                #0이나 11을 넘어가면 루프
                while (note_pitch < 0) or (note_pitch > 11) :
                    if note_pitch < 0 :
                        note_pitch += 12
                        note_octave -= 1
                    elif note_pitch > 11 :
                        note_pitch -= 12
                        note_octave += 1

                #첫 번째 단어의 마지막 글자에 따라 옥타브 설정
                note_octave += int(is_float(line[0][-1], default = 4))
                #한 자리 수가 아니면 4로 처리
                
                act[1] = f"{note_octave-1}.{note_pitch:0>2}" #최종 피치 설정
                note_in_range = ((float(act[1]) >= 0) and (float(act[1]) < 7)) #피치 범위

                #피치가 범위 내일 경우 추가
                if is_looping and note_in_range :
                    loop.append(act)
                elif (not is_looping) and note_in_range :
                    intro.append(act)

                if len(line) > 1 : #박자 추가, 0보다 작으면 무시
                    beat += is_float(line[1], no_negative = 1)/speed_modifier

            elif is_float(line[0], default=False, no_negative=2) : #첫 번째 단어가 양수
                act = ["change_bpm", float(line[0]), beat] #BPM 변경
                if is_looping : loop.append(act) #추가
                else : intro.append(act)

                if len(line) > 1 : #박자 추가
                    beat += is_float(line[1], no_negative = 1)/speed_modifier

            elif (line[0][0] == "!") and (len(line) > 1) : #첫 번째 글자가 "!"면
                command = line[0].lstrip("!")

                if (command == "반복") and (not is_looping) : #이미 설정하지 않았을 때
                    if type(is_float(line[1], default = "no", no_negative = 1)) == float :
                        is_looping = True #반복 설정
                        loop_count = int(line[1]) #반복 횟수 설정
                        loop.append(["do_nothing", None, beat]) #반복을 시작한 박자 저장

                elif command == "피치" :
                    if type(is_float(line[1], default = "no")) == float :
                        pitch_modifier = int(line[1]) #피치 조절
                
                elif command == "속도" :
                    if is_float(line[1], default = False, no_negative = 2) :
                        speed_modifier = float(line[1]) #배속 조절

                elif (command == "악기") and (line[1].lower() in inst_list) : #악기 변경
                    act = ["change_inst", str(inst_list.index(line[1])), beat, block_num]
                    if is_looping : loop.append(act) #추가
                    else : intro.append(act)

            #첫 번째 글자가 "#"이면 각주, 박자에 반영 안 함
            elif line[0][0] == "#" :
                try:
                    if line[0][1] == "#" : #두 번째 글자도 "#"이면
                        chars = " ".join(line)
                        act = ["print", chars[2:36].strip(), beat] #print 추가
                        if is_looping : loop.append(act) #추가
                        else : intro.append(act)
                except: pass

            else : #전부 아니면 대기
                if len(line) > 1 :
                    beat += is_float(line[1], no_negative = 1)/speed_modifier
        
        sheet.close() #파일 닫기
    else : continue #txt가 아니면 건너뛰기

    total_sheet += intro #통합 리스트에 반복하지 않는 부분 추가

    #반복하는 부분이 존재할 때
    if loop != [] :
        loop_start_beat = loop[0][2]

    for I in range(loop_count) :
        total_sheet += [x[ : ] for x in loop] #반복하는 부분 추가
        for J in range(len(loop)):
            loop[J][2] += (beat - loop_start_beat) #처음과 마지막 박자의 차이만큼 더함

    #박자가 어긋나지 않게 마지막에 아무것도 하지 않는 act 추가
    if (loop != []) and (total_sheet[-1][2] < loop[0][2]) :
        total_sheet.append(["do_nothing", None, loop[0][2]])
    elif (loop == []) and (intro != []) and (total_sheet[-1][2] < beat) :
        total_sheet.append(["do_nothing", None, beat])

total_sheet.sort(key = lambda x : x[2])

print() #폴더 읽기 완료

#0번째 프로세서 내용 생성
process_0 = f"""\
setrate 100
read playing cell1 0
jump 11 notEqual playing 0
sensor start switch1 @enabled
jump 9 notEqual start 1
set t1 @time
write t1 cell1 1
write 1 cell1 0
jump 11 always
print "{folder}\\n"
jump 20 equal playing 0
control enabled switch1 0
read t1 cell1 1
set t2 @time
op sub t t2 t1
op div t t 10
op idiv t t 1
op div t t 100
print t
print "\\n"
print "[#2030D0]Made with"
print "[#FFFF00] Sheet2Logic 3"
printflush message1"""

#1번째 이후 프로세서 내용 생성
BPM = 150 #기본 BPM
beat = 0 #시작 박자
process = [] #전체 프로세서 코드
#프로세서 하나의 코드
process_onepage = ["setrate 100", "read playing cell1 0", "jump 1 notEqual playing 1"]

for I in range(len(total_sheet)) :
    if total_sheet[I][2] > beat : #박자가 차이가 날 경우
        waiting_time = 60*(total_sheet[I][2] - beat)/BPM
        process_onepage.append(f"wait {waiting_time}")
        beat = total_sheet[I][2]

        if (len(process_onepage) == 999) and ((I+1) < len(total_sheet)) : #프로세서 길이 제한
            process_onepage.append(f"write {len(process)+2} cell1 0") #다음 프로세서로 넘김
            process.append("\n".join(process_onepage)) #전체 코드 리스트에 추가
            #하나의 코드 초기화
            process_onepage = ["setrate 100", "read playing cell1 0", f"jump 1 notEqual playing {len(process)+1}"]
            
    if total_sheet[I][0] == "play_note" : #음 연주
        process_onepage.append(f"control config block{total_sheet[I][3]} {total_sheet[I][1]}")
        if (len(process_onepage) == 999) and ((I+1) < len(total_sheet)) : #프로세서 길이 제한
            process_onepage.append(f"write {len(process)+2} cell1 0") #다음 프로세서로 넘김
            process.append("\n".join(process_onepage)) #전체 코드 리스트에 추가
            #하나의 코드 초기화
            process_onepage = ["setrate 100", "read playing cell1 0", f"jump 1 notEqual playing {len(process)+1}"]

    elif total_sheet[I][0] == "change_bpm" : #BPM 변경
        BPM = total_sheet[I][1]
    
    elif total_sheet[I][0] == "change_inst" : #악기 변경
        process_onepage.append(f"control color block{total_sheet[I][3]} {total_sheet[I][1]}")
        if (len(process_onepage) == 999) and ((I+1) < len(total_sheet)) : #프로세서 길이 제한
            process_onepage.append(f"write {len(process)+2} cell1 0") #다음 프로세서로 넘김
            process.append("\n".join(process_onepage)) #전체 코드 리스트에 추가
            #하나의 코드 초기화
            process_onepage = ["setrate 100", "read playing cell1 0", f"jump 1 notEqual playing {len(process)+1}"]

    elif total_sheet[I][0] == "print" : #내용 출력
        process_onepage.append(f"print \"{total_sheet[I][1]}\"")
        if (len(process_onepage) == 999) and ((I+1) < len(total_sheet)) : #프로세서 길이 제한
            process_onepage.append(f"write {len(process)+2} cell1 0") #다음 프로세서로 넘김
            process.append("\n".join(process_onepage)) #전체 코드 리스트에 추가
            #하나의 코드 초기화
            process_onepage = ["setrate 100", "read playing cell1 0", f"jump 1 notEqual playing {len(process)+1}"]


process_onepage.append("write 0 cell1 0") #마지막 프로세서
process.append("\n".join(process_onepage)) #전체 코드 리스트에 추가

#각 페이지를 파일로 저장하기
print("프로세서 코드가 작성된 텍스트 파일을 저장할 폴더의 이름 또는 경로를 입력하세요.")
print("주의: 입력한 폴더 내에 이름이 같은 파일이 이미 존재할 경우, 기존 파일은 삭제됩니다!")

while True: #제대로 된 입력이 들어올 때까지 반복
    folder = input(70*"-"+"\n").replace("/","\\").rstrip("\\").split("\\") #입력 받기

    if len(folder) == 1 : #슬래시가 없음
        folder_full = __file__.split("\\")[0:-1]+folder #파일 경로 추가
    else : #슬래시가 있음
        folder_full = folder #입력한 그대로
    folder_full = "\\".join(folder_full).rstrip("\\") #폴더 경로를 문자열로

    try:
        files = listdir(folder_full) #폴더가 존재하는지 확인
        for I in range(len(files)) :
            files[I] = files[I].lower() #파일명을 소문자로
    except: #경로가 잘못됨
        print("해당 경로의 폴더를 찾을 수 없습니다. 다시 입력해 주세요.")
        continue

    else: #경로가 잘못되지 않음
        print(f"\n{folder_full} 폴더에 저장합니다.")
        dupes = []
        for I in range(len(process)+1) : #각각의 파일에 대해
            if f"page {I}.txt" in files:
                dupes.append(f"page {I}") #중복 있으면 값 증가

        if len(dupes) > 0 : #폴더 내 중복 파일이 있음
            print(f"{", ".join(dupes)} 파일이 덮어씌워집니다.", end=" ")
        
        choice = input("계속하시겠습니까? (y/n) ")
        if choice.strip().lower()!="y" : #y를 입력하지 않으면
            print("저장이 취소되었습니다. 폴더 이름을 다시 입력해 주세요.")
            continue
        
        with open(f"{folder_full}\\page 0.txt","w",encoding="UTF-8") as logic :
            logic.write(process_0) #페이지 0 저장
        for I in range(len(process)) : #페이지 1 이후 저장
            with open(f"{folder_full}\\page {I+1}.txt","w",encoding="UTF-8") as logic :
                logic.write(process[I])
        break

print("\n성공적으로 저장되었습니다!")
print(f"{len(process)+1}개의 프로세서를 각각 {block_num}개의 노트블록과 메모리에 연결하세요.")
input("Enter를 눌러 종료합니다... ")
system("cls")
sys.exit(0)