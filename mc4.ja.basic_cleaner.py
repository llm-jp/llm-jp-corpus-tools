#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json,re
import sys
from tqdm import tqdm
import os

stop_pattern_files = [
    "misc/patterns_unethical.txt",
    "misc/patterns_commercial.txt",
    "misc/patterns_not_language.txt",
]
stop_patterns = []
for spf in stop_pattern_files:
    with open(os.path.join(os.path.dirname(__file__),spf)) as f:
        sp = re.compile(f.read().strip())
    stop_patterns.append(sp)
end_patterns = re.compile(r".*[！？!?。．…]$")
repetitive_patters = list(map(re.compile,[r"　",r"・",r"区"]))

def basic_cleanup(input_file,output_file,required_remain_ratio=0.5):
    with open(output_file,'w') as f:
        for line in tqdm(open(input_file).readlines()):

            data=json.loads(line)

            # TODO: 日本語以外を取り除く

            # stop words
            for sp in stop_patterns:
                if sp.search(data['text']):
                    break
            else:
                null_lines=0
                orig_sentences = data['text'].split('\n')
                sentences=[]

                # 改行文字で区切って文（文章）ごとに処理
                for ss in orig_sentences:
                    ss = ss.strip()
                    if len(ss)==0:
                        null_lines+=1

                    # 文（文章）の末尾記号制限（日本語らしい末尾記号で改行されていない場合は捨てる）
                    # 強権的な気もするがわりと効いている
                    if end_patterns.match(ss):
                        # 繰り返し制限
                        for rep in repetitive_patters:
                            if len(rep.findall(ss))>10:
                                # print(ss,len(rep.findall(ss)))
                                break
                        else:
                            sentences.append(ss)
                            print(ss)

                num_required_sentences = (len(orig_sentences)-null_lines)
                # print(len(sentences),num_required_sentences)

                # 文が消されすぎた記事は使わない
                if len(sentences)>num_required_sentences * required_remain_ratio:
                    data['text']='\n'.join(sentences)
                    f.write(json.dumps(data)+'\n')
            print()

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = input_file+".filtered.jsonl"
    basic_cleanup(input_file,output_file)

