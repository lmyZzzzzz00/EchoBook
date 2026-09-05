from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QRect
from PyQt5.QtGui import QGuiApplication, QPixmap, QPainter, QPen
from src.ocr.Run import run_ocr as get_ocr
from src.generate_book.SettingsWidget import SettingsWidget
import sys
import os
import hashlib


def get_md5(text: str) -> str:
    """获取字符串的MD5值"""
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


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

        self.settings_widget = SettingsWidget(self)
        self.settings_widget.hide()

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
            if self.settings_widget.isVisible():
                self.settings_widget.hide()
                return
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
            self.deal_with_img(rect)

    def deal_with_img(self, rect: QRect):
        print("[INFO] 返回的矩形（窗口坐标）:", rect)
        dpi = self.devicePixelRatioF()

        # 1. 计算居中偏移（逻辑像素）
        # bg_scaled_pixmap 的物理尺寸为 (width, height)，逻辑尺寸 = 物理尺寸 / dpi
        logical_w = self.bg_scaled_pixmap.width() / dpi
        logical_h = self.bg_scaled_pixmap.height() / dpi
        offset_x = (self.width() - logical_w) / 2
        offset_y = (self.height() - logical_h) / 2

        # 2. 窗口坐标 -> 缩放图上的逻辑坐标（减去偏移）
        crop_x = rect.x() - offset_x
        crop_y = rect.y() - offset_y
        crop_w = rect.width()
        crop_h = rect.height()

        # 3. 限制在缩放图范围内
        crop_x = max(0, min(crop_x, logical_w))
        crop_y = max(0, min(crop_y, logical_h))
        crop_w = min(crop_w, logical_w - crop_x)
        crop_h = min(crop_h, logical_h - crop_y)

        # 4. 缩放图逻辑坐标 -> 缩放图物理坐标（乘以 dpi）
        physical_x = int(crop_x * dpi)
        physical_y = int(crop_y * dpi)
        physical_w = int(crop_w * dpi)
        physical_h = int(crop_h * dpi)

        # 5. 缩放图物理坐标 -> 原始图片物理坐标（乘以缩放比例）
        # 比例因子 = 原始图片宽 / 缩放图宽（都是物理像素）
        scale_x = self.bg_ori_pixmap.width() / self.bg_scaled_pixmap.width()
        scale_y = self.bg_ori_pixmap.height() / self.bg_scaled_pixmap.height()
        # 由于保持宽高比，scale_x 和 scale_y 应该相等，但为了严谨仍分别计算
        final_rect = QRect(
            int(physical_x * scale_x),
            int(physical_y * scale_y),
            int(physical_w * scale_x),
            int(physical_h * scale_y)
        )

        print("[INFO] 裁剪区域（原始图片物理坐标）:", final_rect)
        cropped_img = self.bg_ori_pixmap.copy(final_rect)
        if not cropped_img.isNull():
            save_dir = "res/snap_image"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            cropped_img.save(os.path.join(save_dir, "chosen_image.jpg"))
            print("[INFO] 裁剪完成！保存至", save_dir)
            try:
                data, result_text = self.run_ocr()
                print("[INFO] OCR识别结果：", result_text)
                self.show_settings(result_text)
            except BaseException:
                QMessageBox.critical(None, "OCR识别失败", "[ERROR] OCR识别失败，请检查图片内容。") # type: ignore[arg]
        else:
            QMessageBox.critical(None, "裁剪失败", "[ERROR] 裁剪区域无效，请检查矩形是否在图片范围内。") # type: ignore[arg]

    @staticmethod
    def run_ocr():
        img_path = "res/snap_image/chosen_image.jpg"
        data, result_text = get_ocr(img_path)
        return data, result_text

    def show_settings(self, result_text: str):
        if not result_text: return
        self.settings_widget.ui.text_info_lb.setText(result_text)
        self.settings_widget.ui.textEdit.setPlainText(result_text)
        self.settings_widget.ui.md5_info_lb.setText(get_md5(result_text))
        self.settings_widget.move((self.width()-self.settings_widget.width())//2, (self.height()-self.settings_widget.height())//2)
        self.settings_widget.show()


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