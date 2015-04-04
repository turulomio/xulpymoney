from PyQt5.QtCore import *
import odf
import odf.opendocument
import odf.style
import odf.text
import odf.table
import odf.draw
import odf.meta
import odf.dc
from libxulpymoney import *

class ODT(QObject):
    def __init__(self, mem, filename, template=None):    
        QObject.__init__(self)
        
        self.mem=mem
        self.filename=filename
        self.doc=odf.opendocument.OpenDocumentText()
        
        if template!=None:
            templatedoc= odf.opendocument.load(template)
            for style in templatedoc.styles.childNodes[:]:
                self.doc.styles.addElement(style)
          
            for autostyle in templatedoc.automaticstyles.childNodes[:]:
                self.doc.automaticstyles.addElement(autostyle)
                
            for master in templatedoc.masterstyles.childNodes[:]:
                self.doc.masterstyles.addElement(master)
            
        
    def emptyParagraph(self, style="Standard", number=1):
        for i in range(number):
            self.simpleParagraph("",style)
            
    def simpleParagraph(self, text, style="Standard"):
        p=odf.text.P(stylename=style, text=text)
        self.doc.text.addElement(p)
        
        
#    
#        self.metadata()
#        self.styles_page()
#        self.styles_automatic()
#        self.styles()
#    
#        
#        
#    def generate(self):
#        h=odf.text.H(outlinelevel=1, stylename="Heading 1", text=self.tr("Current assets report"))
#        self.doc.text.addElement(h)
#        
#        self.doc.text.addElement(odf.text.P(text=self.tr("Your current balance is {}.").format(self.mem.localcurrency.string(232.233))))
#        
#
#        
#        self.doc.save(self.filename)
#    def styles_page(self):  
#        pagelayout = odf.style.PageLayout(name="PageLayoutVertical")
#        self.doc.automaticstyles.addElement(pagelayout)
#        pagelayout.addElement(odf.style.PageLayoutProperties( pagewidth="21cm", pageheight="29.7cm", printorientation="portrait", margintop="2cm",  marginbottom="2cm",  marginright="2cm",  marginleft="2cm"))
#        
#        footer=odf.style.Footer()
#        t=odf.text.PageNumber(text="1", selectpage="current")
#        p=odf.text.P()
#        p.addElement(t)
#        footer.addElement(p)
#        
#        mp = odf.style.MasterPage(name="Standard", pagelayoutname=pagelayout)
#        mp.addElement(footer)
#        self.doc.masterstyles.addElement(mp)
#    
#    def styles_automatic(self):
#        # Create automatic styles for the column widths.
#        # We want two different widths, one in inches, the other one in metric.
#        # ODF Standard section 15.9.1
#        widthshort = odf.style.Style(name="Wshort", family="table-column")
#        widthshort.addElement(odf.style.TableColumnProperties(columnwidth="1.7cm"))
#        self.doc.automaticstyles.addElement(widthshort)
#        
#        widthwide = odf.style.Style(name="Wwide", family="table-column")
#        widthwide.addElement(odf.style.TableColumnProperties(columnwidth="1.5in"))
#        self.doc.automaticstyles.addElement(widthwide)
#        
#        # An automatic style
#        boldstyle = odf.style.Style(name="Bold", family="text")
#        boldprop = odf.style.TextProperties(fontweight="bold")
#        boldstyle.addElement(boldprop)
#        self.doc.automaticstyles.addElement(boldstyle)
#        
#        sPageBreak= odf.style.Style(name="PageBreak", family="paragraph")
#        sPageBreak.addElement(odf.style.ParagraphProperties(breakbefore="page"))
#        self.doc.automaticstyles.addElement(sPageBreak)
#        
#    
#
#    def styles(self):
#        h1style = odf.style.Style(name="Heading 1", family="paragraph")
#        h1style.addElement(odf.style.ParagraphProperties(margintop="1cm", marginbottom="0.7cm"))
#        h1style.addElement(odf.style.TextProperties(fontname="DejaVu Sans", attributes={'fontfamily':"DejaVu Sans",'fontsize':"16pt",'fontweight':"bold" }))
#        self.doc.styles.addElement(h1style)
#        
#        h2style = odf.style.Style(name="Heading 2", family="paragraph")
#        h2style.addElement(odf.style.ParagraphProperties(margintop="0.8cm", marginbottom="0.5cm"))
#        h2style.addElement(odf.style.TextProperties(fontname="DejaVu Sans", attributes={'fontfamily':"DejaVu Sans",'fontsize':"16pt",'fontweight':"bold" }))
#        self.doc.styles.addElement(h2style)
#        
#        standard = odf.style.Style(name="Standard", family="paragraph")
#        standard.addElement(odf.style.ParagraphProperties(margintop="0.2cm", marginbottom="0.2cm"))
#        standard.addElement(odf.style.TextProperties(fontname="DejaVu Sans", attributes={'fontfamily':"DejaVu Sans",'fontsize':"11pt"}))
#        self.doc.styles.addElement(standard)
#        
#        footer= odf.style.Style(name="Footer", family="paragraph")
#        footer.addElement(odf.style.ParagraphProperties(textalign="center", ))
#        footer.addElement(odf.style.TextProperties(fontname="DejaVu Sans", attributes={'fontfamily':"DejaVu Sans","fontstylename":"book",'fontsize':"9pt" }))
#        self.doc.styles.addElement(footer)
#        
#
#            
#    def tablacontenido(self):
#        """LO SAQUE VIENDO UN FODT CON TABLA DE CONTENIDOS"""
#        content=odf.text.TableOfContent(name="Tabla de contenido")
#        source=odf.text.TableOfContentSource()
#        t1=odf.text.TableOfContentEntryTemplate(outlinelevel=1, stylename="Heading 1")
#        t1.addElement(odf.text.IndexEntryChapter())
#        t1.addElement(odf.text.IndexEntryText())
#        t1.addElement(odf.text.IndexEntryPageNumber())
#        source.addElement(t1)
#        source.addElement(odf.text.TableOfContentEntryTemplate(outlinelevel=2, stylename="Heading 1"))
#        source.addElement(odf.text.TableOfContentEntryTemplate(outlinelevel=3, stylename="Heading 1"))
#        content.addElement(source)
#        self.doc.text.addElement(content)
#        
#    def metadata(self):
#        self.doc.meta.addElement(odf.dc.Title(text=self.tr("Assets report")))
#        self.doc.meta.addElement(odf.dc.Description(text=self.tr("This is an automatic generated report from Xulpymoney")))
#        self.doc.meta.addElement(odf.meta.InitialCreator(text="Xulpymoney-{}".format(version)))
#        self.doc.meta.addElement(odf.dc.Creator(text=u'đđðæßðđæ€ł'))
#        
    def pageBreak(self):    
        p=odf.text.P(stylename="PageBreak")#Is an automatic style
        self.doc.text.addElement(p)
