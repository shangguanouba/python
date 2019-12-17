import re


names = ["name", "_name", "__name__"]

for name in names:
    # 如果在正则表达式中需要用到普通的字符，比如 . 或者 ？等，只需要 \ 进行转义
    ret = re.match(r"[a-zA-Z_0-9]{4,20}@163\.com$", name)
    if ret:
        print("变量名%s符合要求" % ret.group())
    else:
        print("变量名%s不符合要求" % name)