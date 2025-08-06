#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QTabWidget,
                             QGridLayout, QFrame, QSizePolicy, QSpacerItem,
                             QStyle, QFileDialog, QDialog, QMessageBox, QMenu,
                             QTabBar) # QTabBar eklendi
from PyQt5.QtCore import Qt, QTimer, QTime, QDate, QSize, QUrl, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor # QColor eklendi
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent 

import json
import os
import platform

# --- Medya Oynatıcı Fonksiyonu ---
_player_instance = QMediaPlayer()

def _play_sound(file_path, parent_widget=None):
    """Verilen dosya yolundaki sesi çalar."""
    print(f"DEBUG: _play_sound çağrıldı. file_path: {file_path}")
    print(f"DEBUG: Player state before playing: {_player_instance.state()}")

    if not file_path:
        error_message = "Ses dosyası yolu boş."
        print(f"DEBUG: {error_message}")
        if parent_widget:
            QMessageBox.warning(parent_widget, "Ses Çalma Hatası", error_message)
        else:
            print(f"Uyarı: {error_message}")
        return

    url = QUrl.fromLocalFile(file_path)
    if not url.isValid():
        error_message = f"Ses dosyası yolu geçersiz bir URL formatında: {file_path}"
        print(f"DEBUG: {error_message}")
        if parent_widget:
            QMessageBox.warning(parent_widget, "Ses Çalma Hatası", error_message)
        else:
            print(f"Uyarı: {error_message}")
        return

    if not os.path.exists(file_path):
        error_message = f"Ses dosyası bulunamadı: {file_path}"
        print(f"DEBUG: {error_message}")
        if parent_widget:
            QMessageBox.warning(parent_widget, "Ses Çalma Hatası", error_message)
        else:
            print(f"Uyarı: {error_message}")
        return

    if _player_instance.state() == QMediaPlayer.PlayingState:
        _player_instance.stop()
    _player_instance.setMedia(QMediaContent(url))
    _player_instance.play()
    print(f"Ses çalınıyor: {file_path}")

def _stop_sound():
    """Çalmakta olan sesi durdurur."""
    print(f"DEBUG: _stop_sound çağrıldı. Player state before stop: {_player_instance.state()}")
    if _player_instance.state() == QMediaPlayer.PlayingState:
        _player_instance.stop()
        print("Ses durduruldu.")
    else:
        print("Şu anda çalan bir ses yok.")


