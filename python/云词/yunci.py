import matplotlib.pyplot as plt
import pickle
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
text1 =['网络攻城狮','Linux','防火墙','交换机','深信服上网行为管理','网络加速','Juniper','WiFi','思科','H3C','×××','ACL','华为','DELL','机房巡检','网络专线','机房检查','大数据','虚拟机','防病毒','上网行为管理','光纤','无线项目','视频会议','信息安全','局域网','广域网','IP电话','爬山',]
text=' '.join(text1)
backgroud_Image = plt.imread('2.jpg')
wc = WordCloud( background_color = 'white',    # 设置背景颜色
                mask = backgroud_Image,        # 设置背景图片
                max_words = 200,            # 设置最大现实的字数
                stopwords = STOPWORDS,        # 设置停用词
                font_path = 'C:\Windows\Fonts\simhei.ttf',# 设置字体格式，如不设置显示不了中文
                max_font_size = 180,            # 设置字体最大值
                #min_font_size =10,
    random_state = 15,            # 设置有多少种随机生成状态，即有多少种配色方案
                )
wc.generate(text)
p_w_picpath_colors = ImageColorGenerator(backgroud_Image)
wc.recolor(color_func = p_w_picpath_colors)
plt.imshow(wc)
plt.axis('off')
plt.show()