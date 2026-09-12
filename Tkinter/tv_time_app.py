#github version0
import sys
import os
import random
import threading
import time
import locale
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import wave
import numpy as np
import pygame
from tkinterdnd2 import DND_FILES, TkinterDnD


# Helper function for PyInstaller to locate bundled assets at runtime
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None

film_files = {
    "7 meme sounds": "7 meme sounds.mp4",
    "explosion sound effects": "explosion sound effects.mp4",
}
film_list = list(film_files.keys())

THEMES = {
    "Royal Purple": "#4B0082",
    "Midnight Blue": "#0A192F",
    "Dark Charcoal": "#1E1E1E",
    "Retro Teal": "#005F73",
    "Crimson Red": "#641220",
    "Forest Green": "#1B4332",
    "Cyberpunk Pink": "#7209B7",
    "Slate Gray": "#343A40",
    "Sunset Orange": "#9D0208",
    "Deep Indigo": "#3F37C9",
    "Chocolate Brown": "#372213",
    "Pitch Black": "#000000",
    "Vintage Sepia": "#4A3B32"
}

BAR_WHITE = "#FFFFFF"

current_theme_name = "Royal Purple"
BG_COLOR = THEMES[current_theme_name]
current_alpha = 0.15

selected_movie = ""
selected_index = 0

is_video_playing = False
is_paused = False
is_seeking = False
is_muted = False
is_looping = False
is_pip_mode = False
is_fullscreen = False

normal_geom = "600x630"
playback_speed = 1.0
previous_volume = 80
gif_frames = []

current_frame_pos = 0
total_frames = 0
video_fps = 30
controls_visible = False

last_ui_update_sec = -1

LOCALE_MAP = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "tr": "Turkish",
    "pt": "Portuguese",
    "it": "Italian",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese"
}

LANGUAGES_WITH_FLAGS = {
    "English": "🇺🇸 English",
    "Spanish": "🇪🇸 Español",
    "French": "🇫🇷 Français",
    "German": "🇩🇪 Deutsch",
    "Turkish": "🇹🇷 Türkçe",
    "Portuguese": "🇧🇷 Português",
    "Italian": "🇮🇹 Italiano",
    "Russian": "🇷🇺 Русский",
    "Chinese": "🇨🇳 中文",
    "Japanese": "🇯🇵 日本語"
}


def detect_os_language():
    try:
        sys_lang, _ = locale.getdefaultlocale()
        if sys_lang:
            lang_code = sys_lang[:2].lower()
            return LOCALE_MAP.get(lang_code, "English")
    except Exception:
        pass
    return "English"


current_language = detect_os_language()

