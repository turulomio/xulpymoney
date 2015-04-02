#!/usr/bin/python2
# -*- coding: utf-8 -*-
# PUEDES MIRAR DENTRO DE UN DOCUMENTO CON LO QUE QUIERAS CONSEGUIR Y SIMULARLO EN ODF


## ODT generated directly
import odf.opendocument
import odf.style
import odf.text
import odf.table
import odf.draw
import odf.meta
import odf.dc

def odt_generated_directly():
    def styles_page():  
        pagelayout = odf.style.PageLayout(name="MyLayoutdddd")
        textdoc.automaticstyles.addElement(pagelayout)
        pagelayout.addElement(odf.style.PageLayoutProperties(margin="5cm", pagewidth="28cm", pageheight="21cm", printorientation="landscape"))
        mp = odf.style.MasterPage(name="Standardddd", pagelayoutname=pagelayout)
        textdoc.masterstyles.addElement(mp)
    
    def styles_automatic():
        # Create automatic styles for the column widths.
        # We want two different widths, one in inches, the other one in metric.
        # ODF Standard section 15.9.1
        widthshort = odf.style.Style(name="Wshort", family="table-column")
        widthshort.addElement(odf.style.TableColumnProperties(columnwidth="1.7cm"))
        textdoc.automaticstyles.addElement(widthshort)
        
        widthwide = odf.style.Style(name="Wwide", family="table-column")
        widthwide.addElement(odf.style.TableColumnProperties(columnwidth="1.5in"))
        textdoc.automaticstyles.addElement(widthwide)
        
        # An automatic style
        boldstyle = odf.style.Style(name="Bold", family="text")
        boldprop = odf.style.TextProperties(fontweight="bold")
        boldstyle.addElement(boldprop)
        textdoc.automaticstyles.addElement(boldstyle)
        
        sPageBreak= odf.style.Style(name="PageBreak", family="paragraph")
        sPageBreak.addElement(odf.style.ParagraphProperties(breakbefore="page"))
        textdoc.automaticstyles.addElement(sPageBreak)
        
    

    def styles():
        h1style = odf.style.Style(name="Heading 1", family="paragraph")
        h1style.addElement(odf.style.TextProperties(attributes={'fontsize':"16pt",'fontweight':"bold" }))
        textdoc.styles.addElement(h1style)
        
        h2style = odf.style.Style(name="Heading 2", family="paragraph")
        h2style.addElement(odf.style.TextProperties(attributes={'fontsize':"14pt",'fontweight':"bold" }))
        textdoc.styles.addElement(h2style)
        
        tablecontents = odf.style.Style(name="TableContents", family="paragraph")
        tablecontents.addElement(odf.style.ParagraphProperties(numberlines="false", linenumber="0"))
        textdoc.styles.addElement(tablecontents)

            
        
    def metadata():
        textdoc.meta.addElement(odf.dc.Title(text="pyodf example"))
        textdoc.meta.addElement(odf.dc.Description(text=u"This is a nice description of Muñoz"))
        textdoc.meta.addElement(odf.meta.InitialCreator(text=u"Mariano Muñoz Marqu´inez"))
        textdoc.meta.addElement(odf.dc.Creator(text=u'đđðæßðđæ€ł'))
        
    def pagebreak():    
        p=odf.text.P(stylename="PageBreak")#Is an automatic style
        textdoc.text.addElement(p)

    def link():
        para = odf.text.P()
        anchor = odf.text.A(href="http://www.com/", text="A link label")
        para.addElement(anchor)
        textdoc.text.addElement(para)
        
    #######################################
    textdoc = odf.opendocument.OpenDocumentText()

    metadata()
    styles_page()
    styles_automatic()
    styles()

    
    
    # Text
    h=odf.text.H(outlinelevel=1, stylename="Heading 1", text="My first text")
    textdoc.text.addElement(h)
    p = odf.text.P(text="Hello world. ")
    boldpart = odf.text.Span(stylename="Bold",text="This part is bold. ")
    p.addElement(boldpart)
    p.addText("This is after bold.")
    textdoc.text.addElement(p)
    
    table = odf.table.Table()
    table.addElement(odf.table.TableColumn(numbercolumnsrepeated=4,stylename="Wshort"))
    table.addElement(odf.table.TableColumn(numbercolumnsrepeated=3,stylename="Wwide"))
    
    f = open('/etc/passwd')
    for i in range(5):
    #for line in f:
        line=f.readline()
        rec = line.strip().split(":")
        tr = odf.table.TableRow()
        table.addElement(tr)
        for val in rec:
            tc = odf.table.TableCell()
            tr.addElement(tc)
            p = odf.text.P(stylename="TableContents",text=val)
            tc.addElement(p)
    
    textdoc.text.addElement(table)
    
    pagebreak()
    
    link()
    
    ###Generating images
    textdoc.text.addElement(odf.text.H(outlinelevel=2,text='Generating An Image', stylename="Heading 2"))
    p = odf.text.P()
    
    href = textdoc.addPicture("../images/spain.gif")
    f = odf.draw.Frame(name="graphics1", anchortype="character") #, width="2cm", height="2cm", zindex="0")
    p.addElement(f)
    img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
    f.addElement(img)
    textdoc.text.addElement(p)
    
    
    pagebreak()
    
    ###Foot note
    textdoc.text.addElement(odf.text.H(outlinelevel=1,text='Footnotes (Heading 1)',stylename="Heading 1"))
    p = odf.text.P()
    textdoc.text.addElement(p)
    p.addText("This sentence has an accompanying footnote.")
    note = odf.text.Note(id="ftn0", noteclass="footnote")
    p.addElement(note)
    note.addElement(odf.text.NoteCitation(text='1'))
    notebody = odf.text.NoteBody()
    note.addElement(notebody)
    notebody.addElement(odf.text.P(stylename="Footnote", text="You are reading a footnote."))
    p.addElement(odf.text.S(c=2))
    p.addText("Where does the text after a footnote go?")
    
    
    
    pagebreak()
    textdoc.text.addElement(odf.text.H(outlinelevel=1,text='Generating An Image', stylename="Heading 1"))
    
    textdoc.save("odfpy_generated_directly.odt")





