# -*- coding: utf-8 -*-
import pyltp
#分句，也就是将一片文本分割为独立的句子
def sentence_splitter(sentence='你好，你觉得这个例子从哪里来的？当然还是直接复制官方文档，然后改了下这里得到的。'):
    sents = pyltp.SentenceSplitter.split(sentence)  # 分句
    print '\n'.join(sents)

#测试分句子
sentence_splitter()


from pyltp import Segmentor
#分词
def segmentor(sentence='你好，你觉得这个例子从哪里来的？当然还是直接复制官方文档，然后改了下这里得到的。我的微博是MebiuW，转载请注明来自MebiuW！'):
    segmentor = Segmentor()  # 初始化实例
    segmentor.load('/home/adien/ltp_data/cws.model')  # 加载模型
    words = segmentor.segment(sentence)  # 分词
    #默认可以这样输出
    # print '\t'.join(words)
    # 可以转换成List 输出
    words_list = list(words)
    for word in words_list:
        print word
    segmentor.release()  # 释放模型
    return words_list
#测试分词
segmentor()