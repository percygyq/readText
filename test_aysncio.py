#!/user/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format=" %(asctime)s [*] %(threadName)s %(message)s"
)


def call_back01(x):
    time.sleep(3)
    logging.info(f"Get:{x}")


async def call_back02(x):
    await asyncio.sleep(3)
    logging.info(f"Get:{x}")


if __name__ == "__main__":
    now = time.time()
    loop = asyncio.get_event_loop()

    # 1.协程和线程池-----------------------------------------------------
    # ex = ThreadPoolExecutor(max_workers=10)
    # tasks = list()
    # for i in range(20):
    #     tasks.append(loop.run_in_executor(ex, call_back01, i))

    # 2.单单协程---------------------------------------------------------
    tasks = [asyncio.ensure_future(call_back02(i)) for i in range(20)]
    loop.run_until_complete(asyncio.wait(tasks))
    print("总用时", time.time() - now)
