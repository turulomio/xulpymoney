from odf.opendocument import OpenDocumentSpreadsheet,  OpenDocumentText,  load
from odf.style import Footer, FooterStyle, HeaderFooterProperties, Style, TextProperties, TableColumnProperties, Map,  TableProperties,  TableCellProperties, PageLayout, PageLayoutProperties, ParagraphProperties,  ListLevelProperties,  MasterPage
from odf.number import  CurrencyStyle, CurrencySymbol,  Number,  Text
from odf.text import P,  H,  Span, ListStyle,  ListLevelStyleBullet,  List,  ListItem, ListLevelStyleNumber,  OutlineLevelStyle,  OutlineStyle,  PageNumber,  PageCount
from odf.table import Table, TableColumn, TableRow, TableCell,  TableHeaderRows
from odf.draw import Frame, Image
from odf.dc import Creator, Description, Title
from odf.meta import InitialCreator

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



class Cell:
    def __init__(self, letter, number, object, style=None):
        self.letter=letter
        self.number=number
        self.object=object
        self.style=style


class Sheet:
    def __init__(self, title, rows,  columns):
        self.title=title
        self.columns=columns
        self.rows=rows
        self.widths=None#Se carga desde ODS.setColumnWidths
        self.arr=[[None for x in range(self.columns)] for y in range(self.rows)]

    def caracter2value(self, caracter):
        r=ord(caracter)-65
#        print("{} -> {}".format(caracter, r))
        return r

    def letter2column(self, letters):
        if len(letters)==1:
            return self.caracter2value(letters[0])
            
        
    def number2row(self, number):
        return int(number)-1
        
    def add(self, cell): 
        self.arr[self.number2row(cell.number)][self.letter2column(cell.letter)]=cell

    def generate(self, ods):
        # Start the table, and describe the columns
        table = Table(name=self.title)
        for w in self.widths:
            tc=TableColumn(stylename="{}_{}".format(id(self), w))
            table.addElement(tc)
        # Create a column (same as <col> in HTML) Make all cells in column default to currency
#        table.addElement(TableColumn(stylename=widewidth, defaultcellstylename="ce1"))
        for j in range(self.rows):
            # Create a row (same as <tr> in HTML)
            tr = TableRow()
            table.addElement(tr)
            # Create a cell with a negative value. It should show as red.
            for i in range(self.columns):
                if self.arr[j][i]!=None:
#                    print (self.arr[i][j])
                    tr.addElement(ods.cell2odfcell(self.arr[j][i]))
                else:
                    tr.addElement(TableCell())
        ods.doc.spreadsheet.addElement(table)
        

class ODS():
    def __init__(self, filename):
        self.filename=filename
        self.doc=OpenDocumentSpreadsheet()
        self.sheets=[]

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

        hs=Style(name="TextRight", family="table-cell")
        hs.addElement(TableCellProperties(border="0.06pt solid #000000"))
        hs.addElement(ParagraphProperties(textalign="end"))
        self.doc.styles.addElement(hs)

        hs=Style(name="TextLeft", family="table-cell")
        hs.addElement(TableCellProperties(border="0.06pt solid #000000"))
        hs.addElement(ParagraphProperties(textalign="left"))
        self.doc.styles.addElement(hs)

    def createSheet(self, title, rows, columns):
        s=Sheet(title, rows, columns)
        self.sheets.append(s)
        return s
        
    def cell2odfcell(self, cell):
        print("Must be overriden")
        #c = TableCell(valuetype="currency", currency=object.currency.id, value=object.amount)

    def save(self):
        for sheet in self.sheets:
            sheet.generate(self)
        self.doc.save(self.filename)
        
    def setColumnWidths(self, sheet, widths):
        """
            widths is an int array
            id es el id del sheet de python
        """
        for w in widths:
            s=Style(name="{}_{}".format(id(sheet), w), family="table-column")
            s.addElement(TableColumnProperties(columnwidth="{}pt".format(w)))
            self.doc.automaticstyles.addElement(s)   
        sheet.widths=widths
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
