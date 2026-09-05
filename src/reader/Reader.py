import os
import edge_tts
import subprocess
import asyncio
import hashlib
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class Reader:
    def __init__(self):
        self.client = None
        self.sub = None
        self.voices_list = []
        self.file_path = ""
        self._player = None

    def get_voices(self):
        self.sub = subprocess.Popen('"res/edge-tts/edge-tts.exe" --list-voices', shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = self.sub.communicate()
        ret_list = stdout.split('\n')
        self.voices_list = []
        for i in ret_list:
            if i.startswith("zh-CN-"):
                voice = i.split(' ')[0]
                print(voice)
                self.voices_list.append(voice)
                print(i)
        return self.voices_list

    async def _read_text_async(self, text, voice):
        if not text or not text.strip():
            print("[WARNING] 文本为空，跳过生成音频")
            return

        file_name = hashlib.md5(f"{text}_{voice}".encode('utf-8')).hexdigest()
        self.file_path = f"res/audio/audio_{file_name}.mp3"
        if os.path.exists(self.file_path):
            print(f"[INFO] 音频文件已存在，跳过生成音频: {self.file_path}")
            return
        self.client = edge_tts.Communicate(text, voice)
        print(f"[INFO] 音频文件保存名称：{file_name}")
        print(f"[INFO] 文本内容：{text[:50]}..." if len(text) > 50 else f"[INFO] 文本内容：{text}")

        try:
            await self.client.save(audio_fname=self.file_path)
            print(f"[INFO] edge-tts 保存完成")
        except Exception as e:
            print(f"[ERROR] edge-tts 保存失败: {e}")
            raise

    def generate_audio(self, text, voice):
        """生成音频文件，作为入口"""
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._read_text_async(text, voice))
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except RuntimeError:
                pass
            finally:
                loop.close()

        if not os.path.exists(self.file_path):
            print(f"[ERROR] 音频文件不存在: {self.file_path}")
            return False

        file_size = os.path.getsize(self.file_path)
        if file_size == 0:
            print(f"[ERROR] 音频文件为空: {self.file_path}")
            return False

        print(f"[INFO] 音频文件大小: {file_size} bytes")
        return True

    def play_audio(self):
        if self._player is not None:
            self._player.stop()
            self._player.deleteLater()
        self._player = QMediaPlayer()
        self._player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.file_path))))
        self._player.play()
        print("[INFO] 开始播放音频")

    def is_playing(self):
        if self._player is None:
            return False
        return self._player.state() == QMediaPlayer.PlayingState

    @staticmethod
    def clean():
        for file in os.listdir("res/audio"):
            if file.startswith("audio_"):
                os.remove(os.path.join("res/audio", file))
        print("[INFO] 已清理缓存")
