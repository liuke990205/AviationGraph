class Word:
    word = ""
    pageno = 0

    def __init__(self):
        self.Word = ""
        self.PageNo = 0

    def setWord(self, x):
        self.Word = x

    def setPageNo(self, x):
        self.PageNo = x

    def getWord(self):
        return self.Word

    def getPageNo(self):
        return self.PageNo