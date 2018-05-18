#-*- coding:utf-8 -*-

import os
import sys

import re
import collections
import math
from xml.etree import ElementTree as ET
from ctypes import *
import copy
import argparse

# 追加でｲﾝｽﾄｰﾙが必要なﾓｼﾞｭｰﾙ
#  pip install <ﾓｼﾞｭｰﾙ名> でｲﾝｽﾄｰﾙが必要
#   PIL  : pillow   ->> pip install pillow
#   numpy: numpy
from PIL import Image, ImageDraw
import numpy as np

import colorCode

user32 = windll.user32

MB_ICONSTOP	= 0x10
MB_ICONQUESTION = 0x20
MB_ICONWARNING = 0x30
MB_ICONINFORMATION = 0x40

parser = argparse.ArgumentParser(
		prog="ipcConv",
		usage="ipcConv.py <option> ipc_file",
		description='This script is ...'
		)

parser.add_argument('ipc_file',	action='store', nargs=None, const=None,default=None,	type=str,	choices=None,help='IPC-2581 filename',metavar=None)

parser.add_argument('-o','--output',	action='store', nargs='?', const=None,default=None,	type=str,	choices=None,help='output filename (default:stdout)',metavar=None)
parser.add_argument('-t','--type',		action='store', nargs='?', const=None,default=None,	type=str,	choices=None,help='output type(default:None[parts, via]')
parser.add_argument('-l','--layer',		action='store', nargs='?', const=None,default=0,	type=int,	choices=None,help='layer number(0:all,1:bottom) default:0',metavar=None)
parser.add_argument('-n','--name',		action='append',nargs='?', const=None,default=None,	type=str,	choices=None,help='object name(default:None)')
parser.add_argument('-p','--partname',	action='store',	nargs='?', const=None,default=None, type=str,	choices=None,help='set partName(default:None)')
parser.add_argument('-x','--offsetx',	action='store', nargs='?', const=None,default='0.0',type=str,	choices=None,help='offset x pos(default:0.0) ex. +1.2')
parser.add_argument('-y','--offsety',	action='store', nargs='?', const=None,default='0.0',type=str,	choices=None,help='offset y pos(default:0.0) ex. -0.2')
parser.add_argument('-z','--offsetz',	action='store', nargs='?', const=None,default='0.0',type=str,	choices=None,help='offset z pos(default:0.0)' )
parser.add_argument('-d','--debug',		action='store_true', default=False,	help='debug mode (default:False)')

###########################################################
__DEBUG__ = False

# xml の namespace 部を '' で置換するための正規表現ﾃﾞｰﾀ
#  XML に xmlns="http://webstds.ipc.org/2581" のﾈｰﾑｽﾍﾟｰｽが設定されているために
#  全てのﾀｸﾞに {http://webstds.ipc.org/2581}/<Tag名>  のようにﾈｰﾑｽﾍﾟｰｽが追加されている
#  処理しづらいので、{} 部分を置換するための定義
re_pat = re.compile('\{.*?\}')

# 層ﾃﾞｨｸｼｮﾅﾘ={'層名':Layer}
layers={}

# {'ﾚｲﾔｰｸﾞﾙｰﾌﾟ名':[ﾚｲﾔｰ,ﾚｲﾔｰ, ...]}
layer_group = collections.OrderedDict()		#※順番を規定したいので順番保持型のﾃﾞｨｸｼｮﾅﾘを使用
phy_net_group = {}	#{'PhyNet名':[NetPoint,NetPoint, ...]}

# 図形定義(EntryStandard)={'id':IPC_Shape}
entryStandard = {}

# {'Component名':IPCObject_Component}
# <Component refDes=""> refDesをComponent名
components = {}

# <Package> {'ﾊﾟｯｹｰｼﾞ名':IPCObject_Package}
# Component のPackageRef で参照される
packages = {}

#色定義 {'ﾚｲﾔｰ名':IPCObject_Color, ...}
colors = {}

_holeObj_list = []


# XML ElementTree root
root = None

dotSize = 0.0423	#1ﾄﾞｯﾄのｻｲｽﾞ(mm)
layerThick = 0.067	#1層の厚み(mm)

nexim_items=[	('Ref.',       ["",]),
				('Pos X',      ["",]),
				('Pos Y',      ["",]),
				('Pos Z',      ["",]),
				('Rotation',   ["",]),
				('Part Number',["",]),
				('Skip',			['No', ]),
				('Board',			['1',  ]),
				('Gluing',			['Yes',]),
				('Carry Mode',		['Arc',]),
				('Allocate To M6',	['No', ]),
				('Adjoining Placement Direction',['None',]),
				('Adjoining Placement Distance', ['0.5',]),
				('Adjoining Placement Height',	 ['2.5',]),
				('Adjoining Placement Z',		 ['0',]),
				('Adjoining Placement Speed',	 ['0',]),
				('Adjoining Placement Offset X', ['0',]),
				('Adjoining Placement Offset Y', ['0',])]

#出力座標のｵﾌｾｯﾄ値(-offsetx, --offsety, --offsetz で指定)
_x_offset = 0.0
_y_offset = 0.0
_z_offset = 0.0

__VERSION__ = '1.0.0'

##########################################################################################

def rot(deg):
	u'''
		座標を角度変換するための行列ﾃﾞｰﾀ作成
		deg: 角度
	'''
	r = np.radians(deg)
	obj = np.matrix( ((np.cos(r),-np.sin(r)),(np.sin(r),np.cos(r))) )
	return obj


class IPCObject(object):
	def __init__(self, name,attrib=None):
		self.attrib_ = attrib
		self.name_ = name
		if attrib != None:
			if attrib.has_key('name') == True:
				self.name_ = attrib['name']
	@property
	def name(self):
		return self.name_
	@property
	def attribute(self):
		return self.attrib_

## IPC Shape
class IPC_RectRound(IPCObject):
	def __init__(self, attrib):
		super(IPC_RectRound,self).__init__(attrib['id'],attrib)

	def polygon(self, centerPos):
		w = float(self.attribute['width']) / 2.0
		h = float(self.attribute['height']) / 2.0
		x = float(centerPos[0])
		y = float(centerPos[1])

		x1 = int( (x-w)/dotSize )
		x2 = int( (x+w)/dotSize )
		y1 = int( (y-h)/dotSize )
		y2 = int( (y+h)/dotSize )

		return ('RectRound',[(x1,y1),(x2,y1),(x2,y2),(x1,y2)])

