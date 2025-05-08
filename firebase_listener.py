import firebase_admin
from firebase_admin import credentials, firestore

# Khởi tạo Firebase Admin SDK với khóa dịch vụ
cred = credentials.Certificate('truyen-tranh-a2185-firebase-adminsdk-k4hic-d48ffc9683.json')
firebase_admin.initialize_app(cred)

# Truy cập Firestore
db = firestore.client()
