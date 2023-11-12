from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextBrowser, QScrollBar, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from bs4 import BeautifulSoup
import requests
from plyer import notification
import sys

# Bildirim göndermek için iş ilanlarının linklerini saklıyoruz
jobs = []


class StyledScrollBar(QScrollBar):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        # ScrollBar'ın css özellikleri
        self.setStyleSheet("""
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                margin: 16px 0 16px 0;
            }

            QScrollBar::handle:vertical {
                background-color: #4253ce;
                min-height: 30px;
                border-radius: 6px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background-color: #f0f0f0;
            }
        """)


class JobSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Burada uygulamamızın giriş ekranını oluşturuyoruz
        layout = QVBoxLayout()

        label = QLabel("İş ilanı uygulaması", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; color: #4253ce;")
        label.setFont(QFont("Times", 14, QFont.Bold))

        self.inputField = QLineEdit(self)
        self.inputField.setPlaceholderText("Okuduğunuz bölüm")
        self.inputField.returnPressed.connect(self.getJobs)

        submit_button = QPushButton('İş İlanlarını Bul', self)
        submit_button.clicked.connect(self.getJobs)

        layout.addWidget(label)
        layout.addWidget(self.inputField)
        layout.addWidget(submit_button)
        layout.addWidget(QWidget())

        self.jobText = QTextBrowser()
        self.jobText.setOpenExternalLinks(True)
        self.jobText.setReadOnly(True)
        self.jobText.setVerticalScrollBar(StyledScrollBar(Qt.Vertical))
        self.jobText.hide()

        layout.addWidget(self.jobText)

        self.setLayout(layout)

        # Uygulamanın css özellikleri
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: monaco,Consolas,Lucida Console,monospace;
            }

            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: #ecf0f1;
            }

            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4253ce;
                color: #ffffff;
                border: 1px solid #3498db;
                border-radius: 5px;
                width: 20px;
            }

            QPushButton:hover {
                background-color: #2980b9;
                border: 1px solid #2980b9;
            }

            QTextBrowser {
                margin-top: 20px;
                font-family: monaco,Consolas,Lucida Console,monospace;
            }
        """)

        # Ekran genişliğini ve yüksekliğini alırız
        screen = self.screen()
        screen_width, screen_height = screen.size().width(), screen.size().height()

        # Uygulamanın boyutları ayarlanır ve ortada açılır
        self.setGeometry((screen_width - self.width()) // 2,
                         (screen_height - self.height()) // 3, 800, 600)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        # Tam ekran modunu devre dışı bırak
        self.setWindowState(Qt.WindowNoState)

        self.setWindowTitle('İş İlanı Arama Uygulaması')
        self.show()

    # getJobs fonksiyonu gelen iş ilanlarını uygulamada gösterir. Ayrıca linkleri listede saklar bildirim göndermek için
    def getJobs(self):
        section = self.inputField.text()

        # Eğer giriş alanı boşsa uyarı penceresi göster
        if not section:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Uyarı")
            
            # Font ayarlarını güncelle
            font = QFont("monaco,Consolas,Lucida Console,monospace", 12)
            msgBox.setFont(font)
            
            msgBox.setText("Lütfen bir bölüm girin !")
            
            # Buton stilini güncelle
            okButton = QPushButton("Tamam")
            okButton.setStyleSheet("""
                padding: 10px;
                font-size: 14px;
                background-color: #4253ce;
                color: #ffffff;
                border: 1px solid #3498db;
                border-radius: 5px;
                width: 50px;
            """)
            
            msgBox.addButton(okButton, QMessageBox.AcceptRole)
            
            msgBox.exec_()
            return

        job_descriptions = self.get_yenibiris_jobs(
            section) + self.get_kariyer_jobs(section)

        # Eski iş ilanları listesini temizle
        jobs.clear()

        # Yeni iş ilanlarını listeye ekle
        for link in job_descriptions.split("<a style='text-decoration: none; color: #4253ce; ' href='")[1:]:
            job_link = link.split("'")[0]
            jobs.append(job_link)

        # HTML içeriğini güncelle
        self.jobText.clear()
        self.jobText.setHtml(job_descriptions.rstrip())

        style = "font-size: 25px; margin-bottom: 10px; text-decoration: none; color: blue; "
        self.jobText.document().setDefaultStyleSheet(style)
        self.jobText.show()

        # HTML içeriğini güncelle
        self.jobText.clear()
        self.jobText.setHtml(job_descriptions.rstrip())

        style = "font-size: 25px; margin-bottom: 10px; text-decoration: none; color: blue; "
        self.jobText.document().setDefaultStyleSheet(style)
        self.jobText.show()
        bildirim_gonder(jobs)

    # Yenibiris sitesinden iş ilanlarını getirir
    def get_yenibiris_jobs(self, section):
        url = f"https://www.yenibiris.com/is-ilanlari?q={section}&siralama=uygunluk"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        div = soup.find("div", class_="jobListRightPanelWrapper")
        job_descriptions = ""

        for tag in div.find_all("div", class_="listViewRows"):
            title = tag.find("a", class_="gtmTitle").text
            link = tag.find("a", class_="gtmTitle")['href']
            jobs.append(link)
            job_descriptions += f" <a style='text-decoration: none; color: #4253ce; ' href='{link}'><span style='font-size: 23px;'>{title}</span></a><br><br>"

        return job_descriptions

    # Kariyernet sitesinden iş ilanlarını getirir
    def get_kariyer_jobs(self, section):
        url = f"https://www.kariyer.net/is-ilanlari?kw={section}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        job_descriptions = ""

        for tag in soup.find_all("div", class_="list-items"):
            title = tag.find("span", class_="k-ad-card-title").text
            link = tag.find("a", class_="k-ad-card")['href']
            jobs.append(link)
            job_descriptions += f" <a style='text-decoration: none; color: #4253ce; ' href='https://www.kariyer.net{link}'><span style='font-size: 23px;'>{title}</span></a><br><br>"

        return job_descriptions

# Masaüstüne bildirim gönderir
def bildirim_gonder(liste):
    liste_uzunlugu = len(liste)
    bildirim = f"{liste_uzunlugu} iş ilanı bulundu"

    notification.notify(
        title="İş ilanı bildirimi",
        message=bildirim,
        timeout=5,
        app_icon="C:/Users/furka/Desktop/Me/Makü/Sistem analizi ve tasarımı/proje/logo.ico"
    )

# Uygulamanın ana başlangıç noktasıdır
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(
        "C:/Users/furka/Desktop/Me/Makü/Sistem analizi ve tasarımı/proje/logo.png"))
    ex = JobSearchApp()
    sys.exit(app.exec_())

# Python dosyası doğrudan çalıştırıldığında (başka bir dosya tarafından içe aktarılmadığında) çalışır
if __name__ == '__main__':
    main()