class IPC_Circle(IPCObject):
	def __init__(self, attrib):
		super(IPC_Circle,self).__init__(attrib['id'],attrib)

	def polygon(self, centerPos):
		r = int( float( self.attribute['diameter'] ) / dotSize)
		x = int(float(centerPos[0])/dotSize)
		y = int(float(centerPos[1])/dotSize)
		return ('Circle',[(x,y),(r,r)])

### 色定義
class IPC_Color(IPCObject):
	def __init__(self,attrib):
		super(IPC_Color,self).__init__('Color')
		self.red_ = int(attrib['r'])
		self.green_ = int(attrib['g'])
		self.blue_ = int(attrib['b'])

	@property
	def rgb(self):
		return (self.red_,self.green_,self.blue_)


###
### 層内ｵﾌﾞｼﾞｪｸﾄ
###
##### ｷｬﾋﾞﾃｨ
class IPCObject_Cavity(IPCObject):
	def __init__(self, pos, attrib):
		super(IPCObject_Cavity,self).__init__('Cavity',attrib)
		self.pos_ = pos
		if attrib.has_key('x') == False:
			# x,y の属性が無いので始点をx,yとする
			self.attrib_['x'] = str(pos[0][0])
			self.attrib_['y'] = str(pos[0][1])

	def polygon(self):
		return ('Polygon',map(lambda arg: (int(arg[0]/dotSize),int(arg[1]/dotSize)), self.pos_))


### ﾎｰﾙ
class IPCObject_Hole(IPCObject):
	def __init__(self, net, attrib):
		super(IPCObject_Hole,self).__init__('Hole',attrib)
		self.net_ = net

	def polygon(self):
		shape_obj = entryStandard[self.attribute['id']]
		return shape_obj.polygon( (self.attribute['x'],self.attribute['y']) )

	def pos(self):
		return (self.attribute['x'],self.attribute['y'])

### ﾊﾟｯﾄﾞ
class IPCObject_Pad(IPCObject):
	def __init__(self, net, attrib):
		super(IPCObject_Pad,self).__init__('Pad',attrib)
		self.net_ = net

	def polygon(self):
		shape_obj = entryStandard[self.attribute['id']]
		ret = shape_obj.polygon( (self.attribute['x'],self.attribute['y']) )
		if self.attribute.has_key('rotation') == False:
			return ret
		else:
			#角度がある
			rr = rot(float( self.attribute['rotation']))
			pos = ret[1]	#ret[0]='RectRound' ret[1]=[(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
			if ret[0] == 'RectRound':
				cx = (pos[0][0] + pos[2][0]) / 2	#(x1+x2)/2
				cy = (pos[0][1] + pos[2][1]) / 2	#(y1+y2)/2
				r1 =  map(lambda arg:((arg[0]-cx,arg[1]-cy)),pos)	#中心を移動
				r2 =  map(lambda arg:(round(rr.dot(arg)[0,0],3),round(rr.dot(arg)[0,1],3)),r1)	#回転
				r3 =  map(lambda arg:((arg[0]+cx,arg[1]+cy)),r2)	#中心を戻す
				return (ret[0],r3)
			else:
				return ret


class IPCObject_Package(IPCObject):
	def __init__(self, polygon, attrib):
		super(IPCObject_Package,self).__init__('Package',attrib)
		self.polygon_ = polygon
		self.pad_list_ = []	

	def polygon(self, rotate='0.0'):
		if rotate == '0.0':
			return ('Polygon',self.polygon_)
		else:
			rr = rot(float(rotate))
			#poly=[]
			#for pos in self.polygon_:
			#	p = rr.dot(pos)
			#	poly.append( (round(p[0,0],3),round(p[0,1],3)) )
			#return poly
			return ('Polygon',map(lambda arg:(round(rr.dot(arg)[0,0],3),round(rr.dot(arg)[0,1],3)),self.polygon_))

	def set_land_pattern(self, pad_list):
		self.pad_list_ = pad_list

	def set_pin(self, attr_pin):
		self.attr_pin_ = attr_pin

class IPCObject_Component(IPCObject):
	def __init__(self, attrib):
		super(IPCObject_Component,self).__init__(attrib['refDes'],attrib)
		self.rotation_ = 0.0
		self.location_ = (0.0,0.0)
		self.pad_list_ = []

	def set_rotation(self, r):
		self.rotation_ = r
		self.attrib_['rotation'] = str(r)

	def set_location(self, pos):
		self.location_ = pos
		self.attrib_['x'] = str(pos[0])
		self.attrib_['y'] = str(pos[1])

	def add_pad(self, obj):
		self.pad_list_.append(obj)
	
	def set_polygon(self, pos):
		self.pos_ = pos

	def polygon(self):
		if packages.has_key(self.attribute['packageRef']) == True:
			package = packages[ self.attribute['packageRef'] ]

			pol = package.polygon(str(self.rotation_))
			pos = map(lambda arg:( int((self.location_[0]+arg[0])/dotSize), int((self.location_[1]+arg[1])/dotSize)),pol[1])
			return ('Polygon',pos)
		else:
			return ('None',[(0,0),(0,0),(0,0),(0,0)])
	@property
	def location(self):
		return self.location_
	@property
	def rotation(self):
		if self.attrib_.has_key('rotation'):
			return self.attrib_['rotation']
		else:
			return '0.0'
	@property
	def partName(self):
		return self.attrib_['part']
	@property
	def layerRef(self):
		return self.attrib_['layerRef']


class IPCObject_Logicalnet(IPCObject):
	def __init__(self, attrib):
		super(IPCObject_Logicalnet,self).__init__('LogicalNet',attrib)
		self.pin_ref_ = []

	def add_pin_ref(self, pinRef):
		'''
			pinRef(tuple): ('ｺﾝﾎﾟｰﾈﾝﾄ名',pin番号)
		'''
		self.pin_ref_.append(pinRef)

	def polygon(self):
		return ('None',[(0,0)])


class IPCObject_PhyNetPoint(IPCObject):
	def __init__(self, attrib):
		super(IPCObject_PhyNetPoint,self).__init__('PhyNetPoint',attrib)
		self.net_point_ = []	# [{PhyNetPoint Attrib},{}, ...]

	def add_net_point(self, net_point):
		self.net_point_.append(net_point)

	def polygon(self):
		return ('None',[(0,0)])

