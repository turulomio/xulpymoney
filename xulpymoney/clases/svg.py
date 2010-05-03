# -*- coding: UTF-8 -*-
import math
from core import *
#def piechart(sectors):
#    """Recibe un arrays con dos columans la primera la descripción y la segunda el valor"""
##    s = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
##    s=s+'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n'
##    s=s+'"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
#    s='<svg flex="2" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
#    svgfile = 'salida.svg'
#    #sectors = [190.0,9.0,90.0,90.0]
#    mylog(str(sectors))
#    total = 0
#    i = 0
#    seg = 0
#    radius = 150
#    startx = 200   # The screen x-origin: center of pie chart
#    starty = 200   # The screen y-origin: center of pie chart
#    lastx = radius # Starting coordinates of 
#    lasty = 0      # the first arc
#    ykey = 25
#    
#    # If you don't like my colors -- here's where to fix the ugliness. 
#    # If you need more than 9, add as many as you like
#    colors = ['red','blue','yellow','magenta','orange','slateblue','slategrey','greenyellow','wheat']
#    bordercolor = 'black'
#    for n in sectors:
#        total = total + n[1]  # we have to do this ahead, since we need the total for the next for loop
#    
#    for n in sectors:
#        arc = "0"                   # default is to draw short arc (< 180 degrees)
#        seg = n[1]/total * 360 + seg   # this angle will be current plus all previous
#        if ((n[1]/total * 360) > 180): # just in case this piece is > 180 degrees
#            arc = "1"
#        radseg = math.radians(seg)  # we need to convert to radians for cosine, sine functions
#        nextx = int(math.cos(radseg) * radius)
#        nexty = int(math.sin(radseg) * radius)
#    
#    # The weirdly placed minus signs [eg, (-(lasty))] are due to the fact that
#    # our calculations are for a graph with positive Y values going up, but on the
#    # screen positive Y values go down.
#    
#        s=s+'<path d="M '+str(startx)+','+str(starty) + ' l '+str(lastx)+','+str(-(lasty))+' a' + str(radius) + ',' + str(radius) + ' 0 ' + arc + ',0 '+str(nextx - lastx)+','+str(-(nexty - lasty))+ ' z" \n'
#        s=s+'fill="'+colors[i]+'" stroke="' + bordercolor + '" stroke-width="2" stroke-linejoin="round" />\n'
#    # We are writing the XML commands one segment at a time, so we abandon old points
#    # we don't need anymore, and nextx becomes lastx for the next segment
#        s=s+'<rect x="375" y="'+ str(ykey) + '" width="40" height="30" fill="'+colors[i] + '" stroke="black" stroke-width="1"/><text x="425" y="'+str(ykey+20)+'"	style="font-family:verdana, arial, sans-serif;			font-size: 14;			fill: black;			stroke: none">'+n[0]+ ". " +  str(n[1])+ " €. (" +  str(round(n[1]*100/total, 2))+' %)</text>\n'
#        ykey = ykey + 35
#        lastx = nextx
#        lasty = nexty
#        i += 1        
#    s=s+'<text x="425" y="'+str(ykey+20)+'"	style="font-family:verdana, arial, sans-serif;			font-size: 16;			fill: black;			stroke: none">TOTAL: ' +  str(round(total, 2))+  €.</text>\n'
#    s=s+'</svg>'        # End tag for the SVG file
#    return s
