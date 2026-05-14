from django.test import TestCase
import json
from rest_framework.test import APIClient #APIClient mô phỏng client gửi request đến API
from django.urls import reverse

def test_register_ok(db): #tên bắt đầu bằng test_ để pytest nhận diện là hàm test
    c = APIClient() #tạo client giả lập gửi request đến API
    payload = {
        "email":"patient1@example.com",
        "password":"password123",
        "password_confirm":"password123",
        "full_name":"Nguyễn Văn A",
        "phone_num":"0901234567",
        "role":"patient",
        "date_of_birth":"1990-01-15",
        "gender":"male",
        "address":"123 Nguyễn Huệ, Q1, TPHCM"
    }
    url = reverse("accounts:register") #lấy URL của API register
    res = c.post(url, payload, format='json')
    assert res.status_code == 201, res.content
    print(json.dumps(res.json(), ensure_ascii=False, indent=2)) 
    
    