TRANSLATIONS = {
    "English": {
        "app_brand": "📺 TV TIME by MR ant TENNA",
        "title": "Click the button Below or Drop an .mp4 here\n[ESC: Stop | Space: Pause | ←/→: Seek | M: Mute]",
        "show_tv": "Show TV SHOW:",
        "pause": "⏸ Pause",
        "resume": "▶ Resume",
        "stop": "⏹ Stop",
        "loop_off": "🔁 Loop: OFF",
        "loop_on": "🔁 Loop: ON",
        "select_lang": "🌐 Select Language / Seleccionar Idioma:",
        "settings_title": "Offline TV Settings",
        "theme_label": "Background Color Theme:",
        "static_label": "TV Static Background Intensity:",
        "btn_save": "Save & Apply",
        "warn_title": "TV TIME - Warning",
        "warn_text": "This will show you the TV\nSelected: {movie}\n\nPress Start to start the movie or Change to pick another.",
        "btn_start": "Start",
        "btn_change": "Change",
        "err_title": "System Error",
        "err_file_missing": "'{file}' could not be located!",
        "err_invalid_file": "Please drop a valid .mp4 video file!",
        "btn_ok": "OK"
    },
    "Spanish": {
        "app_brand": "📺 TIEMPO DE TV por MR ant TENNA",
        "title": "Haga clic en el botón de abajo o arrastre un .mp4 aquí\n[ESC: Detener | Espacio: Pausa | ←/→: Buscar | M: Silenciar]",
        "show_tv": "Mostrar Programa de TV:",
        "pause": "⏸ Pausa",
        "resume": "▶ Continuar",
        "stop": "⏹ Detener",
        "loop_off": "🔁 Bucle: DESACTIVADO",
        "loop_on": "🔁 Bucle: ACTIVADO",
        "select_lang": "🌐 Seleccionar Idioma / Select Language:",
        "settings_title": "Configuración de TV sin conexión",
        "theme_label": "Tema de color de fondo:",
        "static_label": "Intensidad de estática de TV:",
        "btn_save": "Guardar y aplicar",
        "warn_title": "TIEMPO DE TV - Advertencia",
        "warn_text": "Esto te mostrará la TV\nSeleccionado: {movie}\n\nPresiona Iniciar para ver o Cambiar para elegir otro.",
        "btn_start": "Iniciar",
        "btn_change": "Cambiar",
        "err_title": "Error del sistema",
        "err_file_missing": "¡No se pudo encontrar '{file}'!",
        "err_invalid_file": "¡Por favor arrastre un archivo .mp4 válido!",
        "btn_ok": "Aceptar"
    },
    "French": {
        "app_brand": "📺 HEURE DE LA TV par MR ant TENNA",
        "title": "Cliquez sur le bouton ci-dessous ou déposez un .mp4 ici\n[ESC: Arrêter | Espace: Pause | ←/→: Chercher | M: Muet]",
        "show_tv": "Afficher l'émission TV:",
        "pause": "⏸ Pause",
        "resume": "▶ Reprendre",
        "stop": "⏹ Arrêter",
        "loop_off": "🔁 Boucle: DÉSACTIVÉE",
        "loop_on": "🔁 Boucle: ACTIVÉE",
        "select_lang": "🌐 Sélectionner la langue:",
        "settings_title": "Paramètres TV hors ligne",
        "theme_label": "Thème de couleur de fond:",
        "static_label": "Intensité des parasites TV:",
        "btn_save": "Enregistrer et appliquer",
        "warn_title": "HEURE DE LA TV - Avertissement",
        "warn_text": "Ceci va afficher la TV\nSélectionné: {movie}\n\nAppuyez sur Démarrer pour regarder ou Modifier pour en choisir un autre.",
        "btn_start": "Démarrer",
        "btn_change": "Modifier",
        "err_title": "Erreur système",
        "err_file_missing": "'{file}' est introuvable!",
        "err_invalid_file": "Veuillez déposer un fichier .mp4 valide!",
        "btn_ok": "OK"
    },
    "German": {
        "app_brand": "📺 ZEIT FÜR TV von MR ant TENNA",
        "title": "Klicken Sie unten oder ziehen Sie eine .mp4-Datei hierher\n[ESC: Stopp | Leertaste: Pause | ←/→: Suchen | M: Stumm]",
        "show_tv": "TV-Sendung anzeigen:",
        "pause": "⏸ Pause",
        "resume": "▶ Fortsetzen",
        "stop": "⏹ Stopp",
        "loop_off": "🔁 Schleife: AUS",
        "loop_on": "🔁 Schleife: EIN",
        "select_lang": "🌐 Sprache auswählen:",
        "settings_title": "Offline-TV-Einstellungen",
        "theme_label": "Hintergrundfarbthema:",
        "static_label": "TV-Rauschintensität:",
        "btn_save": "Speichern & Anwenden",
        "warn_title": "ZEIT FÜR TV - Warnung",
        "warn_text": "Dies zeigt Ihnen den Fernseher\nAusgewählt: {movie}\n\nDrücken Sie Start zum Abspielen oder Ändern für einen anderen Film.",
        "btn_start": "Start",
        "btn_change": "Ändern",
        "err_title": "Systemfehler",
        "err_file_missing": "'{file}' konnte nicht gefunden werden!",
        "err_invalid_file": "Bitte ziehen Sie eine gültige .mp4-Datei hierher!",
        "btn_ok": "OK"
    },
    "Turkish": {
        "app_brand": "📺 Bay TENNA ile TV ZAMANI",
        "title": "Aşağıdaki düğmeye tıklayın veya buraya bir .mp4 sürükleyin\n[ESC: Durdur | Alan: Duraklat | ←/→: Ara | M: Sessiz]",
        "show_tv": "TV Programını Göster:",
        "pause": "⏸ Duraklat",
        "resume": "▶ Devam Et",
        "stop": "⏹ Durdur",
        "loop_off": "🔁 Döngü: KAPALI",
        "loop_on": "🔁 Döngü: AÇIK",
        "select_lang": "🌐 Dil Seçin / Select Language:",
        "settings_title": "Çevrimdışı TV Ayarları",
        "theme_label": "Arka Plan Renk Teması:",
        "static_label": "TV Parazit Arka Plan Yoğunluğu:",
        "btn_save": "Kaydet ve Uygula",
        "warn_title": "TV ZAMANI - Uyarı",
        "warn_text": "Bu işlem TV gösterimini başlatacak\nSeçilen: {movie}\n\nBaşlat'a basarak izleyin veya Değiştir'e basarak başka bir tane seçin.",
        "btn_start": "Başlat",
        "btn_change": "Değiştir",
        "err_title": "Sistem Hatası",
        "err_file_missing": "'{file}' dosyası bulunamadı!",
        "err_invalid_file": "Lütfen geçerli bir .mp4 video dosyası sürükleyin!",
        "btn_ok": "Tamam"
    },
    "Portuguese": {
        "app_brand": "📺 HORA DA TV por MR ant TENNA",
        "title": "Clique no botão abaixo ou solte um .mp4 aqui\n[ESC: Parar | Espaço: Pausa | ←/→: Buscar | M: Mudo]",
        "show_tv": "Mostrar Programa de TV:",
        "pause": "⏸ Pausa",
        "resume": "▶ Continuar",
        "stop": "⏹ Parar",
        "loop_off": "🔁 Loop: DESLIGADO",
        "loop_on": "🔁 Loop: LIGADO",
        "select_lang": "🌐 Selecionar Idioma:",
        "settings_title": "Configurações de TV Offline",
        "theme_label": "Tema de Cor de Fundo:",
        "static_label": "Intensidade de Chiado da TV:",
        "btn_save": "Salvar e Aplicar",
        "warn_title": "HORA DA TV - Aviso",
        "warn_text": "Isso mostrará a TV\nSelecionado: {movie}\n\nPressione Iniciar para assistir ou Alterar para escolher outro.",
        "btn_start": "Iniciar",
        "btn_change": "Alterar",
        "err_title": "Erro do Sistema",
        "err_file_missing": "'{file}' não pôde ser localizado!",
        "err_invalid_file": "Por favor, solte um arquivo .mp4 válido!",
        "btn_ok": "OK"
    },
    "Italian": {
        "app_brand": "📺 ORA DELLA TV di MR ant TENNA",
        "title": "Fai clic sul pulsante qui sotto o rilascia un .mp4 qui\n[ESC: Ferma | Spazio: Pausa | ←/→: Cerca | M: Muto]",
        "show_tv": "Mostra Programma TV:",
        "pause": "⏸ Pausa",
        "resume": "▶ Riprendi",
        "stop": "⏹ Ferma",
        "loop_off": "🔁 Loop: DISATTIVATO",
        "loop_on": "🔁 Loop: ATTIVATO",
        "select_lang": "🌐 Seleziona Lingua:",
        "settings_title": "Impostazioni TV Offline",
        "theme_label": "Tema Colore di Sfondo:",
        "static_label": "Intensità Effetto TV Statico:",
        "btn_save": "Salva e Applica",
        "warn_title": "ORA DELLA TV - Avviso",
        "warn_text": "Questo mostrerà la TV\nSelezionato: {movie}\n\nPremi Inizia per guardare o Modifica per sceglierne un altro.",
        "btn_start": "Inizia",
        "btn_change": "Modifica",
        "err_title": "Errore di Sistema",
        "err_file_missing": "Impossibile trovare '{file}'!",
        "err_invalid_file": "Rilascia un file .mp4 valido!",
        "btn_ok": "OK"
    },
    "Russian": {
        "app_brand": "📺 ВРЕМЯ ТВ от MR ant TENNA",
        "title": "Нажмите кнопку ниже или перетащите сюда .mp4\n[ESC: Стоп | Пробел: Пауза | ←/→: Поиск | M: Без звука]",
        "show_tv": "Показать ТВ-шоу:",
        "pause": "⏸ Пауза",
        "resume": "▶ Продолжить",
        "stop": "⏹ Стоп",
        "loop_off": "🔁 Повтор: ВЫКЛ",
        "loop_on": "🔁 Повтор: ВКЛ",
        "select_lang": "🌐 Выберите язык:",
        "settings_title": "Настройки оффлайн ТВ",
        "theme_label": "Тема цвета фона:",
        "static_label": "Интенсивность помех ТВ:",
        "btn_save": "Сохранить и применить",
        "warn_title": "ВРЕМЯ ТВ - Предупреждение",
        "warn_text": "Это покажет вам ТВ\nВыбрано: {movie}\n\nНажмите Старт для просмотра или Изменить для выбора другого.",
        "btn_start": "Старт",
        "btn_change": "Изменить",
        "err_title": "Системная ошибка",
        "err_file_missing": "Файл '{file}' не найден!",
        "err_invalid_file": "Пожалуйста, перетащите корректный файл .mp4!",
        "btn_ok": "ОК"
    },
    "Chinese": {
        "app_brand": "📺 MR ant TENNA 的电视时间",
        "title": "点击下方按钮或在此拖入 .mp4 文件\n[ESC: 停止 | 空格: 暂停 | ←/→: 快进/快退 | M: 静音]",
        "show_tv": "播放电视节目：",
        "pause": "⏸ 暂停",
        "resume": "▶ 继续",
        "stop": "⏹ 停止",
        "loop_off": "🔁 循环：关闭",
        "loop_on": "🔁 循环：开启",
        "select_lang": "🌐 选择语言 / Select Language:",
        "settings_title": "离线电视设置",
        "theme_label": "背景颜色主题：",
        "static_label": "电视雪花噪音强度：",
        "btn_save": "保存并应用",
        "warn_title": "电视时间 - 警告",
        "warn_text": "将为您播放电视内容\n已选择：{movie}\n\n点击开始播放，或点击更改选择其他内容。",
        "btn_start": "开始",
        "btn_change": "更改",
        "err_title": "系统错误",
        "err_file_missing": "无法找到文件 '{file}'！",
        "err_invalid_file": "请拖入有效的 .mp4 视频文件！",
        "btn_ok": "确定"
    },
    "Japanese": {
        "app_brand": "📺 MR ant TENNAのテレビタイム",
        "title": "下のボタンをクリックするか、ここに .mp4 をドロップしてください\n[ESC: 停止 | スペース: 一時停止 | ←/→: シーク | M: 消音]",
        "show_tv": "テレビ番組を表示:",
        "pause": "⏸ 一時停止",
        "resume": "▶ 再生",
        "stop": "⏹ 停止",
        "loop_off": "🔁 ループ: オフ",
        "loop_on": "🔁 ループ: オン",
        "select_lang": "🌐 言語を選択:",
        "settings_title": "オフラインTV設定",
        "theme_label": "背景色テーマ:",
        "static_label": "TV砂嵐の強度:",
        "btn_save": "保存して適用",
        "warn_title": "テレビタイム - 警告",
        "warn_text": "テレビを表示します\n選択中: {movie}\n\n開始を押して視聴するか、変更を押して別のものを選択してください。",
        "btn_start": "開始",
        "btn_change": "変更",
        "err_title": "システムエラー",
        "err_file_missing": "'{file}' が見つかりませんでした！",
        "err_invalid_file": "有効な .mp4 文件をドロップしてください！",
        "btn_ok": "OK"
    }
}


