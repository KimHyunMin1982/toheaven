import BlynkLib
from pop import Leds, PiezoBuzzer, Oled
from pop import Switches, Potentiometer
from random import randint
from pop import PopThread
import time
import threading

#from subprocess import Popen, PIPE

leds = buzzer = oled = switchs = poten = None
blynk = BlynkLib.Blynk("sBYZ5MrzfSb7yzBRq2R8D2NaAysvH3y5", server="127.0.0.1",port=8080) #프로젝트를 생성할 때 메일로 받은 인증 코드  
vital_value = 0
vital_value_file = []
previous_vital_value = []
next_vital_value = []
total_vital = 0
send_total_blynk = 0

poten_value = 0

thread_current_time = 0
thread_start_time = 0
thread_elapsed_time = 0

time_cnt = 0
temp = 0

# 심장박동 데이터 생성 패턴 쓰레드
def execute(number):
    global thread_current_time, thread_start_time, thread_elapsed_time
    global vital_value, poten_value, time_cnt
    global blynk
    global previous_vital_value
    global total_vital, send_total_blynk

    while True:
        start = time.perf_counter()
        elapsed = time.perf_counter() - start
        thread_current_time += elapsed

        if thread_current_time >= 1:
            thread_current_time = 0
            
            if time_cnt < 60:
                if poten_value == 0 or poten_value == 1 or poten_value == 2 or poten_value == 3 or poten_value == 4 or poten_value == 5:
                    previous_vital_value.append(randint(1, 2)) # 정상 범위의 심장박동
                elif poten_value == 5 or poten_value == 6 or poten_value == 7 or poten_value == 8 or poten_value == 9 or poten_value == 10 or poten_value == 11:
                    previous_vital_value.append(randint(1, 3)) # 1단계 범위의 심장박동

                print(previous_vital_value)

                total_vital = 0

                for i in range(len(previous_vital_value)):
                    total_vital += previous_vital_value[i]
                
                send_total_blynk = total_vital

                print("60초 이하%d"%(total_vital))

            print("%d초 입니다."%(time_cnt))    
            time_cnt += 1

            if time_cnt >= 60:
                previous_vital_value.pop(0)
                if poten_value == 0 or poten_value == 1 or poten_value == 2 or poten_value == 3 or poten_value == 4 or poten_value == 5:
                    previous_vital_value.insert(59, randint(1, 2)) # 정상 범위의 심장박동
                elif poten_value == 5 or poten_value == 6 or poten_value == 7 or poten_value == 8 or poten_value == 9 or poten_value == 10 or poten_value == 11:
                    previous_vital_value.insert(59, randint(1, 3)) # 1단계 범위의 심장박동

                total_vital = 0

                for i in range(len(previous_vital_value)):
                    total_vital += previous_vital_value[i]
                
                send_total_blynk = total_vital

                print("60초 이상%d"%(total_vital))
            
                #time_cnt = 0                
                #vital_value_file.append(vital_value)
                #dataframe = pd.DataFrame(vital_value_file)
                #dataframe.to_csv("vital_signs.csv", header=False, index=False)

def execute_buzzer(number):
    global temp

    while True:
        print(temp)

        if temp == 0:
            buzzer.setTempo(80)   # 심박수 0(심정지시)
            buzzer.tone(3,7,4)
            buzzer.tone(3,0,32)

        elif 30 <= temp <= 50 or 110 <= temp <= 130:
            buzzer.setTempo(200)   # 심박수 위 아래로 조금 빨라졌을때 경고음
            buzzer.tone(6,7,16)
            buzzer.tone(7,9,8)
        
        elif 10 <= temp < 30 or 130 < temp <= 150:
            buzzer.setTempo(80)   # 심박수가 매우 높아 졌을때
            buzzer.tone(7,7,4)
            buzzer.tone(7,0,32)


def on_vital_signs(val):
    global buzzer, temp
    # global vital_value, poten_value, send_total_blynk

    # poten_value = val
    # blynk.virtual_write(0, send_total_blynk)
    # blynk.virtual_write(2, poten_value)
    if val == 0:
        temp = randint(60, 100)
    elif val == 1:
        temp = randint(55, 105)
    elif val == 2:
        temp = randint(50, 110)
    elif val == 3:
        temp = randint(45, 115)
    elif val == 4:
        temp = randint(40, 120)
    elif val == 5:
        temp = randint(35, 125)
    elif val == 6:
        temp = randint(30, 130)
    elif val == 7:
        temp = randint(25, 135)
    elif val == 8:
        temp = randint(20, 140)
    elif val == 9:
        temp = randint(15, 145)
    elif val == 10:
        temp = randint(0, 0)

    print(temp)

    # if temp == 0:
    #     buzzer.setTempo(80)   # 심박수 0(심정지시)
    #     buzzer.tone(3,7,4)
    #     buzzer.tone(3,0,32)

    # elif 30 <= temp <= 50 or 110 <= temp <= 130:
    #     buzzer.setTempo(200)   # 심박수 위 아래로 조금 빨라졌을때 경고음
    #     buzzer.tone(6,7,16)
    #     buzzer.tone(7,9,8)
    
    # elif 10 <= temp < 30 or 130 < temp <= 150:
    #     buzzer.setTempo(80)   # 심박수가 매우 높아 졌을때
    #     buzzer.tone(7,7,4)
    #     buzzer.tone(7,0,32)

    blynk.virtual_write(0, temp)
    blynk.virtual_write(2, val)

def sensor_rw():
    poten.setRangeTable([144, 629, 1112, 1621, 2085, 2642, 3158, 3590, 3992, 4094])
    poten.setCallback(on_vital_signs)

    #input("Press <ENTER> key...\n")
    #poten.stop()

@blynk.VIRTUAL_WRITE(3)
def on_led1_ctl(on):
    global vital_value, vital_value_file
    
    #if int(on[0]):
    while int(on[0]):
        #vital_value_file.append(vital_value)
        #print(vital_value);print(vital_value_file)
        #dataframe = pd.DataFrame(vital_value_file)
        dataframe.to_csv("vital_signs.csv", header=False, index=False)
        leds[0].on()
        
    # else:
    #     leds[0].off()

@blynk.VIRTUAL_WRITE(4)
def on_led2_ctl(on):
    if int(on[0]):
        leds[1].on()
    else:
        leds[1].off()

def main():
    global blynk
    global leds, buzzer, oled, switchs, poten
    global vital_value, vital_value_file
    #blynk = BlynkLib.Blynk("sBYZ5MrzfSb7yzBRq2R8D2NaAysvH3y5", server="127.0.0.1",port=8080) #프로젝트를 생성할 때 메일로 받은 인증 코드

    leds = Leds()
    buzzer = PiezoBuzzer()
    oled = Oled()
    switchs = Switches()
    poten = Potentiometer()

    #threading.Thread(target=execute, args=(1,)).start()
    #threading.Thread(target=execute_buzzer, args=(2,)).start()

    sensor_rw()

    while True:
        blynk.run()

if __name__ == "__main__":
    main()