class IPCObject_Via(IPCObject):
	def __init__(self, attrib):
		super(IPCObject_Via,self).__init__('Via',attrib)
		self.location_ = (0,0)

	def polygon(self):
		shape_obj = entryStandard[self.attribute['id']]
		return shape_obj.polygon( (self.attribute['x'],self.attribute['y']) )


class IPCObject_Line(IPCObject):
	def __init__(self, pos, attrib=None):
		super(IPCObject_Line,self).__init__('Line',attrib)
		self.pos_ = pos

	def polygon(self):
		pos = map(lambda arg:( int((arg[0])/dotSize), int((arg[1])/dotSize)),self.pos_)
		return ('Line',pos)


class IPCObject_Polygon(IPCObject):
	def __init__(self, pos, attrib=None):
		super(IPCObject_Polygon,self).__init__('Polygon',attrib)
		self.pos_ = pos

	def polygon(self):
		pos = map(lambda arg:( int((arg[0])/dotSize), int((arg[1])/dotSize)),self.pos_)
		return ('Polygon',pos)


class IPCObject_Polyline(IPCObject):
	def __init__(self,pos, attrib=None):
		super(IPCObject_Polyline,self).__init__('Polyline',attrib)
		self.pos_ = pos

	def polygon(self):
		pos = map(lambda arg:( int((arg[0])/dotSize), int((arg[1])/dotSize)),self.pos_)
		return ('Polyline',pos)

### 層
class Layer(IPCObject):
	def __init__(self, attrib):
		super(Layer,self).__init__(attrib['name'], attrib)
		self.items_ = []	#層内ｵﾌﾞｼﾞｪｸﾄ
		#self.params_ = []
		self.thickness_ = 0.0

	@property
	def items(self):
		return self.items_

	@property
	def thickness(self):
		return self.thickness_

	@property
	def function(self):
		return self.attrib_['layerFunction']


class Layer_Cavity(Layer):
	def __init__(self, attrib):
		super(Layer_Cavity,self).__init__(attrib)


class Layer_Hole(Layer):
	def __init__(self, attrib):
		super(Layer_Hole,self).__init__(attrib)


###############################################################################

def create_object(objType, net,attr):
	if objType == 'Hole':
		obj = IPCObject_Hole(net,attr)
		_holeObj_list.append(obj)

	return obj


def create_shape(elem):
	u'''
		形状定義(EntryStandard)
	'''
	ch = elem.getchildren()
	tn = re.sub(re_pat,'',ch[0].tag)

	attr = elem.attrib
	attr.update(ch[0].attrib)

	if tn == 'RectRound':
		return IPC_RectRound(attr)
	elif tn == 'Circle':
		return IPC_Circle(attr)
	elif tn == 'Contour':
		pass
	else:
		print 'UnSupport:{0}'.format(tn)
		return None


def xml_entry_standard(elem):
	u'''
		<EntryStandard> ﾀｸﾞ処理
	'''
	for n,ee in enumerate(elem):
		if type(ee).__name__ == 'Element':
			tagName = re.sub(re_pat,'',ee.tag)
			if tagName == 'EntryStandard':
				entryStandard[ee.attrib['id']] = create_shape(ee)


def xml_entry_color(elem):
	u'''
		<EntryColor>ﾀｸﾞ処理
	'''
	for n,ee in enumerate(elem):
		if type(ee).__name__ == 'Element':
			tagName = re.sub(re_pat,'',ee.tag)
			if tagName == 'EntryColor':
				cl = ee.getchildren()
				for col in cl:
					# 色ｵﾌﾞｼﾞｪｸﾄを追加
					colors[ee.attrib['id']] = IPC_Color(col.attrib)
					#layers[ee.attrib['id']].params_.append( IPC_Color(col.attrib) )


def xml_content(elem):
	u'''
		<Content>処理
	'''
	for n, ee in enumerate(elem):
		if type(ee).__name__ == 'Element':
			#print '{0}:{1}={2}'.format(n,re.sub(re_pat,'',ee.tag),ee.attrib)
			tagName = re.sub(re_pat,'',ee.tag)

			if tagName == 'FunctionMode':
				pass
			elif tagName == 'StepRef':
				pass
			elif tagName == 'LayerRef':
				#layers[ee.attrib['name']] = Layer(ee.attrib['name'])
				pass
			elif tagName == 'BomRef':
				pass
			elif tagName == 'DictionaryStandard':
				xml_entry_standard( ee.getchildren() )
			elif tagName == 'DictionaryUser':
				pass
			elif tagName == 'DictionaryColor':
				xml_entry_color( ee.getchildren() )
			else:
				print 'Unsupport tag:{0}'.format(tagName)

def bom_item(elem):
	u'''
		<BomItem> ﾀｸﾞ処理
	'''
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'RefDes':
			pass
		elif tagName == 'Characteristics':
			pass
		else:
			print 'Unsupport tag:{0}'.format(tagName)


def xml_bom(elem):
	u'''
		<Bom> 処理
	'''
	for n,ee in enumerate(elem):
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'BomHeader':
			pass
		elif tagName == 'BomItem':
			bom_item( ee.getchildren() )
		else:
			print 'UnSupport tag:{0}'.format(tagName)


def xml_stuckup(elem, thick):
	u'''
		<Stuckup> ﾀｸﾞ処理
		層構造定義
	'''
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'StackupGroup':
			ch = ee.getchildren()
			#ｸﾞﾙｰﾌﾟ
			#layer_group.append( (ee.attrib['name'],[layers[ cc.attrib['layerOrGroupRef'] ] for cc in ch]) )
			layer_group[ee.attrib['name']] = [layers[ cc.attrib['layerOrGroupRef'] ] for cc in ch] 
			#層厚み
			for cc in ch:
				layers[ cc.attrib['layerOrGroupRef']].thickness_ = float(cc.attrib['thickness'])


def get_layer_list(fromLayerName, toLayerName):
	u'''
		ﾚｲﾔｰｸﾞﾙｰﾌﾟで fromLayerName～toLayerName までのﾚｲﾔｰをﾘｽﾄで取得
	'''
	layer_list = []

	lst = 0
	for groupName,layers in layer_group.iteritems():
		for layer in layers:
			if layer.name == fromLayerName:
				layer_list.append(layer)
				lst = 1

			elif layer.name == toLayerName:
				layer_list.append(layer)
				lst = 0

			else:
				if lst == 1:
					layer_list.append(layer)

		if toLayerName == fromLayerName:
			return layer_list

	return layer_list