def get_text(key):
    if current_language in TRANSLATIONS and key in TRANSLATIONS[current_language]:
        return TRANSLATIONS[current_language][key]
    return TRANSLATIONS["English"].get(key, key)


def show_custom_alert(title_key, message_key, format_val=""):
    alert_box = tk.Toplevel(root)
    alert_box.title(get_text(title_key))
    alert_box.geometry("380x150")
    alert_box.resizable(False, False)
    alert_box.configure(bg="#F0F0F0")

    alert_box.transient(root)
    alert_box.grab_set()

    msg_text = get_text(message_key).format(file=format_val) if format_val else get_text(message_key)

    lbl = tk.Label(
        alert_box,
        text=msg_text,
        font=("Arial", 10),
        bg="#F0F0F0",
        justify="center",
        wraplength=340
    )
    lbl.pack(pady=20)

    btn_ok = tk.Button(
        alert_box,
        text=get_text("btn_ok"),
        width=10,
        command=alert_box.destroy,
        font=("Arial", 9, "bold")
    )
    btn_ok.pack(side="bottom", pady=15)


try:
    pygame.mixer.init()
except Exception as e:
    print(f"Pygame mixer init error: {e}")

root = TkinterDnD.Tk()
root.title("TV Viewer Global V1.0")
root.geometry("600x630")
root.configure(bg=BG_COLOR)

