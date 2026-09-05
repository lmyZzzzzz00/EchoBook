from src.ocr.ParseJSON import get_ocr_result
from src.ocr.RapidOCRConnect import RapidOCRConnect
from src.ocr.DealWithImage import deal_with_image


def run_ocr(img_path):
    img_w, img_h = deal_with_image(img_path)
    print("预处理结果已保存")
    rapid_ocr = RapidOCRConnect()
    data, text_result = get_ocr_result(rapid_ocr.ocr(img_path="res/temp/temp_saving_ocr_image.jpg"),
                                       img_w, img_h)
    print("[INFO] 处理后的文字结果", text_result)
    return data, text_result


if __name__ == '__main__':
    run_ocr("res/snap_image/chosen_img.jpg")
