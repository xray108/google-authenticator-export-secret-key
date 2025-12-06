# Google Authenticator Migration Decoder

![Build Status](https://github.com/xray108/google-authenticator-export-secret-key/actions/workflows/release.yml/badge.svg)

Утилита для декодирования QR-кодов экспорта из приложения **Google Authenticator**. Позволяет извлечь секретные ключи (TOTP Secret Keys) для переноса их в другие приложения (например, KeePassXC, Bitwarden, 2FAS, Proton Authentificator) или для создания резервной копии.

## 🚀 Возможности

* **Полная локальность:** Все вычисления происходят на вашем компьютере, данные никуда не отправляются.
* **Поддержка форматов:** Работает с PNG, JPG, JPEG, BMP, WEBP.
* **Умное чтение:** Если QR-код не читается сразу, применяется алгоритм повышения контрастности.
* **Накопительный режим:** Результаты сохраняются в файл `accounts.txt`. Если файл уже существует, новые данные добавляются в конец (append), а не перезаписывают старые.
* **Minimal Dependencies:** Использует только OpenCV для чтения картинки. Декодирование Protobuf написано вручную без тяжелых библиотек.

---


[![Latest Release](https://img.shields.io/github/v/release/xray108/google-authenticator-export-secret-key?label=Download&style=for-the-badge&color=success)](https://github.com/xray108/google-authenticator-export-secret-key/releases/latest)

## 📥 Скачать

Скачайте готовую версию для вашей системы со страницы **[Releases](https://github.com/xray108/google-authenticator-export-secret-key/releases/latest)**:

* 🖥 **Windows:** `GoogleAuthDecoder-Windows.exe`
* 🐧 **Linux:** `GoogleAuthDecoder-Linux`

---

## 📥 Как пользоваться (Windows / Linux)

Вам не нужно устанавливать Python. Вы можете скачать готовую сборку.

1.  Перейдите во вкладку **Releases** в этом репозитории.
2.  Скачайте версию для вашей ОС (`GoogleAuthDecoder-Windows.exe` для Windows).
3.  Подготовьте скриншот QR-кода экспорта (см. инструкцию ниже).
4.  Запустите программу.
5.  **Перетащите файл картинки** в окно консоли и нажмите Enter.
6.  Рядом с программой появится файл `accounts.txt` с вашими ключами.

---

## 🛠 Запуск из исходного кода (Python)

Если вы хотите запустить скрипт вручную:

1.  **Клонируйте репозиторий:**
    ```bash
    git clone [https://github.com/xray108/google-authenticator-export-secret-key.git](https://github.com/xray108/google-authenticator-export-secret-key.git)
    cd google-authenticator-export-secret-key
    ```

2.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
    *(В requirements.txt находится только `opencv-python-headless`)*

3.  **Запустите:**
    ```bash
    python main.py
    ```

---

## 📱 Как получить QR-код

1.  Откройте приложение **Google Authenticator** на телефоне.
2.  Нажмите на меню (три точки) или иконку профиля.
3.  Выберите **Перенести аккаунты** -> **Экспорт аккаунтов**.
4.  Выберите аккаунты и нажмите **Далее**.
5.  Появится QR-код. Сделайте его скриншот или фото.
    * *Совет: Если аккаунтов много, Google разобьет их на несколько QR-кодов. Программа поддерживает это — просто скармливайте ей картинки по очереди, все данные сохранятся в один файл.*

---

## 🔒 Безопасность

* Файл `accounts.txt` содержит **незашифрованные секретные ключи**.
* Любой, кто получит доступ к этому файлу, сможет генерировать коды для входа в ваши аккаунты.
* **Рекомендация:** После импорта ключей в новый менеджер паролей, **удалите** файл `accounts.txt` и сами картинки QR-кодов безвозвратно (Shift+Delete).

## 📄 Лицензия

MIT License. Вы можете использовать этот код свободно.