icon_path = resource_path("Low quality TV.ico")
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except Exception:
        pass


def extract_audio_if_needed(mp4_path):
    wav_path = os.path.splitext(mp4_path)[0] + ".wav"
    if not os.path.exists(wav_path):
        if VideoFileClip is None:
            return None
        try:
            clip = VideoFileClip(mp4_path)
            if clip.audio is not None:
                clip.audio.write_audiofile(wav_path, logger=None)
            clip.close()
        except Exception as e:
            print(f"Audio extraction error: {e}")
            return None
    return wav_path


def get_sped_up_wav(wav_path, speed):
    if speed == 1.0 or not wav_path or not os.path.exists(wav_path):
        return wav_path

    base, ext = os.path.splitext(wav_path)
    temp_wav_path = f"{base}_speed_{speed}x{ext}"

    if os.path.exists(temp_wav_path):
        return temp_wav_path

    try:
        with wave.open(wav_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_data = wf.readframes(n_frames)

        dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sampwidth)
        if not dtype:
            return wav_path

        audio_np = np.frombuffer(audio_data, dtype=dtype)

        if n_channels > 1:
            audio_np = audio_np.reshape(-1, n_channels)

        old_len = len(audio_np)
        new_len = int(old_len / speed)
        old_indices = np.arange(old_len)
        new_indices = np.linspace(0, old_len - 1, new_len)

        if n_channels > 1:
            new_audio = np.zeros((new_len, n_channels), dtype=dtype)
            for c in range(n_channels):
                new_audio[:, c] = np.interp(new_indices, old_indices, audio_np[:, c]).astype(dtype)
        else:
            new_audio = np.interp(new_indices, old_indices, audio_np).astype(dtype)

        with wave.open(temp_wav_path, 'wb') as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(framerate)
            wf.writeframes(new_audio.tobytes())

        return temp_wav_path
    except Exception as e:
        print(f"Error generating sped up audio: {e}")
        return wav_path


def play_audio_file(file_name_or_path, loop=False, start_sec=0.0, apply_speed=True):
    if os.path.isabs(file_name_or_path) and os.path.exists(file_name_or_path):
        final_path = file_name_or_path
    else:
        path1 = resource_path(file_name_or_path)
        path2 = os.path.join(os.getcwd(), file_name_or_path)
        if os.path.exists(path1):
            final_path = path1
        elif os.path.exists(path2):
            final_path = path2
        else:
            final_path = None

    if final_path:
        if apply_speed:
            final_path = get_sped_up_wav(final_path, playback_speed)

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(final_path)
            val = volume_slider.get() / 100.0 if 'volume_slider' in globals() else 0.8
            pygame.mixer.music.set_volume(0.0 if (is_muted or is_paused) else val)
            pygame.mixer.music.play(-1 if loop else 0, start=start_sec)
        except Exception as e:
            print(f"Audio playback error: {e}")


def stream_video_engine(video_path, target_w, target_h, wav_path):
    global is_video_playing, is_paused, current_frame_pos, total_frames, video_fps, is_seeking, last_ui_update_sec

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 30
    frame_delay = 1.0 / video_fps
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    root.after(0, lambda: progress_slider.config(to=max(1, total_frames)))
    root.after(0, lambda: pip_progress.config(to=max(1, total_frames)))

    if wav_path:
        play_audio_file(wav_path, loop=is_looping, apply_speed=True)

    while cap.isOpened() and is_video_playing:
        if is_paused:
            time.sleep(0.02)
            continue

        if is_seeking:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos)
            if wav_path:
                seek_time = current_frame_pos / video_fps
                play_audio_file(wav_path, loop=is_looping, start_sec=seek_time, apply_speed=True)
            is_seeking = False

        start_time = time.time()
        ret, frame = cap.read()

        if not ret:
            if is_looping:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                current_frame_pos = 0
                if wav_path:
                    play_audio_file(wav_path, loop=True, start_sec=0.0, apply_speed=True)
                continue
            else:
                is_video_playing = False
                root.after(0, terminate_and_close_video)
                break

        current_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        current_sec = int(current_frame_pos / video_fps)
        if current_sec != last_ui_update_sec:
            last_ui_update_sec = current_sec
            root.after(0, update_progress_ui)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        current_w = video_label.winfo_width() if video_label.winfo_width() > 10 else (
            340 if is_pip_mode else root.winfo_width())
        current_h = video_label.winfo_height() if video_label.winfo_height() > 10 else (
            220 if is_pip_mode else root.winfo_height())

        frame = cv2.resize(frame, (max(1, current_w), max(1, current_h)))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        if is_video_playing:
            try:
                video_label.config(image=img)
                video_label.image = img
            except Exception:
                break

        elapsed = time.time() - start_time
        sleep_time = max(0.001, (frame_delay / playback_speed) - elapsed)
        time.sleep(sleep_time)

    cap.release()


