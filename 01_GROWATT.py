
import time
import requests
import growattServer
# import schedule

api = growattServer.GrowattApi()
login_response = api.login('pree', '0866555182')
#Get a list of growatt plants.
print(api.plant_list(login_response['user']['id']))

"""#CONFIG"""

c_loop = 1800 # wait for 5 minutes
c_hour = int(3600 / c_loop) #เก็บค่า ชม
c_30min = int(1800 / c_loop) #แจ้งเตือนทุกครึ่งชม

c_bat1 = 0
c_bat2 = 0

check_alert = []

VbatFull = 56.5
VbatEmp = 48.2
lowAlert = 46.1

message = ""

plant_id = '2440489'

storage_id1 = 'ZRK2DCC0KG'
battery_capacity1 = 0 # initial capacity in volts

capacity_record_use1 = []
capacity_record_charge1 = []

storage_id2 = 'ZRK2DCC0HL'
battery_capacity2 = 0 # initial capacity in volts
capacity_record_use2 = []
capacity_record_charge2 = []


print(c_loop,c_hour,c_30min)

def line_alert(modelName,path = ""):
	url = 'https://notify-api.line.me/api/notify'
	#token = 'jfknM3hTWnHiLYS2Asl4Ygeu1bPUBYYlUr9GEU4xC5H'
	token = 'EyyzdDbL0Yso9SxMJlGYvQfUJyAdKggJI1GoJo9tQjh'

	headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
	msg = modelName

	# รูปภาพที่ต้องการส่ง
	if(path != ""):
		#files = {'imageFile': open(path, 'rb')}
		#r = requests.post(url, headers=headers, data = {'message':msg}, files=files)
		r = requests.post(url, headers=headers, data = {'message':msg})
		print("ข้อความ")
		print("รูป")
	else:
		r = requests.post(url, headers=headers, data = {'message':msg})
		print("ข้อความ")
	print (r.text)

def convert_sec_to_hms(secs):

    total_seconds = int(secs)
    # คำนวณชั่วโมง
    hours = total_seconds // 3600

    # คำนวณนาที
    minutes = (total_seconds % 3600) // 60

    # คำนวณวินาทีที่เหลือ
    seconds = total_seconds % 60


    return hours, minutes, seconds

# ตัวอย่างการใช้งาน
hours_decimal = 3661  # 2
hours, minutes, seconds = convert_sec_to_hms(hours_decimal)
print(f"{hours_decimal} ชั่วโมง คือ {hours} ชั่วโมง {minutes} นาที {seconds} วินาที")

def battery(storage_id):
  a1 = api.storage_params(storage_id)
  b1 = a1["storageDetailBean"]["vBatText"]
  #print(b1)
  number_part1 = ''.join([char for char in b1 if char.isdigit() or char == '.'])

  # แปลงสตริงที่ได้เป็นตัวเลขแบบ float
  battery_r = float(number_part1)
  return float(battery_r)

print(battery(storage_id1),battery(storage_id2))

"""#แบต 1"""

def calculate_hourly_average_use1():
    global message
    if len(capacity_record_use1) >= c_30min:
        last_hour_capacities = capacity_record_use1[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)
        print(average)
        if(average != 0):
          sec_to_drop = (battery_capacity1 - VbatEmp) / (average/c_loop)

          hours, minutes, seconds = convert_sec_to_hms(abs(sec_to_drop))
          # print(f"กำลังใช้แบต ปัจจุบันแบตเหลือ {battery_capacity:4.2f} Volts และจะตำกว่า {VbatEmp} V ในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังใช้แบต ปัจจุบันแบตเหลือ {battery_capacity:4.2f} Volts และจะตำกว่า {VbatEmp} V ในอีก {hours} ชั่วโมง {minutes} นาที")

          print(f"\nBatt 1 สถานะ : use \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts \n หมดในอีก {hours} ชั่วโมง {minutes} นาที")
          #line_alert(f"กำลังใช้แบตตัวที่ 1 ({average/c_loop*3600:4.2f} V/hr) ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และคาดว่าจะใช้แบตหมดในอีก {hours} ชั่วโมง {minutes} นาที")
          # กำลังใช้แบต (xx.xx V/hr) **อย่าลืมคูณ 12 ก่อน** ปัจจุบันแบตเหลือ 52.60 Volts และคาดว่าจะใช้แบตหมดในอีก -3 ชั่วโมง 27 นาที
          message = (f"\nBatt 1 สถานะ : use \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts \n หมดในอีก {hours} ชั่วโมง {minutes} นาที")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"\nBatt 1 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")