def create_pad_stuck(elem, net=None):
	u'''
		elem: [<LayerPad> or <LayerHole>, ...]
	'''
	attr = {}
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'LayerPad':
			attr.update( {k:el.attrib[k] for el in ee.getchildren() for k in el.attrib} )
			if attr.has_key('diameter') == True:
				obj = create_object('Hole',net,attr)
				lst = get_layer_list(attr['fromLayer'],attr['toLayer'])

				#該当する全てのﾚｲﾔｰに追加する
				for layer in lst:
					layer.items_.append(obj)
			else:
				layers[ ee.attrib['layerRef'] ].items_.append( IPCObject_Pad(net,attr) )
			attr = {}

		elif tagName == 'LayerHole':
			attr = ee.attrib
			# <Span> の attrib を取り出して、<LayerHole> の attrib と繋げる
			attr.update( {k:el.attrib[k] for el in ee.getchildren() for k in el.attrib} )


def pos_polygon(elem):
	u'''
		elemの属性値、'x','y'を(x,y)のﾘｽﾄとする
	'''
	#[(x,y),(x,y), ...]
	#return [(float(el.attrib['x']),float(el.attrib['y'])) for el in elem.getchildren()]
	return [(float(el.attrib['x']),float(el.attrib['y'])) for el in elem.getchildren() if el.attrib.has_key('x') and el.attrib.has_key('y')]

def step_profile(elem):
	u'''
		<Profile> ﾀｸﾞ処理
		基板外形
		list[elem]: elem[0]= <Polygon>
		children(): <PolyStepSegment>
	'''
	## pos=[(x,y),(x,y), ...]
	pos = pos_polygon(elem[0])

def pin_num(pinStr):
	nn = re.split('\D*',pinStr)
	if len(nn) > 1:
		return int(nn[1])
	else:
		return int(nn[0])

def package_land_pattern(elem):
	u'''
		<Package>-<LandPattern> ﾀｸﾞ処理
	'''
	attrs = []
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Pad':
			attrs.append({k:el.attrib[k] for el in ee.getchildren() for k in el.attrib})

	#'pin'番号の小さい順に並べる
	#return sorted(attrs,key=lambda x:int(x['pin']))
	return sorted(attrs,key=lambda x:pin_num(x['pin']))


def step_package(elem, attrib):
	u'''
		<Package> ﾀｸﾞ処理
		list[elem]: elem[0]= <Outline> elem[1]= <LandPattern>
	'''
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Outline':
			ch = ee.getchildren()
			pol = pos_polygon(ch[0])	#ch[0]=<Polygon>
			#ch[1].attrib				#ch[1]=<LineDesc>
			package = IPCObject_Package(pol,attrib)
			pass
		elif tagName == 'LandPattern':
			package.set_land_pattern( package_land_pattern( ee.getchildren() ))
			pass
		elif tagName == 'Pin':
			attr = ee.attrib
			ch = ee.getchildren()
			if 'Contour' in ch[0].tag:
				pol = pos_polygon( ch[0].getchildren()[0] )
				attr.update({'Contour':pol})
			else:
				attr.update({k:el.attrib[k] for el in ch for k in el.attrib})

			package.set_pin(attr)

	packages[attrib['name']] = package

def step_component(elem, attrib):
	u'''
		<Component> ﾀｸﾞ処理
	'''
	component = IPCObject_Component(attrib)
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Xform':
			component.set_rotation( float(ee.attrib['rotation']) )
		elif tagName == 'Location':
			component.set_location( (float(ee.attrib['x']),float(ee.attrib['y'])) )

	#部品登録(名前、位置(Location))
	components[attrib['refDes']] = component

	#部品を層に登録
	layers[attrib['layerRef']].items_.append(component)

def step_logical_net(elem, attrib):
	u'''
		<LogicalNet> ﾀｸﾞ処理
	'''
	netObj = IPCObject_Logicalnet(attrib)

	for ee in elem:
		#netObj.add_pin_ref( (ee.attrib['componentRef'],int(ee.attrib['pin'])) )
		netObj.add_pin_ref( (ee.attrib['componentRef'],pin_num(ee.attrib['pin'])) )


def step_phynet_group(elem, attrib):
	u'''
	
		elem: [<PhyNet>,<PhyNet>, ...]
	'''
	for ee in elem:
		net_point = ee.getchildren()	#[<PhyNetPoint>,<PhyNetPoint>, ...]

		net_point_list = []
		for np in net_point:
			attr = np.attrib

			ch = np.getchildren()		#Circle
			tagName = re.sub(re_pat,'',ch[0].tag)
			if tagName == 'Circle':
				attr.update(ch[0].attrib)

			obj = IPCObject_PhyNetPoint(attr)
			net_point_list.append(obj)

			layers[np.attrib['layerRef']].items_.append(obj)

		phy_net_group[ ee.attrib['name'] ] = net_point_list;


def set_layer_object(layer, obj):
	u'''
		ﾚｲﾔｰの属性が ROUT(Cavity) または DRILL(Hole) である場合に
		fromLayer～toLayer の各ﾚｲﾔｰにｵﾌﾞｼﾞｪｸﾄを設定する
	'''
	layer_list = []

	if layer.function == 'ROUT':
		if layer.attribute.has_key('fromLayer') == True:
			layer_list = get_layer_list(layer.attribute['fromLayer'], layer.attribute['toLayer'])

	elif layer.function == 'DRILL':
		if layer.attribute.has_key('fromLayer') == True:
			layer_list = get_layer_list(layer.attribute['fromLayer'], layer.attribute['toLayer'])

	#該当するﾚｲﾔｰにｵﾌﾞｼﾞｪｸﾄを設定
	ln = [l.name for l in layer_list]
	if __DEBUG__ == True:
		print '{0} APPEND {1}::{2}'.format(ln, type(obj).__name__, obj.name)

	for ll in layer_list:
		ll.items_.append(obj)	


def findItem(items, objType, attr):
	u'''
		指定されたｵﾌﾞｼﾞｪｸﾄﾘｽﾄ内で指定されたｱﾄﾘﾋﾞｭｰﾄ値が一致するものを検索する
	 [戻り値]
	 	見つけた場合   :一致するｵﾌﾞｼﾞｪｸﾄ
		見つからない場合:None
	'''
	objFind = False
	for item in items:
		if type(item).__name__ == objType:
			objFind = True
			att = True
			for atr in attr:
				if item.attribute.has_key(atr) == False:
					att = False
					continue
				if item.attribute[atr] != attr[atr]:
					att = False
					continue
			# 同一のｱﾄﾘﾋﾞｭｰﾄを持つｵﾌﾞｼﾞｪｸﾄがある
			if att == True:
				return item

	if objFind == False:
		return None

