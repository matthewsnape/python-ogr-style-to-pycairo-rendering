import cairo
import math

canvaswidth = 1000
canvasheight = 1000
dpi = 256


surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,canvaswidth,canvasheight)
#surface =  cairo.PDFSurface("a.pdd",canvaswidth,canvasheight)
context = cairo.Context(surface)


examples= """PEN(c:#FF0000FF,w:0.01px)
PEN(c:#FF0000FF,w:5px,p:"4px 5px",id:"ogr-pen-0"")
BRUSH(fc:#0000FF);LINE(c:#000000)
SYMBOL(c:#00FF00,id:"points.sym-45,ogr-sym-7")
LABEL(f:"Times New Roman",s:12pt,t:{text_string})"""

examples = examples.split("\n")

a = examples[0]
import re

#a = a.replace(" ","")  
pattern = "(PEN|BRUSH|SYMBOL|LABEL)\((.*)\)"
(tool,params) = re.search(pattern, a).groups()


def parseParams(params):
    params = params.split(",")
    params = [a.split(":") for a in params]
    return dict(params)
    
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))


def unitconversion(inunit,dpi):
    (width,units) = re.search("(\d*)(g|px|pt|mm|cm|in)", inunit).groups()
            
    dpi = 256
    pixelwidthmm = 25.4//dpi
            
    conversions = { 'pt':0.3527, 'mm':1, 'cm':10, 'in':25.4} #no idea what a g is TODO: find out!
    if units == 'px':
        return float(width)
    else:
        return float((conversions[units]*width)/pixelwidthmm)

def setPen(pen):
    if not pen.startswith("ogr"):
        test = re.match(".*-(\d*)", pen)
        if test:
            pen = 'ogr-pen-' + test.group(1)
        
        
    if pen =='ogr-pen-0': 
    #solid (the default when no id is provided)
        a=1

    elif pen =='ogr-pen-1': 
    #null pen (invisible)
        context.set_source_rgb(0)

    elif pen =='ogr-pen-2': 
    #dash
        context.set_dash([3,3])

    elif pen =='ogr-pen-3': 
    #short-dash
        context.set_dash([2,2])

    elif pen =='ogr-pen-4': 
    #long-dash
        context.set_dash([5,5])

    elif pen =='ogr-pen-5': 
    #dot line
        context.set_dash([1,2])

    elif pen =='ogr-pen-6': 
    #dash-dot line
        context.set_dash([3,2,1,2])

    elif pen =='ogr-pen-7': 
    #dash-dot-dot line
        context.set_dash([3,2,1,2,1])

    elif pen =='ogr-pen-8': 
    #alternate-line (sets every other pixel)
        context.set_dash([1,1])
        
    else:
        return False

params = parseParams(params)    
currentcolor = (0,0,0,1.0)
if tool == "PEN":
    
    # Cairo tool line_to
    
    #set defaults
    context.set_source_rgb(0,0,0)
    context.set_line_width(1)
    
    
    for param in params:
        option = params[param]
        
        # stroke color - c:#FF0000
        if param == "c":
            rgba = hex_to_rgb(option)
            
            # set default alpha if missing
            if len(rgba) == 3:
                rgba.append(1)
            
            context.set_source_rgba(*rgba)
            
            #set the alpha if one is defined c:#FF0000FF
            if len(rgba) ==4:
                p=1
                
                #context.paint_with_alpha(255//rgba[3])
                

        # stroke width - w:5px
        if param=="w":
            px = unitconversion(option,dpi)
            context.set_line_width(px)
            
            
        #set dash patter p:"4px 5px"
        if param=="p":
            option = option.replace('"',"")
            option = re.split("\s",option)
            option = [unitconversion(a,dpi) for a in option]
            context.set_dash(option)
            
        
        #set pen by id d:"mapinfo-5,ogr-pen-7"
        if param=='id':
            option = option.replace('"',"")
            option = re.split("\s",option)
            
            for op in option:
                if setPen(op) != False:
                    break
                    




from osgeo import ogr
ds = ogr.Open("C:/Documents and Settings/Matt/pywktstyle/test data/magntrails.shp")
lyr = ds.GetLayer("magntrails")

extents = lyr.GetExtent()
width = extents[1] - extents[0]
height = extents[3] - extents[2]
minx = extents[0]
maxy = extents[3]

scaler = max(canvaswidth,canvasheight)/max(width,height)

print extents, scaler

slip = []

def plotLineString(tgeometry):
    count = tgeometry.GetPointCount()
    
    x = (tgeometry.GetPoint(0)[0] - minx) * scaler
    y = (maxy - tgeometry.GetPoint(1)[1] ) * scaler
    
    context.new_path()
    context.move_to ((tgeometry.GetPoint(0)[0] - minx) * scaler,(maxy - tgeometry.GetPoint(0)[1] ) * scaler)

    for pointn in range(1,count):
        x = (tgeometry.GetPoint(pointn)[0] - minx) * scaler
        y = (maxy - tgeometry.GetPoint(pointn)[1] ) * scaler
        context.line_to (x,y)
   

    context.stroke ()
    context.close_path ()
    

for f in lyr:
    geometry = f.GetGeometryRef()
    type = geometry.GetGeometryType()
    
    
    #multilinestring
    if type == 5:
        for geomn in range(0,geometry.GetGeometryCount()):

            plotLineString(geometry.GetGeometryRef(geomn))
         
    #Linestring
    if type == 2:

        plotLineString(geometry)

     
   

surface.write_to_png ("example.png") # Output to PNG
    
