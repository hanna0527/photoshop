import sys
import numpy as np
import cv2
from os import remove
import matplotlib.pyplot as plt
from PIL import Image
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        #메뉴바 만들기
        self.menu = self.menuBar()
#--------------------------------------------------------------------------
        self.menu_file = self.menu.addMenu("파일") #상단
        save = QAction("저장" ,self)
        self.menu_file.addAction(save)
        save.setShortcut("ctrl+s")
        save.triggered.connect(self.save)

        exitAction = QAction('나가기', self)
        exitAction.setShortcut("esc")
        self.menu_file.addAction(exitAction)
        exitAction.triggered.connect(qApp.quit)
#--------------------------------------------------------------------------
        self.menu_file = self.menu.addMenu("회전") 
        spin30 = QAction("30°" ,self)
        self.menu_file.addAction(spin30)
        spin30.triggered.connect(self.rotatePixmap30)

        spin45 = QAction("45°" ,self)
        self.menu_file.addAction(spin45)
        spin45.triggered.connect(self.rotatePixmap45)

        spin90 = QAction("90°" ,self)
        self.menu_file.addAction(spin90)
        spin90.triggered.connect(self.rotatePixmap90)

        spin180 = QAction("180°" ,self)
        self.menu_file.addAction(spin180)
        spin180.triggered.connect(self.rotatePixmap180)

        spinCst = QAction("사용자 정의" ,self)
        self.menu_file.addAction(spinCst)
        spinCst.triggered.connect(self.rotateCustom)
#--------------------------------------------------------------------------
        self.menu_file = self.menu.addMenu("효과") 
        lens = QAction("렌즈 왜곡" ,self)
        self.menu_file.addAction(lens)
        lens.triggered.connect(self.lensDstr)
       
        bw = QAction("흑백" ,self)
        self.menu_file.addAction(bw)
        bw.triggered.connect(self.blackWhite)

        inv = QAction("색반전" ,self)
        self.menu_file.addAction(inv)
        inv.triggered.connect(self.invImg)
#--------------------------------------------------------------------------
        self.menu_file = self.menu.addMenu("마스크") 
        maskedCir = QAction("원" ,self)
        self.menu_file.addAction(maskedCir)
        maskedCir.triggered.connect(self.maskImgCir)

        maskedRect = QAction("사각형" ,self)
        self.menu_file.addAction(maskedRect)
        maskedRect.triggered.connect(self.maskImgRect)

        maskedTri = QAction("삼각형" ,self)
        self.menu_file.addAction(maskedTri)
        maskedTri.triggered.connect(self.maskImgTri)
#--------------------------------------------------------------------------
        self.menu_file = self.menu.addMenu("편집") 
        zoomIn = QAction("확대" ,self)
        self.menu_file.addAction(zoomIn)
        zoomIn.triggered.connect(self.onZoomIn)

        zoomOut = QAction("축소" ,self)
        self.menu_file.addAction(zoomOut)
        zoomOut.triggered.connect(self.onZoomOut)

        mirror = QAction("좌우반전" ,self)
        self.menu_file.addAction(mirror)
        mirror.triggered.connect(self.flipImage)
#--------------------------------------------------------------------------
        #메인화면 레이아웃
        main_layout = QHBoxLayout()


        #사이드바 메뉴버튼 
        sidebar1 = QVBoxLayout()
        button1 = QPushButton("이미지 열기")
        button2 = QPushButton("새로고침")
        button3 = QPushButton("적용")
        button4 = QPushButton("처음 상태로")
        button5 = QPushButton("저장")

        button1.clicked.connect(self.show_flie_dialog)
        button2.clicked.connect(self.clear_label)
        button3.clicked.connect(self.image_use)
        button4.clicked.connect(self.backtoOri)
        button5.clicked.connect(self.save)

        sidebar1.addWidget(button1)
        sidebar1.addWidget(button2)
        sidebar1.addWidget(button3)
        sidebar1.addWidget(button4)
        sidebar1.addWidget(button5)

        main_layout.addLayout(sidebar1)
        
#--------------------------------------------------------------------------------
        sidebar2 = QVBoxLayout() #커스텀 솔로 사이드바(렌즈)
        self.slider = QSlider(Qt.Horizontal, self)
        sidebar2.addWidget(self.slider)
        min = 1.0 
        max = 19.0
        self.default_L = min+max//2 #렌즈 왜곡 디폴트값
        self.slider.setRange(min, max)
        self.slider.setValue(self.default_L)
        self.slider.setSingleStep(1)
        self.slider.valueChanged[int].connect(self.soloSlider)
        
        self.sliderDft = QPushButton('Default', self)
        sidebar2.addWidget(self.sliderDft)
        self.sliderDft.clicked.connect(self.clicked_event_default)

        self.sliderFin = QPushButton('닫기', self)
        sidebar2.addWidget(self.sliderFin)
        self.sliderFin.clicked.connect(self.clicked_event_finish)
        
        self.slider_hide()

        main_layout.addLayout(sidebar2)