def odt_generated_from_template():
    pass



##ODT generated from template









## ODS generated directly
def ods_generated_directly():

    doc = odf.opendocument.OpenDocumentSpreadsheet()
    # Create a style for the table content. One we can modify
    # later in the word processor.
    tablecontents = odf.style.Style(name="Table Contents", family="paragraph")
    tablecontents.addElement(odf.style.ParagraphProperties(numberlines="false", linenumber="0"))
    doc.styles.addElement(tablecontents)
    
    # Create automatic styles for the column widths.
    # We want two different widths, one in inches, the other one in metric.
    # ODF Standard section 15.9.1
    widthshort = odf.style.Style(name="Wshort", family="table-column")
    widthshort.addElement(odf.style.TableColumnProperties(columnwidth="1.7cm"))
    doc.automaticstyles.addElement(widthshort)
    
    widthwide = odf.style.Style(name="Wwide", family="table-column")
    widthwide.addElement(odf.style.TableColumnProperties(columnwidth="1.5in"))
    doc.automaticstyles.addElement(widthwide)
    
    # Start the table, and describe the columns
    table = odf.table.Table(name="Password")
    table.addElement(odf.table.TableColumn(numbercolumnsrepeated=4,stylename=widthshort))
    table.addElement(odf.table.TableColumn(numbercolumnsrepeated=3,stylename=widthwide))
    
    f = open('/etc/passwd')
    for line in f:
        rec = line.strip().split(":")
        tr = odf.table.TableRow()
        table.addElement(tr)
        for val in rec:
            tc = odf.table.TableCell()
            tr.addElement(tc)
            p = odf.text.P(stylename=tablecontents,text=val)
            tc.addElement(p)
    
    doc.spreadsheet.addElement(table)
    doc.save("odfpy_generated_directly.ods")

## ODS generated from template

def ods_generated_from_template():
    pass
    
    
############################################
odt_generated_directly()
odt_generated_from_template()
ods_generated_directly()
ods_generated_from_template()