# --- Özel Durumlar Penceresi Sınıfı ---
class SpecialSituationsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Özel Durumlar ve Manuel Çalma")
        self.setFixedSize(500, 680) # Pencere yüksekliği 610'dan 680'e çıkarıldı

        # Sirenlerin ve marşların yolunu ana pencereden al
        self.sirenler_base_path = parent.sirenler_base_path if parent else ""
        self.ten_kasim_siren_path = os.path.join(self.sirenler_base_path, "10 KASIM siren ve İstiklal Marşı bileşik.mp3")
        self.istiklal_marsi_path = os.path.join(self.sirenler_base_path, "İSTİKLAL MARŞI.mp3")
        self.saygi_ti_path = os.path.join(self.sirenler_base_path, "saygı_ti.mp3") # Yeni eklenen dosya yolu
        
        self.bell_sound_paths = parent.bell_sound_paths if parent else {} # Ayarlardan gelen zil sesleri


        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # --- 10 Kasım Siren Butonu Grubu ---
        ten_kasim_group = QFrame(self)
        ten_kasim_group.setFrameShape(QFrame.StyledPanel)
        ten_kasim_group.setContentsMargins(10, 10, 10, 10)
        ten_kasim_layout = QVBoxLayout(ten_kasim_group)
        ten_kasim_group.setLayout(ten_kasim_layout)
        ten_kasim_layout.setSpacing(8)

        self.ten_kasim_label = QLabel("<b>10 Kasım Sireni:</b>")
        ten_kasim_layout.addWidget(self.ten_kasim_label)

        # Butonlar için yatay layout
        ten_kasim_buttons_layout = QHBoxLayout()
        self.ten_kasim_button = QPushButton("10 Kasım Siren Çal")
        self.ten_kasim_button.setStyleSheet("background-color: #6a0dad; color: white; font-weight: bold;")
        self.ten_kasim_button.clicked.connect(self._play_ten_kasim_siren)
        self.ten_kasim_button.setMinimumHeight(30)
        ten_kasim_buttons_layout.addWidget(self.ten_kasim_button)

        self.ten_kasim_stop_button = QPushButton("Durdur")
        self.ten_kasim_stop_button.clicked.connect(_stop_sound)
        self.ten_kasim_stop_button.setMinimumHeight(30)
        ten_kasim_buttons_layout.addWidget(self.ten_kasim_stop_button)
        ten_kasim_layout.addLayout(ten_kasim_buttons_layout)

        layout.addWidget(ten_kasim_group)

        # --- Manuel Zil Çalma Grubu ---
        manual_play_group = QFrame(self)
        manual_play_group.setFrameShape(QFrame.StyledPanel)
        manual_play_group.setContentsMargins(10, 10, 10, 10)
        manual_play_layout = QVBoxLayout(manual_play_group)
        manual_play_group.setLayout(manual_play_layout)
        manual_play_layout.setSpacing(8)

        manual_play_layout.addWidget(QLabel("<b>Manuel Ders Zili Çalma:</b>"))

        bell_types = ["İçeri", "Öğretmenler", "Teneffüs"]
        for bell_type in bell_types:
            bell_row_layout = QHBoxLayout()
            play_button = QPushButton(f"{bell_type} Zili Çal")
            play_button.clicked.connect(lambda _, bt=bell_type: self._play_manual_bell(bt))
            play_button.setMinimumHeight(30)
            bell_row_layout.addWidget(play_button)

            stop_button = QPushButton("Durdur")
            stop_button.clicked.connect(_stop_sound)
            stop_button.setMinimumHeight(30)
            bell_row_layout.addWidget(stop_button)
            manual_play_layout.addLayout(bell_row_layout)

        layout.addWidget(manual_play_group)

        # --- Milli Marşlar Grubu ---
        national_anthems_group = QFrame(self)
        national_anthems_group.setFrameShape(QFrame.StyledPanel)
        national_anthems_group.setContentsMargins(10, 10, 10, 10)
        national_anthems_layout = QVBoxLayout(national_anthems_group)
        national_anthems_group.setLayout(national_anthems_layout)
        national_anthems_layout.setSpacing(8)

        national_anthems_layout.addWidget(QLabel("<b>Milli Marşlar:</b>"))

        istiklal_marsi_row_layout = QHBoxLayout()
        self.istiklal_marsi_button = QPushButton("İstiklal Marşımız")
        self.istiklal_marsi_button.setStyleSheet("background-color: #8B0000; color: white; font-weight: bold;")
        self.istiklal_marsi_button.clicked.connect(self._play_istiklal_marsi)
        self.istiklal_marsi_button.setMinimumHeight(30)
        istiklal_marsi_row_layout.addWidget(self.istiklal_marsi_button)
        national_anthems_layout.addLayout(istiklal_marsi_row_layout)
        layout.addWidget(national_anthems_group)
        
        # --- Saygı Duruşu Ti Butonu ---
        saygi_ti_row_layout = QHBoxLayout()
        self.saygi_ti_button = QPushButton("Saygı Duruşu Ti")
        self.saygi_ti_button.setStyleSheet("background-color: #4682B4; color: white; font-weight: bold;")
        self.saygi_ti_button.clicked.connect(self._play_saygi_ti)
        self.saygi_ti_button.setMinimumHeight(30)
        saygi_ti_row_layout.addWidget(self.saygi_ti_button)

        self.saygi_ti_stop_button = QPushButton("Durdur")
        self.saygi_ti_stop_button.clicked.connect(_stop_sound)
        self.saygi_ti_stop_button.setMinimumHeight(30)
        saygi_ti_row_layout.addWidget(self.saygi_ti_stop_button)
        national_anthems_layout.addLayout(saygi_ti_row_layout) # Milli Marşlar grubuna eklendi

        # --- Acil Durum Butonları Grubu ---
        emergency_group = QFrame(self)
        emergency_group.setFrameShape(QFrame.StyledPanel)
        emergency_group.setContentsMargins(10, 10, 10, 10)
        emergency_layout = QVBoxLayout(emergency_group)
        emergency_group.setLayout(emergency_layout)
        emergency_layout.setSpacing(8)

        emergency_layout.addWidget(QLabel("<b>Acil Durum Sirenleri:</b>"))

        # Deprem Sireni
        deprem_row_layout = QHBoxLayout()
        self.deprem_button = QPushButton("Deprem Sireni Çal")
        self.deprem_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.deprem_button.clicked.connect(lambda: self._play_emergency_siren("Deprem", os.path.join(self.sirenler_base_path, "deprem.mp3")))
        self.deprem_button.setMinimumHeight(30)
        deprem_row_layout.addWidget(self.deprem_button)

        self.deprem_stop_button = QPushButton("Durdur")
        self.deprem_stop_button.clicked.connect(_stop_sound)
        self.deprem_stop_button.setMinimumHeight(30)
        deprem_row_layout.addWidget(self.deprem_stop_button)
        emergency_layout.addLayout(deprem_row_layout)

        # Yangın Sireni
        yangin_row_layout = QHBoxLayout()
        self.yangin_button = QPushButton("Yangın Sireni Çal")
        self.yangin_button.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        self.yangin_button.clicked.connect(lambda: self._play_emergency_siren("Yangın", os.path.join(self.sirenler_base_path, "yangın.mp3")))
        self.yangin_button.setMinimumHeight(30)
        yangin_row_layout.addWidget(self.yangin_button)

        self.yangin_stop_button = QPushButton("Durdur")
        self.yangin_stop_button.clicked.connect(_stop_sound)
        self.yangin_stop_button.setMinimumHeight(30)
        yangin_row_layout.addWidget(self.yangin_stop_button)
        emergency_layout.addLayout(yangin_row_layout)


        layout.addWidget(emergency_group)

        layout.addStretch(1)

        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumHeight(30)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def _play_ten_kasim_siren(self):
        _play_sound(self.ten_kasim_siren_path, self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()

    def _play_manual_bell(self, bell_type):
        _play_sound(self.bell_sound_paths.get(bell_type), self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()

    def _play_emergency_siren(self, siren_type, file_path):
        _play_sound(file_path, self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()

    def _play_istiklal_marsi(self):
        _play_sound(self.istiklal_marsi_path, self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()

    def _play_saygi_ti(self): # Yeni eklenen metod
        _play_sound(self.saygi_ti_path, self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()


# --- Ayarlar Penceresi Sınıfı ---
class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setFixedSize(550, 450)

        self.bell_sound_paths = parent.bell_sound_paths if parent else {}
        self.school_name_text = parent.school_name_text if parent else ""
        self.school_logo_path = parent.school_logo_path if parent else ""
        self.bell_path_displays = {}

        self.initUI()
        self._load_settings_data()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        school_info_group = QFrame(self)
        school_info_group.setFrameShape(QFrame.StyledPanel)
        school_info_group.setContentsMargins(10, 10, 10, 10)
        school_info_layout = QGridLayout(school_info_group)
        school_info_group.setLayout(school_info_layout)
        school_info_layout.setSpacing(10)

        school_info_layout.addWidget(QLabel("Okul Adı:"), 0, 0)
        self.school_name_edit = QLineEdit()
        self.school_name_edit.setMinimumHeight(30)
        school_info_layout.addWidget(self.school_name_edit, 0, 1)

        school_info_layout.addWidget(QLabel("Okul Logosu:"), 1, 0)
        self.school_logo_display = QLineEdit()
        self.school_logo_display.setReadOnly(True)
        self.school_logo_display.setMinimumHeight(30)
        school_info_layout.addWidget(self.school_logo_display, 1, 1)
        self.school_logo_browse_btn = QPushButton("Gözat")
        self.school_logo_browse_btn.setMinimumHeight(30)
        self.school_logo_browse_btn.clicked.connect(self._browse_school_logo)
        school_info_layout.addWidget(self.school_logo_browse_btn, 1, 2)

        layout.addWidget(school_info_group)

        bell_settings_group = QFrame(self)
        bell_settings_group.setFrameShape(QFrame.StyledPanel)
        bell_settings_group.setContentsMargins(10, 10, 10, 10)
        bell_settings_layout = QGridLayout(bell_settings_group)
        bell_settings_group.setLayout(bell_settings_layout)
        bell_settings_layout.setSpacing(10)

        bell_settings_layout.addWidget(QLabel("<b>Genel Zil Sesi Ayarları:</b>"), 0, 0, 1, 4, Qt.AlignCenter)

        bell_settings_layout.addWidget(QLabel(""), 1, 0)
        bell_settings_layout.addWidget(QLabel("Seçilen Dosya Yolu"), 1, 1, Qt.AlignCenter)
        bell_settings_layout.addWidget(QLabel("Zil Seç"), 1, 2, Qt.AlignCenter)
        bell_settings_layout.addWidget(QLabel("Sına"), 1, 3, Qt.AlignCenter)

        bell_types = ["İçeri", "Öğretmenler", "Teneffüs"]
        for row_idx, bell_type in enumerate(bell_types):
            current_row = row_idx + 2

            bell_settings_layout.addWidget(QLabel(f"{bell_type} Zili:"), current_row, 0, Qt.AlignLeft | Qt.AlignVCenter)

            path_display = QLineEdit()
            path_display.setReadOnly(True)
            path_display.setMinimumHeight(30)
            self.bell_path_displays[bell_type] = path_display
            bell_settings_layout.addWidget(path_display, current_row, 1)

            select_button = QPushButton("Zil Seç")
            select_button.setMinimumHeight(30)
            select_button.clicked.connect(lambda _, bt=bell_type: self._select_bell_sound(bt))
            bell_settings_layout.addWidget(select_button, current_row, 2)

            test_button = QPushButton("Sına")
            test_button.setMinimumHeight(30)
            test_button.clicked.connect(lambda _, bt=bell_type: self._test_bell_sound(bt))
            bell_settings_layout.addWidget(test_button, current_row, 3)


        bell_settings_layout.setColumnStretch(0, 0)
        bell_settings_layout.setColumnStretch(1, 1)
        bell_settings_layout.setColumnStretch(2, 0)
        bell_settings_layout.setColumnStretch(3, 0)

        layout.addWidget(bell_settings_group)
        layout.addStretch(1)

        button_box = QHBoxLayout()
        save_button = QPushButton("Kaydet")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self._save_settings)
        cancel_button = QPushButton("İptal")
        cancel_button.setMinimumHeight(40)
        cancel_button.clicked.connect(self.reject)

        button_box.addStretch(1)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

    def _load_settings_data(self):
        self.school_name_edit.setText(self.school_name_text)
        self.school_logo_display.setText(self.school_logo_path)
        for bell_type, path_display in self.bell_path_displays.items():
            path = self.bell_sound_paths.get(bell_type, "")
            path_display.setText(path)


    def _browse_school_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Okul Logosu Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.gif);;Tüm Dosyalar (*)")
        if file_path:
            self.school_logo_display.setText(file_path)

    def _select_bell_sound(self, bell_type):
        default_dir = "/usr/share/Atam_Okul_Zili/melodiler"
        if not os.path.isdir(default_dir):
            default_dir = os.path.expanduser("~")

        file_path, _ = QFileDialog.getOpenFileName(self, f"{bell_type} Zili Sesi Seç", default_dir, "Ses Dosyaları (*.mp3 *.wav *.ogg);;Tüm Dosyalar (*)")
        if file_path:
            self.bell_sound_paths[bell_type] = file_path
            self.bell_path_displays[bell_type].setText(file_path)
            pass


    def _test_bell_sound(self, bell_type):
        sound_path = self.bell_sound_paths.get(bell_type)
        _play_sound(sound_path, self)
        if self.parent():
            self.parent()._show_bell_ringing_indicator()

    def _save_settings(self):
        parent = self.parent()
        if parent:
            parent.school_name_text = self.school_name_edit.text()
            parent.school_logo_path = self.school_logo_display.text()
            parent.bell_sound_paths = self.bell_sound_paths

            parent.school_name_label.setText(parent.school_name_text)
            parent._load_logo(parent.school_logo_label, parent.school_logo_path)

            parent._save_all_data()
            QMessageBox.information(self, "Ayarlar", "Ayarlar başarıyla kaydedildi!")
        self.accept()

# --- Ana Program Sınıfı ---
class OkulZiliProgrami(QWidget):
    # SIRENLER_BASE_PATH ve meb_logo_path sistem genelindeki yollara güncellendi
    # Bu yollar, .deb paketi kurulumunda `/usr/share/Atam_Okul_Zili/` altına yerleştirilmelidir.
    SIRENLER_BASE_PATH = "/usr/share/Atam_Okul_Zili/sirenler/" 
    MEB_LOGO_SYSTEM_PATH = "/usr/share/Atam_Okul_Zili/meb_logo.png"

    def __init__(self):
        super().__init__()
        self.bell_sound_paths = {
            "İçeri": "",
            "Öğretmenler": "",
            "Teneffüs": ""
        }
        self.school_name_text = "Ayarlardan Okul Adınızı Giriniz"
        self.school_logo_path = ""
        self.meb_logo_path = self.MEB_LOGO_SYSTEM_PATH # Sistemdeki MEB logosu yolu kullanılıyor

        # JSON dosyasının kaydedileceği uygulama veri dizini
        self.app_data_dir = self._get_app_data_directory()
        self.DATA_FILE = os.path.join(self.app_data_dir, "okul_zili_data.json")


        self.sirenler_base_path = self.SIRENLER_BASE_PATH # Yeni sistem yolu kullanılıyor
        self.ten_kasim_siren_path = os.path.join(self.SIRENLER_BASE_PATH, "10 KASIM siren ve İstiklal Marşı bileşik.mp3")

        self.lesson_times = {}
        self.day_tabs_widgets = {}

        self._initialize_data_structures()

        self.bells_rung_today = set()
        self.last_day_checked = QDate.currentDate()

        self.initUI()
        self._load_all_data()
        self.initClock()
        self._set_current_day_tab_highlight() # Sekmeyi zorla değiştirmek yerine sadece vurgula

        _player_instance.stateChanged.connect(self._handle_player_state_changed_for_debug)
        _player_instance.mediaStatusChanged.connect(self._handle_player_media_status_changed_for_debug)

        self.blinking_timer = QTimer(self)
        self.blinking_timer.timeout.connect(self._toggle_indicator_visibility)
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self._hide_bell_ringing_indicator) # Hata veren satır

    def _get_app_data_directory(self):
        """İşletim sistemine göre uygulama veri dizinini döndürür."""
        if platform.system() == "Windows":
            # %APPDATA% dizini (C:\Users\<User>\AppData\Roaming)
            app_data_path = os.path.join(os.getenv('APPDATA'), "ATAM Okul Zili")
        elif platform.system() == "Darwin": # macOS
            app_data_path = os.path.join(os.path.expanduser('~'), "Library", "Application Support", "ATAM Okul Zili")
        else: # Linux ve diğer Unix benzeri sistemler
            app_data_path = os.path.join(os.path.expanduser('~'), ".ATAM Okul Zili") # Gizli klasör önerisi
        
        # Dizinin mevcut olduğundan emin olun, yoksa oluşturun
        os.makedirs(app_data_path, exist_ok=True)
        return app_data_path

    def _initialize_data_structures(self):
        day_names_turkish = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        bell_types_internal = ["İçeri", "Öğretmenler", "Teneffüs"]

        for day in day_names_turkish:
            self.lesson_times[day] = {
                "Sabah": {},
                "Öğle": {}
            }
            self.day_tabs_widgets[day] = {
                "Sabah": {},
                "Öğle": {}
            }
            # Ders sayısını 7'den 9'a çıkarıldı (range(1, 10))
            for session in ["Sabah", "Öğle"]:
                for i in range(1, 10): # 1. Ders'ten 9. Ders'e kadar
                    lesson_key = f"{i}.Ders"
                    self.lesson_times[day][session][lesson_key] = {bt: "" for bt in bell_types_internal}
                    self.day_tabs_widgets[day][session][lesson_key] = {bt: None for bt in bell_types_internal}

    def initUI(self):
        self.setWindowTitle('ATAM Okul Zili')
        self.setWindowIcon(QIcon('/usr/share/Atam_Okul_Zili/atam.png'))
        # Pencere yüksekliği 700'den 780'e çıkarıldı
        self.setFixedSize(850, 780) 
        self.setMinimumSize(850, 780)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(5)

        top_header_grid_layout = QGridLayout()
        main_layout.addLayout(top_header_grid_layout)
        top_header_grid_layout.setContentsMargins(0, 0, 0, 0)
        top_header_grid_layout.setSpacing(5)

        self.meb_logo_label = QLabel()
        self.meb_logo_label.setFixedSize(140, 140)
        self.meb_logo_label.setAlignment(Qt.AlignCenter)
        self._load_logo(self.meb_logo_label, self.meb_logo_path)
        top_header_grid_layout.addWidget(self.meb_logo_label, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        meb_school_name_combined_layout = QVBoxLayout()
        meb_school_name_combined_layout.setSpacing(0)

        meb_text_label = QLabel("T.C.\nMilli Eğitim Bakanlığı")
        meb_text_label.setFont(QFont("Arial", 10, QFont.Bold))
        meb_text_label.setAlignment(Qt.AlignCenter)
        meb_school_name_combined_layout.addWidget(meb_text_label)

        self.school_name_label = QLabel(self.school_name_text)
        self.school_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.school_name_label.setAlignment(Qt.AlignCenter)
        meb_school_name_combined_layout.addWidget(self.school_name_label)

        top_header_grid_layout.addLayout(meb_school_name_combined_layout, 0, 1, Qt.AlignCenter)

        self.school_logo_label = QLabel()
        self.school_logo_label.setFixedSize(140, 140)
        self.school_logo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._load_logo(self.school_logo_label, self.school_logo_path)
        top_header_grid_layout.addWidget(self.school_logo_label, 0, 2, Qt.AlignRight | Qt.AlignVCenter)

        top_header_grid_layout.setColumnStretch(0, 0)
        top_header_grid_layout.setColumnStretch(1, 1)
        top_header_grid_layout.setColumnStretch(2, 0)

        time_date_layout = QHBoxLayout()
        time_date_layout.setSpacing(5)

        self.time_label = QLabel("HH:MM")
        self.time_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        time_date_layout.addWidget(self.time_label)

        time_date_layout.addStretch(1)

        # Yeni QVBoxLayout: Tarih ve Gün Adı için
        date_day_combined_layout = QVBoxLayout()
        date_day_combined_layout.setSpacing(0)

        self.date_label = QLabel("GG.AA.YYYY")
        self.date_label.setFont(QFont("Arial", 32, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        date_day_combined_layout.addWidget(self.date_label)

        self.day_name_label = QLabel("Gün Adı")
        self.day_name_label.setFont(QFont("Arial", 22, QFont.Normal))
        self.day_name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        date_day_combined_layout.addWidget(self.day_name_label)

        time_date_layout.addLayout(date_day_combined_layout)

        top_header_grid_layout.addLayout(time_date_layout, 1, 0, 1, 3)

        ataturk_full_quote = QLabel(
            "\"Öğretmenler! Yeni nesil, Cumhuriyetin fedakâr öğretmen ve eğitimcilerini, sizler yetiştireceksiniz"
            "<br>ve yeni nesil, sizin eseriniz olacaktır.\" <b>Mustafa Kemal ATATÜRK</b>"
        )
        ataturk_full_quote.setFont(QFont("Arial", 11))
        ataturk_full_quote.setAlignment(Qt.AlignCenter)
        ataturk_full_quote.setWordWrap(True)
        top_header_grid_layout.addWidget(ataturk_full_quote, 3, 0, 1, 3)

        self.bell_ringing_indicator = QLabel("ZİL ÇALINIYOR!")
        self.bell_ringing_indicator.setFont(QFont("Arial", 24, QFont.Bold))
        self.bell_ringing_indicator.setStyleSheet("color: red;")
        self.bell_ringing_indicator.setAlignment(Qt.AlignCenter)
        self.bell_ringing_indicator.hide()
        top_header_grid_layout.addWidget(self.bell_ringing_indicator, 4, 0, 1, 3, Qt.AlignCenter)

        top_header_grid_layout.setRowStretch(0, 0)
        top_header_grid_layout.setRowStretch(1, 0)
        top_header_grid_layout.setRowStretch(2, 0)
        top_header_grid_layout.setRowStretch(3, 0)
        top_header_grid_layout.setRowStretch(4, 0)

        main_layout.addStretch(1)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        day_names_turkish = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for day in day_names_turkish:
            day_widget = QWidget()
            self.tab_widget.addTab(day_widget, day)
            self._setup_day_tab(day_widget, day)
        
        # Tüm sekme çubuğunun genel fontunu ayarlayın
        self.tab_widget.tabBar().setFont(QFont("Arial", 10, QFont.Normal))


        bottom_button_layout = QHBoxLayout()
        main_layout.addLayout(bottom_button_layout)
        bottom_button_layout.setSpacing(10)

        self.special_situations_button = QPushButton("Özel Durumlar")
        self.special_situations_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.special_situations_button.clicked.connect(self.show_special_situations_window)
        bottom_button_layout.addWidget(self.special_situations_button)

        bottom_button_layout.addStretch(1)

        self.settings_button = QPushButton("Ayarlar")
        self.settings_button.clicked.connect(self.show_settings_window)
        bottom_button_layout.addWidget(self.settings_button)

        self.about_button = QPushButton("Hakkında")
        self.about_button.clicked.connect(self.show_about_window)
        bottom_button_layout.addWidget(self.about_button)


    def _load_logo(self, label, path):
        print(f"DEBUG: _load_logo çağrıldı. path: {path}")
        if not path or path.isspace():
            label.setText("LOGO YOK")
            label.setFont(QFont("SansSerif", 8))
            label.setStyleSheet("border: 1px solid gray; color: gray;")
            label.setAlignment(Qt.AlignCenter)
            print(f"DEBUG: Logo yolu boş veya geçersiz.")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            label.setText("LOGO YOK")
            label.setFont(QFont("SansSerif", 8))
            label.setStyleSheet("border: 1px solid gray; color: gray;")
            label.setAlignment(Qt.AlignCenter)
            print(f"DEBUG: Logo yüklenemedi: {path} (dosya bulunamadı veya format hatası)")
        else:
            scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.setStyleSheet("border: none;")
            label.setText("")
            print(f"DEBUG: Logo başarıyla yüklendi: {path}")

    def _setup_day_tab(self, tab_widget, day_name):
        day_layout = QHBoxLayout()
        tab_widget.setLayout(day_layout)
        day_layout.setContentsMargins(10, 10, 10, 10)
        day_layout.setSpacing(15)

        sabah_frame = QFrame()
        sabah_frame.setFrameShape(QFrame.StyledPanel)
        sabah_frame.setContentsMargins(10, 10, 10, 10)
        sabah_layout = QGridLayout(sabah_frame)
        sabah_frame.setLayout(sabah_layout)
        sabah_layout.setSpacing(1)

        sabah_layout.addWidget(QLabel("<b>Sabah</b>"), 0, 0, 1, 4, Qt.AlignCenter)

        sabah_layout.addWidget(QLabel(""), 1, 0)
        sabah_layout.addWidget(QLabel("İçeri Zili"), 1, 1, Qt.AlignCenter)
        sabah_layout.addWidget(QLabel("Öğretmenler Zili"), 1, 2, Qt.AlignCenter)
        sabah_layout.addWidget(QLabel("Teneffüs Zili"), 1, 3, Qt.AlignCenter)

        bell_types_internal = ["İçeri", "Öğretmenler", "Teneffüs"]
        # Ders sayısını 7'den 9'a çıkarıldı (range(1, 10))
        for i in range(1, 10): # 1. Ders'ten 9. Ders'e kadar
            row = i + 1
            lesson_key = f"{i}.Ders"
            lesson_label = QLabel(f"<b>{i}.Ders</b>")
            sabah_layout.addWidget(lesson_label, row, 0, Qt.AlignLeft | Qt.AlignVCenter)

            for col_idx, bell_type_internal in enumerate(bell_types_internal):
                time_entry = QLineEdit()
                time_entry.setFixedWidth(60)
                time_entry.setMinimumHeight(28)
                time_entry.setInputMask("99:99")
                time_entry.setAlignment(Qt.AlignCenter)
                time_entry.setPlaceholderText("HH:MM")
                time_entry.setToolTip("Saati silmek (DELETE) zili iptal eder.")

                time_entry.textChanged.connect(
                    lambda text, d=day_name, s="Sabah", l=lesson_key, bt=bell_type_internal:
                        self._update_lesson_time(d, s, l, bt, text)
                )

                initial_time = self.lesson_times.get(day_name, {}).get("Sabah", {}).get(lesson_key, {}).get(bell_type_internal, "")
                if initial_time:
                    time_entry.setText(initial_time)

                sabah_layout.addWidget(time_entry, row, col_idx + 1, Qt.AlignCenter)
                self.day_tabs_widgets[day_name]["Sabah"][lesson_key][bell_type_internal] = time_entry

        day_layout.addWidget(sabah_frame, 1)

        ogle_frame = QFrame()
        ogle_frame.setFrameShape(QFrame.StyledPanel)
        ogle_frame.setContentsMargins(10, 10, 10, 10)
        ogle_layout = QGridLayout(ogle_frame)
        ogle_frame.setLayout(ogle_layout)
        ogle_layout.setSpacing(1)

        ogle_layout.addWidget(QLabel("<b>Öğle</b>"), 0, 0, 1, 4, Qt.AlignCenter)

        ogle_layout.addWidget(QLabel(""), 1, 0)
        ogle_layout.addWidget(QLabel("İçeri Zili"), 1, 1, Qt.AlignCenter)
        ogle_layout.addWidget(QLabel("Öğretmenler Zili"), 1, 2, Qt.AlignCenter)
        ogle_layout.addWidget(QLabel("Teneffüs Zili"), 1, 3, Qt.AlignCenter)

        # Ders sayısını 7'den 9'a çıkarıldı (range(1, 10))
        for i in range(1, 10): # 1. Ders'ten 9. Ders'e kadar
            row = i + 1
            lesson_key = f"{i}.Ders"
            lesson_label = QLabel(f"<b>{i}.Ders</b>")
            ogle_layout.addWidget(lesson_label, row, 0, Qt.AlignLeft | Qt.AlignVCenter)

            for col_idx, bell_type_internal in enumerate(bell_types_internal):
                time_entry = QLineEdit()
                time_entry.setFixedWidth(60)
                time_entry.setMinimumHeight(28)
                time_entry.setInputMask("99:99")
                time_entry.setAlignment(Qt.AlignCenter)
                time_entry.setPlaceholderText("HH:MM")
                time_entry.setToolTip("Saati silmek (DELETE) zili iptal eder.")

                time_entry.textChanged.connect(
                    lambda text, d=day_name, s="Öğle", l=lesson_key, bt=bell_type_internal:
                        self._update_lesson_time(d, s, l, bt, text)
                )

                initial_time = self.lesson_times.get(day_name, {}).get("Öğle", {}).get(lesson_key, {}).get(bell_type_internal, "")
                if initial_time:
                    time_entry.setText(initial_time)

                ogle_layout.addWidget(time_entry, row, col_idx + 1, Qt.AlignCenter)
                self.day_tabs_widgets[day_name]["Öğle"][lesson_key][bell_type_internal] = time_entry

        day_layout.addWidget(ogle_frame, 1)

    def _update_lesson_time(self, day, session, lesson_key, bell_type, text):
        self.lesson_times[day][session][lesson_key][bell_type] = text.strip()

    def initClock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

        self.updateTime()

    def updateTime(self):
        current_datetime = QDateTime.currentDateTime()
        current_time_str = current_datetime.toString("HH:mm")
        current_date_obj = current_datetime.date()

        day_names_turkish_list = ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]
        current_day_index = current_date_obj.dayOfWeek() # QDate.dayOfWeek() Pazartesi=1, Pazar=7
        current_day_name_turkish = day_names_turkish_list[current_day_index % 7] # 7 (Pazar) -> 0, 1 (Pazartesi) -> 1 ...

        if current_date_obj != self.last_day_checked:
            self.bells_rung_today.clear()
            self.last_day_checked = current_date_obj
            print("Yeni gün, çalınan ziller sıfırlandı.")
            self._mark_past_bells_as_rung_for_day(current_day_name_turkish)

        self.time_label.setText(current_time_str)
        self.date_label.setText(current_date_obj.toString("dd.MM.yyyy"))
        self.day_name_label.setText(current_day_name_turkish)

        self._check_and_ring_bell(current_day_name_turkish, current_time_str)
        self._set_current_day_tab_highlight() # Sadece vurgulama için çağır

    def _set_current_day_tab_highlight(self):
        """Mevcut günün sekmesini vurgular ve diğerlerini varsayılan renge döner."""
        current_day_of_week_int = QDate.currentDate().dayOfWeek()
        
        # QDate.dayOfWeek() Pazartesi=1, Pazar=7 değerleri döndürürken,
        # day_names_turkish_list_for_tabs listesi Pazartesi=0, Salı=1,... Pazar=6 şeklindedir.
        # Bu nedenle doğru indeksi bulmak için dönüştürme gereklidir.
        day_names_turkish_map_for_tab_index = {
            1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe",
            5: "Cuma", 6: "Cumartesi", 7: "Pazar"
        }
        current_day_name_for_tab = day_names_turkish_map_for_tab_index.get(current_day_of_week_int)
        
        day_names_turkish_list_for_tabs = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        current_tab_index = -1
        try:
            current_tab_index = day_names_turkish_list_for_tabs.index(current_day_name_for_tab)
        except ValueError:
            print(f"UYARI: '{current_day_name_for_tab}' için sekme indeksi bulunamadı.")
            return

        for i in range(self.tab_widget.count()):
            tab_bar = self.tab_widget.tabBar()
            if i == current_tab_index:
                tab_bar.setTabTextColor(i, QColor('darkgreen'))
            else:
                tab_bar.setTabTextColor(i, QColor('black'))

    def _check_and_ring_bell(self, day, current_time_str):
        if day not in self.lesson_times:
            return

        day_schedule = self.lesson_times[day]
        bell_types_internal = ["İçeri", "Öğretmenler", "Teneffüs"]

        for session in ["Sabah", "Öğle"]:
            if session not in day_schedule:
                continue

            for lesson_key in day_schedule[session]:
                if lesson_key not in day_schedule[session]:
                    continue

                for bell_type in bell_types_internal:
                    scheduled_time = day_schedule[session][lesson_key].get(bell_type, "").strip()

                    if not scheduled_time:
                        continue

                    bell_identifier = (current_time_str, bell_type, day, session, lesson_key)

                    if current_time_str == scheduled_time and bell_identifier not in self.bells_rung_today:
                        print(f"DEBUG: Eşleşen zil bulundu: Gün={day}, Oturum={session}, Ders={lesson_key}, Zil Tipi={bell_type}, Planlanan Saat={scheduled_time}, Anlık Saat={current_time_str}")
                        sound_path = self.bell_sound_paths.get(bell_type)
                        if sound_path:
                            _play_sound(sound_path, self)
                            self._show_bell_ringing_indicator()
                            self.bells_rung_today.add(bell_identifier)
                        else:
                            print(f"UYARI: '{bell_type}' için ses yolu tanımlanmamış. Zil çalmadı: {scheduled_time}")
                            pass

    def _mark_past_bells_as_rung_for_day(self, day_name_turkish):
        current_time_obj = QTime.currentTime()

        if day_name_turkish not in self.lesson_times:
            return

        day_schedule = self.lesson_times[day_name_turkish]
        bell_types_internal = ["İçeri", "Öğretmenler", "Teneffüs"]

        for session in ["Sabah", "Öğle"]:
            if session not in day_schedule:
                continue
            for lesson_key in day_schedule[session]:
                if lesson_key not in day_schedule[session]:
                    continue
                for bell_type in bell_types_internal:
                    scheduled_time_str = day_schedule[session][lesson_key].get(bell_type, "").strip()
                    if not scheduled_time_str:
                        continue
                    
                    try:
                        scheduled_time_obj = QTime.fromString(scheduled_time_str, "HH:mm")
                        if scheduled_time_obj < current_time_obj:
                            bell_identifier = (scheduled_time_str, bell_type, day_name_turkish, session, lesson_key)
                            self.bells_rung_today.add(bell_identifier)
                            print(f"DEBUG: Geçmiş zil işaretlendi (başlangıçta/gün değişiminde çalmayacak): {bell_identifier}")
                    except Exception as e:
                        print(f"UYARI: Zaman dönüşüm hatası for {scheduled_time_str}: {e}")

    def _show_bell_ringing_indicator(self):
        print("DEBUG: _show_bell_ringing_indicator çağrıldı. Gösterge aktif ediliyor.")
        self.blinking_timer.stop()
        self.display_timer.stop()
        
        self.bell_ringing_indicator.show()
        self.bell_ringing_indicator.setVisible(True)

        self.blinking_timer.start(500)

        self.display_timer.start(12000)
    
    def _hide_bell_ringing_indicator(self):
        """Zil çalıyor göstergesini gizler ve yanıp sönmeyi durdurur."""
        print("DEBUG: _hide_bell_ringing_indicator çağrıldı. Gösterge gizleniyor.")
        self.bell_ringing_indicator.hide()
        self.blinking_timer.stop() # Yanıp sönmeyi durdur

    def _toggle_indicator_visibility(self):
        self.bell_ringing_indicator.setVisible(not self.bell_ringing_indicator.isVisible())
        print(f"DEBUG: Gösterge görünürlüğü değiştirildi: {self.bell_ringing_indicator.isVisible()}")


    def _handle_player_state_changed_for_debug(self, state):
        state_map = {
            QMediaPlayer.StoppedState: "StoppedState",
            QMediaPlayer.PlayingState: "PlayingState",
            QMediaPlayer.PausedState: "PausedState"
        }
        current_state_name = state_map.get(state, f"Unknown State ({state})")
        print(f"DEBUG: QMediaPlayer STATE CHANGED to {current_state_name}.")

    def _handle_player_media_status_changed_for_debug(self, status):
        status_map = {
            QMediaPlayer.NoMedia: "NoMedia",
            QMediaPlayer.LoadingMedia: "LoadingMedia",
            QMediaPlayer.StalledMedia: "StalledMedia",
            QMediaPlayer.BufferingMedia: "BufferingMedia",
            QMediaPlayer.BufferedMedia: "BufferingMedia",
            QMediaPlayer.EndOfMedia: "EndOfMedia",
            QMediaPlayer.InvalidMedia: "InvalidMedia",
            QMediaPlayer.LoadedMedia: "LoadedMedia",
            QMediaPlayer.UnknownMediaStatus: "UnknownMediaStatus"
        }
        current_status_name = status_map.get(status, f"Unknown Status ({status})")
        print(f"DEBUG: QMediaPlayer MEDIA STATUS CHANGED to {current_status_name}.")


    def show_special_situations_window(self):
        special_dialog = SpecialSituationsWindow(self)
        special_dialog.exec_()

    def show_settings_window(self):
        settings_dialog = SettingsWindow(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            print("Ayarlar kaydedildi ve ana pencere güncellendi.")
        else:
            print("Ayarlar iptal edildi.")

    def show_about_window(self):
        QMessageBox.information(self, "Hakkında",
            "ATAM Okul Zili\nSürüm 1.0\nLisans: GNU GPLv3 \nGeliştiren: A. Serhat KILIÇOĞLU\ngithub.com/shampuan\n\nResmi ve özel okullar için zil otomasyonu.\n"
            
        )

    def _save_all_data(self):
        data = {
            "school_name": self.school_name_text,
            "school_logo_path": self.school_logo_path,
            "bell_sound_paths": self.bell_sound_paths,
            "lesson_times": self.lesson_times,
        }
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Tüm veriler '{self.DATA_FILE}' dosyasına kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Kayıt Hatası", f"Veriler kaydedilirken bir hata oluştu: {e}")

    def _load_all_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.school_name_text = data.get("school_name", self.school_name_text)
                self.school_logo_path = data.get("school_logo_path", self.school_logo_path)
                self.bell_sound_paths = data.get("bell_sound_paths", self.bell_sound_paths)

                loaded_lesson_times = data.get("lesson_times", {})
                for day, sessions in self.lesson_times.items():
                    for session, lessons in sessions.items():
                        for lesson_key, bell_times in lessons.items():
                            for bell_type in bell_times:
                                self.lesson_times[day][session][lesson_key][bell_type] = \
                                    loaded_lesson_times.get(day, {}).get(session, {}).get(lesson_key, {}).get(bell_type, "")

                self.school_name_label.setText(self.school_name_text)
                self._load_logo(self.school_logo_label, self.school_logo_path)

                for day_name, sessions in self.day_tabs_widgets.items():
                    for session_name, lessons in sessions.items():
                        for lesson_key, bell_type_entries in lessons.items():
                            for bell_type, line_edit_obj in bell_type_entries.items():
                                if line_edit_obj:
                                    time_value = self.lesson_times.get(day_name, {}).get(session_name, {}).get(lesson_key, {}).get(bell_type, "")
                                    line_edit_obj.setText(time_value)

                current_date_obj = QDate.currentDate()
                day_names_turkish_list = ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]
                current_day_index = current_date_obj.dayOfWeek()
                current_day_name_turkish = day_names_turkish_list[current_day_index % 7]
                self._mark_past_bells_as_rung_for_day(current_day_name_turkish)

                print(f"Tüm veriler '{self.DATA_FILE}' dosyasından yüklendi.")
            except Exception as e:
                QMessageBox.critical(self, "Yükleme Hatası", f"Veriler yüklenirken bir hata oluştu: {e}")
        else:
            print(f"'{self.DATA_FILE}' dosyası bulunamadı, varsayılan veriler kullanılıyor.")

    def closeEvent(self, event):
        self._save_all_data()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OkulZiliProgrami()
    ex.show()
    sys.exit(app.exec_())
