from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QRect
from PyQt5.QtGui import QGuiApplication, QPixmap, QPainter, QPen
import sys
import os


class GenerateBookWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Echo Book --- 生成电子书文件")
        self.resize(800, 600)

        # 图片相关
        self.bg_ori_pixmap = QPixmap()   # 原始图片
        self.bg_scaled_pixmap = QPixmap()  # 缩放后的背景图（用于绘制）
        self.img_path = ""  # 图片路径

        # 鼠标拖拽矩形
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_dragging = False

        # 窗口背景色（备用）
        self.setStyleSheet("background-color: rgb(240, 240, 240);")

        # 启用鼠标追踪（可选，便于调试）
        self.setMouseTracking(True)

    def load_img(self, book_name: str, img_path: str):
        """加载图片并创建书籍目录"""
        if not os.path.exists(img_path):
            print(f"[ERROR] 图片文件不存在：{img_path}")
            return

        self.img_path = img_path
        book_path = os.path.join("data", "books", book_name)
        if not os.path.exists(book_path):
            os.makedirs(book_path)
        else:
            for root, dirs, files in os.walk(book_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        print("[INFO] 生成文件夹准备就绪！")

        # 加载原始图片
        self.bg_ori_pixmap.load(img_path)
        self.update_background()  # 缩放并更新

    def update_background(self):
        """根据当前窗口大小缩放背景图（无矩形）"""
        if self.bg_ori_pixmap.isNull():
            return

        dpi_ratio = self.devicePixelRatioF()
        # 缩放到窗口物理尺寸
        scaled = self.bg_ori_pixmap.scaled(
            int(self.width() * dpi_ratio),
            int(self.height() * dpi_ratio),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        scaled.setDevicePixelRatio(dpi_ratio)
        self.bg_scaled_pixmap = scaled
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """绘制背景图和矩形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        # 1. 绘制背景图（居中）
        if not self.bg_scaled_pixmap.isNull():
            dpi_ratio = self.devicePixelRatioF()
            # 计算逻辑尺寸（因为 scaled 设置了 devicePixelRatio）
            logical_w = self.bg_scaled_pixmap.width() / dpi_ratio
            logical_h = self.bg_scaled_pixmap.height() / dpi_ratio
            x = int((self.width() - logical_w) / 2)
            y = int((self.height() - logical_h) / 2)
            # 绘制（QPixmap 自带 DPI 信息，绘制时自动缩放）
            painter.drawPixmap(x, y, self.bg_scaled_pixmap)
        else:
            # 无图片时填充背景色（已通过样式表设置）
            pass

        # 2. 绘制矩形（如果正在拖拽）
        if self.is_dragging and not self.start_pos.isNull() and not self.end_pos.isNull():
            dpi_ratio = self.devicePixelRatioF()
            pen = QPen(Qt.red, 1 * dpi_ratio)
            painter.setPen(pen)
            # 确保矩形从左上到右下
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)

    def resizeEvent(self, event):
        """窗口大小改变时重新缩放背景"""
        self.update_background()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            self.is_dragging = True
            self.update()  # 清除矩形（因为 is_dragging 变为 False，重绘时不再绘制）

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return
        delta = event.pos() - self.start_pos
        if delta.manhattanLength() < 5:  # 防误触
            return
        self.end_pos = event.pos()
        self.update()  # 触发重绘

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            # 打印最终矩形（窗口坐标）
            rect = QRect(self.start_pos, self.end_pos).normalized()
            print(f"[INFO] 矩形区域：{rect.topLeft()} -> {rect.bottomRight()}")


if __name__ == "__main__":
    # 高DPI支持
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass

    app = QApplication(sys.argv)
    window = GenerateBookWindow()
    window.show()
    window.load_img("TestBook", "a.jpeg")
    sys.exit(app.exec_())