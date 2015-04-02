#!/usr/bin/python3
from ezodf import *



odt = newdoc(doctype='odt', filename='text.odt')


odt.meta['generator']='Xulpymoney'
odt.meta['description']='Prueba con ezodf desde python'
odt.meta['title']='Título de Mariano'
odt.meta['creator']='Mariano Muñoz'
odt.meta['initial-creator']='Mariano Muñoz'


odt.body += Heading("Chapter 1")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")
odt.body += Paragraph("This is a paragraph.")

odt.body += Heading("Chapter 3",2)

odt.body += Heading("Chapter 3")

odt.body += SoftPageBreak()

odt.body += Heading("Chapter 3",3)
odt.body += ezlist(['Point 1', 'Point 2', 'Point 3'])


odt.body += Heading("Table",1)
t=Table('Table 1', (5,5))
t.set_cell((1,2),Cell("Hola"))
odt.body += t

odt.save()



ods = newdoc(doctype='ods', filename='spreadsheet.ods')
sheet = Sheet('SHEET', size=(10, 10))
ods.sheets += sheet
sheet['A1'].set_value("cell with text")
sheet['B2'].set_value(3.141592)
sheet['C3'].set_value(100, currency='USD')
sheet['D4'].formula = "of:=SUM([.B2];[.C3])"
pi = sheet[1, 1].value
ods.save()
