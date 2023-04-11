# -*- coding: utf-8 -*-
import datetime
import sys

import edge_tts

from text_to_mp3 import TextToMp3

TEXT = "你好哟，我是智能语音助手，小伊"
VOICE = "zh-CN-XiaoyiNeural"
OUTPUT_FILE = "test.mp3"


async def _main() -> None:
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    # asyncio.run(_main())
    # playsound(OUTPUT_FILE)

    txt_file = 'test.txt'
    # txt_file = 'a.md'
    text_limit = 1000
    voice_rate = "+0%"

    print(f"sys.argv:{sys.argv}")

    if len(sys.argv) >= 2:
        txt_file = sys.argv[1]
        if len(sys.argv) >= 3:
            try:
                text_limit = int(sys.argv[2])
            except:
                pass
            if len(sys.argv) >= 4:
                voice_rate = sys.argv[3]

    if txt_file is None:
        print("Usage: python readText.py filename ,default file is test.txt")
    else:
        convertor = TextToMp3()
        convertor.input_txt_file = txt_file

        now = datetime.datetime.now().strftime("%m-%d_%H%M%S")
        convertor.out_lrc_file = f'test_{now}.lrc'
        convertor.out_mp3_file = f'test_{now}.mp3'

        print(f'编码测试')

        # asyncio.run(convertor.execute())
        convertor.TEXT_LIMIT = text_limit
        convertor.rate = voice_rate
        convertor.execute_long_text()
