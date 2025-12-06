import cv2
import base64
import urllib.parse
import sys
import os
import datetime

# ==========================================
# ЧАСТЬ 1: ЛОГИКА PROTOBUF (БЕЗ ИЗМЕНЕНИЙ)
# ==========================================

def read_varint(buffer, idx):
    result = 0
    shift = 0
    while True:
        if idx >= len(buffer): return result, idx
        byte = buffer[idx]
        idx += 1
        result |= (byte & 0x7f) << shift
        if not (byte & 0x80): return result, idx
        shift += 7

def parse_otp_account(data):
    idx = 0
    info = {}
    while idx < len(data):
        key, idx = read_varint(data, idx)
        wire_type = key & 7
        if wire_type == 2: 
            length, idx = read_varint(data, idx)
            value = data[idx : idx + length]
            idx += length
            field_num = key >> 3
            if field_num == 1: info['secret'] = value
            elif field_num == 2: info['name'] = value.decode('utf-8', errors='ignore')
            elif field_num == 3: info['issuer'] = value.decode('utf-8', errors='ignore')
        elif wire_type == 0: _, idx = read_varint(data, idx)
        elif wire_type == 1: idx += 8
        elif wire_type == 5: idx += 4
    return info

def extract_accounts(uri):
    if not uri or "otpauth-migration" not in uri: return []
    parsed = urllib.parse.urlparse(uri)
    query_params = urllib.parse.parse_qs(parsed.query)
    if 'data' not in query_params: return []
    data_b64 = query_params['data'][0]
    pad = len(data_b64) % 4
    if pad: data_b64 += '=' * (4 - pad)
    try: data_bytes = base64.b64decode(data_b64)
    except: return []

    buffer = data_bytes
    idx = 0
    accounts = []
    while idx < len(buffer):
        key, idx = read_varint(buffer, idx)
        wire_type = key & 7
        if (key >> 3) == 1 and wire_type == 2:
            length, idx = read_varint(buffer, idx)
            accounts.append(parse_otp_account(buffer[idx : idx + length]))
            idx += length
        else:
            if wire_type == 0: _, idx = read_varint(buffer, idx)
            elif wire_type == 2: l, idx = read_varint(buffer, idx); idx += l
            elif wire_type == 1: idx += 8
            elif wire_type == 5: idx += 4
            else: break
    return accounts

# ==========================================
# ЧАСТЬ 2: РАБОТА С ФАЙЛОМ И ЗАПИСЬ
# ==========================================

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh

def run_decoder(image_path, output_file):
    print(f"\n[*] Загружаю файл: {image_path}")
    
    img = cv2.imread(image_path)
    if img is None:
        print("[!] ОШИБКА: Не удалось прочитать картинку.")
        return

    detector = cv2.QRCodeDetector()
    data_uri, _, _ = detector.detectAndDecode(img)
    
    if not data_uri:
        print("[i] Усиливаю контраст...")
        processed_img = preprocess_image(img)
        data_uri, _, _ = detector.detectAndDecode(processed_img)

    if not data_uri:
        print("[!] НЕУДАЧА: QR-код не найден.")
        return

    print("[*] QR-код распознан!")
    accounts = extract_accounts(data_uri)
    
    if not accounts:
        print("[!] Аккаунтов внутри не найдено.")
        return

    print(f"[*] Найдено новых аккаунтов: {len(accounts)}")

    # === ЛОГИКА ДОБАВЛЕНИЯ (APPEND) ===
    
    mode = 'w' # По умолчанию - перезапись
    is_append = False
    
    # Проверка: существует ли файл и не пустой ли он
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        mode = 'a' # Режим добавления
        is_append = True
        print(f"[*] Файл '{output_file}' существует и не пуст. Добавляем данные...")
    else:
        print(f"[*] Создаем новый файл '{output_file}'...")

    try:
        with open(output_file, mode, encoding='utf-8') as f:
            
            # Если это добавление, пишем разделитель
            if is_append:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write("\n\n" + "="*40 + "\n")
                f.write(f"=== ДОБАВЛЕНО: {timestamp} ===\n")
                f.write("="*40 + "\n\n")
            else:
                # Если новый файл - пишем заголовок
                f.write("=== EXPORTED GOOGLE AUTH KEYS ===\n\n")

            for i, acc in enumerate(accounts, 1):
                name = acc.get('name', 'Без названия')
                issuer = acc.get('issuer', 'Без издателя')
                sec_bytes = acc.get('secret')
                
                sec_b32 = "ERROR"
                if sec_bytes:
                    sec_b32 = base64.b32encode(sec_bytes).decode().replace('=', '')
                
                block = (f"Account {i}:\n"
                         f"Name:   {name}\n"
                         f"Issuer: {issuer}\n"
                         f"Secret: {sec_b32}\n"
                         f"{'-'*40}\n")
                
                print(block.strip()) # Вывод в консоль
                f.write(block)       # Запись в файл
                
        print(f"\n[OK] Успешно сохранено в {output_file}")
        
    except Exception as e:
        print(f"[!] Ошибка при записи файла: {e}")

# ==========================================
# ЧАСТЬ 3: ВВОД ПОЛЬЗОВАТЕЛЯ
# ==========================================

if __name__ == "__main__":
    print("=== Google Authenticator Decoder (Append Mode) ===")
    
    while True:
        raw_input = input("Перетащите картинку сюда (или 'q' для выхода): ")
        filepath = raw_input.strip(' "\'')
        
        if filepath.lower() == 'q':
            sys.exit()
            
        if not filepath:
            continue
            
        if os.path.exists(filepath):
            run_decoder(filepath, "accounts.txt")
            # Не выходим из цикла, чтобы можно было добавить следующий файл сразу
            print("\n--- Готов к следующему файлу ---\n")
        else:
            print(f"[!] Файл не найден.\n")
    input("\nНажмите Enter, чтобы выйти...")