def update_progress_ui():
    if not is_seeking and total_frames > 0 and is_video_playing:
        progress_slider.set(current_frame_pos)
        pip_progress.set(current_frame_pos)

        m, s = divmod(int(current_frame_pos / video_fps), 60)
        tm, ts = divmod(int(total_frames / video_fps), 60)
        time_label.config(text=f"{m:02d}:{s:02d} / {tm:02d}:{ts:02d}")


def on_seek_drag(val):
    global is_seeking, current_frame_pos
    is_seeking = True
    current_frame_pos = int(float(val))


def show_channel_overlay():
    channel_info.config(text=f"CH {selected_index + 1:02d} - {selected_movie}")
    channel_info.place(relx=0.05, rely=0.08, anchor="nw")
    channel_info.lift()
    root.after(3000, lambda: channel_info.place_forget())


def load_gif_frames(w, h):
    global gif_frames
    gif_frames.clear()
    gif_path = resource_path("static-tv-static.gif")
    if os.path.exists(gif_path):
        try:
            gif_img = Image.open(gif_path)
            while True:
                frame = gif_img.copy().convert("RGBA").resize((max(1, w), max(1, h)), Image.Resampling.LANCZOS)
                gif_frames.append(ImageTk.PhotoImage(frame))
                gif_img.seek(gif_img.tell() + 1)
        except EOFError:
            pass
        except Exception:
            gif_frames = []


def render_static_canvas(w, h):
    canvas.delete("static")
    if gif_frames:
        frame_idx = random.randint(0, len(gif_frames) - 1)
        canvas.create_image(0, 0, image=gif_frames[frame_idx], anchor="nw", tags="static")
    else:
        gray_val = random.randint(50, 200)
        color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
        canvas.create_rectangle(0, 0, w, h, fill=color, outline="", tags="static")


def play_static_glitch_transition(callback_fn):
    global current_alpha
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

    current_alpha = 1.0
    load_gif_frames(root.winfo_width(), root.winfo_height())
    play_audio_file("its-tv-time-deltarune.wav", apply_speed=False)

    root.after(600, callback_fn)


def boot_video_player():
    global current_alpha, is_video_playing, is_paused, controls_visible, last_ui_update_sec

    target_path_or_name = film_files.get(selected_movie)
    if target_path_or_name and os.path.isabs(target_path_or_name):
        final_video_path = target_path_or_name if os.path.exists(target_path_or_name) else None
    else:
        v_path1 = resource_path(target_path_or_name) if target_path_or_name else None
        v_path2 = os.path.join(os.getcwd(), target_path_or_name) if target_path_or_name else None
        if v_path1 and os.path.exists(v_path1):
            final_video_path = v_path1
        elif v_path2 and os.path.exists(v_path2):
            final_video_path = v_path2
        else:
            final_video_path = None

    if not final_video_path:
        exit_fullscreen()
        show_custom_alert("err_title", "err_file_missing", format_val=target_path_or_name)
        return

    wav_path = extract_audio_if_needed(final_video_path)

    current_alpha = 0.05
    load_gif_frames(root.winfo_width(), root.winfo_height())

    title_bar.lift()
    video_label.place(relx=0, rely=0.06, relwidth=1.0, relheight=0.94)
    controls_frame.place(relx=0.5, rely=0.88, anchor="center")
    controls_visible = True

    video_label.lift()
    controls_frame.lift()

    show_channel_overlay()

    is_video_playing = True
    is_paused = False
    last_ui_update_sec = -1
    btn_pause.config(text=get_text("pause"), bg="#FF9800")
    pip_center_pause.config(text="║")

    w = root.winfo_width()
    h = root.winfo_height()

    threading.Thread(target=stream_video_engine, args=(final_video_path, w, h, wav_path), daemon=True).start()


def start_pip_drag(e):
    root.offset_x = e.x_root - root.winfo_x()
    root.offset_y = e.y_root - root.winfo_y()


def do_pip_drag(e):
    x = e.x_root - root.offset_x
    y = e.y_root - root.offset_y
    root.geometry(f"+{x}+{y}")


def toggle_pip_mode():
    global is_pip_mode, normal_geom, is_fullscreen
    if not is_video_playing:
        return

    if not is_pip_mode:
        is_pip_mode = True
        btn_pip.config(text="🔲 Exit PiP", bg="#00838F")
        normal_geom = root.geometry()

        if is_fullscreen:
            root.attributes("-fullscreen", False)
            is_fullscreen = False

        controls_frame.place_forget()
        title_bar.pack_forget()
        canvas.pack_forget()
        dock_frame.pack_forget()

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.geometry("340x220+100+100")

        video_label.place_forget()
        video_label.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        pip_overlay_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        pip_overlay_frame.lift()

        for element in [pip_top_bar, pip_title_lbl]:
            element.bind("<Button-1>", start_pip_drag)
            element.bind("<B1-Motion>", do_pip_drag)

    else:
        is_pip_mode = False
        btn_pip.config(text="🔲 PiP", bg="#333333")
        pip_overlay_frame.place_forget()

        root.attributes("-topmost", False)
        root.overrideredirect(False)

        for element in [pip_top_bar, pip_title_lbl]:
            element.unbind("<Button-1>")
            element.unbind("<B1-Motion>")

        title_bar.pack(side="top", fill="x")
        canvas.pack(fill="both", expand=True)
        dock_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        root.geometry(normal_geom)

        video_label.place(relx=0, rely=0.06, relwidth=1.0, relheight=0.94)
        controls_frame.place(relx=0.5, rely=0.88, anchor="center")

        video_label.lift()
        controls_frame.lift()


