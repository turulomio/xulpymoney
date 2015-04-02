
#!/usr/bin/python2
# -*- coding: utf-8 -*-


## ODT generated directly
import odf.opendocument
import odf.style
import odf.text
import odf.table
import odf.draw
#from odf.opendocument import OpenDocumentText
#from odf.style import Style, TextProperties
#from odf.text import H, P, Span

textdoc = odf.opendocument.OpenDocumentText()
# Styles
s = textdoc.styles
h1style = odf.style.Style(name="Heading 1", family="paragraph")
h1style.addElement(odf.style.TextProperties(attributes={'fontsize':"24pt",'fontweight':"bold" }))
s.addElement(h1style)

tablecontents = odf.style.Style(name="Table Contents", family="paragraph")
tablecontents.addElement(odf.style.ParagraphProperties(numberlines="false", linenumber="0"))
textdoc.styles.addElement(tablecontents)

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




# Text
h=odf.text.H(outlinelevel=1, stylename=h1style, text="My first text")
textdoc.text.addElement(h)
p = odf.text.P(text="Hello world. ")
boldpart = odf.text.Span(stylename="Bold",text="This part is bold. ")
p.addElement(boldpart)
p.addText("This is after bold.")
textdoc.text.addElement(p)

table = odf.table.Table()
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

textdoc.text.addElement(table)


###Generating images
textdoc.text.addElement(odf.text.H(outlinelevel=1,text='Generating An Image', stylename=h1style))
p = odf.text.P()

href = textdoc.addPicture("../images/spain.gif")
f = odf.draw.Frame(name="graphics1", anchortype="character") #, width="2cm", height="2cm", zindex="0")
p.addElement(f)
img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
f.addElement(img)
textdoc.text.addElement(p)


textdoc.save("odfpy_generated_directly.odt")









##ODT generated from template









## ODS generated directly


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