def layer_feature_set(elem, attrib, layerName):
	u'''
		<LayerFeature>-<Set> ﾀｸﾞ処理
		elem:[<Features>, ...]
		attrib:{}
	'''
	#print '--------------:', layerName, '--------------------'

	layer = layers[layerName]
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Pad':
			attr = {k:el.attrib[k] for el in ee.getchildren() for k in el.attrib}
			if attrib.has_key('componentRef'):
				component = components[attrib['componentRef']]
				obj = findItem(layer.items_,'IPCObject_Pad',attr)
				if obj == None:
					obj = IPCObject_Pad('',attr)
					layer.items_.append( obj )

				# ｺﾝﾎﾟｰﾈﾝﾄに加えるかどうかは要検討
				component.add_pad( obj )
				if __DEBUG__ == True:
					print 'Component:{0} add_Pad {1}:({2},{3})'.format(component.name,obj.name,obj.attribute['x'],obj.attribute['y'])
			else:
				attr.update(attrib)
				obj = IPCObject_Via(attr)
				#ﾚｲﾔｰにﾋﾞｱを追加[※Pad(IPCObject_Pad)と同じ座標にﾋﾞｱを定義している]
				layer.items_.append( obj )

			if __DEBUG__ == True:
				print 'Layer:{0} add_{1} {2}:({3},{4})'.format(layer.name, type(obj).__name__,obj.name, obj.attribute['x'],obj.attribute['y'])

		elif tagName == 'Features':
			ch = ee.getchildren()
			if 'Line' in ch[0].tag:
				attr = attrib
				attr.update(ch[0].attrib)
				attr.update( {k:el.attrib[k] for el in ch[0].getchildren() for k in el.attrib})
				pos = [ (float(attr['startX']),float(attr['startY'])), (float(attr['endX']),float(attr['endY'])) ]
				layer.items_.append( IPCObject_Line(pos,attr) )
			elif 'Polyline' in ch[0].tag:
				attr = attrib
				attr.update({k:el.attrib[k] for el in ch[0].getchildren() for k in el.attrib})
				pos = pos_polygon(ch[0])
				layer.items_.append( IPCObject_Polyline(pos,attr) )
			elif 'Contour' in ch[0].tag:
				pos = pos_polygon( ch[0].getchildren()[0] )
				if attrib.has_key('componentRef') == True:
					component = components[attrib['componentRef']]
					component.set_polygon(pos)
			else:
				if __DEBUG__ == True:
					print '{0} is Undefined'.format(ch[0].tag)

		elif tagName == 'Hole':
			attr = attrib
			attr.update( ee.attrib )
			if attr.has_key('net'):
				layer.items_.append( create_object('Hole',attr['net'],attr) )
			else:
				layer.items_.append( create_object('Hole',None,attr) )

		elif tagName == 'SlotCavity':
			attr = attrib
			attr.update( ee.attrib )
			ch = ee.getchildren()
			pos = pos_polygon(ch[0].getchildren()[0])

			obj = IPCObject_Cavity(pos, attr)

			set_layer_object(layer,obj)


def layer_tag(layer,tags):
	for tag in tags:
		if 'Line' in tag.tag:
			attr = tag.attrib
			pos = ( (float(attr['startX']),float(attr['startY'])), (float(attr['endX']),float(attr['endY'])) )
			layer.items_.append( IPCObject_Line(pos) )
		elif 'Polyline' in tag.tag:
			pos = pos_polygon( tag )	
			layer.items_.append( IPCObject_Polyline(pos) )
		elif 'Contour' in tag.tag:
			pos = pos_polygon( tag.getchildren()[0] )
			layer.items_.append( IPCObject_Polygon(pos) )

def step_layer_feature(elem, attrib):
	u'''
		<LayerFeature> ﾀｸﾞ処理
		elem:[<Set>,<Set>,...]
		attrib: {'layerRef':'ﾚｲﾔｰ名'}
	'''
	layer = layers[ attrib['layerRef'] ]

	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Set':
			ch = ee.getchildren()
			if len(ee.attrib) != 0:
				layer_feature_set( ch, ee.attrib, attrib['layerRef'])
			else:
				for hh in ch:
					if 'Pad' in hh.tag:
						pass
					elif 'SlotCavity' in hh.tag:
						ch2 = hh.getchildren()
						pos = pos_polygon( ch2[0].getchildren()[0] )
						obj = IPCObject_Cavity(pos,hh.attrib)

						set_layer_object(layer,obj)
					elif 'NonstandardAttribute' in hh.tag:
						print 'NonStandardAttribute'
					else:
						ch2 = hh.getchildren()
						if 'UserSpecial' in ch2[0].tag:
							layer_tag(layer,ch2[0].getchildren())
						else:
							layer_tag(layer,[ch2[0],])


def xml_step(elem):
	u'''
		<Step> ﾀｸﾞ処理
	'''
	for ee in elem:
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'PadStack':
			if ee.attrib.has_key('net') == True:
				create_pad_stuck( ee.getchildren(), ee.attrib['net'] )
			else:
				create_pad_stuck( ee.getchildren())
		elif tagName == 'Datum':
			pass
		elif tagName == 'Profile':
			step_profile( ee.getchildren() )
			pass
		elif tagName == 'Package':
			step_package( ee.getchildren(),ee.attrib )
			pass
		elif tagName == 'Component':
			step_component( ee.getchildren(),ee.attrib )
			pass
		elif tagName == 'LogicalNet':
			step_logical_net( ee.getchildren(), ee.attrib )
			pass
		elif tagName == 'PhyNetGroup':
			step_phynet_group( ee.getchildren(), ee.attrib )
			pass
		elif tagName == 'LayerFeature':
			step_layer_feature( ee.getchildren(), ee.attrib )
			pass

def xml_cad_data(elem):
	u'''
		<CadData> ﾀｸﾞ処理
	'''
	for n,ee in enumerate(elem):
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'Layer':
			ch = ee.getchildren()
			if len(ch) != 0:
				attrib = ee.attrib
				attrib.update(ch[0].attrib)
				if 'Span' in ch[0].tag:
					if ee.attrib['layerFunction'] == 'DRILL':
						layers[ee.attrib['name']] = Layer_Hole(attrib)
					else:
						layers[ee.attrib['name']] = Layer_Cavity(attrib)
				elif 'SpecRef' in ch[0].tag:
					layers[ee.attrib['name']] = Layer(ee.attrib)

			else:
				layers[ee.attrib['name']] = Layer(ee.attrib)

		elif tagName == 'Stackup':
			xml_stuckup(ee.getchildren(),ee.attrib['overallThickness'])
		elif tagName == 'Step':
			xml_step( ee.getchildren() )

