import cairo

width = 255
height = 255

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
context = cairo.Context(surface)

examples= """PEN(c:#FF0000,w:5px)
BRUSH(fc:#0000FF);LINE(c:#000000)
SYMBOL(c:#00FF00,id:"points.sym-45,ogr-sym-7")
LABEL(f:"Times New Roman",s:12pt,t:{text_string})"""

examples = examples.split("\n")

a = examples[0]
import re

a = a.replace(" ","")  
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

params = parseParams(params)    

if tool == "PEN":
	
	# Cairo tool line_to
	
	for param in params:
		option = params[param]
		
		# stroke color
		if param == "c":
			rgb = hex_to_rgb(option)
			context.set_source_rgb(*rgb)
			
		# stroke width
		if param=="w":
			(width,units) = re.search("(\d*)(g|px|pt|mm|cm|in)", option).groups()
			
			dpi = 256
			pixelwidthmm = 25.4//dpi
			
			conversions = { 'pt':0.3527, 'mm':1, 'cm':10, 'in':25.4} #no idea what a g is TODO: find out!
			
			if units in conversions:
				px = (conversions[units]*width)/pixelwidthmm
			if units == 'px':
				px = width
			
			context.set_line_width(float(px))
			
			
			
	
	
	
