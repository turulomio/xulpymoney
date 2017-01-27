import datetime
import logging
import sys
from odf.opendocument import OpenDocumentSpreadsheet,  OpenDocumentText,  load
from odf.style import Footer, FooterStyle, HeaderFooterProperties, Style, TextProperties, TableColumnProperties, Map,  TableProperties,  TableCellProperties, PageLayout, PageLayoutProperties, ParagraphProperties,  ListLevelProperties,  MasterPage
from odf.number import  CurrencyStyle, CurrencySymbol,  Number, NumberStyle, Text,  PercentageStyle,  DateStyle, Year, Month, Day, Hours, Minutes, Seconds
from odf.text import P,  H,  Span, ListStyle,  ListLevelStyleBullet,  List,  ListItem, ListLevelStyleNumber,  OutlineLevelStyle,  OutlineStyle,  PageNumber,  PageCount
from odf.table import Table, TableColumn, TableRow, TableCell,  TableHeaderRows
from odf.draw import Frame, Image
from odf.dc import Creator, Description, Title
from odf.meta import InitialCreator
from odf.config import ConfigItem, ConfigItemMapEntry, ConfigItemMapIndexed, ConfigItemMapNamed,  ConfigItemSet
from decimal import Decimal

class ODT():
    def __init__(self, filename, template=None):
        self.filename=filename
        self.doc=OpenDocumentText()
        
        if template!=None:
            templatedoc= load(template)
            for style in templatedoc.styles.childNodes[:]:
                self.doc.styles.addElement(style)
          
            for autostyle in templatedoc.automaticstyles.childNodes[:]:
                self.doc.automaticstyles.addElement(autostyle)
                
            for master in templatedoc.masterstyles.childNodes[:]:
                self.doc.masterstyles.addElement(master)
                
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
                
        #Pagebreak styles horizontal y vertical        
        s = Style(name="PH", family="paragraph",  parentstylename="Standard", masterpagename="Landscape")
        s.addElement(ParagraphProperties(pagenumber="auto"))
        self.doc.styles.addElement(s)
        s = Style(name="PV", family="paragraph",  parentstylename="Standard", masterpagename="Standard")
        s.addElement(ParagraphProperties(pagenumber="auto"))
        self.doc.styles.addElement(s)
        
#        #Header1
#        #    <style:style style:auto-update="true" style:display-name="Heading 1" style:default-outline-level="1" style:family="paragraph" style:name="Heading_20_1" style:next-style-name="Text_20_body" style:parent-style-name="Heading" style:class="text">
#      <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-right="0cm" fo:text-align="justify" fo:text-indent="0cm" ns42:contextual-spacing="false" style:writing-mode="page" fo:margin-left="0cm" fo:margin-bottom="0.212cm" style:auto-text-indent="false" style:justify-single-word="false"/>
#      <style:text-properties style:font-weight-complex="bold" fo:font-size="15pt" style:font-size-asian="130%" style:font-size-complex="130%" fo:font-weight="bold" style:font-weight-asian="bold"/>
#    </style:style>
        h1style = Style(name="Heading1", family="paragraph",  autoupdate="true", defaultoutlinelevel="1")
        h1style.addElement(ParagraphProperties(attributes={"margintop":"0.6cm", "textalign":"justify", "marginbottom":"0.3cm"}))
        h1style.addElement(TextProperties(attributes={"fontsize": "15pt", "fontweight": "bold"}))
        self.doc.styles.addElement(h1style)
        h2style = Style(name="Heading2", family="paragraph",  autoupdate="true", defaultoutlinelevel="2")
        h2style.addElement(ParagraphProperties(attributes={"margintop":"0.5cm", "textalign":"justify", "marginbottom":"0.25cm"}))
        h2style.addElement(TextProperties(attributes={"fontsize": "14pt", "fontweight": "bold"}))
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
        
        standard= Style(name="Standard", family="paragraph",  autoupdate="true")
        standard.addElement(ParagraphProperties(attributes={"margintop":"0.2cm", "textalign":"justify", "marginbottom":"0.2cm", "textindent":"1cm"}))
        standard.addElement(TextProperties(attributes={"fontsize": "12pt"}))
        self.doc.styles.addElement(standard)


        
        liststandard= Style(name="ListStandard", family="paragraph",  autoupdate="true")
        liststandard.addElement(ParagraphProperties(attributes={"margintop":"0.1cm", "textalign":"justify", "marginbottom":"0.1cm", "textindent":"0cm"}))
        liststandard.addElement(TextProperties(attributes={"fontsize": "12pt"}))
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
            
        self.seqTables=0#Sequence of tables
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
        s.addElement(TextProperties(attributes={"fontsize": "9pt"}))
        self.doc.styles.addElement(s)