#--------------------------------------------------------------------------------
        #커스텀 솔로 다이얼(회전) 
        sidebar3 = QVBoxLayout()
        self.dial = QDial(self)

        sidebar3.addWidget(self.dial)
        min = 0
        max = 360
        self.default_d = 0
        self.dial.setRange(min, max)
        self.dial.setValue(min)
        self.dial.setSingleStep(1)
        self.dial.valueChanged[int].connect(self.soloDial)
        
        self.dialDft = QPushButton('Default', self)
        sidebar3.addWidget(self.dialDft)
        self.dialDft.clicked.connect(self.clicked_event_default)

        self.dialFin = QPushButton('닫기', self)
        sidebar3.addWidget(self.dialFin)
        self.dialFin.clicked.connect(self.clicked_event_finish)

        self.dial_hide()
        
        main_layout.addLayout(sidebar3)

#--------------------------------------------------------------------------------
        self.label1 = QLabel(self) #원본 사진 레이블
        self.label1.setFixedSize(640, 480)
        main_layout.addWidget(self.label1)
        self.label1.setAlignment(Qt.AlignCenter)
#--------------------------------------------------------------------------------
        #화살표
        self.labelArrow = QLabel("center",self)
        self.labelArrow.setFixedSize(100, 100)
        main_layout.addWidget(self.labelArrow)
        self.labelArrow.setPixmap(QPixmap(r"arrow.png"))
        self.labelArrow.move(50, 200)
        self.labelArrow.setAlignment(Qt.AlignCenter)
#--------------------------------------------------------------------------------
        self.label2 = QLabel(self) #포토샵 사진
        self.label2.setFixedSize(640, 480)
        main_layout.addWidget(self.label2)
        self.label2.setAlignment(Qt.AlignCenter)
    
        widget = QWidget(self)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
 #--------------------------------------------------------------------------------
    def show_flie_dialog(self): #이미지 열기
        self.allHide()
        file_name = QFileDialog.getOpenFileName(self, "이미지 열기", "./")
        self.image = cv2.imread(file_name[0]) #파일 경로 0
        h, w, _ = self.image.shape
        bytes_per_line = 3 * w
        image = QImage(
            self.image.data, w, h, bytes_per_line,
             QImage.Format_RGB888
        ).rgbSwapped()
        self.QImg1 = image
        self.orginal = self.QImg1
        pixmap = QPixmap(image)
        self.label1.setPixmap(pixmap)

    def backtoOri(self): #원본으로 돌아가기
        self.QImg1 = self.orginal
        pixmap = QPixmap(self.QImg1)
        self.label1.setPixmap(pixmap)

    def flipImage(self): #좌우반전
        self.allHide()
        pixmap = QPixmap(self.QImg1)
        image = pixmap.transformed(QTransform().scale(-1, 1))
        self.Qpixmap2 = image
        self.label2.setPixmap(image)
     
    def onZoomIn(self): #확대
        self.allHide()
        self.scale *= 2
        self.resize_image()

    def onZoomOut(self): #축소
        self.allHide()
        self.scale /= 2
        self.resize_image()

    def resize_image(self):
        pixmap = QPixmap(self.QImg1)
        size = pixmap.size()
        scaled_pixmap = pixmap.scaled(self.scale * size)
        self.Qpixmap2 = scaled_pixmap
        self.label2.setPixmap(scaled_pixmap)


    def clear_label(self): #새로고침
        self.allHide()
        self.label2.clear()


    def save(self): #저장
        self.allHide()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                            "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
                return
        self.QImg1.save(filePath)

    def image_use(self): #적용
        self.allHide()
        self.QImg1 = self.Qpixmap2
        self.label1.setPixmap(self.QImg1)
        self.label2.clear()

    def initUI(self): #UI
        self.scale = 1 #zoom
        self.rotation = 0 #spin
        self.mod = 0 #사이드 바
      
        self.setWindowTitle("Simple Photoshop")
        self.setWindowIcon(QIcon('phicon.png'))
        self.setGeometry(300, 300, 300, 200)
#--------------------------------------------------------------------------
    def rotatePixmap30(self): #회전30
        self.allHide()
        img = QPixmap(self.QImg1)
        pixmap = img.copy()
        self.rotation += 30
        transform = QTransform().rotate(self.rotation)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def rotatePixmap45(self): #회전45
        self.allHide()
        img = QPixmap(self.QImg1)
        pixmap = img.copy()
        self.rotation += 45
        transform = QTransform().rotate(self.rotation)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def rotatePixmap90(self): #회전90
        self.allHide()
        img = QPixmap(self.QImg1)
        pixmap = img.copy()
        self.rotation += 90
        transform = QTransform().rotate(self.rotation)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def rotatePixmap180(self): #회전180
        self.allHide()
        img = QPixmap(self.QImg1)
        pixmap = img.copy()
        self.rotation += 180
        transform = QTransform().rotate(self.rotation)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def rotateCustom(self, value): #사용자 정의 회전
        self.mod = "회전"
        self.slider_hide()
        self.dial_show()
        pixmap = QPixmap(self.QImg1)
        self.rotation = value
        transform = QTransform().rotate(self.rotation)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)