def xml_ecad(elem):
	u'''
		<Ecad> ﾀｸﾞ処理
	'''
	for n,ee in enumerate(elem):
		tagName = re.sub(re_pat,'',ee.tag)
		if tagName == 'CadHeader':
			pass
		elif tagName == 'CadData':
			xml_cad_data( ee.getchildren() )

#############################################
#
# 公開関数
#
def convert():
	u'''
		読み込んだXML を層ﾃﾞｰﾀに展開する
	'''
	global root

	if root == None:
		print u'XML ﾌｧｲﾙが読み込まれていません'
		return

	for tag in root:
		#print tag.tag
		tt = re.split(re_pat,tag.tag)
		if tt[1] == 'Content':
			xml_content(tag.getchildren())
		elif tt[1] == 'LogisticHeader':
			pass
		elif tt[1] == 'HistoryRecord':
			pass
		elif tt[1] == 'Bom':
			xml_bom(tag.getchildren())
		elif tt[1] == 'Ecad':
			xml_ecad( tag.getchildren() )
		elif tt[1] == 'Avl':
			pass
		else:
			print 'Unsupport tag:{0}'.format(tt[1])

def load_xml(fileName):
	u'''
		XML ﾌｧｲﾙを読み込む
	'''
	global root

	tree = ET.parse(fileName)
	root = tree.getroot()

def layer_thick(groupName):
	u'''
		ﾚｲﾔｰｸﾞﾙｰﾌﾟに含まれるﾚｲﾔｰの厚みを取得する
	'''

	if layer_group.has_key(groupName) == False:
		return 0.0

	#厚みのﾘｽﾄを作成
	tks = [layer.thickness for layer in layer_group[groupName]]
	tk = sum(tks)

	return  tk

def layer_items(groupName):
	u'''
		ﾚｲﾔｰｸﾞﾙｰﾌﾟに含まれるﾚｲﾔｰ名と含まれるｵﾌﾞｼﾞｪｸﾄ名を表示する
	'''
	if layer_group.has_key(groupName) == False:
		return []

	for layer in layer_group[groupName]:
		tn = [type(x).__name__ for x in layer.items_]
		print layer.name, tn

def layer_list():
	u'''
		ﾚｲﾔｰ一覧表示
	'''
	for groupName in layer_group:
		print '{0}:{1} mm'.format(groupName,layer_thick(groupName))
		for layer in layer_group[groupName]:
			print '    {0}:T={1}'.format(layer.name,layer.thickness)

def layer_height(layerRef):
	u'''
		最下層から指定された層までの厚みを取得する
		layerRef:層名
		return: 厚み(mm)
	'''
	thick = 0.0
	total = sum( [layer_thick(gn) for gn in layer_group.keys()])

	for groupName,layers in layer_group.iteritems():
		for layer in layers:
			if layer.attribute['name'] == layerRef:
				return total-thick
		thick += layer_thick(groupName)

	return 0.0

def layer_height2(layerRef):
	u'''
		最下層から指定された層までの厚みを取得する
		layerRef:層名
		return: 厚み(mm)
	'''
	thick = 0.0
	keys = layer_group.keys()

	for key in keys[::-1]:
		layers = layer_group[key]
		hh = 0.0
		for layer in layers:
			if layer.attribute['name'] == layerRef:
				#層ｸﾞﾙｰﾌﾟ内に指定された層が含まれている
				return thick
			hh += float(layer.thickness)
		#層ｸﾞﾙｰﾌﾟ内に無かったので、ｸﾞﾙｰﾌﾟの厚みを加算する
		thick += hh

	return 0.0

def get_layerName(layerNo):
	u'''
		層番号から層名を取得する(最下層を1とする)
		layerNo:層番号(1～)
		retrn: 層名(層ｸﾞﾙｰﾌﾟ名), 存在しない場合は None
	'''
	if layerNo <=0 or layerNo > len(layer_group):
		return None

	return layer_group.keys()[-layerNo]

def create_board_image():
	u'''
		BoardShape から矩形のﾎﾞｰﾄﾞｲﾒｰｼﾞﾃﾞｰﾀを生成する ※黒埋め
		return: Image
	'''
	#ﾎﾞｰﾄﾞｻｲｽﾞ
	layer = layers['BoardShape']
	pol = layer.items[0].polygon()

	sh = sorted(set(pol[1]), key=lambda d: (d[0],d[1]))

	L1 = sh[0]		#(x,y)の最小値
	L2 = sh[-1]		#(x,y)の最大値

	#xs = int(math.ceil((L2[0] - L1[0])/dotSize))
	#ys = int(math.ceil((L2[1] - L1[1])/dotSize))
	xs = L2[0] - L1[0]
	ys = L2[1] - L1[1]

	# ﾎﾞｰﾄﾞｻｲｽﾞのｲﾒｰｼﾞを生成
	#return Image.new('L',(xs,ys))
	return Image.new('RGB',(xs,ys), colors['BoardShape'].rgb)


def group_print(groupName, fileName):
	u'''
		ｸﾞﾙｰﾌﾟに含まれるﾚｲﾔｰのﾋﾞｯﾄﾏｯﾌﾟを作成する
	'''

	print '----', groupName, '----'
	layers = layer_group[groupName]

	img = create_board_image()
	drw = ImageDraw.Draw(img)

	for ly in layers:
		print ly.name
		for obj in ly.items_:
			if obj.attribute.has_key('x') == True:
				print '   {0}::{1}=({2},{3})'.format(type(obj).__name__, obj.name,obj.attribute['x'],obj.attribute['y'])
			else:
				print '   {0}::{1}'.format(type(obj).__name__, obj.name)

			polygonData = obj.polygon()
			print polygonData

			col = colors[ly.name].rgb
			if polygonData[0] == 'Polygon' or polygonData[0] == 'RectRound':
				polygon = map(lambda arg:(arg[0],img.size[1]-arg[1]),polygonData[1])
				drw.polygon( polygon ,col)
				#drw.polygon( polygon ,255)
			elif polygonData[0] == 'Circle':
				rr = polygonData[1]	
				x1 = rr[0][0] - (rr[1][0]/2)
				x2 = rr[0][0] + (rr[1][0]/2)
				y1 = img.size[1] - (rr[0][1] - (rr[1][1]/2))
				y2 = img.size[1] - (rr[0][1] + (rr[1][1]/2))
				drw.ellipse([x1,y1,x2,y2],fill=(0,0,0))
			elif polygonData[0] == 'Polyline':
				lw = int( round(float(obj.attribute['lineWidth'])/dotSize) )
				pos = map(lambda arg:(arg[0],img.size[1]-arg[1]),polygonData[1])
				pp = [pos[0],pos[1]]
				for p2 in pos[2:]:
					drw.line(pp,col,width=lw)
					pp[0] = pp[1]
					pp[1] = p2
				drw.line(pp,col,width=lw)

			elif polygonData[0] == 'Line':
				lw = int( round(float(obj.attribute['lineWidth'])/dotSize) )
				pos = map(lambda arg:(arg[0],img.size[1]-arg[1]),polygonData[1])
				drw.line(pos,col,width=lw)

			elif polygonData[0] == 'None':
				pass

	#ﾌｧｲﾙ保存
	img.save(fileName)

