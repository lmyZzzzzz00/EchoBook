import cv2
import os
from src.ocr.ParseJSON import get_ocr_result


def deal_with_image(img_path):
    img = cv2.imread(os.path.abspath(img_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_w = img.shape[1]
    img_h = img.shape[0]
    if img_w > 500 and img_h > 500:
        img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    if not os.path.exists("res/temp"): os.makedirs("res/temp")
    cv2.imwrite(os.path.abspath("res/temp/temp_saving_ocr_image.jpg"), img)
    return img_w, img_h


if __name__ == '__main__':
    image_path = "a.jpg"
    deal_with_image(image_path)
    print("预处理结果已保存")

    from src.ocr.RapidOCRConnect import RapidOCRConnect
    rapid_ocr = RapidOCRConnect()
    rst = rapid_ocr.ocr(img_path="res/temp/temp_saving_ocr_image.jpg")
    print("[INFO] 处理后的结果", get_ocr_result(rst, 1366, 768)[1])
