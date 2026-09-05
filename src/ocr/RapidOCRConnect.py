"""
介绍：本代码用于实现与RapidOCR-json.exe的管道连接
"""

import subprocess as sp
import json
import os
import time
import chardet
from src.ocr.ParseJSON import get_ocr_result


class RapidOCRConnect:
    def __init__(self, exe_path=os.path.abspath("src/plugins/RapidOCR_json_x64/RapidOCR-json.exe"),
                 models_path=os.path.abspath("src/plugins/RapidOCR_json_x64/models"),
                 det_path="ch_PP-OCRv4_det_infer.onnx",
                 rec_path="rec_ch_PP-OCRv4_infer.onnx",
                 work_dir=os.path.abspath("src/plugins/RapidOCR_json_x64")):
        self.exe_path = exe_path
        self.models_path = models_path
        self.det_path = det_path
        self.rec_path = rec_path
        self.work_dir = work_dir

        # 定义列表、变量
        self.result_list = []

        # 创建管道进程对象
        self.process = sp.Popen("cmd", shell=True,
                                stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.PIPE,
                                cwd=self.work_dir, bufsize=0)

        # 清除一开始的输出
        for _ in range(3):
            _ = self.process.stdout.readline()
            self.encoding = chardet.detect(_)["encoding"]
        print("当前编码：", self.encoding)
        print("初始化完成！")

        # 测试RapidOCR-json是否正常
        self.process.stdin.write(f'{self.exe_path} --help & echo "<---END--->" \n'.encode(self.encoding))
        print("正在测试RapidOCR-json...")
        while True:
            line = self.process.stdout.readline().decode(self.encoding)
            if "Usage" in line:
                print("RapidOCR-json正常！")
                break

        # 清除测试输出
        while True:
            line = self.process.stdout.readline().decode(self.encoding)
            if "<---END--->" in line:
                print("测试完成！")
                break

    def ocr(self, img_path):
        time_1 = time.time()
        end_sign = f"<---END---><TIME:{str(time_1).replace('.', '')}>"
        push_str = f'{self.exe_path} --image_path="{os.path.abspath(img_path)}" --models={self.models_path} ' \
                   f'--det={self.det_path} --rec={self.rec_path} & echo "{end_sign}" \n'
        print("推送命令：", push_str)
        self.process.stdin.write(push_str.encode(self.encoding))
        print("正在识别...")
        end_count = 0
        print("[INFO] JSON数据强制使用UTF-8格式解码！")
        while True:
            line = self.process.stdout.readline().decode("utf-8").lstrip(" ")
            if end_sign in line:
                if end_count == 0:
                    end_count += 1
                else:
                    print("[INFO] 识别完成！")
                    result_json = "".join(self.result_list)
                    result = json.loads(result_json)
                    print("=====最终返回结果=====：", result)
                    time_2 = time.time()
                    print("识别时间：", time_2 - time_1, "秒")
                    return result
            else:
                if not line.rstrip("\r\n"):
                    continue
                else:
                    if line.rstrip("\r\n")[0] == "{":
                        print("[INFO] 传回JSON格式数据，此处省略。")
                        self.result_list.append(line.rstrip("\r\n"))
                    else:
                        print("[INFO] 传回非JSON格式数据：", line.rstrip("\r\n"))


if __name__ == '__main__':
    rapid_ocr = RapidOCRConnect()
    rst = rapid_ocr.ocr(img_path="a.jpg")
    print("[INFO] 处理后的结果", get_ocr_result(rst, 1366, 768)[1])
