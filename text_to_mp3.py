# coding=utf-8
import asyncio
import datetime
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

import docx2txt
import edge_tts

import vtt_to_lrc


class TextToMp3:
    """
    convert txt to mp3
    """
    text: str = ''
    """
    name of txt 
    """
    file_name: str
    """
    directory of txt
    """
    directory: str

    input_txt_file: str
    out_mp3_file: str
    out_lrc_file: str
    rate: str = "+0%"
    voice: str = "zh-CN-XiaoxiaoNeural"

    temp_folder = 'd:/data/edge_tts/tmp'

    tag = 'txt'
    thread_count = 2
    subs_map = {}

    TEXT_LIMIT = 1000

    def __init__(self) -> None:
        super().__init__()
        self._taskThreadPool = None
        self.sem = asyncio.Semaphore(self.thread_count)

    @property
    def executor(self) -> ThreadPoolExecutor:
        if self._taskThreadPool is None:
            self._taskThreadPool = ThreadPoolExecutor(max_workers=self.thread_count, thread_name_prefix=self.tag)
        return self._taskThreadPool

    def init_text(self):
        """
        init text
        """
        # 创建临时文件夹
        mkdir(self.temp_folder)

        split = os.path.split(self.input_txt_file)
        spl = split[1]

        splitext = os.path.splitext(spl)
        self.file_name = splitext[0]
        # 扩展名
        extension = splitext[1]
        if not (extension == '.txt' or extension or '.md' or extension == '.doc' or extension == '.docx'):
            raise Exception('只支持:txt,markdown,doc,docx!')

        abspath = os.path.abspath(self.input_txt_file)
        self.directory = os.path.split(abspath)[0]

        mp3_file = f'{self.file_name}.mp3'
        i = 0
        while os.path.exists(mp3_file):
            i += 1
            mp3_file = f'{self.file_name}_{i}.mp3'

        self.out_mp3_file = mp3_file
        if i == 0:
            self.out_lrc_file = f'{self.file_name}.lrc'
        else:
            self.out_lrc_file = f'{self.file_name}_{i}.lrc'

        print(f'input file [{self.input_txt_file}] is in dir :{self.directory}')

        if extension == '.doc' or extension == '.docx':
            self.text = get_doc_text(self.input_txt_file)
        else:
            with open(self.input_txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for s in lines:
                    self.text += s
            if extension == '.md':
                # replace markdown syntax with plain text
                txt_text = re.sub(r"\n#*\s*(.*)\n", r"\n\1\n" + "=" * 50 + "\n", self.text)
                txt_text = re.sub(r"\n##*\s*(.*)\n", r"\n\1\n" + "-" * 50 + "\n", txt_text)
                txt_text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", txt_text)
                txt_text = re.sub(r"~~(.*?)~~", r"\1", txt_text)
                txt_text = re.sub(r"`(.*?)`", r"\1", txt_text)
                txt_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", txt_text)
                self.text = txt_text
                # print(f'text:-->{self.text}')

    async def execute(self):
        """
        execute
        """
        self.init_text()

        if len(self.text) > self.TEXT_LIMIT:
            raise Exception(f'文本内容不可超过{self.TEXT_LIMIT}字!')

        communicate = edge_tts.Communicate(self.text, self.voice, rate=self.rate)
        sub_maker = edge_tts.SubMaker()
        with open(self.out_mp3_file, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

        subs = sub_maker.generate_subs()

        now = datetime.datetime.now().strftime("%m-%d_%H%M%S")

        out_vtt_file = f'{self.file_name}_{now}.vtt'
        with open(out_vtt_file, "w", encoding="utf-8") as file:
            file.write(subs)

        vtt_to_lrc.convert_vtt_to_lyc(subs, self.out_lrc_file)

    async def handle_part_txt(self, index, now, text) -> str:
        # return f'{index}'
        """
        execute
        """
        async with self.sem:
            print(f'handle text:index:{index},text:{text}')
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            sub_maker = edge_tts.SubMaker()

            out_mp3_file = f'{self.temp_folder}/{self.file_name}-{now}-{index}.mp3'

            with open(out_mp3_file, "wb") as file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        sub_maker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

            subs = sub_maker.generate_subs()
            self.subs_map[index] = subs

    def execute_long_text(self):
        begin_time = time.time()
        self.init_text()
        txt_list = split_text(self.text, self.TEXT_LIMIT)

        loop = asyncio.get_event_loop()

        now = datetime.datetime.now().strftime("%m-%d_%H%M%S")

        tasks = list()
        index = 0
        for text in txt_list:
            # await self.handle_txt(index, now, text)
            t = asyncio.ensure_future(self.handle_part_txt(index, now, text))
            tasks.append(t)
            index += 1

        print(f'all task {index} -> {len(tasks)}')
        loop.run_until_complete(asyncio.wait(tasks))

        print("总用时:", time.time() - begin_time)

        while len(self.subs_map) < index:
            print(f'---> waiting .... -> edge-tts is working:{len(self.subs_map)}/{index}')
            time.sleep(1.0)

        out_mp3_file_list = []

        vtt_list = list()
        for i in range(0, index):
            subs = self.subs_map[i]
            vtt_list.append(subs)
            # tmp_mp3_file = f'{self.temp_folder}/{self.file_name}-{now}-{i}.mp3'
            # out_mp3_file_list.append(tmp_mp3_file)
            out_mp3_file_list.append(f'{self.file_name}-{now}-{i}.mp3')

            tmp_lrc_file = f'{self.temp_folder}/{self.file_name}-{now}-{i}.vtt'
            # with open(tmp_lrc_file, "w", encoding="utf-8") as f:
            #     f.write(subs)

        if len(out_mp3_file_list) > 1:
            join = '|'.join(out_mp3_file_list)
            cmd = f'cd {self.temp_folder} && ffmpeg -i "concat:{join}" -c:a copy {self.directory}\\{self.out_mp3_file}'
            print(f'cmd:{cmd}')
            # c = os.system(cmd)
            r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(" 合并失败输出:out: " + r.stdout.read().decode('utf-8'))
            print(" 合并失败输出:err " + r.stderr.read().decode('utf-8'))
        else:
            cmd = f"cd {self.temp_folder} && copy {out_mp3_file_list[0]} {self.directory}\\{self.out_mp3_file}"
            print(f'cmd:{cmd}')
            r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pass

        vtt_to_lrc.convert_vtts_to_lyc(vtt_list, f'{self.directory}\\{self.out_lrc_file}')


def split_text(text: str, size: int) -> list[str]:
    part: int = int(len(text) / size) + 1
    txt_list: list[str] = list()
    start = 0
    for i in range(0, part):
        end = (i + 1) * size
        if end > len(text):
            # print(f'{start}')
            txt_list.append(text[start:])
        else:
            # print(f'{start}-{end}')
            txt_list.append(text[start:end])
        start = end
    return txt_list


def get_doc_text(file_path):
    print(f'get content of docx:{file_path}')
    # 提取 Word 文档内容
    text = docx2txt.process(file_path)
    # 删除所有表格内容
    text = re.sub(r'\+-*\+-*\+', '', text)
    text = re.sub(r'\|\s*\|\s*\|', '', text)
    return text


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print(f"create new folder:{path}")


if __name__ == '__main__':
    s = '上弦月和下弦月就是说阴历的前半个月'
    s = '12345678'
    text_arr = split_text(s, 3)
    for s in text_arr:
        print(s)
    mkdir(r'd:/data/edge_tts/tmp')
