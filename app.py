import hmac
import hashlib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import my_pb2
import output_pb2
import warnings
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
from msdk import GeneRateMsdk
from flask import Flask, request, jsonify

# تعطيل تحذيرات الاتصال غير الآمن
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

app = Flask(__name__)

# الإعدادات الثابتة
login_url = "https://loginbp.common.ggbluefox.com"
ob = "OB54"
version = "2.126.3"
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

def parse_response(response_content):
    """تحويل نص استجابة الـ Protobuf المفكك إلى دكشنري"""
    response_dict = {}
    lines = response_content.split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            response_dict[key.strip()] = value.strip().strip('"')
    return response_dict

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

    # الخطوة 2: بناء حزمة Protobuf
    game_data = my_pb2.GameData()
    game_data.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = version
    game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "Verizon Wireless"
    game_data.connection_type = "WIFI"
    game_data.screen_width = 1280
    game_data.screen_height = 960
    game_data.dpi = "240"
    game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
    game_data.total_ram = 5951
    game_data.gpu_name = "Adreno (TM) 640"
    game_data.gpu_version = "OpenGL ES 3.0"
    game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
    game_data.ip_address = "172.190.111.97"
    game_data.language = "en"
    game_data.open_id = token_data['open_id']
    game_data.access_token = token_data['access_token']
    game_data.platform_type = 4
    game_data.device_form_factor = "Handheld"
    game_data.device_model = "Asus ASUS_I005DA"
    game_data.field_60 = 32968
    game_data.field_61 = 29815
    game_data.field_62 = 2479
    game_data.field_63 = 914
    game_data.field_64 = 31213
    game_data.field_65 = 32968
    game_data.field_66 = 31213
    game_data.field_67 = 32968
    game_data.field_70 = 4
    game_data.field_73 = 2
    game_data.library_path = "/data/app/com.dts.freefireth-QPvBnTUhYWE-7DMZSOGdmA==/lib/arm"
    game_data.field_76 = 1
    game_data.apk_info = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-QPvBnTUhYWE-7DMZSOGdmA==/base.apk"
    game_data.field_78 = 6
    game_data.field_79 = 1
    game_data.os_architecture = "32"
    game_data.build_number = "2019117877"
    game_data.field_85 = 1
    game_data.graphics_backend = "OpenGLES2"
    game_data.max_texture_units = 16383
    game_data.rendering_api = 4
    game_data.encoded_field_89 = "\u0017T\u0011\u0017\u0002\b\u000eUMQ\bEZ\u0003@ZK;Z\u0002\u000eV\ri[QVi\u0003\ro\t\u0007e"
    game_data.field_92 = 9204
    game_data.marketplace = "3rd_party"
    game_data.encryption_key = "KqsHT2B4It60T/65PGR5PXwFxQkVjGNi+IMCK3CFBCBfrNpSUA1dZnjaT3HcYchlIFFL1ZJOg0cnulKCPGD3C3h1eFQ="
    game_data.total_storage = 111107
    game_data.field_97 = 1
    game_data.field_98 = 1
    game_data.field_99 = "4"
    game_data.field_100 = "4"
    
    default_md5 = "7428b253defc164018c604a1ebbfebdf"
    if hasattr(game_data, 'signature_md5'):
        game_data.signature_md5 = default_md5
    elif hasattr(game_data, 'client_using_version'):
        game_data.client_using_version = default_md5
    else:
        for field_name in ['signature', 'sign', 'md5', 'client_sign']:
            if hasattr(game_data, field_name):
                setattr(game_data, field_name, default_md5)
                break

    serialized_data = game_data.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)

    # الخطوة 3: إرسال الطلب للسيرفر الرئيسي
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
                example_msg.ParseFromString(response.content)
                response_dict = parse_response(str(example_msg))
                
                # إرجاع النتيجة بتنسيق JSON المطلوب
                return jsonify({
                    "status": response_dict.get('status', 'SUCCESS'),
                    "uid": uid,
                    "region": response_dict.get('region', 'N/A'),
                    "token": response_dict.get('token', 'N/A')
                }), 200
                
            except Exception as e:
                return jsonify({"status": "error", "message": f"Deserialization error: {str(e)}"}), 500
        else:
            return jsonify({"status": "error", "message": f"MajorLogin failed with status {response.status_code}"}), response.status_code
            
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Network error: {str(e)}"}), 500

if __name__ == "__main__":
    # تشغيل السيرفر محلياً على المنفذ 5000
    app.run(host="0.0.0.0", port=13266, debug=True)