#แบต 1 หมด
def calculate_hourly_average_use_emp1():
    global message
    if len(capacity_record_use1) >= c_30min:
        last_hour_capacities = capacity_record_use1[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)
        print(average)
        if(average != 0):
          sec_to_drop = (battery_capacity1 - VbatEmp) / (average/c_loop)

          hours, minutes, seconds = convert_sec_to_hms(abs(sec_to_drop))
          
          print(f"\nBatt 1 สถานะ : ใช้หมด \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts")
          message = (f"\nBatt 1 สถานะ : ใช้หมด \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"\nBatt 1 สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")



def calculate_hourly_average_charge1():
    global message
    if len(capacity_record_charge1) >= c_30min:
        last_hour_capacities = capacity_record_charge1[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)

        print(average)
        if(average != 0):
          sec_to_drop = (VbatFull - battery_capacity1) / (average/c_loop)
          hours, minutes, seconds = convert_sec_to_hms(sec_to_drop)
          # print(f"กำลังชาร์จแบต ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และจะชาร์จถึง {VbatFull} V ในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังชาร์จแบต ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และจะชาร์จถึง {VbatFull} V ในอีก {hours} ชั่วโมง {minutes} นาที")

          print(f"\nBatt 1 สถานะ : charge \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts \n เต็มในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังชาร์จแบตตัวที่ 1 ({average/c_loop*3600:4.2f} V/hr) ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และคาดว่าจะชาร์จแบตเต็มในอีก {hours} ชั่วโมง {minutes} นาที")
          message = (f"\nBatt 1 สถานะ : charge \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts \n เต็มในอีก {hours} ชั่วโมง {minutes} นาที")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"\nBatt 1 สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
"""#แบต 2"""

def calculate_hourly_average_use2():
    global message
    if len(capacity_record_use2) >= c_30min:
        last_hour_capacities = capacity_record_use2[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)
        print(average)
        if(average != 0):
          sec_to_drop = (battery_capacity2 - VbatEmp) / (average/c_loop)

          hours, minutes, seconds = convert_sec_to_hms(sec_to_drop)
          # print(f"กำลังใช้แบต ปัจจุบันแบตเหลือ {battery_capacity:4.2f} Volts และจะตำกว่า {VbatEmp} V ในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังใช้แบต ปัจจุบันแบตเหลือ {battery_capacity:4.2f} Volts และจะตำกว่า {VbatEmp} V ในอีก {hours} ชั่วโมง {minutes} นาที")

          print(f"Batt 2 สถานะ : use \n {average/c_loop*3600:4.2f} V/hr {battery_capacity2:4.2f} Volts \n หมดในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังใช้แบตตัวที่ 2 ({average/c_loop*3600:4.2f} V/hr) ปัจจุบันแบตเหลือ {battery_capacity2:4.2f} Volts และคาดว่าจะใช้แบตหมดในอีก {hours} ชั่วโมง {minutes} นาที")
          # กำลังใช้แบต (xx.xx V/hr) **อย่าลืมคูณ 12 ก่อน** ปัจจุบันแบตเหลือ 52.60 Volts และคาดว่าจะใช้แบตหมดในอีก -3 ชั่วโมง 27 นาที
          message = message + "\n" + (f"Batt 2 สถานะ : use \n {average/c_loop*3600:4.2f} V/hr {battery_capacity2:4.2f} Volts \n หมดในอีก {hours} ชั่วโมง {minutes} นาที")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"Batt 2 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = message + "\n" + (f"Batt 2 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")

#แบต 2 หมด
def calculate_hourly_average_use_emp2():
    global message
    if len(capacity_record_use2) >= c_30min:
        last_hour_capacities = capacity_record_use2[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)
        print(average)
        if(average != 0):
          sec_to_drop = (battery_capacity2 - VbatEmp) / (average/c_loop)

          hours, minutes, seconds = convert_sec_to_hms(sec_to_drop)
          print(f"\nBatt 2 สถานะ : ใช้หมด \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts")
          message = (f"\nBatt 2 สถานะ : ใช้หมด \n {average/c_loop*3600:4.2f} V/hr {battery_capacity1:4.2f} Volts")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"\nBatt 2  สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 2  สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")



