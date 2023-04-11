#!/user/bin/env python3
# -*- coding: utf-8 -*-
import datetime


def convert_vtt_to_lyc(vtt: str, out_vtt_file):
    """
    vtt : vtt文件的内容
    :param vtt:
    :param out_vtt_file:
    :return:
    """
    split = vtt.split('\r\n')
    if len(split) == 1:
        pass
        split = vtt.split('\n')

    start = False

    is_time = True
    is_new_line = True

    lines = list()

    line = ''
    for s in split:
        if s == '':
            continue
        if s == 'WEBVTT':
            start = True
            continue
        if start:
            is_new_line = len(line) == 0 or len(line) > 35
            if len(line) > 35:
                lines.append(line)
                line = ''

            is_time = s.__contains__(' --> ')

            if is_new_line:
                if is_time:
                    i = s.index(' --> ')
                    s = s[0:i]
                    line = f'[{s}]'
                else:
                    line += s
            else:
                if is_time:
                    pass
                else:
                    line += ' ' + s

    lines.append(line)

    lyc_content = '\n'.join(lines)
    print(lyc_content)
    with open(out_vtt_file, "w", encoding="utf-8") as file:
        file.writelines(lyc_content)
        print(f'lyc 文件生成成功:{out_vtt_file}')


def convert_vtts_to_lyc(vtt_list: list[str], out_vtt_file):
    """
    :param vtt_list:
    :param out_vtt_file:
    :return:
    """

    lines = list()

    last_end_time = None

    for vtt in vtt_list:
        pass
        split = vtt.split('\r\n')
        if len(split) == 1:
            pass
            split = vtt.split('\n')

        start = False

        is_time = True
        is_new_line = True

        line = ''
        time_start = None
        time_end = None
        for s in split:
            if s == '':
                continue
            if s == 'WEBVTT':
                start = True
                continue
            if start:
                is_new_line = len(line) == 0 or len(line) > 35
                if len(line) > 35:
                    lines.append(line)
                    line = ''

                is_time = s.__contains__(' --> ')

                if is_time:
                    i = s.index(' --> ')
                    j = s[0:i]
                    k = s[i+5:]
                    if last_end_time is not None:
                        time_start = time_add(last_end_time, time_delta(j))
                        time_end = time_add(last_end_time, time_delta(k))
                    else:
                        time_start = j
                        time_end = k

                if is_new_line:
                    if is_time:
                        line = f'[{time_start}]'
                    else:
                        line += s
                else:
                    if is_time:
                        pass
                    else:
                        line += (' ' + s)

        lines.append(line)
        last_end_time = time_end
        print(f'last_end_time--->{last_end_time}')

    lyc_content = '\n'.join(lines)
    print(f'content of lyc:\n{lyc_content}')
    with open(out_vtt_file, "w", encoding="utf-8") as file:
        file.writelines(lyc_content)
        print(f'lyc 文件生成成功:{out_vtt_file}')


def time_delta(time_max, time_min='00:00:00.000'):
    """ time_2-time_1
    时间间隔
    :param time_min: time_str
    :param time_max: time_str
    :return:
    """
    pass
    t_1 = datetime.datetime.strptime(time_min, '%H:%M:%S.%f')
    t_2 = datetime.datetime.strptime(time_max, '%H:%M:%S.%f')
    return t_2 - t_1


def time_add(time_1, delta):
    """
    时间相加
    :param time_1: time_str
    :param delta: time_delta
    :return: time_str
    """
    t_1 = datetime.datetime.strptime(time_1, '%H:%M:%S.%f')
    t_2 = t_1 + delta
    return t_2.strftime("%H:%M:%S.%f")[:-3]


def test():
    name = r'D:\data\edge_tss\tmp\test-04-10_143430-0.vtt'
    vtts = []

    for i in range(0, 2):
        name = f'D:\\data\\edge_tss\\tmp\\test-04-10_143430-{i}.vtt'
        with open(name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            subs = ''.join(lines)
            vtts.append(subs)
            # convert_vtt_to_lyc(subs, f'out.lrc')

    convert_vtts_to_lyc(vtts, 'out2.lrc')
    pass


if __name__ == '__main__':
    pass
    test()
    # d = time_delta('00:00:00.000', '00:02:00.100')
    # s = time_add('00:03:00.100', d)
    # print(s)
