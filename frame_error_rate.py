import re
import json


def frame_error_rate(log_file_path, output_file_path='result.json'):
    log_reg = re.compile(r'(.*?)\s\[(.*?)\]\s(.*?)\s(.*?)\s\[(.*?)\]\s\-\s(.*?)$')
    total = 0
    count = 0
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            res = log_reg.findall(line)
            log_type = res[0][4]
            log_content = res[0][5]
            if log_type == 'processed':
                total += 1
                data = json.loads(log_content)
                if 'raptorQ' in data and 'encodingPacket' in data['raptorQ']:
                    count += 1
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            'total': total,
            'count': count,
            'frame_error_rate': count / total
        }))


if __name__ == '__main__':
    frame_error_rate(
        '/Volumes/扩展存储/MegaLight附加实验/拍摄到视频/小米mix2/100/VID_20180913_160548/Screen-Camera/2018-10-23-23-31-00.log')