def calculate_hourly_average_charge2():
    global message
    if len(capacity_record_charge2) >= c_30min:
        last_hour_capacities = capacity_record_charge2[-c_30min:]
        print(last_hour_capacities)
        average = sum(last_hour_capacities) / len(last_hour_capacities)

        print(average)
        if(average != 0):
          sec_to_drop = (VbatFull - battery_capacity2) / (average/c_loop)
          hours, minutes, seconds = convert_sec_to_hms(sec_to_drop)
          # print(f"กำลังชาร์จแบต ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และจะชาร์จถึง {VbatFull} V ในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังชาร์จแบต ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} Volts และจะชาร์จถึง {VbatFull} V ในอีก {hours} ชั่วโมง {minutes} นาที")

          print(f"Batt 2 สถานะ : charge \n {average/c_loop*3600:4.2f} V/hr {battery_capacity2:4.2f} Volts \n เต็มในอีก {hours} ชั่วโมง {minutes} นาที")
          # line_alert(f"กำลังชาร์จแบตตัวที่ 2 ({average/c_loop*3600:4.2f} V/hr) ปัจจุบันแบตเหลือ {battery_capacity2:4.2f} Volts และคาดว่าจะชาร์จแบตเต็มในอีก {hours} ชั่วโมง {minutes} นาที")
          message = message + "\n" + (f"Batt 2 สถานะ : charge \n {average/c_loop*3600:4.2f} V/hr {battery_capacity2:4.2f} Volts \n เต็มในอีก {hours} ชั่วโมง {minutes} นาที")
    else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(last_hour_capacities)
        print(f"Batt 2 สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = message + "\n" + (f"Batt 2 สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")

battery_capacity1 = battery(storage_id1)
battery_capacity2 = battery(storage_id2)

line_alert("เริ่มรันโปรแกรมใหม่",path = "test.png")

while True:
  message = ""


  time.sleep(c_loop)  # wait for 5 minute
  check_alert.append(1)
#แบต 1
  c_battery1 = battery(storage_id1)
  chackBatt1 = battery_capacity1 - c_battery1
  battery_capacityy1 = battery_capacity1
  
  battery_capacity1 = c_battery1

  
#แบต 2
  c_battery2 = battery(storage_id2)
  chackBatt2 = battery_capacity2 - c_battery2
  battery_capacityy2 = battery_capacity2
  
  battery_capacity2 = c_battery2

  if len(check_alert) % c_30min != 0:
    print("------------------- แบตตัวที่ 1 ---------------------------")
    print("แบตก่อนหน้า",battery_capacityy1," แบตปัจจุบัน ",c_battery1," เหลือ",chackBatt1)    
    if(chackBatt1 < 0 and chackBatt1 > -40): # กำลังชาร์จแบต
      print("กำลังชาร์จแบต")
      capacity_record_use1 = []
      capacity_record_charge1.append(abs(chackBatt1))
      if len(capacity_record_charge1) < c_30min:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_charge1)
        print(f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")


    elif(chackBatt1 > 0 and chackBatt1 < 40): # แบตถูกใช้
      print("แบตถูกใช้")
      capacity_record_charge1 = []
      capacity_record_use1.append(abs(chackBatt1))
      if len(capacity_record_use1) < c_30min:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use1)
        print(f"\nBatt 1 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")

#แบต2------------
        

    print("------------------- แบตตัวที่ 2 ---------------------------")
    print("แบตก่อนหน้า",battery_capacityy2," แบตปัจจุบัน ",c_battery2," เหลือ",chackBatt2) 
    
    if(chackBatt2 < 0 and chackBatt2 > -40): # กำลังชาร์จแบต
      print("กำลังชาร์จแบต")
      capacity_record_use2 = []
      capacity_record_charge2.append(abs(chackBatt2))
      if len(capacity_record_charge2) < c_30min:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_charge2)
        print(f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")


    elif(chackBatt2 > 0 and chackBatt2 < 40): # แบตถูกใช้
      print("แบตถูกใช้")
      capacity_record_charge2 = []
      capacity_record_use2.append(abs(chackBatt2))
      if len(capacity_record_use2) < c_30min:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use2)
        print(f"\nBatt  สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt  สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")


#----------------------------------------------------------------------------------------

  if len(check_alert) % c_30min == 0:
