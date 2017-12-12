# encoding:utf-8
from Preprocessing import *
import pyltp
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SentenceSplitter
import math
class EmotionAnalysis():
    """
    情感分析
    """
    segment_model_path = '/home/adien/ltp_data/cws.model'  # ltp分词模型
    pos_model_path = '/home/adien/ltp_data/pos.model'  # ltp词性标注模型
    parser_model_path = '/home/adien/ltp_data/parser.model'  # ltp依存句法解析模型
    def __init__(self,book = "西游记白话文"):
        self.emotion_dict = read_dict()
        self.book = book  # 书名
        self.chapter_num = get_files_num(path="Book/"+book)  # 章节数
        self.segmentor = Segmentor()  # 分词器
        self.segmentor.load(self.segment_model_path)
        self.postagger = Postagger()  # 词性标注器
        self.postagger.load()
        self.recognizer=NamedEntityRecognizer()
        self.recognizer.load(self.pos_model_path)
        self.parser = Parser()  # 句法分析模型
        self.parser.load(self.parser_model_path)
        self.positive_num,self.negative_num = self.count_dict_num()  # 正向词和负向词的个数

    def count_dict_num(self):
        positive_num = 0
        negative_num = 0
        for i in self.emotion_dict.values():
            if i==1:
                positive_num+=1
            else:
                negative_num+=1
        print "postive_words_num:",positive_num
        print "negative_words_num:",negative_num
        return positive_num,negative_num


    def set_books(self,book):
        self.book = book
        self.chapter_num = get_files_num(path="Book/"+book)

    def get_roles(self):
        f = codecs.open("ResultDocs/MainRole/"+self.book+"/AllChapter.txt")
        rows = f.readlines()
        roles = []
        for row in rows:
             roles.append(row.replace("\n","").replace("\r",""))
        return roles

    def get_chapterList(self):
        contents = []
        for i in range(1,self.chapter_num+1):
            f = codecs.open("Book/"+self.book+"/"+str(i)+".txt")
            rows = f.readlines()
            content = ""
            for row in rows:
                row = row.replace("\n","")
                content += row
            contents.append(content)
        return contents

    def get_role_emotionWord(self,roles,sent_words):

        role_emotionWords = {}
        for role in roles:
            role_emotionWords[role] = []
        for words in sent_words:
            postags = self.postagger.postag(words)
            arcs = self.parser.parse(words, postags)
            # print '\t'.join(word for word in words)
            # print '\t'.join('%d:%s' % (arc.head, arc.relation) for arc in arcs)
            for i in range(len(arcs)):
                if arcs[i].relation == "SBV" and words[i] in roles:
                    index = arcs[i].head-1
                    role_emotionWords[words[i]].append(words[index])
                    names = []
                    for j in range(len(arcs)):
                        if arcs[j].relation == "COO" and arcs[j].head == i+1 and words[j] in roles: #抽取主语的并列
                            role_emotionWords[words[j]].append(words[index])
                            names.append(words[j])
                    for j in range(len(arcs)):
                        if arcs[j].relation == "COO" and arcs[j].head == index+1: #抽取核心词的并列词
                            role_emotionWords[words[i]].append(words[j])
                            for name in names:
                                role_emotionWords[name].append(words[j])
                    for j in range(len(arcs)):
                        if arcs[j].relation == "ADV" and arcs[j].head == index+1:
                            role_emotionWords[words[i]].append(words[j])
                    for j in range(len(arcs)):
                        if arcs[j].relation == "ATT" and arcs[j].head == i+1:
                            role_emotionWords[words[i]].append(words[j])
            for i in range(len(arcs)):
                if arcs[i].relation == "ATT" and words[i] in roles:
                    index = arcs[i].head - 1
                    role_emotionWords[words[i]].append(words[index])
        return role_emotionWords


    def count_point(self,role_emotionWords,roles):
        '''
        计算情感得分
        :param role_emotionWords: 角色对应情绪词字典
        :param roles: 角色列表
        :return:  情绪得分
        '''
        postive = [0 for i in range(len(roles))]
        negative = [0 for i in range(len(roles))]
        num = [0 for i in range(len(roles))]
        points = [0 for i in range(len(roles))]
        for role in role_emotionWords:
            index = roles.index(role)
            num[index] = len(role_emotionWords[role])
            for word in role_emotionWords[role]:
                try:
                    point = self.emotion_dict[word]
                    if point == 1:
                        postive[index] += 1
                    else:
                        negative[index] += 1
                except:
                    pass
        for i in range(len(postive)):
            if num[i] == 0:
                continue
            postive[i] = math.log(1+float(postive[i]))/(math.log(1+num[i])*math.log(1+self.positive_num))
            postive[i] = round(postive[i],7)
            negative[i] = math.log(1+float(negative[i]))/(math.log(1+num[i])*math.log(1+self.negative_num))
            negative[i] = round(negative[i],7)
        for role in roles:
            print role,
        for i in range(len(points)):
            points[i] = postive[i]-negative[i]
        print
        print postive
        print negative
        print points
        return points

    def get_roles_emotions(self):
        '''
        获取self.book中的人物及情绪变化指标
        :return:
        '''
        contents = self.get_chapterList()
        roles = self.get_roles()
        role_points = [ [] for i in range(len(roles))]

        for content in contents:
            sents = SentenceSplitter.split(content)
            sent_words = []
            for sent in sents:
                words = list(self.segmentor.segment(sent))
                for role in roles:
                    if role in words:
                        sent_words.append(words)
                        break
            role_emotionWords = self.get_role_emotionWord(roles,sent_words)
            points = self.count_point(role_emotionWords,roles)
            for i in range(len(role_points)):
                role_points[i].append(points[i])
        for term in range(role_points.__len__()):
            index = role_points[term].__len__()-2
            while index>=1:
                if role_points[term][index] == 0 or role_points[term][index] == 0.0:
                    role_points[term][index] = (role_points[term][index-1]+role_points[term][index+1])/2
                index -= 1
        for i in range(len(role_points)):
            print roles[i], role_points[i]
        return roles, role_points

ea = EmotionAnalysis()
contents = ea.get_chapterList()
for i in range(len(contents)):
    sents = SentenceSplitter.split(contents[i])
    content = ""
    for j in sents:
        content += j+"\n"
    content = content.replace("　","")
    index = str(i+1)
    path = "Novels/"+ea.book+"/"+index+".txt"
    print path
    f = open(path, "w")
    f.write(content)
    f.close()