import json
from datetime import datetime

from reportlab.pdfgen import canvas

from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
doc = SimpleDocTemplate("form_letter.pdf",pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)


class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = LETTER
    
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_canvas(self, page_count):
        page = "%s" % (self._pageNumber)
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.1)
        # self.drawImage("static/lr.png", self.width-inch*8-5, self.height-50, width=100, height=20, preserveAspectRatio=True)
        # self.drawImage("static/ohka.png", self.width - inch * 2, self.height-50, width=100, height=30, preserveAspectRatio=True, mask='auto')
        # self.line(30, 760, LETTER[0] - 50, 760)
        self.line(66, 78, LETTER[0] - 66, 78)
        self.setFont('Times-Roman', 10)
        self.drawString(LETTER[0]-x, 65, page)
        self.restoreState()


class PDFGenerator:

    def __init__(self, path, data):
        self.path = path
        self.data = data

        self.styleSheet = getSampleStyleSheet()
        self.elements = []
        self.font_name = 'Times New Roman'
        self.blueColor = Color((13.0/255), (71.0/255), (161.0/255), 1)
        self.redColor = Color(red=1)
        self.greenColor = Color(green=1)

        
        self.addUserInfo()
        self.build()
        self.doc = SimpleDocTemplate(path, pagesize=LETTER)
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    def addUserInfo(self):
        timeString = datetime.now().strftime("%D")
        timeStyle = ParagraphStyle(self.font_name, fontSize = 10, alignment = TA_RIGHT, justifyLastLine = 1)
        timeSection = Paragraph(timeString, timeStyle)
        self.elements.append(timeSection)

        userInfo = self.data['userInfo']
        name, email = userInfo['name'], userInfo['email']
        info = f"{name}<br />{email}"
        infoStyle = ParagraphStyle(self.font_name, fontSize = 10, alignment = TA_LEFT, justifyLastLine = 1)
        infoSection = Paragraph(info, infoStyle)
        self.elements.append(infoSection)
        self.elements.append(Spacer(0, 10))


    def build(self):
        for key, val in self.data['sections'].items():
            titleStyle = ParagraphStyle(self.font_name, fontSize = 16, alignment = TA_LEFT, justifyLastLine = 1)
            title = f"<font color={self.blueColor}><b>{key}</b></font><br />"
            titleSection = Paragraph(title, titleStyle)
            self.elements.append(titleSection)

            self.elements.append(Spacer(0, 10))

            scoreValue = val['score'] or 0
            scoreColor = 'red' if scoreValue < 50 else 'green'
            score = f"Score - <font color={scoreColor} size=13>{scoreValue}%</font><br />"
            scoreStyle = ParagraphStyle(self.font_name, fontSize = 13, alignment = TA_LEFT, justifyLastLine = 1)
            scoreSection = Paragraph(score, scoreStyle)
            self.elements.append(scoreSection)

            self.elements.append(Spacer(0, 20))

            for q, obj in val['questions'].items():
                text = f"{q}. {obj['title']} <br /> Your Answer: {obj['answer']} <br /> Suggestion: {obj['suggestion']}"
                textStyle = ParagraphStyle(self.font_name, fontSize = 12, alignment = TA_LEFT, justifyLastLine = 1)
                textStyle.leading = 16
                textSection = Paragraph(text, textStyle)
                self.elements.append(textSection)


def changeResponseToPdfFormat(userResponse):
    questionInfo = open('question_info.json')
    questions = json.load(questionInfo)
    
    questionInfo.close()
    
    output = {}

    response = userResponse['response']
    userInfo = {
        'name': userResponse['email'],
        'email': userResponse['name']
    }
    output['userInfo'] = userInfo
    output['sections'] = {}

    for sectionTitle in questions:
        section = questions[sectionTitle]
        
        output['sections'][sectionTitle] = {}
        output['sections'][sectionTitle]['questions'] = {}

        totalCorrectResponse = 0
        totalQuestions = 0

        for q in section:
            totalQuestions += 1
            question = section[q]

            if response[q] == question['correctAnswer']:
                totalCorrectResponse += 1
            else:
                output['sections'][sectionTitle][q] = {
                    'answer': response[q],
                    'title': question['question'],
                    'suggestion': question['suggestion']['details']
                }
        score = int((totalCorrectResponse / totalCorrectResponse) * 100)
        output['sections'][sectionTitle]['score'] = score
    
    return output



if __name__ == '__main__':
    userResponse = {
    "response": {
        "1": "yes",
        "2": "NO"
    },
    "email": "tst@tste.com",
    "name":"test"
}
    output = changeResponseToPdfFormat(userResponse)
    report = PDFGenerator('sample.pdf', output)


