#-*- coding:utf-8 -*-

u'''
	Slic3r で出力された SVG ﾌｧｲﾙを PNGﾌｧｲﾙへ変換する
'''

import os
import sys

import re
import math
import argparse
from xml.etree import ElementTree as ET

import cairosvg

re_pat = re.compile('\{.*?\}')

root = None

svg_xmlns = '\"http://www.w3.org/2000/svg\"'
svg_header = ''

parser = argparse.ArgumentParser(description='This script is ...')

parser.add_argument('svg_file',      action='store', nargs=None, const=None,default=None,type=str,choices=None,help='SVG filename',metavar=None)
parser.add_argument('-o', '--output',action='store', nargs=1,    const=None,default=None,type=str,choices=None,help='output filename',metavar=None)
parser.add_argument('-s', '--start', action='store', nargs=None, type=int, default=0, help='Start Layer number')
parser.add_argument('-e', '--end',   action='store', nargs=None, type=int, default=-1,help='End Layer number')
parser.add_argument('-d', '--debug', action='store_true', default=False, help='debug mode if this flag is set (default:False)')

def load_xml(fileName):
	u'''
		SVG ﾌｧｲﾙを読み込む
	'''
	global root

	try:
		tree = ET.parse(fileName)
		root = tree.getroot()
	except IOError:
		print '{0} not found'.format(fileName)


def str2png(svg_str, out_file):
	u'''
		SVG 文字列を PNG ﾌｧｲﾙへ出力する
	'''
	global svg_header

	svg = svg_header + svg_str + '</svg>'

	#print svg
	cairosvg.svg2png(bytestring=svg,write_to=out_file)

	print 'Created::{0}'.format(out_file)


def layer_to_image(elements, out_file, xdpm, ydpm):
	u'''
		SVG ﾌｧｲﾙの各層 <g> を処理する
		elements: [<g>]  <g> Elementのﾘｽﾄ
		out_file: 出力ﾌｧｲﾙ名
		    xdmp: 1ﾄﾞｯﾄの長さX(mm)
		    ydmp: 1ﾄﾞｯﾄの長さY(mm)
	'''
	svg_str = ''

	for elem in elements:
		tg = re.sub(re_pat,'',elem.tag)
		hd = '<' + tg
		attr = ''
		for key in elem.attrib.keys():
			kk = re.sub(re_pat,'',key)
			vv = re.sub(re_pat,'', elem.attrib[key])
			if kk == 'points':
				# 座標がmmなので、ﾄﾞｯﾄ単位に変換する
				vs = ''
				kl = vv.split(' ')
				for v in kl:
					v2 = v.split(',')
					vx = int( float(v2[0]) / xdpm)
					vy = int( float(v2[1]) / ydpm)
					s2 = ' ' + str(vx) + ',' + str(vy)
					vs += s2
				vv = vs

			ss =  ' ' + kk + '=\"' + vv + '\"'
			attr += ss
		svg_tag = hd + attr + ' />'

		#print svg_tag
		svg_str += svg_tag

	str2png(svg_str,out_file)

def convert(out_file, startLayer = 0, endLayer = 0, xdpm=0.0423, ydpm=0.0423):
	u'''
		読み込んだSVG を PNG に展開する
		startLayer: 開始ﾚｲﾔｰ
		  endLayer: 終了ﾚｲﾔｰ
		      xdpm: 1ﾄﾞｯﾄの長さX(mm)
		      ydpm: 1ﾄﾞｯﾄの長さY(mm)
	'''
	global root
	global svg_header

	if root == None:
		print u'SVG ﾌｧｲﾙが読み込まれていません'
		return

	width = ' width=\"'  + str( int(float(root.attrib['width']) / xdpm) ) + '\"'
	height= ' height=\"' + str( int(float(root.attrib['height'])/ ydpm) ) + '\"'
	xmlns = ' xmlns=' + svg_xmlns + ' xmlns:svg=' + svg_xmlns

	svg_header = '<' + re.sub(re_pat,'',root.tag) + width + height + xmlns + '>'

	if endLayer <= 0:
		endLayer = len(root)

	if startLayer > endLayer:
		st = startLayer
		startLayer = endLayer
		endLayer = st

	if startLayer < 0 or startLayer > len(root):
		print 'out of layer Total={0} start={1} end={2}'.format( len(root), startLayer,endLayer)
		return

	if endLayer < 0 or endLayer > len(root):
		print 'out of layer Total={0} start={1} end={2}'.format( len(root), startLayer,endLayer)
		return

	print 'Total:{0} layer {1}-{2}'.format(len(root),startLayer,endLayer)

	path,ext = os.path.splitext(out_file)

	for num,tag in enumerate(root[startLayer:endLayer]):
		tt = re.split(re_pat,tag.tag)
		if tt[1] == 'g':
			file = path + '{0:03d}'.format(num+startLayer) + ext
			layer_to_image( tag.getchildren(), file, xdpm, ydpm )
		else:
			print 'Unsupport tag:{0}'.format(tt[1])

##########################################################

def svg_to_png(in_file, out_file, startLayer = 0, endLayer = -1, xdpm=0.0423, ydpm=0.0423):
	u''' SVG ﾌｧｲﾙをPNGﾌｧｲﾙへ変換する
	       in_file: SVG ﾌｧｲﾙ名
	      out_file: 出力する PNGﾌｧｲﾙ名
	    startLayer: 開始層番号 [ﾃﾞﾌｫﾙﾄ: 0 最初から]
	      endLayer: 終了層番号 [ﾃﾞﾌｫﾙﾄ:-1 最後まで]
	          xdpm: 1ﾄﾞｯﾄの長さX(mm)
	          ydpm: 1ﾄﾞｯﾄの長さY(mm)
	'''
	load_xml(in_file)
	convert(out_file, startLayer, endLayer,xdpm,ydpm)


##########################################################

if __name__ == '__main__':
	args = parser.parse_args()

	svg_to_png(args.svg_file,args.output[0],args.start,args.end)