def group_object(groupName, objName, attr, st=True, fileName=None):
	u'''
		ｸﾞﾙｰﾌﾟに含まれる'ｵﾌﾞｼﾞｪｸﾄ'を抽出する
		 objName: ｵﾌﾞｼﾞｪｸﾄ名(IPCObject_Pad, IPCObject_Hole, ...)
		    attr: 'Pad' として認識するための属性ｷｰﾜｰﾄﾞ(ex. pin)
		      st: attr を含む(True)、含まない(False)
		fileName: 出力する画像ﾌｧｲﾙ名(指定なしは生成しない)

		例えば    端子は'pin'属性を含む   => objName='IPCObject_Pad' attr='pin' st=True
			 層間接続は'pin'属性を含まない=> objName='IPCObject_Pad' attr='pin' st=False
			     ﾎｰﾙは                 => objName='IPCObject_Hole' attr='diameter' st=True
	'''
	layers = layer_group[groupName]

	img = create_board_image()

	if fileName != None:
		drw = ImageDraw.Draw(img)

	for ly in layers:
		print ly.name
		for obj in ly.items_:
			if type(obj).__name__ == objName:

				if obj.attribute.has_key(attr) == st:
					'''
					if obj.attribute.has_key('x') == True:
						print '   {0}::{1}=({2},{3})'.format(type(obj).__name__, obj.name,obj.attribute['x'],obj.attribute['y'])
					else:
						print '   {0}::{1}'.format(type(obj).__name__, obj.name)
					'''

					#col = colors[ly.name].rgb
					col = colorCode.WHITE
					polygonData = obj.polygon()

					if polygonData[0] == 'Polygon' or polygonData[0] == 'RectRound':
						# polygonData == ('RectRound',[(x,y),(x,y),(x,y),(x,y)])
						# polygonData == ('Polygon',[(x,y),(x,y),...])
						if fileName != None:
							#画像ｲﾒｰｼﾞではYの座標系が上下異なるので
							polygon = map(lambda arg:(arg[0],img.size[1]-arg[1]),polygonData[1])
							drw.polygon( polygon ,col)

						print polygonData

					elif polygonData[0] == 'Circle':
						# polygonData == ('Circle',[(cx,cy),(r,r)])
						if fileName != None:
							cx = polygonData[1][0][0]
							cy = img.size[1] - polygonData[1][0][1]
							r  = polygonData[1][1][0]/2
							drw.ellipse((cx-r,cy-r,cx+r,cy+r),col)
						print polygonData

	#ﾌｧｲﾙ保存
	if fileName != None:
		img.save(fileName)


def group_object_pos(groupName, objName, attr, st=True ):
	u'''
		ｸﾞﾙｰﾌﾟに含まれる'ｵﾌﾞｼﾞｪｸﾄ'の座標を抽出する
		 objName: ｵﾌﾞｼﾞｪｸﾄ名(IPCObject_Pad, IPCObject_Hole, ...)
		    attr: 'Pad' として認識するための属性ｷｰﾜｰﾄﾞ(ex. pin)
		      st: attr を含む(True)、含まない(False)

		例えば    端子は'pin'属性を含む   => objName='IPCObject_Pad' attr='pin' st=True
			 層間接続は'pin'属性を含まない=> objName='IPCObject_Pad' attr='pin' st=False
			     ﾎｰﾙは                 => objName='IPCObject_Hole' attr='diameter' st=True
	'''
	layers = layer_group[groupName]

	for ly in layers:
		print ly.name
		for obj in ly.items_:
			if type(obj).__name__ == objName:

				if obj.attribute.has_key(attr) == st:

					col = colorCode.WHITE
					polygonData = obj.polygon()

					if polygonData[0] == 'Polygon' or polygonData[0] == 'RectRound':
						print polygonData

					elif polygonData[0] == 'Circle':
						pos = obj.pos()
						print pos


def group_pad(groupName):
	layers = layer_group[groupName]

	idx = 1
	for ly in layers:
		print ly.name
		for obj in ly.items_:
			if type(obj).__name__ == 'IPCObject_Pad':
				if obj.attribute.has_key('pin') == True:
					print '   {0}::{1}=({2},{3}):{4}'.format(idx, obj.name, obj.attribute['x'],obj.attribute['y'], obj.attribute['pin'])
				else:
					print '   {0}::{1}=({2},{3}):'.format(idx, obj.name,obj.attribute['x'],obj.attribute['y'])
				idx += 1


def print_line(list_data):
	u'''
		ﾘｽﾄの各項目をﾀﾌﾞで区切って出力する、最後は\n
	'''
	ln = len(list_data)
	for idx,k in enumerate(list_data):
		if idx == ln-1:
			sys.stdout.write(k+'\n')
		else:
			sys.stdout.write(k+'\t')

def set_item_value(itemList, itemName, val):
	u'''
		itemList: [(name,[str,str,str,...]), (,[]), ...]:=nexim_items
		itemName:  ==name
		    val : setting value
	'''
	for item in itemList:
		if item[0] == itemName:
			item[1][0] = str(val)
			return

