from PyQt5.QtCore import *
import odf
import odf.opendocument
import odf.style
import odf.text
import odf.table
import odf.draw
import odf.meta
import odf.dc
import os
from wdgTotal import *
from wdgInvestments import *
from wdgInvestmentClasses import *
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
                
        #Pagebreak styles horizontal y vertical        
        s = odf.style.Style(name="PH", family="paragraph",  parentstylename="Standard", masterpagename="Landscape")
        s.addElement(odf.style.ParagraphProperties(pagenumber="auto"))
        self.doc.styles.addElement(s)
        s = odf.style.Style(name="PV", family="paragraph",  parentstylename="Standard", masterpagename="Standard")
        s.addElement(odf.style.ParagraphProperties(pagenumber="auto"))
        self.doc.styles.addElement(s)
        
        
            
        self.seqTables=0#Sequence of tables
        
    def emptyParagraph(self, style="Standard", number=1):
        for i in range(number):
            self.simpleParagraph("",style)
            
    def simpleParagraph(self, text, style="Standard"):
        p=odf.text.P(stylename=style, text=text)
        self.doc.text.addElement(p)
        
    def header(self, text, level):
        h=odf.text.H(outlinelevel=level, stylename="Heading {}".format(level), text=text)
        self.doc.text.addElement(h)
        
        
        
    def table(self, header, orientation,  data, sizes, font):
        """Headerl text
        Data: data
        sizes: arr with column widths in cm
        size=font size"""  
    
        self.seqTables=self.seqTables+1
        tablesize=sum(sizes)
        
        s=odf.style.Style(name="Tabla{}".format(self.seqTables))
        s.addElement(odf.style.TableProperties(width="{}cm".format(tablesize), align="center"))
        self.doc.automaticstyles.addElement(s)
        
        #Column sizes
        for i, size in enumerate(sizes):
            sc= odf.style.Style(name="Tabla{}.{}".format(self.seqTables, chr(65+i)), family="table-column")
            sc.addElement(odf.style.TableColumnProperties(columnwidth="{}cm".format(sizes[i])))
            self.doc.automaticstyles.addElement(sc)
        
        #Cell header style
        sch=odf.style.Style(name="Tabla{}.HeaderCell".format(self.seqTables, chr(65), 1), family="table-cell")
        sch.addElement(odf.style.TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)        
        
        #Cell normal
        sch=odf.style.Style(name="Tabla{}.Cell".format(self.seqTables), family="table-cell")
        sch.addElement(odf.style.TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)
        
        
        #TAble contents style
        
        s= odf.style.Style(name="Tabla{}.Heading{}".format(self.seqTables, font), family="paragraph",parentstylename='Table Heading' )
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(odf.style.ParagraphProperties(attributes={'textalign':'center', }))
        self.doc.styles.addElement(s)
        
        s = odf.style.Style(name="Tabla{}.TableContents{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        self.doc.styles.addElement(s)
        
        s = odf.style.Style(name="Tabla{}.TableContentsRight{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(odf.style.ParagraphProperties(attributes={'textalign':'end', }))
        self.doc.styles.addElement(s)
        
        
        
        
        #Table header style
        s = odf.style.Style(name="Tabla{}.HeaderCell{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font+1),'fontweight':"bold" }))
        self.doc.styles.addElement(s)
        
        
    
        #Table columns
        table = odf.table.Table(stylename="Tabla{}".format(self.seqTables))
        for i, head in enumerate(header):
            table.addElement(odf.table.TableColumn(stylename="Tabla{}.{}".format(self.seqTables, chr(65+i))))  
            
            
            
        #Header rows
        headerrow=odf.table.TableHeaderRows()
        tablerow=odf.table.TableRow()
        headerrow.addElement(tablerow)
        for i, head in enumerate(header):
            p=odf.text.P(stylename="Tabla{}.Heading{}".format(self.seqTables, font), text=head)
            tablecell=odf.table.TableCell(stylename="Tabla{}.HeaderCell{}".format(self.seqTables, font))
            tablecell.addElement(p)
            tablerow.addElement(tablecell)
        table.addElement(headerrow)
            
        #Data rows
        for row in data:
            tr = odf.table.TableRow()
            table.addElement(tr)
            for i, col in enumerate(row):
                tc = odf.table.TableCell(stylename="Tabla{}.Cell".format(self.seqTables))
                tr.addElement(tc)
                
                #Parses orientation
                if orientation[i]=="<":
                    p = odf.text.P(stylename="Tabla{}.TableContents{}".format(self.seqTables, font))
                elif orientation[i]==">":
                    p = odf.text.P(stylename="Tabla{}.TableContentsRight{}".format(self.seqTables, font))
                
                #Colorize numbers less than zero
                try:#Formato 23 €
                    if float(col.split(" ")[0])<0:
                        s=odf.text.Span(text=col, stylename="Rojo")
                    else:
                        s=odf.text.Span(text=col)
                except:
                    s=odf.text.Span(text=col)                    
                p.addElement(s)
                
                tc.addElement(p)
        
        self.doc.text.addElement(table)
        
    def image(self, filename, width, height):
        p = odf.text.P(stylename="Illustration")
        href = self.doc.addPicture(filename)
        f = odf.draw.Frame(name="filename", anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
        p.addElement(f)
        img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
        f.addElement(img)
        self.doc.text.addElement(p)

    def pageBreak(self,  horizontal=False):    
        p=odf.text.P(stylename="PageBreak")#Is an automatic style
        self.doc.text.addElement(p)
        if horizontal==True:
            p=odf.text.P(stylename="PH")
        else:
            p=odf.text.P(stylename="PV")
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
        self.dir=None#Directory in tmp
        
    def generate(self):
        self.dir='/tmp/AssetsReport-{}'.format(datetime.datetime.now())
        os.makedirs(self.dir)
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
        c=self.mem.localcurrency.string
        ## About
        self.header(self.tr("About Xulpymoney"), 1)
        self.header(self.tr("About this report"), 2)
        self.pageBreak()
        ## Assets
        self.header(self.tr("Assets"), 1)
        self.simpleParagraph(self.tr("The total assets of the user is {}.").format(c(self.vTotal)))
        if self.vTotalLastYear!=0:
            moreorless="more"
            if self.vTotal-self.vTotalLastYear<0:
                moreorless="less"
            self.simpleParagraph(self.tr("It's a {} {} of the total assets at the end of the last year.").format(tpc(100*(self.vTotal-self.vTotalLastYear)/self.vTotalLastYear), moreorless))
        
        ### Assets by bank
        self.header(self.tr("Assets by bank"), 2)
        data=[]
        self.mem.data.banks_active.order_by_name()
        sumbalances=0
        for bank in self.mem.data.banks_active.arr:
            balance=bank.balance(self.mem.data.accounts_active, self.mem.data.investments_active)
            sumbalances=sumbalances+balance
            data.append((bank.name, c(balance)))
        self.table( [self.tr("Bank"), self.tr("Balance")], ["<", ">"], data, [3, 2], 12)       
        self.simpleParagraph(self.tr("Sum of all bank balances is {}").format(c(sumbalances)))
        
        self.pageBreak(True)
        ### Assests current year
        self.header(self.tr("Assets current year evolution"), 2)
        
        setData=TotalYear(self.mem, datetime.date.today().year)
        columns=[]
        columns.append([self.tr("Incomes"), self.tr("Gains"), self.tr("Dividends"), self.tr("Expenses"), self.tr("I+G+D-E"), "",  self.tr("Accounts"), self.tr("Investments"), self.tr("Total"),"",  self.tr("Monthly difference"), "",  self.tr("% current year")])
        self.simpleParagraph(self.tr("Assets Balance at {0}-12-31 is {1}".format(setData.year-1, self.mem.localcurrency.string(setData.total_last_year))))
        for i, m in enumerate(setData.arr):
            if m.year<datetime.date.today().year or (m.year==datetime.date.today().year and m.month<=datetime.date.today().month):
                columns.append([c(m.incomes()), c(m.gains()), c(m.dividends()), c(m.expenses()), c(m.i_d_g_e()), "", c(m.total_accounts()), c(m.total_investments()), c(m.total()),"",  c(setData.difference_with_previous_month(m)),"",  tpc(setData.assets_percentage_in_month(m.month))])
            else:
                columns.append(["","","","","","","","","", "", "", "", ""])
        columns.append([c(setData.incomes()), c(setData.gains()), c(setData.dividends()), c(setData.expenses()), c(setData.i_d_g_e()), "", "", "", "", "", c(setData.difference_with_previous_year()), "", tpc(setData.assets_percentage_in_month(12))]) 
        data=zip(*columns)
        
        self.table(   [self.tr("Concept"), self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")], 
                            ["<", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">"], data, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 7)       
                
        ## Target
        target=AnnualTarget(self.mem).init__from_db(datetime.date.today().year)
        self.simpleParagraph(self.tr("The investment system has established a {} year target.").format(tpc(target.percentage))+" " +
                self.tr("With this target you will gain {} at the end of the year.").format(c(target.annual_balance())) +" " +
                self.tr("Up to date you have got  {} (gains + dividends) what represents a {} of the target.").format(c(setData.dividends()+setData.gains()), tpc((setData.gains()+setData.dividends())*100/target.annual_balance())))
        self.pageBreak()
        ### Assets evolution graphic
        self.header(self.tr("Assets graphical evolution"), 2)
        
        w=wdgTotal(self.mem)
        w.load_graphic("{}/wdgTotal.png".format(self.dir))
        self.image("{}/wdgTotal.png".format(self.dir), 15, 10)
        self.simpleParagraph("")
        
        self.pageBreak()
        
        
        ## Accounts
        self.header(self.tr("Current Accounts"), 1)
        data=[]
        self.mem.data.accounts_active.order_by_name()
        for account in self.mem.data.accounts_active.arr:
            data.append((account.name, account.eb.name, c(account.balance())))
        self.table( [self.tr("Account"), self.tr("Bank"),  self.tr("Balance")], ["<","<",  ">"], data, [5,5, 2], 11)       
        
        self.simpleParagraph(self.tr("Sum of all account balances is {}").format(c(self.mem.data.accounts_active.balance())))

        
        self.pageBreak(True)
        
        ## Investments
        self.header(self.tr("Current investments"), 1)
        
        self.header(self.tr("Investments list"), 2)
        self.simpleParagraph(self.tr("Next list is sorted by the distance in percent to the selling point."))
        sumpendiente=0
        suminvertido=0
        sumpositivos=0
        sumnegativos=0
        data=[]
        self.mem.data.investments_active.order_by_percentage_sellingpoint()
        for inv in self.mem.data.investments_active.arr:            
            suminvertido=suminvertido+inv.invertido()
            pendiente=inv.pendiente()
            if pendiente>0:
                sumpositivos=sumpositivos+pendiente
            else:
                sumnegativos=sumnegativos+pendiente
            suminvertido=suminvertido+inv.tpc_invertido()
            arr=("{0} ({1})".format(inv.name, inv.account.name), c(inv.balance()), c(pendiente), tpc(inv.tpc_invertido()), tpc(inv.tpc_venta()))
            data.append(arr)

        self.table( [self.tr("Investment"), self.tr("Balance"), self.tr("Gains"), self.tr("% Invested"), self.tr("% Selling point")], ["<", ">", ">", ">", ">"], data, [3, 1, 1, 1,1], 9)       
        
        sumpendiente=sumpositivos+sumnegativos
        if suminvertido!=0:
            self.simpleParagraph(self.tr("Sum of all invested assets is {}.").format(c(suminvertido)))
            self.simpleParagraph(self.tr("Investment gains (positive minus negative results): {} - {} are {}, what represents a {} of total assets.").format( c(sumpositivos),  c(-sumnegativos),  c(sumpendiente), tpc(100*sumpendiente/suminvertido) ))
            self.simpleParagraph(self.tr(" Assets average age: {}").format(  days_to_year_month(self.mem.data.investments_active.average_age())))
        else:
            self.simpleParagraph(self.tr("There aren't invested assets"))
        self.pageBreak()
        ### Graphics wdgInvestments clases
        w=wdgInvestmentClasses(self.mem)
        
        wit=15
        self.header(self.tr("Investments group by variable percentage"), 2)
        w.canvasTPC.savePixmap("{}/wdgInvestmentsClasses_canvasTPC.png".format(self.dir))
        wi, he=w.canvasTPC.savePixmapLegend("{}/wdgInvestmentsClasses_canvasTPC_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasTPC.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasTPC_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("")
        self.pageBreak()
        
        self.header(self.tr("Investments group by investment type"), 2)
        w.canvasTipo.savePixmap("{}/wdgInvestmentsClasses_canvasTipo.png".format(self.dir))
        wi, he=w.canvasTipo.savePixmapLegend("{}/wdgInvestmentsClasses_canvasTipo_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasTipo.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasTipo_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("") 
        self.pageBreak()
        
        self.header(self.tr("Investments group by leverage"), 2)
        w.canvasApalancado.savePixmap("{}/wdgInvestmentsClasses_canvasApalancado.png".format(self.dir))
        wi, he=w.canvasApalancado.savePixmapLegend("{}/wdgInvestmentsClasses_canvasApalancado_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasApalancado.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasApalancado_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by investment product"), 2)
        w.canvasProduct.savePixmap("{}/wdgInvestmentsClasses_canvasProduct.png".format(self.dir))
        wi, he=w.canvasProduct.savePixmapLegend("{}/wdgInvestmentsClasses_canvasProduct_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasProduct.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasProduct_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by country"), 2)
        w.canvasCountry.savePixmap("{}/wdgInvestmentsClasses_canvasCountry.png".format(self.dir))
        wi, he=w.canvasCountry.savePixmapLegend("{}/wdgInvestmentsClasses_canvasCountry_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasCountry.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasCountry_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by Call/Put/Inline"), 2)
        w.canvasPCI.savePixmap("{}/wdgInvestmentsClasses_canvasPCI.png".format(self.dir))
        wi, he=w.canvasPCI.savePixmapLegend("{}/wdgInvestmentsClasses_canvasPCI_legend.png".format(self.dir))
        self.image("{}/wdgInvestmentsClasses_canvasPCI.png".format(self.dir), 15, 10)
        self.image("{}/wdgInvestmentsClasses_canvasPCI_legend.png".format(self.dir), wit, he)
        self.simpleParagraph("")
        
        
    def metadata(self):
        self.doc.meta.addElement(odf.dc.Title(text=self.tr("Assets report")))
        self.doc.meta.addElement(odf.dc.Description(text=self.tr("This is an automatic generated report from Xulpymoney")))
        creator="Xulpymoney-{}".format(version)
        self.doc.meta.addElement(odf.meta.InitialCreator(text=creator))
        self.doc.meta.addElement(odf.dc.Creator(text=creator))