def toggle_fullscreen(event=None):
    global is_fullscreen
    if is_pip_mode:
        return
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)


def exit_fullscreen():
    global is_fullscreen
    root.attributes("-fullscreen", False)
    is_fullscreen = False


def change_channel(direction):
    global selected_index, selected_movie, is_video_playing
    if not film_list:
        return

    if is_pip_mode:
        toggle_pip_mode()

    is_video_playing = False
    selected_index = (selected_index + direction) % len(film_list)
    selected_movie = film_list[selected_index]

    play_static_glitch_transition(boot_video_player)


def trigger_tv_transition():
    canvas.itemconfig(result_text_id, text="")
    play_static_glitch_transition(boot_video_player)


def show_random_film():
    global selected_movie, selected_index
    if not film_list:
        return
    selected_index = random.randint(0, len(film_list) - 1)
    selected_movie = film_list[selected_index]

    warning_box = tk.Toplevel(root)
    warning_box.title(get_text("warn_title"))
    warning_box.geometry("420x180")
    warning_box.resizable(False, False)
    warning_box.configure(bg="#F0F0F0")

    warning_box.transient(root)
    warning_box.grab_set()

    lbl = tk.Label(
        warning_box,
        text=get_text("warn_text").format(movie=selected_movie),
        font=("Arial", 10),
        bg="#F0F0F0",
        justify="center",
        wraplength=380
    )
    lbl.pack(pady=20)

    btn_frame = tk.Frame(warning_box, bg="#F0F0F0")
    btn_frame.pack(side="bottom", pady=15)

    btn_start = tk.Button(
        btn_frame,
        text=get_text("btn_start"),
        width=12,
        command=lambda: [warning_box.destroy(), trigger_tv_transition()],
        font=("Arial", 9, "bold")
    )
    btn_start.pack(side="left", padx=10)

    btn_change = tk.Button(
        btn_frame,
        text=get_text("btn_change"),
        width=12,
        command=lambda: [warning_box.destroy(), show_random_film()]
    )
    btn_change.pack(side="left", padx=10)


def handle_file_drop(event):
    global selected_movie, selected_index
    raw_data = event.data

    if raw_data.startswith('{') and raw_data.endswith('}'):
        paths = [p.strip('{}') for p in raw_data.split('} {')]
    else:
        paths = [raw_data]

    for file_path in paths:
        if os.path.exists(file_path) and file_path.lower().endswith('.mp4'):
            file_name = os.path.basename(file_path)
            film_files[file_name] = file_path

            if file_name not in film_list:
                film_list.append(file_name)

            selected_movie = file_name
            selected_index = film_list.index(file_name)

            trigger_tv_transition()
            break
        else:
            show_custom_alert("err_title", "err_invalid_file")
            break


def terminate_and_close_video():
    global is_video_playing, controls_visible
    is_video_playing = False
    controls_visible = False

    if is_pip_mode:
        toggle_pip_mode()

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

    video_label.config(image="")
    video_label.place_forget()
    controls_frame.place_forget()
    channel_info.place_forget()

    play_audio_file("Explosion Sound Effects (for test).wav", apply_speed=False)

    exit_fullscreen()


def toggle_pause_resume(event=None):
    global is_paused
    if not is_video_playing:
        return

    if not is_paused:
        is_paused = True
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass
        btn_pause.config(text=get_text("pause"), bg="#4CAF50")
        pip_center_pause.config(text="▶")
    else:
        is_paused = False
        try:
            target_path_or_name = film_files.get(selected_movie)
            if target_path_or_name:
                if os.path.isabs(target_path_or_name):
                    v_path = target_path_or_name
                else:
                    v_path = os.path.join(os.getcwd(), target_path_or_name)

                wav_path = os.path.splitext(v_path)[0] + ".wav"
                if os.path.exists(wav_path):
                    resume_sec = current_frame_pos / (video_fps if video_fps > 0 else 30)
                    play_audio_file(wav_path, loop=is_looping, start_sec=resume_sec, apply_speed=True)
        except Exception as e:
            print(f"Resume sync error: {e}")

        btn_pause.config(text=get_text("pause"), bg="#FF9800")
        pip_center_pause.config(text="║")


def toggle_loop():
    global is_looping
    is_looping = not is_looping
    if is_looping:
        btn_loop.config(text=get_text("loop_on"), bg="#00838F")
    else:
        btn_loop.config(text=get_text("loop_off"), bg="#333333")


def cycle_playback_speed():
    global playback_speed
    speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    try:
        current_idx = speeds.index(playback_speed)
        playback_speed = speeds[(current_idx + 1) % len(speeds)]
    except ValueError:
        playback_speed = 1.0

    btn_speed.config(text=f"⚡ {playback_speed}x")

    if is_video_playing and not is_paused:
        target_path_or_name = film_files.get(selected_movie)
        if target_path_or_name:
            v_path = target_path_or_name if os.path.isabs(target_path_or_name) else os.path.join(os.getcwd(),
                                                                                                 target_path_or_name)
            wav_path = os.path.splitext(v_path)[0] + ".wav"
            if os.path.exists(wav_path):
                current_sec = current_frame_pos / (video_fps if video_fps > 0 else 30)
                play_audio_file(wav_path, loop=is_looping, start_sec=current_sec, apply_speed=True)