#    <style:master-page style:name="Standard" style:page-layout-name="Mpm1">
#      <style:footer>
#        <text:p text:style-name="MP1">Página <text:page-number text:select-page="current">1</text:page-number> de <text:page-count>1</text:page-count></text:p>
#      </style:footer>
#    </style:master-page>
        #Footer
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

    def setMetadata(self, title,  description, creator):
        self.doc.meta.addElement(Title(text=title))
        self.doc.meta.addElement(Description(text=description))
        self.doc.meta.addElement(InitialCreator(text=creator))
        self.doc.meta.addElement(Creator(text=creator))

    def emptyParagraph(self, style="Standard", number=1):
        for i in range(number):
            self.simpleParagraph("",style)
                
    def save(self):
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
        
    def image(self, filename, width, height):
        p = P(stylename="Illustration")
        href = self.doc.addPicture(filename)
        f = Frame(name="filename", anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
        p.addElement(f)
        img = Image(href=href, type="simple", show="embed", actuate="onLoad")
        f.addElement(img)
        self.doc.text.addElement(p)

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
        else:
            odfcell = TableCell(valuetype="string", value=self.object,  stylename=self.style)
            odfcell.addElement(P(text = self.object))
        return odfcell
        
        

class OdfSheet:
    def __init__(self, doc,  title):
        self.doc=doc
        self.title=title
        self.widths=None
        self.arr=[]


    def setSplitPosition(self, letter, number):
        """
                split/freeze vertical (0|1|2) - 1 = split ; 2 = freeze


    split/freeze horizontal (0|1|2) - 1 = split ; 2 = freeze


    vertical position = in cell if fixed, in screen unit if frozen


    horizontal position = in cell if fixed, in screen unit if frozen
    active zone in the splitted|frozen sheet (0..3 from let to right, top
to bottom)"""
        self.horizontalSplitPosition=str(self.letter2column(letter))
        self.verticalSplitPosition=str(self.number2row(number))
        self.horizontalSplitMode="0" if self.horizontalSplitPosition=="0" else "2"
        self.verticalSplitMode="0" if self.verticalSplitPosition=="0" else "2"
        self.activeSplitRange="2"
        self.positionTop="0"
        self.positionBottom="0" if self.verticalSplitPosition=="0" else "1"
        self.positionLeft="0"
        self.positionRight="0" if self.horizontalSplitPosition=="0" else "1"
        
        
        
    def setCursorPosition(self, letter, number):
        """
            Sets the cursor in a Sheet
        """
        self.cursorPositionX=self.letter2column(letter)
        self.cursorPositionY=self.number2row(number)
        
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

    def letter2column(self, letters):
        def caracter2value(caracter):
            return ord(caracter)-65
        ############################
        if len(letters)==1:
            return caracter2value(letters[0])

    def number2row(self, number):
        return int(number)-1
        
    def addCell(self, cell): 
        self.arr.append(cell)
        
    def add(self, letter,number, result, style=None):
        if result.__class__ in (str, int, float, datetime.datetime, OdfMoney, OdfPercentage, OdfFormula, Decimal):#Un solo valor
            self.addCell(OdfCell(letter, number, result, style))
        elif result.__class__ in (list,):#Una lista
            for i,row in enumerate(result):
                if row.__class__ in (int, str, float, datetime.datetime):#Una lista de una columna
                    self.addCell(OdfCell(letter, number_add(number, i), result[i], style))
                elif row.__class__ in (list, ):#Una lista de varias columnas
                    for j,column in enumerate(row):
                        self.addCell(OdfCell(letter_add(letter, j), number_add(number, i), result[i][j], style))
                else:
                    print(row.__class__, "ROW CLASS NOT FOUND",  row)

    def generate(self, ods):
        # Start the table
        columns=self.columns()
        rows=self.rows()
        grid=[[None for x in range(columns)] for y in range(rows)]
        for cell in self.arr:
            grid[self.number2row(cell.number)][self.letter2column(cell.letter)]=cell
        
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
            column=self.letter2column(cell.letter)
            if column>r:
                r=column
        return r+1

    def rows(self):
        """
            Gets column number
        """
        r=0
        for cell in self.arr:
            column=self.number2row(cell.number)
            if column>r:
                r=column
        return r+1

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
            print (self.currency, money.currency )
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
            print (o.__class__)
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
class ODS():
    def __init__(self, filename):
        self.filename=filename
        self.doc=OpenDocumentSpreadsheet()
        self.sheets=[]
        self.activeSheet=None

#    <style:style style:family="table-cell" style:parent-style-name="Default" style:name="HHeaderOrange">
#      <style:table-cell-properties style:repeat-content="false" ns42:vertical-justify="auto" fo:background-color="#ffcc99" style:text-align-source="fix" fo:border="0.06pt solid #000000"/>
#      <style:paragraph-properties fo:text-align="center" css3t:text-justify="auto"/>
#      <style:text-properties fo:font-weight="bold"/>
#    </style:style>
        hs=Style(name="HeaderOrange", family="table-cell")
        hs.addElement(TableCellProperties(backgroundcolor="#ffcc99", border="0.06pt solid #000000"))
        hs.addElement(TextProperties( fontweight="bold"))
        hs.addElement(ParagraphProperties(textalign="center"))
        self.doc.styles.addElement(hs)
        
        hs=Style(name="HeaderYellow", family="table-cell")
        hs.addElement(TableCellProperties(backgroundcolor="#ffff7f", border="0.06pt solid #000000"))
        hs.addElement(TextProperties(fontweight="bold"))
        hs.addElement(ParagraphProperties(textalign="left"))
        self.doc.styles.addElement(hs)        

        tr=Style(name="TextRight", family="table-cell")
        tr.addElement(TableCellProperties(border="0.06pt solid #000000"))
        tr.addElement(ParagraphProperties(textalign="end"))
        self.doc.styles.addElement(tr)

        hs=Style(name="TextLeft", family="table-cell")
        hs.addElement(TableCellProperties(border="0.06pt solid #000000"))
        hs.addElement(ParagraphProperties(textalign="left"))
        self.doc.styles.addElement(hs)
        
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

    def createSheet(self, title):
        s=OdfSheet(self.doc, title)
        self.sheets.append(s)
        return s
        
    def getActiveSheet(self):
        if self.__activeSheet==None:
            return self.sheets[0].title
        return self.__activeSheet
        
    def setActiveSheet(self, value):
        """value is OdfSheet"""
        self.__activeSheet=value.title


    def save(self):
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
        self.doc.save(self.filename)


    def setMetadata(self, title,  description, creator):
        self.doc.meta.addElement(Title(text=title))
        self.doc.meta.addElement(Description(text=description))
        self.doc.meta.addElement(InitialCreator(text=creator))
        self.doc.meta.addElement(Creator(text=creator))

##########################################################################################
def letter_add(letter, number):
    """Add to columns to letter
    el ord de A=65
    el ord de Z=90
    
    Z es sumar 24
    """
    maxord=ord(letter)+number
    result=""
    while maxord>90:
        result=result+"A"
        maxord=maxord-26   
    result=result+chr(maxord)
    return result

def number_add(letter,number):
    return str(int(letter)+number)


if __name__ == "__main__":
    #ODS
    doc=ODS("libodfgenerator.ods")
    doc.setMetadata("LibODFGenerator example",  "This class documentation", "Mariano Muñoz")
    s1=doc.createSheet("Example")
    s1.add("A", "1", [["Title", "Value"]], "HeaderOrange")
    s1.add("A", "2", "Percentage", "TextLeft")
    s1.add("B", "2",  OdfPercentage(12, 56))
    s1.setCursorPosition("A", "3")
    s1.setSplitPosition("A", "2")
    s1=doc.createSheet("Example 2")
    s1.add("A", "1", [["Title", "Value"]], "HeaderOrange")
    s1.add("A", "2", "Currency", "TextLeft")
    s1.add("B", "2",  OdfMoney(12, "EUR"))
    s1.add("A", "3", "Datetime", "TextLeft")
    s1.add("B", "3",  datetime.datetime.now())
    s1.setColumnsWidth([330, 150])
    s1.setCursorPosition("D", "6")
    s1.setSplitPosition("B", "2")
    doc.setActiveSheet(s1)
    doc.save()
