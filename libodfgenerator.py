## @package libodfgenerator
## @brief Package that allows to read and write Libreoffice ods and odt files
## This file is from the Xulpymoney project. If you want to change it. Ask for project administrator

import datetime
import logging
import os
import sys
from odf.opendocument import OpenDocumentSpreadsheet,  OpenDocumentText,  load,  __version__
from odf.style import Footer, FooterStyle, GraphicProperties, HeaderFooterProperties, Style, TextProperties, TableColumnProperties, Map,  TableProperties,  TableCellProperties, PageLayout, PageLayoutProperties, ParagraphProperties,  ListLevelProperties,  MasterPage
from odf.number import  CurrencyStyle, CurrencySymbol,  Number, NumberStyle, Text,  PercentageStyle,  DateStyle, Year, Month, Day, Hours, Minutes, Seconds
from odf.text import P,  H,  Span, ListStyle,  ListLevelStyleBullet,  List,  ListItem, ListLevelStyleNumber,  OutlineLevelStyle,  OutlineStyle,  PageNumber,  PageCount
from odf.table import Table, TableColumn, TableRow, TableCell,  TableHeaderRows
from odf.draw import Frame, Image
from odf.dc import Creator, Description, Title, Date
from odf.meta import InitialCreator
from odf.config import ConfigItem, ConfigItemMapEntry, ConfigItemMapIndexed, ConfigItemMapNamed,  ConfigItemSet
from odf.office import Annotation

from decimal import Decimal

class ODF:
    def __init__(self, filename):
        self.filename=filename
        self.images={}
        
    def setMetadata(self, title,  description, creator):
        self.doc.meta.addElement(Title(text=title))
        self.doc.meta.addElement(Description(text=description))
        self.doc.meta.addElement(InitialCreator(text=creator))
        self.doc.meta.addElement(Creator(text=creator))
        
        
    def addImage(self, path):
        self.images[path]=self.doc.addPicture(path)
        
    def setLanguage(self, language, country):
        """Set the main language of the document"""
        self.language="es"
        self.country="ES"
        
class ODT(ODF):
    def __init__(self, filename, template=None, language="es", country="ES"):
        def styleGraphics():
#            >
#    <style:style style:family="graphic" style:name="Graphics">
#      <style:graphic-properties style:wrap="none" style:vertical-pos="top" style:horizontal-rel="paragraph" style:horizontal-pos="center" svg:x="0cm" style:vertical-rel="paragraph" svg:y="0cm" text:anchor-type="paragraph"/>
#    </style:style>
            ga=Style(family="graphic", name="GraphicsParagraph")
            ga.addElement(GraphicProperties(verticalpos="top", horizontalpos="center", horizontalrel="paragraph",  verticalrel="paragraph", anchortype="paragraph"))
            self.doc.styles.addElement(ga)

