import hmac
import hashlib
import requests
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import warnings
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
from msdk import GeneRateMsdk
from flask import Flask, request, jsonify

# استيراد ملفات الـ Protobuf
import MajoRLoGinrEq_pb2
import output_pb2

# تعطيل تحذيرات الاتصال غير الآمن
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

app = Flask(__name__)

# الإعدادات الثابتة
login_url = "https://loginbp.ggpolarbear.com"
ob = "OB54"
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

def get_token(password, uid):
    """جلب التوكن المبدئي من سيرفر جارينا"""
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": GeneRateMsdk(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=15)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None

def encrypt_message(key, iv, plaintext):
    """تشفير حزمة الـ Protobuf باستخدام AES-CBC"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded_message)

@app.route('/get', methods=['GET'])
def get_account_data():
    # استقبال المعاملات من الرابط (Query Parameters)
    uid = request.args.get('uid')
    password = request.args.get('pass')

    # التحقق من وجود المدخلات
    if not uid or not password:
        return jsonify({
            "status": "error",
            "message": "Missing 'uid' or 'pass' parameters."
        }), 400

    # الخطوة 1: طلب التوكن المبدئي
    token_data = get_token(password, uid)
    if not token_data:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve token from Garena Connect."
        }), 400

    open_id = token_data.get('open_id')
    access_token = token_data.get('access_token')

    # الخطوة 2: بناء حزمة Protobuf الجديدة بالتحديث الحالي
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 2
    major_login.client_version = "1.126.2"
    major_login.client_version_code = "2024010012"
    major_login.system_software = "Android OS 11 / API-30 (RQ3A.210805.001)"
    major_login.system_hardware = "Handheld"
    major_login.device_type = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_operator_a = "Verizon"
    major_login.network_type = "WIFI"
    major_login.network_type_a = "WIFI"
    major_login.screen_width = 1080
    major_login.screen_height = 2400
    major_login.screen_dpi = "440"
    major_login.processor_details = "ARMv8"
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.memory = 6144
    major_login.gpu_renderer = "Adreno (TM) 650"
    major_login.gpu_version = "OpenGL ES 3.2 V@1.50"
    major_login.graphics_api = "OpenGLES3"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = ""
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.login_open_id_type = 4
    major_login.access_token = access_token
    major_login.login_by = 3
    major_login.platform_sdk_id = 2
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    
    # إعداد الحقول الفرعية للذاكرة المتاحة
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    
    major_login.external_storage_total = 128512
    major_login.external_storage_available = random.randint(38000, 52000)
    major_login.internal_storage_total = 110731
    major_login.internal_storage_available = random.randint(18000, 32000)
    major_login.game_disk_storage_total = 26628
    major_login.game_disk_storage_available = random.randint(18000, 25000)
    major_login.external_sdcard_total_storage = 119234
    major_login.external_sdcard_avail_storage = random.randint(25000, 60000)
    major_login.library_path = "/data/app/~~random/base.apk"
    major_login.library_token = "hash|base.apk"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.supported_astc_bitset = 16383
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = random.randint(9000, 18000)
    major_login.release_channel = "android"
    major_login.channel_type = 3
    major_login.reg_avatar = 1
    major_login.if_push = 1
    major_login.is_vpn = 0
    major_login.android_engine_init_flag = 110009

    # تحويل الحزمة إلى بايتات وتشفيرها
    serialized_data = major_login.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)

    # الخطوة 3: إرسال الطلب المشفر للسيرفر الرئيسي
    url = f"{login_url}/MajorLogin"
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': ob
    }

    try:
        response = requests.post(url, data=encrypted_data, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            example_msg = output_pb2.Garena_420()
            try:
                # فك استجابة السيرفر
                example_msg.ParseFromString(response.content)
                
                # قراءة القيم مباشرة
                account_id = example_msg.account_id if example_msg.account_id else uid
                account_region = example_msg.region if example_msg.region else "N/A"
                account_status = example_msg.status if example_msg.status else "N/A"
                major_token = example_msg.token if example_msg.token else "N/A"
                
                # الرد النهائي بالتنسيق المطلوب
                return jsonify({
                    "status": "SUCCESS",
                    "account_info": {
                        "account_id": account_id,
                        "region": account_region,
                        "status": account_status
                    },
                    "tokens": {
                        "open_id": open_id,
                        "access_token": access_token,
                        "token": major_token
                    }
                }), 200
                
            except Exception as e:
                return jsonify({"status": "error", "message": f"Deserialization error: {str(e)}"}), 500
        else:
            return jsonify({"status": "error", "message": f"MajorLogin failed with status {response.status_code}"}), response.status_code
            
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Network error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
