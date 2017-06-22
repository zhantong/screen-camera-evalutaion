import re
import json


class Format:
    def format_log(self, log_file_path, output_file_path='output.json'):
        log_reg = re.compile(r'(.*?)\s\[(.*?)\]\s(.*?)\s(.*?)\s\[(.*?)\]\s\-\s(.*?)$')
        result = {}
        result['frames'] = []
        result['file'] = {}
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                res = log_reg.findall(line)
                log_type = res[0][4]
                log_content = res[0][5]
                if log_type == 'source':
                    result['file']['path'] = log_content
                elif log_type == 'barcodeConfig':
                    result['barcodeConfig'] = json.loads(log_content)
                elif log_type == 'fecParameters':
                    result['fecParameters'] = json.loads(log_content)
                elif log_type == 'processed':
                    result['frames'].append(json.loads(log_content))
                elif log_type == 'sha1':
                    result['file']['sha1'] = log_content
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result))


if __name__ == '__main__':
    format = Format()
    format.format_log('2017-06-22 20-15-02.txt', 'output.json')