def set_volume(val):
    global is_muted
    vol = float(val) / 100.0
    if vol > 0:
        is_muted = False
        btn_mute.config(text="🔊")
    pygame.mixer.music.set_volume(0.0 if (is_muted or is_paused) else vol)


def toggle_mute(event=None):
    global is_muted, previous_volume
    if is_muted:
        is_muted = False
        btn_mute.config(text="🔊")
        volume_slider.set(previous_volume)
        pygame.mixer.music.set_volume(previous_volume / 100.0)
    else:
        is_muted = True
        previous_volume = volume_slider.get()
        btn_mute.config(text="🔇")
        volume_slider.set(0)
        pygame.mixer.music.set_volume(0.0)


def seek_relative(seconds):
    global current_frame_pos, is_seeking
    if is_video_playing:
        delta_frames = int(seconds * video_fps)
        current_frame_pos = max(0, min(total_frames, current_frame_pos + delta_frames))
        is_seeking = True


def open_settings_window():
    global current_alpha, current_language, current_theme_name, BG_COLOR

    set_win = tk.Toplevel(root)
    set_win.title(get_text("settings_title"))
    set_win.geometry("420x420")
    set_win.resizable(False, False)
    set_win.configure(bg="#2E2E2E")

    set_win.transient(root)
    set_win.grab_set()

    lbl_lang = tk.Label(set_win, text=get_text("select_lang"), font=("Segoe UI", 10, "bold"), fg="white", bg="#2E2E2E")
    lbl_lang.pack(pady=(15, 2))

    lang_combobox = ttk.Combobox(set_win, values=list(LANGUAGES_WITH_FLAGS.values()), state="readonly", width=35)
    lang_combobox.set(LANGUAGES_WITH_FLAGS.get(current_language, LANGUAGES_WITH_FLAGS["English"]))
    lang_combobox.pack(pady=2)

    lbl_theme = tk.Label(set_win, text=get_text("theme_label"), font=("Segoe UI", 10, "bold"), fg="white", bg="#2E2E2E")
    lbl_theme.pack(pady=(15, 2))

    theme_combobox = ttk.Combobox(set_win, values=list(THEMES.keys()), state="readonly", width=35)
    theme_combobox.set(current_theme_name)
    theme_combobox.pack(pady=2)

    lbl_alpha = tk.Label(set_win, text=get_text("static_label"), font=("Segoe UI", 10, "bold"), fg="white",
                         bg="#2E2E2E")
    lbl_alpha.pack(pady=(15, 2))

    alpha_slider = tk.Scale(set_win, from_=0.05, to=0.8, resolution=0.05, orient="horizontal", bg="#2E2E2E", fg="white",
                            highlightthickness=0, length=280)
    alpha_slider.set(current_alpha)
    alpha_slider.pack(pady=2)

    def apply_settings():
        global current_language, current_theme_name, BG_COLOR, current_alpha

        selected_flag = lang_combobox.get()
        for lang_name, flag_name in LANGUAGES_WITH_FLAGS.items():
            if flag_name == selected_flag:
                current_language = lang_name
                break

        current_theme_name = theme_combobox.get()
        BG_COLOR = THEMES[current_theme_name]

        current_alpha = alpha_slider.get()

        update_ui_texts()
        root.configure(bg=BG_COLOR)
        canvas.configure(bg=BG_COLOR)

        set_win.destroy()

    btn_save = tk.Button(
        set_win,
        text=get_text("btn_save"),
        command=apply_settings,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        padx=15,
        pady=5
    )
    btn_save.pack(pady=25)


def update_ui_texts():
    app_brand_label.config(text=get_text("app_brand"))
    canvas.itemconfig(result_text_id, text=get_text("title"))
    lbl_show_tv.config(text=get_text("show_tv"))
    btn_stop.config(text=get_text("stop"))

    if is_paused:
        btn_pause.config(text=get_text("resume"))
    else:
        btn_pause.config(text=get_text("pause"))

    if is_looping:
        btn_loop.config(text=get_text("loop_on"))
    else:
        btn_loop.config(text=get_text("loop_off"))


title_bar = tk.Frame(root, bg="#1E1E1E", height=40)
title_bar.pack(side="top", fill="x")

app_brand_label = tk.Label(
    title_bar,
    text=get_text("app_brand"),
    font=("Segoe UI", 11, "bold"),
    fg="#00FFCC",
    bg="#1E1E1E"
)
app_brand_label.pack(side="left", padx=15)

btn_settings = tk.Button(
    title_bar,
    text="⚙ Settings",
    command=open_settings_window,
    bg="#333333",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief=tk.FLAT,
    padx=10
)
btn_settings.pack(side="right", padx=10, pady=5)

canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
canvas.pack(fill="both", expand=True)

result_text_id = canvas.create_text(
    300,
    200,
    text=get_text("title"),
    fill=BAR_WHITE,
    font=("Segoe UI", 12, "bold"),
    justify="center"
)

dock_frame = tk.Frame(root, bg="#1E1E1E")
dock_frame.pack(side="bottom", fill="x", pady=10, padx=10)

lbl_show_tv = tk.Label(
    dock_frame,
    text=get_text("show_tv"),
    font=("Segoe UI", 10, "bold"),
    fg="white",
    bg="#1E1E1E"
)
lbl_show_tv.pack(side="top", pady=2)

btn_show_tv = tk.Button(
    dock_frame,
    text="📺 START TV SHOW",
    command=show_random_film,
    bg="#6200EA",
    fg="white",
    font=("Segoe UI", 11, "bold"),
    relief=tk.RAISED,
    padx=15,
    pady=5
)
btn_show_tv.pack(side="top", pady=5)