#--------------------------------------------------------------------------
    def lensDstr(self, value): #렌즈 왜곡
        self.mod = "렌즈왜곡" 
        self.dial_hide()
        self.slider_show()
        
        image = self.Qimg2cv(self.QImg1)
        height, width = image.shape[:2]
        bytes_per_line = 3* width
        
        exp = value  # 볼록지수 1.1~, 오목지수 0.1~1.0
        if (exp == False):
            exp = self.default_L//10
        scale = 1
        mapy, mapx = np.indices((height, width), dtype=np.float32)
        mapx = 2 * mapx / (width-1) - 1
        mapy = 2 * mapy / (height-1) - 1
        r, theta = cv2.cartToPolar(mapx, mapy)  # 직교좌표를 극좌표로 변환시키는
        r[r < scale] = r[r < scale] ** exp
        mapx, mapy = cv2.polarToCart(r, theta)  # 극좌표를 직교좌표로 변환시켜주는 함수
        mapx = ((mapx +  1) * width - 1) / 2
        mapy = ((mapy +  1) * height - 1) / 2
        distorted = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)
        image = QImage(
            distorted.data, width, height, bytes_per_line,
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(image)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def blackWhite(self): #흑백
        self.allHide()
        image = self.Qimg2cv(self.QImg1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
        dst = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB) 
        img = QImage(
            dst.data, image.shape[1], image.shape[0], 3* image.shape[1],
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(img)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def invImg(self): #색반전
        self.allHide()
        src = self.Qimg2cv(self.QImg1)
        inv = cv2.bitwise_not(src)
        image = QImage(
            inv.data, src.shape[1], src.shape[0], 3*src.shape[1],
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(image)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def Qimg2cv(self, img): #Qimage to cv2
        img.save('temp2020101035.png', 'png')
        mat = cv2.imread('temp2020101035.png')
        remove('temp2020101035.png')
        return mat
#--------------------------------------------------------------------------
    def maskImgCir(self): #원마스크
        self.allHide()
        img = self.Qimg2cv(self.QImg1)
        h, w = img.shape[:2]
        mask = np.zeros_like(img)
        cv2.circle(mask, (h//2, h//2), h//3, (255, 255, 255), -1)
        masked = cv2.bitwise_and(img, mask)
        image = QImage(
            masked.data, img.shape[1], img.shape[0], 3*img.shape[1],
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(image)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def maskImgRect(self): #사각형마스크
        self.allHide()
        img = self.Qimg2cv(self.QImg1)
        h, w = img.shape[:2]
        mask = np.zeros_like(img)
        cv2.rectangle(mask, (w//4, h//4), (3*h//4, 3*w//4), (255, 255, 255), -1)
        masked = cv2.bitwise_and(img, mask)
        image = QImage(
            masked.data, img.shape[1], img.shape[0], 3*img.shape[1],
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(image)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)

    def maskImgTri(self): #삼각형마스크
        self.allHide()
        img = self.Qimg2cv(self.QImg1) 
        h, w = img.shape[:2]
        mask = np.zeros_like(img)
        pts = [np.array([[w//4, 3*h//4],[3*w//4, 3*h//4],[2*w//4, h//4]])]
        cv2.polylines(mask, pts , isClosed =True, color = (255, 255, 255))
        cv2.fillPoly(mask, pts, color = (255, 255, 255))

        masked = cv2.bitwise_and(img, mask)
        image = QImage(
            masked.data, img.shape[1], img.shape[0], 3*img.shape[1],
            QImage.Format_RGB888
        ).rgbSwapped()
        pixmap = QPixmap(image)
        self.Qpixmap2 = pixmap
        self.label2.setPixmap(pixmap)
#--------------------------------------------------------------------------
    def soloSlider(self, value):
        if(self.mod == "렌즈왜곡"): #렌즈 왜곡일 시
            self.lensDstr(value/10)

    def slider_hide(self):
        self.slider.hide()
        self.sliderDft.hide()
        self.sliderFin.hide()
    
    def slider_show(self):
        self.slider.show()
        self.sliderDft.show()
        self.sliderFin.show()
#----------------------------------------------------------------------------
    def clicked_event_default(self):
        if(self.mod == "렌즈왜곡"): self.slider.setValue(self.default_L)
        elif(self.mod == "회전"): self.dial.setValue(self.default_d)

    def clicked_event_finish(self):
        if(self.mod == "렌즈왜곡"):
            self.label2.clear()
            self.slider_hide()
            self.mod = 0
        if(self.mod == "회전"):
            self.label2.clear()
            self.dial_hide()
            self.mod = 0

    def allHide(self):
        self.slider_hide()
        self.dial_hide()
        
#----------------------------------------------------------------------------
    def soloDial(self, value):
        if(self.mod == "회전"): #회전일 시
            self.rotateCustom(value)

    def dial_hide(self):
        self.dial.hide()
        self.dialDft.hide()
        self.dialFin.hide()
    
    def dial_show(self):
        self.dial.show()
        self.dialDft.show()
        self.dialFin.show()

#----------------------------------------------------------------------------
if __name__ == "__main__":
    app= QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())