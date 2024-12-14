from django.shortcuts import render
import requests

API_KEY = '082152d02e-497d687f55-sk0044'
BASE_URL = 'https://api.fastforex.io/fetch-all'

def get_exchange(request):
    exchange_rates = {}
    error_msg = None
    last_updated = None
    converted_amounts = {}
    amount_to_exchange = 0.0  
    """ ประกาศค่าต่างๆในฟังก์ชั่น """
    
    supported_currencies = ['USD', 'JPY', 'THB']
    """ ซัพพอร์ตที่ USD JPY THB """
    
    if request.method == 'POST':
        base_currency = request.POST.get('base_currency', 'USD')
        amount_to_exchange = float(request.POST.get('amount', 0))
        """ เช็ค request เป็น post ไหม post เป็นข้อมูลที่มักใช้เมื่อส่งข้อมูลให้ผู้ใช้กรอก """
        """ post.get รับ params 2 ตัว คือ base_currency , USD ใช้ USD เป็นค่าเริ่มต้น """
        """ ดึงค่าเงินที่ผู้ใช้กรอก ในฟิลด์ amount หากไม่เจอฟิลด์ใช้ค่าเริ่่มเป็น 0  ชนิด float"""

        try: 
            response = requests.get(f"{BASE_URL}", params={'api_key': API_KEY, 'from': base_currency})
            response.raise_for_status()
            data = response.json()
            """ try ตรวจข้อผิดพลาด ถ้าผิดพลาดจะข้ามไปที่ except """
            """ ส่ง http, get ไปที่ BASE_URL """
            """ มีค่า params เป็น api_key และ from ใช้ระบุสกุลเงินหลักที่เลือก """
            """ ตรวจสถานะ http erroor หากเป็น 404, 500 จะส่งไป except """
            """ ถ้าคำขอสำเร็จจะแปลงเป็น json """
            
            print(data)  # ตรวจสอบข้อมูลที่ได้รับจาก API

            if 'results' in data: 
                exchange_rates = data['results']  #เก็บอัตราแลกเปลี่ยนระหว่างสกุลเงิน
                last_updated = data.get('updated') #ดึงข้อมูลวันที่และเวลาที่ข้อมูลอัตราแลกเปลี่ยนล่าสุดถูกอัปเดต
           
                # คำนวณการแปลงเงิน
                for currency, rate in exchange_rates.items(): #ใช้เพื่อไปยังแต่ละสกุลเงินและอัตราแลกเปลี่ยนใน exchange_rates
                    if currency != base_currency:  # ไม่คำนวณอัตราแลกเปลี่ยนของสกุลเงินเดียวกัน
                        converted_amounts[currency] = amount_to_exchange * rate #คำณวณและแปลงค่าเก็บไว้

            else:
                error_msg = "Error: 'results' not found in the API response." #ถ้าไม่พบ results

        except requests.exceptions.HTTPError as http_err: #จับข้อผิดพลาด 404 ไปเก็บไว้ตัวแปร http_err
            error_msg = f"HTTP error occurred: {http_err}" #f-string เป็นสตริงที่อนุญาตให้นำตัวแปรมาแทรก
            
        except requests.exceptions.RequestException as req_err: #จับข้อผิดพลาด ส่งคำขอ HTTP 
            error_msg = f"Request error occurred: {req_err}"
            
        except Exception as e: #จับข้อผิดพลาดทุกประเภท 
            error_msg = f"An unexpected error occurred: {e}"

    context = {
        'exchange_rates': exchange_rates, #เก็บอัตราแลกเปลี่ยนจาก API
        'welcome_msg': "Welcome to Django Exchange Rate App", #เก็บข้อความ
        'error_msg': error_msg, #เก็บ error
        'last_updated': last_updated, #เก็บวันเวลาที่อัพเดทอัตราแลกเปลี่ยน
        'converted_amounts': converted_amounts, #เก็บผลลัพธ์ที่แปลง
        'supported_currencies': supported_currencies, #เก็บรูปแบบที่ซํพพอร์ต
        'amount_to_exchange': amount_to_exchange, # เก็บเงินที่ผู้ใช้กรอก 
        'base_currency': base_currency if 'base_currency' in locals() else 'USD', #เก็บสกุลเงินหลัก และเช็คว่า base_currency มีใน local ไหมถ้าไม่ให้ใช้ USD
    }

    return render(request, "exchang_page/exchange-app.html", context) #ส่งค่าไปที่ html ไป render ด้วย params ต่างๆ
