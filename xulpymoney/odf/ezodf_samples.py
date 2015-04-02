#!/usr/bin/python3
import ezodf

def odt_generated_directly():
    ##ODT generated directly
    odt = ezodf.newdoc(doctype='odt', filename='ezodf_generated_directly.odt')
    
    
    odt.meta['generator']='Xulpymoney'
    odt.meta['description']='Prueba con ezodf desde python'
    odt.meta['title']='Título de Mariano'
    odt.meta['creator']='Mariano Muñoz'
    odt.meta['initial-creator']='Mariano Muñoz'
    
    
    odt.body += ezodf.Heading("Chapter 1")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    odt.body += ezodf.Paragraph("This is a paragraph.")
    
    odt.body += ezodf.Heading("Chapter 1.1",2)
    
    odt.body += ezodf.Heading("Chapter 3")
    
    odt.body += ezodf.SoftPageBreak()
    
    odt.body += ezodf.Heading("Chapter 3",3)
    odt.body += ezodf.ezlist(['Point 1', 'Point 2', 'Point 3'])
    
    
    odt.body += ezodf.Heading("Table",1)
    t=ezodf.Table('Table 1', (5,5))
    t.set_cell((1,2),ezodf.Cell("Hola"))
    odt.body += t
    
    odt.save()


def odt_generated_from_template():
    ##ODT generated from template
    pass

def ods_generated_directly():
    ## ODS generated directly
    ods = ezodf.newdoc(doctype='ods', filename='ezodf_generated_directly.ods')
    sheet = ezodf.Sheet('SHEET', size=(10, 10))
    ods.sheets += sheet
    sheet['A1'].set_value("cell with text")
    sheet['B2'].set_value(3.141592)
    sheet['C3'].set_value(100, currency='USD')
    sheet['D4'].formula = "of:=SUM([.B2];[.C3])"
    pi = sheet[1, 1].value
    ods.save()

## ODS generated from template
def ods_generated_from_template():
    pass
############################################
odt_generated_directly()
odt_generated_from_template()
ods_generated_directly()
ods_generated_from_template()