#    <style:style style:family="graphic" style:parent-style-name="Graphics" style:name="fr1">
#      <style:graphic-properties draw:contrast="0%" fo:clip="rect(0cm 0cm 0cm 0cm)" draw:color-mode="standard" style:mirror="none" draw:gamma="100%" style:horizontal-rel="paragraph" draw:red="0%" draw:luminance="0%" draw:color-inversion="false" style:horizontal-pos="left" draw:blue="0%" draw:image-opacity="100%" draw:green="0%"/>
#    </style:style>
            framea=Style(family="graphic", parentstylename="GraphicsParagraph", name="FrameParagraph")
            self.doc.automaticstyles.addElement(framea)
            
        def stylePage():
    #       <style:page-layout style:name="Mpm1">
    #      <style:page-layout-properties fo:page-width="21.001cm" style:print-orientation="portrait" fo:margin-top="2cm"
    #fo:margin-right="2cm" style:writing-mode="lr-tb" style:footnote-max-height="0cm" style:num-format="1" fo:page-height="29.7cm" fo:margin-left="2cm" fo:margin-bottom="2cm">
    #        <style:footnote-sep style:color="#000000" style:width="0.018cm" style:line-style="solid" style:adjustment="left" style:rel-width="25%" style:distance-after-sep="0.101cm" style:distance-before-sep="0.101cm"/>
    #      </style:page-layout-properties>
    #      <style:header-style/>
    #      <style:footer-style>
    #        <style:header-footer-properties fo:min-height="0cm" fo:margin-top="0.499cm"/>
    #      </style:footer-style>
    #    </style:page-layout>

            pagelayout=PageLayout(name="PageLayout")
            plp=PageLayoutProperties(pagewidth="21cm",  pageheight="29.7cm",  margintop="2cm",  marginright="2cm",  marginleft="2cm",  marginbottom="2cm")
            fs=FooterStyle()
            hfp=HeaderFooterProperties(margintop="0.5cm")
            fs.addElement(hfp)
            pagelayout.addElement(plp)
            pagelayout.addElement(fs)
            self.doc.automaticstyles.addElement(pagelayout)
                    
        def styleParagraphs():
            #Pagebreak styles horizontal y vertical        
            s = Style(name="PH", family="paragraph",  parentstylename="Standard", masterpagename="Landscape")
            s.addElement(ParagraphProperties(pagenumber="auto"))
            self.doc.styles.addElement(s)
            s = Style(name="PV", family="paragraph",  parentstylename="Standard", masterpagename="Standard")
            s.addElement(ParagraphProperties(pagenumber="auto"))
            self.doc.styles.addElement(s)
            
            standard= Style(name="Standard", family="paragraph",  autoupdate="true")
            standard.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"justify", "marginbottom":"0.2cm", "textindent":"1cm"}))
            standard.addElement(TextProperties(attributes={"fontsize": "12pt", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(standard)   
               
            ImageCenter= Style(name="ImageCenter", family="paragraph",  autoupdate="true")
            ImageCenter.addElement(ParagraphProperties(attributes={"margintop":"3cm", "textalign":"center", "marginbottom":"4cm"}))
            ImageCenter.addElement(TextProperties(attributes={"fontsize": "12pt", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(ImageCenter)
            
            standardCenter= Style(name="standardCenter", family="paragraph",  autoupdate="true")
            standardCenter.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"center", "marginbottom":"0.2cm", "textindent":"0cm"}))
            standardCenter.addElement(TextProperties(attributes={"fontsize": "12pt", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(standardCenter)
            
            letra18= Style(name="Bold18Center", family="paragraph",  autoupdate="true")
            letra18.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"center", "marginbottom":"0.2cm", "textindent":"0cm"}))
            letra18.addElement(TextProperties(attributes={"fontsize": "18pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(letra18)
            
            letra16= Style(name="Bold16Center", family="paragraph",  autoupdate="true")
            letra16.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"center", "marginbottom":"0.2cm", "textindent":"0cm"}))
            letra16.addElement(TextProperties(attributes={"fontsize": "16pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(letra16)
            
            letra12= Style(name="Bold12Center", family="paragraph",  autoupdate="true")
            letra12.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"center", "marginbottom":"0.2cm", "textindent":"0cm"}))
            letra12.addElement(TextProperties(attributes={"fontsize": "12pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(letra12)

        def styleHeaders():
    #        #Header1
    #        #    <style:style style:auto-update="true" style:display-name="Heading 1" style:default-outline-level="1" style:family="paragraph" style:name="Heading_20_1" style:next-style-name="Text_20_body" style:parent-style-name="Heading" style:class="text">
    #      <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-right="0cm" fo:text-align="justify" fo:text-indent="0cm" ns42:contextual-spacing="false" style:writing-mode="page" fo:margin-left="0cm" fo:margin-bottom="0.212cm" style:auto-text-indent="false" style:justify-single-word="false"/>
    #      <style:text-properties style:font-weight-complex="bold" fo:font-size="15pt" style:font-size-asian="130%" style:font-size-complex="130%" fo:font-weight="bold" style:font-weight-asian="bold"/>
    #    </style:style>
            titlestyle = Style(name="Title", family="paragraph",  autoupdate="true", defaultoutlinelevel="0")
            titlestyle.addElement(ParagraphProperties(attributes={"margintop":"0.6cm", "textalign":"center", "marginbottom":"0.9cm"}))
            titlestyle.addElement(TextProperties(attributes={"fontsize": "16pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(titlestyle)
            h1style = Style(name="Heading1", family="paragraph",  autoupdate="true", defaultoutlinelevel="1")
            h1style.addElement(ParagraphProperties(attributes={"margintop":"0.6cm", "textalign":"justify", "marginbottom":"0.3cm"}))
            h1style.addElement(TextProperties(attributes={"fontsize": "15pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(h1style)
            h2style = Style(name="Heading2", family="paragraph",  autoupdate="true", defaultoutlinelevel="2")
            h2style.addElement(ParagraphProperties(attributes={"margintop":"0.5cm", "textalign":"justify", "marginbottom":"0.25cm"}))
            h2style.addElement(TextProperties(attributes={"fontsize": "14pt", "fontweight": "bold", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(h2style)
            out=OutlineStyle(name="Outline")
            outl=OutlineLevelStyle(level=1, numformat="1", numsuffix="  ")
            out.addElement(outl)
            outl=OutlineLevelStyle(level=2, displaylevels="2", numformat="1", numsuffix="  ")
            out.addElement(outl)
            self.doc.styles.addElement(out)
            #Standard
            #            <style:style style:auto-update="true" style:name="Standard" style:family="paragraph" style:master-page-name="" style:class="text">
            #      <style:paragraph-properties fo:margin-top="0.199cm" fo:margin-right="0cm" fo:text-align="justify" ns42:contextual-spacing="false" fo:text-indent="1cm" style:page-number="auto" style:writing-mode="page" fo:margin-left="0cm" fo:margin-bottom="0.199cm" style:auto-text-indent="false" style:justify-single-word="false"/>
            #      <style:text-properties style:font-size-asian="10.5pt"/>
            #    </style:style>
            

        def styleList():
            liststandard= Style(name="ListStandard", family="paragraph",  autoupdate="true")
            liststandard.addElement(ParagraphProperties(attributes={"margintop":"0.1cm", "textalign":"justify", "marginbottom":"0.1cm", "textindent":"0cm"}))
            liststandard.addElement(TextProperties(attributes={"fontsize": "12pt", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(liststandard)
            
            # For Bulleted list
            bulletedliststyle = ListStyle(name="BulletList")
            bulletlistproperty = ListLevelStyleBullet(level="1", bulletchar=u"•")
            bulletlistproperty.addElement(ListLevelProperties( minlabelwidth="1cm"))
            bulletedliststyle.addElement(bulletlistproperty)
            self.doc.styles.addElement(bulletedliststyle)

            # For numbered list
            numberedliststyle = ListStyle(name="NumberedList")
            numberedlistproperty = ListLevelStyleNumber(level="1", numsuffix=".", startvalue=1)
            numberedlistproperty.addElement(ListLevelProperties(minlabelwidth="1cm"))
            numberedliststyle.addElement(numberedlistproperty)
            self.doc.styles.addElement(numberedliststyle)
        
        def styleFooter():
            #Footer
    #            <style:style style:master-page-name="" style:class="extra" style:auto-update="true" style:parent-style-name="Standard" style:name="Footer" style:family="paragraph">
    #      <style:paragraph-properties fo:text-align="center" fo:text-indent="0cm" style:auto-text-indent="false" fo:margin-left="0cm" style:writing-mode="page" style:justify-single-word="false" text:number-lines="false" text:line-number="0" fo:margin-right="0cm" style:page-number="auto">
    #        <style:tab-stops>
    #          <style:tab-stop style:position="8.5cm" style:type="center"/>
    #          <style:tab-stop style:position="17cm" style:type="right"/>
    #        </style:tab-stops>
    #      </style:paragraph-properties>
    #      <style:text-properties fo:font-size="8pt"/>
    #    </style:style>
            s= Style(name="Footer", family="paragraph",  autoupdate="true")
            s.addElement(ParagraphProperties(attributes={"margintop":"0cm", "textalign":"center", "marginbottom":"0cm", "textindent":"0cm"}))
            s.addElement(TextProperties(attributes={"fontsize": "9pt", "country": self.country, "language": self.language}))
            self.doc.styles.addElement(s)


    #    <style:master-page style:name="Standard" style:page-layout-name="Mpm1">
    #      <style:footer>
    #        <text:p text:style-name="MP1">Página <text:page-number text:select-page="current">1</text:page-number> de <text:page-count>1</text:page-count></text:p>
    #      </style:footer>
    #    </style:master-page>
            #Footer
        def styleMasterPage():
            foot=MasterPage(name="Standard", pagelayoutname="PageLayout")
            footer=Footer()
            p1=P(stylename="Footer",  text="Página ")
            number=PageNumber(selectpage="current", numformat="1")
            p2=Span(stylename="Footer",  text=" de  ")
            count=PageCount(selectpage="current", numformat="1")
            p1.addElement(number)
            p1.addElement(p2)
            p1.addElement(count)      
            footer.addElement(p1)   
            foot.addElement(footer)
            self.doc.masterstyles.addElement(foot)

        #######################################
        ODF.__init__(self, filename)
        self.setLanguage(language, country)
        self.doc=OpenDocumentText()
        
        self.seqTables=0#Sequence of tables
        self.seqFrames=0#If a frame is repeated it doesn't show its
        if template!=None:
            templatedoc= load(template)
            for style in templatedoc.styles.childNodes[:]:
                self.doc.styles.addElement(style)
          
            for autostyle in templatedoc.automaticstyles.childNodes[:]:
                self.doc.automaticstyles.addElement(autostyle)
                
            for master in templatedoc.masterstyles.childNodes[:]:
                self.doc.masterstyles.addElement(master)
                

        stylePage()
        styleParagraphs()
        styleFooter()
        styleMasterPage()
        styleHeaders()
        styleList()
        styleGraphics()

    def emptyParagraph(self, style="Standard", number=1):
        for i in range(number):
            self.simpleParagraph("",style)
                
    def save(self):
        makedirs(os.path.dirname(self.filename))
        self.doc.save(self.filename)

    def simpleParagraph(self, text, style="Standard"):
        p=P(stylename=style, text=text)
        self.doc.text.addElement(p)
        
    def list(self, arr, style="BulletList"):
        l=List(stylename=style)
        for item in arr:
            it=ListItem()
            p=P(stylename="ListStandard", text=item)
            it.addElement(p)
            l.addElement(it)
        self.doc.text.addElement(l)
                
    def numberedList(self, arr, style="NumberedList"):
        l=List(stylename=style)
        for item in arr:
            it=ListItem()
            p=P(stylename="ListStandard", text=item)
            it.addElement(p)
            l.addElement(it)
        self.doc.text.addElement(l)

    def title(self, text):
        p=P(stylename="Title", text=text)
        self.doc.text.addElement(p)

    def header(self, text, level):
        h=H(outlinelevel=level, stylename="Heading{}".format(level), text=text)
        self.doc.text.addElement(h)

    def table(self, header, orientation,  data, sizes, font):
        """Headerl text
        Data: data
        sizes: arr with column widths in cm
        size=font size"""  
    
        self.seqTables=self.seqTables+1
        tablesize=sum(sizes)
        
        s=Style(name="Tabla{}".format(self.seqTables))
        s.addElement(TableProperties(width="{}cm".format(tablesize), align="center"))
        self.doc.automaticstyles.addElement(s)
        
        #Column sizes
        for i, size in enumerate(sizes):
            sc= Style(name="Tabla{}.{}".format(self.seqTables, chr(65+i)), family="table-column")
            sc.addElement(TableColumnProperties(columnwidth="{}cm".format(sizes[i])))
            self.doc.automaticstyles.addElement(sc)
        
        #Cell header style
        sch=Style(name="Tabla{}.HeaderCell".format(self.seqTables, chr(65), 1), family="table-cell")
        sch.addElement(TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)        
        
        #Cell normal
        sch=Style(name="Tabla{}.Cell".format(self.seqTables), family="table-cell")
        sch.addElement(TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)
        
        
        #TAble contents style
        s= Style(name="Tabla{}.Heading{}".format(self.seqTables, font), family="paragraph",parentstylename='Table Heading' )
        s.addElement(TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(ParagraphProperties(attributes={'textalign':'center', }))
        self.doc.styles.addElement(s)
        
        s = Style(name="Tabla{}.TableContents{}".format(self.seqTables, font), family="paragraph")
        s.addElement(TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        self.doc.styles.addElement(s)
        
        s = Style(name="Tabla{}.TableContentsRight{}".format(self.seqTables, font), family="paragraph")
        s.addElement(TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(ParagraphProperties(attributes={'textalign':'end', }))
        self.doc.styles.addElement(s)
        
        #Table header style
        s = Style(name="Tabla{}.HeaderCell{}".format(self.seqTables, font), family="paragraph")
        s.addElement(TextProperties(attributes={'fontsize':"{}pt".format(font+1),'fontweight':"bold" }))
        self.doc.styles.addElement(s)

        #Table columns
        table = Table(stylename="Tabla{}".format(self.seqTables))
        for i, head in enumerate(header):
            table.addElement(TableColumn(stylename="Tabla{}.{}".format(self.seqTables, chr(65+i))))  

        #Header rows
        headerrow=TableHeaderRows()
        tablerow=TableRow()
        headerrow.addElement(tablerow)
        for i, head in enumerate(header):
            p=P(stylename="Tabla{}.Heading{}".format(self.seqTables, font), text=head)
            tablecell=TableCell(stylename="Tabla{}.HeaderCell{}".format(self.seqTables, font))
            tablecell.addElement(p)
            tablerow.addElement(tablecell)
        table.addElement(headerrow)
            
        #Data rows
        for row in data:
            tr = TableRow()
            table.addElement(tr)
            for i, col in enumerate(row):
                tc = TableCell(stylename="Tabla{}.Cell".format(self.seqTables))
                tr.addElement(tc)
                
                #Parses orientation
                if orientation[i]=="<":
                    p = P(stylename="Tabla{}.TableContents{}".format(self.seqTables, font))
                elif orientation[i]==">":
                    p = P(stylename="Tabla{}.TableContentsRight{}".format(self.seqTables, font))
                
                #Colorize numbers less than zero
                try:#Formato 23 €
                    if float(col.split(" ")[0])<0:
                        s=Span(text=col, stylename="Rojo")
                    else:
                        s=Span(text=col)
                except:
                    s=Span(text=col)                    
                p.addElement(s)
                
                tc.addElement(p)
        
        self.doc.text.addElement(table)
        
    def image(self, href, width, height):
        """
            href must bu added before with addImage
            returns a Frame element
            width and height must bu a int or float value
        """
        f = Frame(name="Frame_{}".format(self.seqFrames), anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
        img = Image(href=self.images[href], type="simple", show="embed", actuate="onLoad")
        f.addElement(img)
        self.seqFrames=self.seqFrames+1
        return f

    def pageBreak(self,  horizontal=False):    
        p=P(stylename="PageBreak")#Is an automatic style
        self.doc.text.addElement(p)
        if horizontal==True:
            p=P(stylename="PH")
        else:
            p=P(stylename="PV")
        self.doc.text.addElement(p)
#
#    def link(self):
#        para = P()
#        anchor = A(href="http://www.com/", text="A link label")
#        para.addElement(anchor)
#        self.doc.text.addElement(para)
#        
#    #######################################



class OdfCell:
    def __init__(self, letter, number, object, style=None):
        """
            Object can be OdfMoney,OdfPercentage, String, datetime.date, datetime.datetime, Decimal
        """
        self.letter=letter
        self.number=number
        self.object=object
        self.style=style
        self.spannedColumns=1
        self.spannedRows=1
        self.comment=None

    def generate(self):
        if self.object.__class__==OdfMoney:
            odfcell = TableCell(valuetype="currency", currency=self.object.currency, value=self.object.amount, stylename="Euro")
        elif self.object.__class__==OdfPercentage:
            odfcell = TableCell(valuetype="percentage", value=self.object.value, stylename="Percentage")
        elif self.object.__class__==datetime.datetime:
            odfcell = TableCell(valuetype="date", datevalue=self.object.strftime("%Y-%m-%dT%H:%M:%S"), stylename="Datetime")
        elif self.object.__class__==datetime.date:
            odfcell = TableCell(valuetype="date", datevalue=str(self.object), stylename="Date")
        elif self.object.__class__ in (Decimal, float):
            odfcell= TableCell(valuetype="float", value=self.object,  stylename="Decimal")
        elif self.object.__class__==int:
            odfcell= TableCell(valuetype="float", value=self.object, stylename="Entero")
        else:#strings
            if self.object[:1]=="=":#Formula
                odfcell = TableCell(formula="of:"+self.object,  stylename=self.style)
            else:#Cadena
                odfcell = TableCell(valuetype="string", value=self.object,  stylename=self.style)
                odfcell.addElement(P(text = self.object))
        if self.spannedRows!=1 or self.spannedColumns!=1:
            odfcell.setAttribute("numberrowsspanned", str(self.spannedRows))
            odfcell.setAttribute("numbercolumnsspanned", str(self.spannedColumns))
        if self.comment!=None:
            a=Annotation(textstylename="TextRight")
            d=Date()
            d.addText(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
            a.addElement(d)
            a.addElement(P(stylename="TextRight", text=self.comment))
            odfcell.addElement(a)
        return odfcell
        
    def setSpanning(self, columns, rows):
        """Siempre es de izquierda a derecha y de arriba a abajo
        Si es 1 no hay spanning"""
        self.spannedColumns=columns
        self.spannedRows=rows
        
    def setComment(self, comment):
        self.comment=comment


## Class to create a sheet in a ods document
## By default cursor position and split position is set to "A1" cell
class OdfSheet:
    def __init__(self, doc,  title):
        self.doc=doc
        self.title=title
        self.widths=None
        self.arr=[]
        self.setCursorPosition("A", "1")#Default values
        self.setSplitPosition("A", "1")


    def setSplitPosition(self, letter, number):
        """
                split/freeze vertical (0|1|2) - 1 = split ; 2 = freeze
    split/freeze horizontal (0|1|2) - 1 = split ; 2 = freeze
    vertical position = in cell if fixed, in screen unit if frozen
    horizontal position = in cell if fixed, in screen unit if frozen
    active zone in the splitted|frozen sheet (0..3 from let to right, top
to bottom)


#   COMPROBADO CON ODF2XML
B1: 
              <config:config-item config:name="HorizontalSplitMode" config:type="short">2</config:config-item>
              <config:config-item config:name="VerticalSplitMode" config:type="short">0</config:config-item>
              <config:config-item config:name="HorizontalSplitPosition" config:type="int">1</config:config-item>
              <config:config-item config:name="VerticalSplitPosition" config:type="int">0</config:config-item>
              <config:config-item config:name="ActiveSplitRange" config:type="short">3</config:config-item>
              <config:config-item config:name="PositionLeft" config:type="int">0</config:config-item>
              <config:config-item config:name="PositionRight" config:type="int">1</config:config-item>
              <config:config-item config:name="PositionTop" config:type="int">0</config:config-item>
              <config:config-item config:name="PositionBottom" config:type="int">0</config:config-item>

"""
        def setActiveSplitRange():
            """
                Creo que es la posición tras los ejes.
            """
            if (self.horizontalSplitPosition!="0" and self.verticalSplitPosition=="0"):
                return "3"
            if (self.horizontalSplitPosition=="0" and self.verticalSplitPosition!="0"):
                return "2"
            if self.horizontalSplitPosition!="0" and self.verticalSplitPosition!="0":
                return "3"
            return "2"


        self.horizontalSplitPosition=str(column2index(letter))
        self.verticalSplitPosition=str(row2index(number))
        self.horizontalSplitMode="0" if self.horizontalSplitPosition=="0" else "2"
        self.verticalSplitMode="0" if self.verticalSplitPosition=="0" else "2"
        self.activeSplitRange=setActiveSplitRange()
        self.positionTop="0"
        self.positionBottom="0" if self.verticalSplitPosition=="0" else str(self.verticalSplitPosition)
        self.positionLeft="0"
        self.positionRight="0" if self.horizontalSplitPosition=="0" else str(self.horizontalSplitPosition)
        ##print (letter,  number, ":", self.horizontalSplitPosition,  self.verticalSplitPosition,  self.activeSplitRange, self.positionTop, self.positionBottom,  self.positionLeft, self.positionRight)

    def setCursorPosition(self, letter, number):
        """
            Sets the cursor in a Sheet
        """
        self.cursorPositionX=column2index(letter)
        self.cursorPositionY=row2index(number)

    def setComment(self, letter, number, comment):
        """
            Sets a comment in the givven cell
        """
        c=self.getCell(letter, number)
        c.setComment(comment)

    def setColumnsWidth(self, widths, unit="pt"):
        """
            widths is an int array
            id es el id del sheet de python
        """
        for w in widths:
            s=Style(name="{}_{}".format(id(self), w), family="table-column")
            s.addElement(TableColumnProperties(columnwidth="{}{}".format(w, unit)))
            self.doc.automaticstyles.addElement(s)   
        self.widths=widths
        
    ## Returns the last letter used in the sheet . Returns a string with the letter name of the column
    def lastColumn(self):
        return number2column(self.columns())

    ## Returns the last  row name used
    ## @return string row name
    def lastRow(self):
        return  number2row(self.rows())

    def mergeCells(self, letter, number,  columns, rows):
        """
            Given a cell position (letter,number), merges columns a rows given
        """
        c=self.getCell(letter, number)
        c.setSpanning(columns, rows)

    def addCell(self, cell): 
        self.arr.append(cell)
        
    def getCell(self, letter, number):
        """Returns a cell in arr"""
        for c in self.arr:
            if c.letter==letter  and c.number==number:
                return c
        return None
        
    def add(self, letter,number, result, style=None):
        if result.__class__ in (str, int, float, datetime.datetime, datetime.date,  OdfMoney, OdfPercentage, OdfFormula, Decimal):#Un solo valor
            self.addCell(OdfCell(letter, number, result, style))
        elif result.__class__ in (list,):#Una lista
            for i,row in enumerate(result):
                if row.__class__ in (int, str, float, datetime.datetime,  datetime.date):#Una lista de una columna
                    self.addCell(OdfCell(letter, rowAdd(number, i), result[i], style))
                elif row.__class__ in (list, ):#Una lista de varias columnas
                    for j,column in enumerate(row):
                        self.addCell(OdfCell(columnAdd(letter, j), rowAdd(number, i), result[i][j], style))
                else:
                    logging.warning(row.__class__, "ROW CLASS NOT FOUND",  row)

    def generate(self, ods):
        # Start the table
        columns=self.columns()
        rows=self.rows()
        grid=[[None for x in range(columns)] for y in range(rows)]
        for cell in self.arr:
            grid[row2index(cell.number)][column2index(cell.letter)]=cell
        
        table = Table(name=self.title)
        for c in range(columns):#Create columns
            try:
                tc=TableColumn(stylename="{}_{}".format(id(self), self.widths[c]))
            except:
                tc=TableColumn()
            table.addElement(tc)
        for j in range(rows):#Crreate rows
            tr = TableRow()
            table.addElement(tr)
            for i in range(columns):#Create cells
                cell=grid[j][i]
                if cell!=None:
                    tr.addElement(cell.generate())
                else:
                    tr.addElement(TableCell())
        ods.doc.spreadsheet.addElement(table)

    def columns(self):
        """
            Gets column number
        """
        r=0
        for cell in self.arr:
            column=column2number(cell.letter)
            if column>r:
                r=column
        return r

    ## Return the number of rows that are used in the cell.
    def rows(self):
        r=0
        for cell in self.arr:
            column=row2number(cell.number)
            if column>r:
                r=column
        return r

class OdfFormula:

    #tc = TableCell(formula='=AVERAGE(C4:CB62)/2',stylename='pourcent', valuetype='percentage')    
    pass

class OdfMoney:
    """
        currency es un ID
        EUR=Euros
        USD=Dolares americanosw
        self.append(Currency().init__create(QApplication.translate("Core","Chinese Yoan"), "¥", 'CNY'))
        self.append(Currency().init__create(QApplication.translate("Core","Euro"), "€", "EUR"))
        self.append(Currency().init__create(QApplication.translate("Core","Pound"),"£", 'GBP'))
        self.append(Currency().init__create(QApplication.translate("Core","Japones Yen"), '¥', "JPY"))
        self.append(Currency().init__create(QApplication.translate("Core","American Dolar"), '$', 'USD'))
        self.append(Currency().init__create(QApplication.translate("Core","Units"), 'u', 'u'))
    """
    def __init__(self, amount=None,  currency='EUR') :
        if amount==None:
            self.amount=Decimal(0)
        else:
            self.amount=Decimal(str(amount))
        if currency==None:
            self.currency='EUR'
        else:
            self.currency=currency


    def __add__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return OdfMoney(self.amount+money.amount, self.currency)
        else:
            logging.error("Before adding, please convert to the same currency")
            raise "OdfMoneyOperationException"
            
        
    def __sub__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return OdfMoney(self.amount-money.amount, self.currency)
        else:
            logging.error("Before substracting, please convert to the same currency")
            raise "OdfMoneyOperationException"
        
    def __lt__(self, money):
        if self.currency==money.currency:
            if self.amount < money.amount:
                return True
            return False
        else:
            logging.error("Before lt ordering, please convert to the same currency")
            sys.exit(1)
        
    def __mul__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero
        En caso de querer multiplicar por un numero debe ser despues
        money*4
        """
        if money.__class__ in (int,  float, Decimal):
            return OdfMoney(self.amount*money, self.currency)
        if self.currency==money.currency:
            return OdfMoney(self.amount*money.amount, self.currency)
        else:
            logging.error("Before multiplying, please convert to the same currency")
            sys.exit(1)
    
    def __truediv__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return OdfMoney(self.amount/money.amount, self.currency)
        else:
            logging.error("Before true dividing, please convert to the same currency")
            sys.exit(1)
        
    def __repr__(self):
        return self.string(2)
        
    def string(self,   digits=2):
        return "{} {}".format(round(self.amount, digits), self.symbol())
        
    def symbol(self):
        if self.currency=="EUR":
            return "€"
        elif self.currency=="USD":
            return "$"
        
    def isZero(self):
        if self.amount==Decimal(0):
            return True
        else:
            return False
            
    def isGETZero(self):
        if self.amount>=Decimal(0):
            return True
        else:
            return False           

    def isGTZero(self):
        if self.amount>Decimal(0):
            return True
        else:
            return False

    def isLTZero(self):
        if self.amount<Decimal(0):
            return True
        else:
            return False

    def isLETZero(self):
        if self.amount<=Decimal(0):
            return True
        else:
            return False
            
    def __neg__(self):
        """Devuelve otro money con el amount con signo cambiado"""
        return OdfMoney(-self.amount, self.currency)

    def round(self, digits=2):
        return round(self.amount, digits)

class OdfPercentage:
    def __init__(self, numerator=None, denominator=None):
        self.value=None
        self.setValue(self.toDecimal(numerator),self.toDecimal(denominator))
        
    def toDecimal(self, o):
        if o==None:
            return o
        if o.__class__==OdfMoney:
            return o.amount
        elif o.__class__==Decimal:
            return o
        elif o.__class__ in ( int, float):
            return Decimal(o)
        elif o.__class__==OdfPercentage:
            return o.value
        else:
            logging.warning (o.__class__)
            return None
        
    def __repr__(self):
        return self.string()
            
    def __neg__(self):
        """Devuelve otro money con el amount con signo cambiado"""
        if self.value==None:
            return self
        return OdfPercentage(-self.value, 1)
        
    def __lt__(self, other):
        if self.value==None:
            value1=Decimal('-Infinity')
        else:
            value1=self.value
        if other.value==None:
            value2=Decimal('-Infinity')
        else:
            value2=other.value
        if value1<value2:
            return True
        return False
        
    def __mul__(self, value):
        if self.value==None or value==None:
            r=None
        else:
            r=self.value*self.toDecimal(value)
        return OdfPercentage(r, 1)

    def __truediv__(self, value):
        try:
            r=self.value/self.toDecimal(value)
        except:
            r=None
        return OdfPercentage(r, 1)
        
    def setValue(self, numerator,  denominator):
        try:
            self.value=Decimal(numerator/denominator)
        except:
            self.value=None
        
        
    def value_100(self):
        if self.value==None:
            return None
        else:
            return self.value*Decimal(100)
        
    def string(self, rnd=2):
        if self.value==None:
            return "None %"
        return "{} %".format(round(self.value_100(), rnd))
        

    def isValid(self):
        if self.value!=None:
            return True
        return False
        
    def isGETZero(self):
        if self.value>=0:
            return True
        return False
    def isGTZero(self):
        if self.value>0:
            return True
        return False
    def isLTZero(self):
        if self.value<0:
            return True
        return False
        
class ODSColumnWidth:
    Date=40
    Detetime=60
    

class ODS(ODF):
    def __init__(self, filename):
        ODF.__init__(self, filename)
        self.doc=OpenDocumentSpreadsheet()
        self.sheets=[]
        self.activeSheet=None

    def createSheet(self, title):
        s=OdfSheet(self.doc, title)
        self.sheets.append(s)
        return s
        
    def getActiveSheet(self):
        if self.activeSheet==None:
            return self.sheets[0].title
        return self.activeSheet
            
    def save(self, filename=None):
        """
            If filename is given, file is saved with a different name.
        """
        #config settings information
        a=ConfigItemSet(name="ooo:view-settings")
        aa=ConfigItem(type="int", name="VisibleAreaTop")
        aa.addText("0")
        a.addElement(aa)
        aa=ConfigItem(type="int", name="VisibleAreaLeft")
        aa.addText("0")
        a.addElement(aa)
        b=ConfigItemMapIndexed(name="Views")
        c=ConfigItemMapEntry()
        d=ConfigItem(name="ViewId", type="string")
        d.addText("view1")#value="view1"
        e=ConfigItemMapNamed(name="Tables")
        for sheet in self.sheets:
            f=ConfigItemMapEntry(name=sheet.title)
            g=ConfigItem(type="int", name="CursorPositionX")
            g.addText(sheet.cursorPositionX)
            f.addElement(g)
            g=ConfigItem(type="int", name="CursorPositionY")
            g.addText(sheet.cursorPositionY)
            f.addElement(g)
            g=ConfigItem(type="int", name="HorizontalSplitPosition")
            g.addText(sheet.horizontalSplitPosition)
            f.addElement(g)
            g=ConfigItem(type="int", name="VerticalSplitPosition")
            g.addText(sheet.verticalSplitPosition)
            f.addElement(g)
            g=ConfigItem(type="short", name="HorizontalSplitMode")
            g.addText(sheet.horizontalSplitMode)
            f.addElement(g)
            g=ConfigItem(type="short", name="VerticalSplitMode")
            g.addText(sheet.verticalSplitMode)
            f.addElement(g)
            g=ConfigItem(type="short", name="ActiveSplitRange")
            g.addText(sheet.activeSplitRange)
            f.addElement(g)
            g=ConfigItem(type="int", name="PositionLeft")
            g.addText(sheet.positionLeft)
            f.addElement(g)
            g=ConfigItem(type="int", name="PositionRight")
            g.addText(sheet.positionRight)
            f.addElement(g)
            g=ConfigItem(type="int", name="PositionTop")
            g.addText(sheet.positionTop)
            f.addElement(g)
            g=ConfigItem(type="int", name="PositionBottom")
            g.addText(sheet.positionBottom)
            f.addElement(g)
            e.addElement(f)
            
        a.addElement(b)
        b.addElement(c)
        c.addElement(d)
        c.addElement(e)

        h=ConfigItem(type="string", name="ActiveTable")
        h.addText(self.getActiveSheet())
        c.addElement(h)
        self.doc.settings.addElement(a)
        
        for sheet in self.sheets:
            sheet.generate(self)
        
        if  filename==None:
            filename=self.filename

        makedirs(os.path.dirname(filename))
        self.doc.save(filename)

    def setActiveSheet(self, value):
        """value is OdfSheet"""
        self.activeSheet=value.title


class ODS_Read:
    """
       Los elementos P tienen los estilos:
       
        if result.__class__ in (str, int, float, datetime.datetime, OdfMoney, OdfPercentage, OdfFormula, Decimal):#Un solo valor
    """
    def __init__(self, filename):
        self.doc=load(filename)#doc is only used in this function. All is generated in self.doc
        self.filename=filename

        
    def getSheetElementByName(self, name):
        """
            Devuelve el elemento de sheet buscando por su nombre
        """
        for numrow, sheet in  enumerate(self.doc.spreadsheet.getElementsByType(Table)):
            if sheet.getAttribute("name")==name:
                return sheet
        return None        

    def getSheetElementByIndex(self, index):
        """
            Devuelve el elemento de sheet buscando por su posición en el documento
        """
        try:
            return self.doc.spreadsheet.getElementsByType(Table)[index]
        except:
            return None
        
        
    def rowNumber(self, sheet_element):
        """
            Devuelve el numero de filas de un determinado sheet_element
        """
        return len(sheet_element.getElementsByType(TableRow))-1
        
    def columnNumber(self, sheet_element):
        """
            Devuelve el numero de filas de un determinado sheet_element
        """
        return len(sheet_element.getElementsByType(TableColumn))
        
        
    def getCellValue(self, sheet_element, letter, number):
        """
            Returns the celll value
        """
        row=sheet_element.getElementsByType(TableRow)[row2index(number)]
        cell=row.getElementsByType(TableCell)[column2index(letter)]
        r=None
        
        if cell.getAttribute('valuetype')=='string':
            r=cell.getAttribute('value')
        if cell.getAttribute('valuetype')=='float':
            r=Decimal(cell.getAttribute('value'))
        if cell.getAttribute('valuetype')=='percentage':
            r=OdfPercentage(Decimal(cell.getAttribute('value')), Decimal(1))
        if cell.getAttribute('formula')!=None:
            r=str(cell.getAttribute('formula'))[3:]
        if cell.getAttribute('valuetype')=='currency':
            r=OdfMoney(Decimal(cell.getAttribute('value')), cell.getAttribute('currency'))
        if cell.getAttribute('valuetype')=='date':
            datevalue=cell.getAttribute('datevalue')
            if len(datevalue)<=10:
                r=datetime.datetime.strptime(datevalue, "%Y-%m-%d").date()
            else:
                r=datetime.datetime.strptime(datevalue, "%Y-%m-%dT%H:%M:%S")
#        print(cell.allowed_attributes(), cell.getAttribute('datevalue'), cell.getAttribute('datatype'))
#        print(cell.getAttribute('value'), cell.getAttribute('valuetype'),   r)
        return r

    def getCell(self, sheet_element,  letter, number):
        """
            Returns an odfcell object
        """
        row=sheet_element.getElementsByType(TableRow)[row2index(number)]
        cell=row.getElementsByType(TableCell)[column2index(letter)]
        object=self.getCellValue(sheet_element, letter, number)
        #Get spanning
        spanning_columns=cell.getAttribute('numbercolumnsspanned')
        if spanning_columns==None:
            spanning_columns=1
        else:
            spanning_columns=int(spanning_columns)
        spanning_rows=cell.getAttribute('numberrowsspanned')
        if spanning_rows==None:
            spanning_rows=1
        else:
            spanning_rows=int(spanning_rows)
        
        #Get Stylename
        stylename=cell.getAttribute('stylename')


        #Odfcell
        r=OdfCell(letter, number, object, stylename)
        r.setSpanning(spanning_columns, spanning_rows)
        
        #Get comment
#        comment=cell.getElementsByType(Annotation)
#        if len(comment)>0:
##            print((comment[0].allowed_attributes()))
#            comment_text=comment[0].getAttribute('name')
#            r.setComment(comment_text)
#            print(comment)

        return r
        
    def setCell(self, sheet_element,  letter, number, cell):
        """
            Updates a cell
            insertBefore(newchild, refchild) – Inserts the node newchild before the existing child node refchild.
appendChild(newchild) – Adds the node newchild to the end of the list of children.
removeChild(oldchild) – Re

        ESTA FUNCION SE USA PARA SUSTITUIR EN UNA PLANTILLA
        NO SE PUEDEN AÑADIR MAS CELDAS O FILAS
        PARA ESO USAR ODS_Write DE MOMENTO
        """
#        if cell.__class__ not in [ODFCell, ODFFORMULA]: FALTA PROGRAMAR
        
        row=sheet_element.getElementsByType(TableRow)[row2index(number)]
        oldcell=row.getElementsByType(TableCell)[column2index(letter)]
        row.insertBefore(cell.generate(), oldcell)
        row.removeChild(oldcell)
        
    def save(self, filename):
        if  filename==self.filename:
            print("You can't overwrite a readed ods")
            return        
        self.doc.save( filename)
                
class ODS_Write(ODS):
    def __init__(self, filename):
        def styleHeaders():
            hs=Style(name="HeaderOrange", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#ffcc99", border="0.06pt solid #000000"))
            hs.addElement(TextProperties( fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs)

            hs=Style(name="HeaderRed", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#ff0000", border="0.06pt solid #000000"))
            hs.addElement(TextProperties( fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs)

            hs=Style(name="HeaderYellow", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#ffff7f", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs) 
            
            hs=Style(name="HeaderGreen", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#9bff9e", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs) 
            
            hs=Style(name="HeaderGray", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#999999", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs) 
            
            hs=Style(name="HeaderOrangeLeft", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#ffcc99", border="0.06pt solid #000000"))
            hs.addElement(TextProperties( fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="left"))
            self.doc.styles.addElement(hs)
            
            hs=Style(name="HeaderYellowLeft", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#ffff7f", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="left"))
            self.doc.styles.addElement(hs)     
            
            hs=Style(name="HeaderGreenLeft", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#9bff9e", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="left"))
            self.doc.styles.addElement(hs)        
        
            hs=Style(name="HeaderGrayLeft", family="table-cell")
            hs.addElement(TableCellProperties(backgroundcolor="#999999", border="0.06pt solid #000000"))
            hs.addElement(TextProperties(fontweight="bold"))
            hs.addElement(ParagraphProperties(textalign="left"))
            self.doc.styles.addElement(hs) 

        def styleParagraphs():
            tr=Style(name="TextRight", family="table-cell")
            tr.addElement(TableCellProperties(border="0.06pt solid #000000"))
            tr.addElement(ParagraphProperties(textalign="end"))
            self.doc.styles.addElement(tr)

            hs=Style(name="TextLeft", family="table-cell")
            hs.addElement(TableCellProperties(border="0.06pt solid #000000"))
            hs.addElement(ParagraphProperties(textalign="left"))
            self.doc.styles.addElement(hs)

            hs=Style(name="TextCenter", family="table-cell")
            hs.addElement(TableCellProperties(border="0.06pt solid #000000"))
            hs.addElement(ParagraphProperties(textalign="center"))
            self.doc.styles.addElement(hs)

        def styleCurrrencies():
            
            # Create the styles for $AUD format currency values
            ns1 = CurrencyStyle(name="EuroBlack", volatile="true")
            ns1.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
            ns1.addElement(CurrencySymbol(language="es", country="ES", text=" €"))
            self.doc.styles.addElement(ns1)

            # Create the main style.
            ns2 = CurrencyStyle(name="EuroColor")
            ns2.addElement(TextProperties(color="#ff0000"))
            ns2.addElement(Text(text="-"))
            ns2.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
            ns2.addElement(CurrencySymbol(language="es", country="ES", text=" €"))
            ns2.addElement(Map(condition="value()>=0", applystylename="EuroBlack"))
            self.doc.styles.addElement(ns2)
            
            # Create automatic style for the price cells.
            moneycontents = Style(name="Euro", family="table-cell",  datastylename="EuroColor",parentstylename="TextRight")
            self.doc.automaticstyles.addElement(moneycontents)
            
        def stylePercentages():
            #Percentage
            nonze = PercentageStyle(name='PercentageBlack')
            nonze.addElement(TextProperties(color="#000000"))
            nonze.addElement(Number(decimalplaces='2', minintegerdigits='1'))
            nonze.addElement(Text(text=' %'))
            self.doc.styles.addElement(nonze)
            
            nonze2 = PercentageStyle(name='PercentageColor')
            nonze2.addElement(TextProperties(color="#ff0000"))
            nonze2.addElement(Text(text="-"))
            nonze2.addElement(Number(decimalplaces='2', minintegerdigits='1'))
            nonze2.addElement(Text(text=' %'))
            nonze2.addElement(Map(condition="value()>=0", applystylename="PercentageBlack"))
            self.doc.styles.addElement(nonze2)
            
            pourcent = Style(name='Percentage', family='table-cell', datastylename='PercentageColor',parentstylename="TextRight")
    #        pourcent.addElement(TableCellProperties(border="0.06pt solid #000000"))
    #        pourcent.addElement(ParagraphProperties(textalign='end'))
    #        pourcent.addElement(TextProperties(attributes={'fontsize':"10pt",'fontweight':"bold", 'color':"#000000" }))
            self.doc.automaticstyles.addElement(pourcent)
            
        def styleDatetimes():
            #create custom format in styles.xml
            date_style = DateStyle(name="DatetimeBlack") #, language="lv", country="LV")
            date_style.addElement(Year(style="long"))
            date_style.addElement(Text(text="-"))
            date_style.addElement(Month(style="long"))
            date_style.addElement(Text(text="-"))
            date_style.addElement(Day(style="long"))
            date_style.addElement(Text(text=" "))
            date_style.addElement(Hours(style="long"))
            date_style.addElement(Text(text=":"))
            date_style.addElement(Minutes(style="long"))
            date_style.addElement(Text(text=":"))
            date_style.addElement(Seconds(style="long"))
            self.doc.styles.addElement(date_style)
            #link to generated style from content.xml
            ds = Style(name="Datetime", datastylename="DatetimeBlack",parentstylename="TextLeft", family="table-cell")
            self.doc.automaticstyles.addElement(ds)
            
            
            #create custom format in styles.xml
            date_style = DateStyle(name="DateBlack") #, language="lv", country="LV")
            date_style.addElement(Year(style="long"))
            date_style.addElement(Text(text="-"))
            date_style.addElement(Month(style="long"))
            date_style.addElement(Text(text="-"))
            date_style.addElement(Day(style="long"))
            self.doc.styles.addElement(date_style)
            #link to generated style from content.xml
            ds = Style(name="Date", datastylename="DateBlack",parentstylename="TextLeft", family="table-cell")
            self.doc.automaticstyles.addElement(ds)

    #    <number:number-style style:volatile="true" style:name="N108P0">
    #      <number:number number:min-integer-digits="1" number:decimal-places="2" ns41:min-decimal-places="2"/>
    #    </number:number-style>
    #    <number:number-style style:name="N108">
    #      <style:text-properties fo:color="#ff0000"/>
    #      <number:text>-</number:text>
    #      <number:number number:min-integer-digits="1" number:decimal-places="2" ns41:min-decimal-places="2"/>
    #      <style:map style:condition="value()&gt;=0" style:apply-style-name="N108P0"/>
    #    </number:number-style>
            # Create the styles for $AUD format currency values
        def styleNumbers():
            ns1 = NumberStyle(name="EnteroBlack", volatile="true")
            ns1.addElement(Number(decimalplaces="0", minintegerdigits="1", grouping="true"))
            self.doc.styles.addElement(ns1)

            # Create the main style.
            ns2 = NumberStyle(name="EnteroColor")
            ns2.addElement(TextProperties(color="#ff0000"))
            ns2.addElement(Text(text="-"))
            ns2.addElement(Number(decimalplaces="0", minintegerdigits="1", grouping="true"))
            ns2.addElement(Map(condition="value()>=0", applystylename="EnteroBlack"))
            self.doc.styles.addElement(ns2)
            
            # Create automatic style for the price cells.
            moneycontents = Style(name="Entero", family="table-cell",  datastylename="EnteroColor",parentstylename="TextRight")
            self.doc.styles.addElement(moneycontents)


            ns1 = NumberStyle(name="DecimalBlack", volatile="true")
            ns1.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
            self.doc.styles.addElement(ns1)

            # Create the main style.
            ns2 = NumberStyle(name="DecimalColor")
            ns2.addElement(TextProperties(color="#ff0000"))
            ns2.addElement(Text(text="-"))
            ns2.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
            ns2.addElement(Map(condition="value()>=0", applystylename="DecimalBlack"))
            self.doc.styles.addElement(ns2)
            
            # Create automatic style for the price cells.
            moneycontents = Style(name="Decimal", family="table-cell",  datastylename="DecimalColor",parentstylename="TextRight")
            self.doc.styles.addElement(moneycontents)

        ##################################################
        ODF.__init__(self, filename)
        self.doc=OpenDocumentSpreadsheet()
        self.sheets=[]
        self.activeSheet=None
        styleHeaders()
        styleParagraphs()
        styleCurrrencies()
        styleDatetimes()
        stylePercentages()
        styleNumbers()

        
    
    def save(self, filename=None):
        if  filename==None:
            filename=self.filename
        ODS.save(self, filename)
        


##########################################################################################
## Allows to operate with columns letter names
## @param letter String with the column name. For example A or AA...
## @param number Columns to move
## @return String With the name of the column after movement
def columnAdd(letter, number):
    letter_value=column2number(letter)+number
    return number2column(letter_value)


def rowAdd(letter,number):
    return str(int(letter)+number)

## Convierte un número  con el numero de columna al nombre de la columna de hoja de datos
##
## Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA.
def number2column(n):
    name = ''
    while n > 0:
        n, r = divmod (n - 1, 26)
        name = chr(r + ord('A')) + name
    return name

## Convierte una columna de hoja de datos a un número
##
## Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703.
def column2number(name):
    n = 0
    for c in name:
        n = n * 26 + 1 + ord(c) - ord('A')
    return n

## Converts a column name to a index position (number of column -1)
def column2index(name):
    return column2number(name)-1

## Convierte el nombre de la fila de la hoja de datos a un índice, es decir el número de la fila -1
def row2index(number):
    return int(number)-1

## Covierte el nombre de la fila de la hoja de datos a un  numero entero que corresponde con el numero de la fila
def row2number(strnumber):
    return int(strnumber)

## Convierte el numero de la fila al nombre de la fila en la hoja de datos , que corresponde con un string del numero de la fila
def number2row(number):
    return str(number)
    
## Convierte el indice de la fila al numero cadena de la hoja de datos
def index2row(index):
    return str(index+1)
    
## Convierte el indice de la columna a la cadena de letras de la columna de la hoja de datos
def index2column(index):
    return number2column(index+1)
    
## Crea un directorio con todos sus subdirectorios
##
## No produce error si ya está creado.
def makedirs(dir):
    try:
        os.makedirs(dir)
    except:
        pass

def ODFPYversion():
    return __version__.split("/")[1]


if __name__ == "__main__":
    #ODS
    doc=ODS_Write("libodfgenerator.ods")
    doc.setMetadata("LibODFGenerator example",  "This class documentation", "Mariano Muñoz")
    s1=doc.createSheet("Example")
    s1.add("A", "1", [["Title", "Value"]], "HeaderOrange")
    s1.add("A", "2", "Percentage", "TextLeft")
    s1.add("A", "4",  "Suma", "TextRight")
    s1.add("B", "2",  OdfPercentage(12, 56))
    s1.add("B", "3",  OdfPercentage(12, 56))
    s1.add("B", "4",  "=sum(B2:B3)","Percentage" )
    s1.add("B", "6",  100.26)
    s1.add("B", "7",  101)
    s1.setCursorPosition("A", "3")
    s1.setSplitPosition("A", "2")
    
    s2=doc.createSheet("Example 2")
    s2.add("A", "1", [["Title", "Value"]], "HeaderOrange")
    s2.add("A", "2", "Currency", "TextLeft")
    s2.add("B", "2",  OdfMoney(12, "EUR"))
    s2.add("A", "3", "Datetime", "TextLeft")
    s2.add("B", "3",  datetime.datetime.now())
    s2.add("A", "4", "Date", "TextLeft")
    s2.add("B", "4",  datetime.date.today())
    s2.setColumnsWidth([330, 150])
    s2.setCursorPosition("D", "6")
    s2.setSplitPosition("B", "2")
    
    #Adding a cell to s1 after s2 definition
    cell=OdfCell("B", "10", "Celda con OdfCell", "HeaderYellow")
    cell.setComment("Comentario")
    cell.setSpanning(2, 2)
    s1.addCell(cell)
    
    s3=doc.createSheet("Styles")
    s3.setColumnsWidth([400, 150, 150])
    s3.add("A","1","LibODFGenerator has the folowing default Styles:")
    for number,  style in enumerate(["HeaderOrange", "HeaderYellow", "HeaderGreen", "HeaderRed", "HeaderGray", "HeaderOrangeLeft", "HeaderYellowLeft","HeaderGreenLeft",  "HeaderGrayLeft", "TextLeft", "TextRight", "TextCenter"]):
        s3.add("B", rowAdd("1", number) , style, style=style)
    s3.add("A",rowAdd("2", number+1) ,"LibODFGenerator has the folowing default cell classes:")
    s3.add("B",rowAdd("2", number+1) ,OdfMoney(1234.23, "EUR"))
    s3.add("C",rowAdd("2", number+1) ,OdfMoney(-1234.23, "EUR"))
    s3.add("B",rowAdd("2", number+2) ,OdfPercentage(1234.23, 10000))
    s3.add("C",rowAdd("2", number+2) ,OdfPercentage(-1234.23, 25000))


    s4=doc.createSheet("Splitting")
    for letter in "ABCDEFGHIJ":
        for number in range(1, 11):
            s4.add(letter, str(number), letter+str(number), "HeaderYellowLeft")
    s4.setCursorPosition("C", "3")
    s4.setSplitPosition("C", "3")
    
    doc.setActiveSheet(s3)
    doc.save()
    print("ODS Generated")

    doc=ODS_Read("libodfgenerator.ods")
    s1=doc.getSheetElementByIndex(0)
    print("Getting values from ODS:")
    print("  + String", doc.getCellValue(s1, "A", "1"))
    print("  + Percentage", doc.getCellValue(s1, "B", "2"))
    print("  + Formula", doc.getCellValue(s1, "B", "4"))
    print("  + Decimal", doc.getCellValue(s1, "B", "6"))
    print("  + Decimal", doc.getCellValue(s1, "B", "7"))
    s2=doc.getSheetElementByIndex(1)
    print("  + Currency", doc.getCellValue(s2, "B", "2"))
    print("  + Datetime", doc.getCellValue(s2, "B", "3"))
    print("  + Date", doc.getCellValue(s2, "B", "4"))
    
    ##Sustituye celda
    odfcell=doc.getCell(s1, "B", "6")
    odfcell.object=1789.12
    doc.setCell(s1, "B", "6", odfcell)
    doc.save("libodfgenerator_readed.ods")

    odfcell=doc.getCell(s1, "B", "10")
    odfcell.object="TURULETE"
#    odfcell.setComment("Turulete")
    doc.setCell(s1, "B", "10", odfcell )

    #ODT#
    doc=ODT("libodfgenerator.odt", language="fr", country="FR")
    doc.setMetadata("LibODFGenerator manual",  "LibODFGenerator documentation", "Mariano Muñoz")
    doc.title("Manual of LibODFGenerator")
    doc.header("ODT Writing", 1)
    doc.simpleParagraph("Hola a todos")
    doc.list(["Pryueba hola no", "Adios", "Bienvenido"], style="BulletList")
    doc.simpleParagraph("Hola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todosHola a todos")
    doc.numberedList(["Pryueba hola no", "Adios", "Bienvenido"])
    doc.simpleParagraph("Con libodfgenerator podemos")
    doc.simpleParagraph("This library create several default styles for writing ODT files:")
    doc.list(["Title: Generates a title with 18pt and bold font", "Header1: Generates a Level 1 header"], style="BulletList")
    doc.addImage("images/crown.png")
    p = P(stylename="Standard")
    p.addText("Este es un ejemplo de imagen as char: ")
    p.addElement(doc.image("images/crown.png", "3cm", "3cm"))
    p.addText(". Ahora sigo escribiendo sin problemas.")
    doc.doc.text.addElement(p)
    doc.simpleParagraph("Como ves puedo repetirla mil veces sin que me aumente el tamaño del fichero, porque uso referencias")
    p=P(stylename="Standard")
    for i in range(100):
        p.addElement(doc.image("images/crown.png", "4cm", "4cm"))
    p.addText(". Se acabó.")
    doc.doc.text.addElement(p)
    doc.pageBreak()

    doc.header("ODS Writing", 1)
    doc.simpleParagraph("This library create several default styles for writing ODS files. You can see examples in libodfgenerator.ods.")
    doc.pageBreak(horizontal=True)

    doc.header("ODS Reading", 1)
    doc.save()
    print("ODT Generated")