video_label = tk.Label(root, bg="black")
channel_info = tk.Label(root, text="", font=("Consolas", 16, "bold"), fg="#00FF00", bg="black", padx=10, pady=5)

controls_frame = tk.Frame(root, bg="#1E1E1E", padx=10, pady=5)

progress_slider = tk.Scale(
    controls_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=on_seek_drag,
    bg="#1E1E1E",
    fg="white",
    highlightthickness=0,
    length=450,
    showvalue=False
)
progress_slider.pack(side="top", fill="x", pady=2)

time_label = tk.Label(controls_frame, text="00:00 / 00:00", font=("Consolas", 9), fg="#AAAAAA", bg="#1E1E1E")
time_label.pack(side="top", anchor="e", padx=5)

btn_ch_prev = tk.Button(controls_frame, text="⏮ Prev", command=lambda: change_channel(-1), bg="#333333", fg="white",
                        font=("Segoe UI", 9, "bold"))
btn_ch_prev.pack(side="left", padx=2)

btn_pause = tk.Button(controls_frame, text=get_text("pause"), command=toggle_pause_resume, bg="#FF9800", fg="white",
                      font=("Segoe UI", 9, "bold"))
btn_pause.pack(side="left", padx=2)

btn_stop = tk.Button(controls_frame, text=get_text("stop"), command=terminate_and_close_video, bg="#E53935", fg="white",
                     font=("Segoe UI", 9, "bold"))
btn_stop.pack(side="left", padx=2)

btn_ch_next = tk.Button(controls_frame, text="Next ⏭", command=lambda: change_channel(1), bg="#333333", fg="white",
                        font=("Segoe UI", 9, "bold"))
btn_ch_next.pack(side="left", padx=2)

btn_loop = tk.Button(controls_frame, text=get_text("loop_off"), command=toggle_loop, bg="#333333", fg="white",
                     font=("Segoe UI", 9, "bold"))
btn_loop.pack(side="left", padx=2)

btn_speed = tk.Button(controls_frame, text="⚡ 1.0x", command=cycle_playback_speed, bg="#333333", fg="white",
                      font=("Segoe UI", 9, "bold"))
btn_speed.pack(side="left", padx=2)

btn_pip = tk.Button(controls_frame, text="🔲 PiP", command=toggle_pip_mode, bg="#333333", fg="white",
                    font=("Segoe UI", 9, "bold"))
btn_pip.pack(side="left", padx=2)

btn_mute = tk.Button(controls_frame, text="🔊", command=toggle_mute, bg="#333333", fg="white",
                     font=("Segoe UI", 9, "bold"))
btn_mute.pack(side="left", padx=(10, 2))

volume_slider = tk.Scale(
    controls_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=set_volume,
    bg="#1E1E1E",
    fg="white",
    highlightthickness=0,
    length=80,
    showvalue=False
)
volume_slider.set(80)
volume_slider.pack(side="left", padx=2)

pip_overlay_frame = tk.Frame(root, bg="")

pip_top_bar = tk.Frame(pip_overlay_frame, bg="#1E1E1E", height=24)
pip_top_bar.pack(side="top", fill="x")

pip_title_lbl = tk.Label(pip_top_bar, text="PiP Mode", font=("Segoe UI", 8, "bold"), fg="#00FFCC", bg="#1E1E1E")
pip_title_lbl.pack(side="left", padx=5)

pip_top_exit_btn = tk.Button(pip_top_bar, text="❌ Exit PiP", command=toggle_pip_mode, bg="#E53935", fg="white",
                             font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=4)
pip_top_exit_btn.pack(side="right", padx=2, pady=1)

pip_center_controls = tk.Frame(pip_overlay_frame, bg="#1E1E1E")
pip_center_controls.place(relx=0.5, rely=0.5, anchor="center")

pip_center_pause = tk.Button(pip_center_controls, text="║", command=toggle_pause_resume, bg="#333333", fg="white",
                             font=("Segoe UI", 12, "bold"), width=3)
pip_center_pause.pack(side="left", padx=2)

pip_center_exit = tk.Button(pip_center_controls, text="Exit PiP", command=toggle_pip_mode, bg="#00838F", fg="white",
                            font=("Segoe UI", 9, "bold"))
pip_center_exit.pack(side="left", padx=2)

pip_progress = tk.Scale(
    pip_overlay_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=on_seek_drag,
    bg="#1E1E1E",
    fg="white",
    highlightthickness=0,
    showvalue=False
)
pip_progress.pack(side="bottom", fill="x")

root.bind("<Escape>", lambda e: terminate_and_close_video())
root.bind("<space>", toggle_pause_resume)
root.bind("<Left>", lambda e: seek_relative(-5))
root.bind("<Right>", lambda e: seek_relative(5))
root.bind("<m>", toggle_mute)
root.bind("<M>", toggle_mute)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_file_drop)

if len(sys.argv) > 1 and sys.argv[1].lower().endswith('.mp4'):
    startup_video = sys.argv[1]
    if os.path.exists(startup_video):
        file_name = os.path.basename(startup_video)
        film_files[file_name] = startup_video
        if file_name not in film_list:
            film_list.append(file_name)
        selected_movie = file_name
        selected_index = film_list.index(file_name)
        root.after(500, trigger_tv_transition)


def draw_animated_static():
    if not is_video_playing:
        w = root.winfo_width()
        h = root.winfo_height()
        render_static_canvas(w, h)
    root.after(50, draw_animated_static)


draw_animated_static()

root.mainloop()