#---------------- แบต 1 ---------------
    print("------------------- แบตตัวที่ 1 ---------------------------")
    print("แบตก่อนหน้า",battery_capacityy1," แบตปัจจุบัน ",c_battery1," เหลือ",chackBatt1)   
    if(c_battery1 >= VbatFull): # แบตชาร์จเต็ม
      print("แบตตัวที่ 1 ชาร์จเต็ม")
      # line_alert(f"แบตตัวที่ 1 ชาร์จเต็ม ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} volts.")
      message = (f"\nBatt 1 สถานะ : ชาร์จเต็ม\nปัจจุบันแบตเหลือ {battery_capacity1:4.2f} volts.")

    elif(c_battery1 <= VbatEmp): # แบตหมด
      print("แบตหมด")
      capacity_record_charge1 = []
      capacity_record_use1.append(abs(chackBatt1))
      if len(capacity_record_use1) >= c_30min:
        c_bat1 = 0
        calculate_hourly_average_use_emp1()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use1)
        print(f"\nBatt 1 สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")      
      # line_alert(f"แบตตัวที่ 1 ใช้หมด ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} volts.")

    elif(chackBatt1 < 0 and chackBatt1 > -40): # กำลังชาร์จแบต
      print("กำลังชาร์จแบต")
      capacity_record_use1 = []
      capacity_record_charge1.append(abs(chackBatt1))
      if len(capacity_record_charge1) >= c_30min:
        c_bat1 = 1
        calculate_hourly_average_charge1()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_charge1)
        print(f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
      

    elif(chackBatt1 > 0 and chackBatt1 <40): # แบตถูกใช้
      print("แบตถูกใช้")
      capacity_record_charge1 = []
      capacity_record_use1.append(abs(chackBatt1))
      if len(capacity_record_use1) >= c_30min:
        c_bat1 = 0
        calculate_hourly_average_use1()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use1)
        print(f"\nBatt  สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = (f"\nBatt 1 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
      
    else:
      print("กำลังทำงาน2")
      message = (f"\nBatt 1 : ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} volts.")

#---------------- แบต 2 ---------------
    print("------------------- แบตตัวที่ 2 ---------------------------")
    print("แบตก่อนหน้า",battery_capacityy2," แบตปัจจุบัน ",c_battery2," เหลือ",chackBatt2)  
    if(c_battery2 >= VbatFull): # แบตชาร์จเต็ม
      print("แบตชาร์จเต็ม")
      # line_alert(f"แบตตัวที่ 2 ชาร์จเต็ม ปัจจุบันแบตเหลือ {battery_capacity2:4.2f} volts.")
      message = message + "\n" + (f"Batt 2 สถานะ : ชาร์จเต็ม\nปัจจุบันแบตเหลือ {battery_capacity2:4.2f} volts.")

    elif(c_battery2 <= VbatEmp): # แบตหมด
      print("แบตหมด")
      capacity_record_charge2 = []
      capacity_record_use2.append(abs(chackBatt2))
      if len(capacity_record_use2)  >= c_30min:
        c_bat2 = 0
        calculate_hourly_average_use_emp2()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use2)
        print(f"\nBatt 2  สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = message + (f"\nBatt 2 สถานะ : ใช้หมด \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
      
    elif(chackBatt2 < 0 and chackBatt1 > -40): # กำลังชาร์จแบต

      print("กำลังชาร์จแบต")
      capacity_record_use2 = []
      capacity_record_charge2.append(abs(chackBatt2))
      if len(capacity_record_charge2)  >= c_30min:
        c_bat2 = 1
        calculate_hourly_average_charge2()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_charge2)
        print(f"\nBatt  สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = message + (f"\nBatt 2 สถานะ : charge \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
      

    elif(chackBatt2 > 0 and chackBatt2 < 40): # แบตถูกใช้
      print("แบตถูกใช้")
      capacity_record_charge2 = []
      capacity_record_use2.append(abs(chackBatt2))
      if len(capacity_record_use2)  >= c_30min:
        c_bat2 = 0
        calculate_hourly_average_use2()
      else:
        print("**ยังไม่สามารถคำนวณได้**")
        print(capacity_record_use2)
        print(f"\nBatt 2  สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
        message = message + (f"\nBatt 2 สถานะ : use \n **ยังไม่สามารถคำนวณได้** ปัจจุบันแบตเหลือ {battery_capacity2:4.2f}")
      
    else:
      print("กำลังทำงาน2")
      message = message + "\n" + (f"\nBatt 2 : ปัจจุบันแบตเหลือ {battery_capacity1:4.2f} volts.")
    print(message)
    line_alert(message)