def get_layer(layerNo):
	u'''
		層番号から層に含まれるﾚｲﾔｰ一覧を取得する
		layerNo: 層番号(最下層を1とし、0は全層)

		戻り値:[Layer(class)Object, ...]
	'''
	if layerNo < 0 or layerNo > len(layer_group):
		raise Exception(u'存在しないレイヤー番号')

	if layerNo != 0:
		key = layer_group.keys()[-layerNo]
		return layer_group[key]

	else:
		retList = []
		for (groupName,layers) in layer_group.iteritems():
			for ll in layers:
				retList.append(ll)

		return retList

def parts_list(layerNo, objName, partName):
	u'''
		指定された層番号に含まれる部品の情報を表示する
		layerNo  : 層番号(1:最下層)
		objName[]: 出力する名前(ﾘｽﾄ)を限定する
		partName: 出力する「Part Number」の項目を指定します
	'''
	if layerNo < 0 or layerNo > len(layer_group):
		raise Exception(u'存在しないレイヤー番号')

	#指定層(ｸﾞﾙｰﾌﾟに含まれる)層ﾘｽﾄの取得
	ly_lst = get_layer(layerNo)

	#指定された層(ｸﾞﾙｰﾌﾟ)に含まれる層名一覧
	layerNames = [obj.name for obj in ly_lst]

	#ﾀｲﾄﾙ表示
	print_line( [n[0] for n in nexim_items] )

	for key,val in components.iteritems():
		#val:IPCObject_Component
		if val.layerRef in layerNames:
			hh = layer_height(val.layerRef)

			if objName != None and not(val.partName in objName):
				#名前が指定されていて、名前が異なる場合
				continue

			tmp_items = copy.deepcopy(nexim_items)
			set_item_value(tmp_items,'Ref.',key)
			set_item_value(tmp_items,'Pos X',val.location[0] + _x_offset)
			set_item_value(tmp_items,'Pos Y',val.location[1] + _y_offset)
			set_item_value(tmp_items,'Pos Z',hh + _z_offset)
			set_item_value(tmp_items,'Rotation',val.rotation)
			if partName != None:
				set_item_value(tmp_items,'Part Number',partName)
			else:
				set_item_value(tmp_items,'Part Number',val.partName)

			print_line( [n[1][0] for n in tmp_items] )

def via_list(layerNo, objName, partName):
	u'''
		指定された層にViaの下端(toLayer)が含まれているViaの座標を表示する
		  viaName: 出力時のﾊﾟｰﾄﾃﾞｰﾀ名
		  layerNo: 層番号(1:bottom)
		objName[]: 出力する名前(ﾘｽﾄ)を限定する
		 partName: 出力する「Part Number」の項目を指定します
	'''
	if layerNo < 0 or layerNo > len(layer_group):
		raise Exception(u'存在しないレイヤー番号')

	#指定層(ｸﾞﾙｰﾌﾟに含まれる)層ﾘｽﾄの取得
	ly_lst = get_layer(layerNo)

	#指定された層(ｸﾞﾙｰﾌﾟ)に含まれる層名一覧
	layerNames = [obj.name for obj in ly_lst]

	#ﾀｲﾄﾙ表示
	print_line( [n[0] for n in nexim_items] )

	for num,obj in enumerate(_holeObj_list):
		if obj.attribute.has_key('fromLayer') and obj.attribute.has_key('toLayer'):

			if objName != None and not(obj.attribute['name'] in objName):
				#表示する名前が限定されている場合で、名前が異なる場合
				continue

			tmp_items = copy.deepcopy(nexim_items)

			set_item_value(tmp_items,'Ref.', '{0}'.format(obj.attribute['name']))
			set_item_value(tmp_items,'Pos X', (float(obj.pos()[0]) + _x_offset) )
			set_item_value(tmp_items,'Pos Y', (float(obj.pos()[1]) + _y_offset) )
			set_item_value(tmp_items,'Pos Z', layer_height2(obj.attribute['toLayer']) + _z_offset)
			set_item_value(tmp_items,'Rotation', 0.0)
			if partName != None:
				set_item_value(tmp_items,'Part Number','{0}'.format(partName))
			else:
				set_item_value(tmp_items,'Part Number','{0}'.format(obj.attribute['name']))

			if layerNo != 0:
				if obj.attribute['toLayer'] in layerNames:
					# 'toLayer' が指定層に含まれるもの
					print_line( [n[1][0] for n in tmp_items] )
			else:
				print_line( [n[1][0] for n in tmp_items] )

def execute(ipcFile,output, outType, layerNo, objName, partName):
	u'''
		IPC変換出力
		 ipcFile: IPC-2581 ﾌｧｲﾙ
		  output: 出力先ﾌｧｲﾙ名、未設定は標準出力
		 outType: 出力したい対象(parts, via, ...)
		 layerNo: 出力したい層番号(1:最下層, 0:全て)
	   objName[]: 出力したい対象物を限定する(未設定は全て)
		partName: 出力する情報のPartNameの項目を指定します
	'''
	try:
		load_xml(ipcFile)

		convert()
	except Exception as e:
		print u'IPC ﾌｧｲﾙの読み込みエラー'
		user32.MessageBoxW(0,u'IPC File の読み込みエラー',u'Error',MB_ICONSTOP)
		return

	if output != None:
		out = open(output,'w')
		sys.stdout = out

	try:
		if outType == None:
			layer_list()

		elif outType.lower() == 'via':
			via_list(layerNo, objName, partName)

		elif outType.lower() == 'parts':
			parts_list(layerNo, objName, partName)

		else:
			layer_list()

		#group_object('Conductor-1Group', 'IPCObject_Pad', 'pin',True,'f:\\pad.png')		#端子
		#group_object('Conductor-1Group', 'IPCObject_Pad', 'pin',False,'f:\\pad2.png')		#層間接続用
		#group_object('Conductor-1Group', 'IPCObject_Hole', 'diameter',True,'f:\\hole.png')	#ﾎｰﾙ
		#group_object_pos('Conductor-1Group', 'IPCObject_Hole', 'diameter',True)	#ﾎｰﾙ

	except Exception as e:
		user32.MessageBoxW(0,e.message.decode('shift-jis'),u"Error",MB_ICONSTOP)
		pass

	finally:
		if output != None:
			sys.stdout = sys.__stdout__
			out.close()


##########################################################

if __name__ == '__main__':
	args = parser.parse_args()

	__DEBUG__ = args.debug

	if args.offsetx != '0.0':
		_x_offset = float(args.offsetx)

	if args.offsety != '0.0':
		_y_offset = float(args.offsety)

	if args.offsetz != '0.0':
		_z_offset = float(args.offsetz)

	execute(args.ipc_file,args.output,args.type,args.layer,args.name,args.partname)
