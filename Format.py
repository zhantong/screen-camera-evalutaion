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
    def format_log_learning(self,log_file_path,output_file_path='output.json'):
        log_reg = re.compile(r'(.*?)\s\[(.*?)\]\s(.*?)\s(.*?)\s\[(.*?)\]\s\-\s(.*?)$')
        result={}
        result['frames']=[]
        with open(log_file_path,'r',encoding='utf-8') as f:
            for line in f:
                res = log_reg.findall(line)
                log_type = res[0][4]
                log_content = res[0][5]
                if log_type == 'barcodeConfig':
                    result['barcodeConfig'] = json.loads(log_content)
                elif log_type == 'fecParameters':
                    result['fecParameters'] = json.loads(log_content)
                elif log_type == 'processed':
                    result['frames'].append(json.loads(log_content))
                elif log_type == 'sha1':
                    result['file']={}
                    result['file']['sha1'] = log_content
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result))
    def prepare_evaluate(self,input_file_path='output.json',output_file_path='prepare.json'):
        def format_frames(frames):
            result=[]
            for frame in frames:
                if 'image' in frame:
                    index=frame['image']['index']
                else:
                    index=frame['index']
                is_rs_decoded=False
                if 'rs' in frame:
                    if type(frame['rs']) is list:
                        for item in frame['rs']:
                            if 'rsDecodedContent' in item:
                                is_rs_decoded=True
                    elif type(frame['rs']) is dict:
                        if 'rsDecodedContent' in frame['rs']:
                            is_rs_decoded = True
                raptorq_index=-1
                if 'raptorQ' in frame and 'encodingPacket' in frame['raptorQ']:
                    if type(frame['raptorQ']['encodingPacket']) is list:
                        for item in frame['raptorQ']['encodingPacket']:
                            if raptorq_index==-1 or raptorq_index>item['encodingSymbolID']:
                                raptorq_index=item['encodingSymbolID']
                    elif type(frame['raptorQ']['encodingPacket']) is dict:
                        if raptorq_index == -1 or raptorq_index > frame['raptorQ']['encodingPacket']['encodingSymbolID']:
                            raptorq_index = frame['raptorQ']['encodingPacket']['encodingSymbolID']
                is_missing_source_symbols_empty=False
                if 'raptorQ' in frame and 'decoder' in frame['raptorQ']:
                    if not frame['raptorQ']['decoder']['missingSourceSymbols']:
                        is_missing_source_symbols_empty=True
                result.append({
                    'index':index,
                    'isRSDecoded':is_rs_decoded,
                    'raptorQIndex':raptorq_index,
                    'isMissingSourceSymbolsEmpty':is_missing_source_symbols_empty
                })
            return result
        def find_first_index(frames):
            first_index=-1
            for frame in frames:
                if frame['raptorQIndex']==0:
                    first_index=frame['index']
                elif first_index!=-1:
                    break
            if first_index==-1:
                for frame in frames:
                    if frame['raptorQIndex']>0:
                        first_index=frame['index']
                        break
            return first_index
        def find_last_index(frames):
            last_index=-1
            raptorq_index=-1
            for frame in frames:
                if frame['isMissingSourceSymbolsEmpty']:
                    last_index=frame['index']
                    raptorq_index=frame['raptorQIndex']
                    break
            return last_index,raptorq_index
        def count_error_frames(frames,first_index,last_index):
            count=0
            for frame in frames:
                if frame['index']>=first_index and frame['index']<=last_index and not frame['isRSDecoded']:
                    count+=1
            return count
        with open(input_file_path,'r',encoding='utf-8') as f:
            data=json.loads(f.read())
        frames_formatted=format_frames(data['frames'])
        first_index=find_first_index(frames_formatted)
        last_index,last_raptorq_index=find_last_index(frames_formatted)
        num_error_frames=count_error_frames(frames_formatted,first_index,last_index)
        fps=data['barcodeConfig']['fps']
        distance=data['barcodeConfig']['distance']
        num_bytes=data['fecParameters']['numDataBytes']
        min_source_symbols=data['fecParameters']['numSourceSymbols']
        with open(output_file_path,'w',encoding='utf-8') as f:
            f.write(json.dumps({
                'firstIndex':first_index,
                'lastIndex':last_index,
                'numErrorFrames':num_error_frames,
                'fps':fps,
                'distance':distance,
                'numBytes':num_bytes,
                'minSourceSymbols':min_source_symbols
            }))

if __name__ == '__main__':
    format = Format()
    #format.format_log('/Volumes/扩展存储/实验/BlackWhiteCodeWithBar/100x100_0.1/视频/28fps_50cm_4x/2017-06-28 13:39:09.txt')
    format.format_log_learning('/Volumes/扩展存储/实验/BlackWhiteCodeML/60x60_0.1/视频/22fps_50cm_3x/1683/learning.txt')
    format.prepare_evaluate()
