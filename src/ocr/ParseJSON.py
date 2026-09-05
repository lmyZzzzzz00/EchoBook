import json


def get_ocr_result(json_result, img_w, img_h):
    """
    解析并返回JSON返回值中的data(以列表形式返回)和文字(以一整个字符串形式返回)
    """
    data = json_result["data"]
    text_list = []
    data_ret_dict = {}
    for i in data:
        box = i["box"]
        text = i["text"]
        text_list.append(text)
        # 核心修复：将坐标限制在图像有效范围内
        cleaned_box = []
        for point in box:
            x = max(0, min(point[0], img_w - 1))
            y = max(0, min(point[1], img_h - 1))
            cleaned_box.append([x, y])
        # 注意此时box列表中的坐标顺序为[左上角xy，右上角xy，右下角xy，左下角xy]
        x1 = cleaned_box[0][0]
        x2 = cleaned_box[1][0]
        y1 = cleaned_box[0][1]
        y2 = cleaned_box[2][1]
        data_ret_dict[text] = [x1, y1, x2, y2]
    text_ret = "".join(text_list)
    with open("data/text_data.json", "w") as f:
        json.dump(data_ret_dict, f)
    return data, text_ret