#
#    def link(self):
#        para = odf.text.P()
#        anchor = odf.text.A(href="http://www.com/", text="A link label")
#        para.addElement(anchor)
#        self.doc.text.addElement(para)
#        
#    #######################################

class AssetsReport(ODT):
    def __init__(self, mem, filename, template):
        ODT.__init__(self, mem, filename, template)
        
    def generate(self):
        self.variables()
        self.metadata()
        self.cover()
        self.body()
        self.doc.save(self.filename)   
        
    def variables(self):
        self.vTotalLastYear=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date(datetime.date.today().year-1, 12, 31))
        self.vTotal=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date.today())


    def cover(self):
        self.emptyParagraph(number=10)
        self.simpleParagraph(self.tr("Assets Report"), "Title")
        self.simpleParagraph(self.tr("Generated by Xulpymoney-{}".format(version)), "Subtitle")
        self.emptyParagraph(number=8)
        self.simpleParagraph("{}".format(datetime.datetime.now()), "Quotations")        
        self.pageBreak()
        
    def body(self):
        ## About
        self.simpleParagraph(self.tr("About Xulpymoney"), "Heading 1")
        self.simpleParagraph(self.tr("About this report"), "Heading 2")
        self.pageBreak()
        ## Assets
        self.simpleParagraph(self.tr("Assets"), "Heading 1")
        self.simpleParagraph(self.tr("The total assets of the user is {}.").format(self.mem.localcurrency.string(self.vTotal)))
        if self.vTotalLastYear!=0:
            moreorless="more"
            if self.vTotal-self.vTotalLastYear<0:
                moreorless="less"
            self.simpleParagraph(self.tr("It's a {} {} of the total assets at the end of the last year.").format(tpc(100*(self.vTotal-self.vTotalLastYear)/self.vTotalLastYear), moreorless))
        self.pageBreak()
        
        ## Statistics
        self.simpleParagraph(self.tr("Statistics"), "Heading 1")
        self.pageBreak()
        
        
    def metadata(self):
        self.doc.meta.addElement(odf.dc.Title(text=self.tr("Assets report")))
        self.doc.meta.addElement(odf.dc.Description(text=self.tr("This is an automatic generated report from Xulpymoney")))
        creator="Xulpymoney-{}".format(version)
        self.doc.meta.addElement(odf.meta.InitialCreator(text=creator))
        self.doc.meta.addElement(odf.dc.Creator(text=creator))
