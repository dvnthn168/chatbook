import firebase_admin
from firebase_admin import credentials, firestore
import requests
import time

# Khởi tạo Firebase Admin SDK
cred = credentials.Certificate('truyen-tranh-a2185-firebase-adminsdk-k4hic-d48ffc9683.json')
firebase_admin.initialize_app(cred)

# Lấy đối tượng Firestore
db = firestore.client()

def send_message_to_rasa(message, token=None, jwt_token=None):
    """Gửi tin nhắn đến Rasa và nhận phản hồi."""
    url = "http://localhost:5005/webhooks/rest/webhook"
    payload = {"message": message}
    headers = {'Content-Type': 'application/json'}

    if token:
        headers['Authorization'] = f"Bearer {token}"
    elif jwt_token:
        headers['Authorization'] = f"Bearer {jwt_token}"

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi gửi đến Rasa: {e}")
        return None

def save_message_to_firestore(chat_id, message, response_text, sender_type):
    """Lưu tin nhắn và phản hồi vào Firestore."""
    message_data = {
        'senderId': message['senderId'],
        'senderType': sender_type,
        'text': message['text'],
        'timestamp': firestore.SERVER_TIMESTAMP,
        'response': response_text,
    }

    doc_ref = db.collection('chats').document(chat_id).collection('messages').add(message_data)
    print(f"✅ Đã lưu message vào chat {chat_id}, ID: {doc_ref[1].id}")

def save_bot_response(chat_id, response_text):
    """Lưu phản hồi của bot vào Firestore."""
    message_data = {
        'senderId': 'bot',
        'senderType': 'bot',
        'text': response_text,
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    db.collection('chats').document(chat_id).collection('messages').add(message_data)
    print(f"🤖 Bot response saved in chat {chat_id}")

def handle_message(chat_id, message):
    """Xử lý tin nhắn mới từ user."""
    if message.get("senderType") != "user":
        return  # Bỏ qua tin nhắn không phải từ user để tránh vòng lặp

    rasa_response = send_message_to_rasa(message['text'])
    if rasa_response:
        response_text = rasa_response[0].get('text', '')
        save_bot_response(chat_id, response_text)
    else:
        print("⚠️ Không nhận được phản hồi từ Rasa.")

def on_snapshot(doc_snapshot, changes, read_time):
    """Lắng nghe các thay đổi trong messages subcollection."""
    print(f"🔥 Có {len(changes)} thay đổi mới")
    for change in changes:
        if change.type.name == "ADDED":
            doc = change.document
            message = doc.to_dict()
            chat_id = doc.reference.parent.parent.id  # Lấy chat_id từ cấu trúc document
            print(f"📩 Tin nhắn mới trong chat {chat_id}: {message}")
            
            # Kiểm tra nếu tin nhắn mới nhất KHÔNG phải từ user thì bỏ qua
            messages_ref = db.collection('chats').document(chat_id).collection('messages')
            latest_messages = messages_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
            
            if not latest_messages:
                continue
            
            latest_message = latest_messages[0].to_dict()
            if latest_message.get("senderType") != "user":
                print(f"⚠️ Tin nhắn mới nhất từ bot hoặc admin => Không xử lý thêm")
                return

            # Cuộc hội thoại kết thúc
            if message.get('isEnded', False):
                print(f"🛑 Cuộc hội thoại {chat_id} đã kết thúc. Không phản hồi.")
                return

            # Nếu admin đang trả lời
            if  message.get("senderType") == "admin":
                print(f"🛑 Admin đang trả lời chat {chat_id}. Bot sẽ không phản hồi.")
                return
            
            # Nếu là của user thì bot phản hồi 
            if  message.get("senderType") == "user":
                print(f"🆕 Tin nhắn mới từ {message.get('senderId')}: {message['text']}")
                handle_message(chat_id, message)

def listen_to_all_messages():
    """Lắng nghe tất cả messages trong mọi chat."""
    messages_ref = db.collection_group('messages')
    messages_ref.on_snapshot(on_snapshot)
    print("👂 Bắt đầu lắng nghe tất cả tin nhắn...")

if __name__ == "__main__":
    listen_to_all_messages()
    while True:
        time.sleep(1)
