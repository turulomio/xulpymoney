#!/usr/bin/python3

## ODT generated directly
import odf.opendocument
import odf.style
import odf.text
import odf.table
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

textdoc.save("odfpy_generated_directly.odt")


##ODT generated from template


## ODS generated directly

## ODS generated from template
