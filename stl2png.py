#-*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
import glob

import cv2
import numpy as np

import svg2png

parser = argparse.ArgumentParser(description='This script is ...')

parser.add_argument('stl_file',      action='store', nargs=None, const=None,default=None,  type=str,  choices=None,help='STL filename',metavar=None)
parser.add_argument('--output',      action='store', nargs=None, const=None,default=None,  type=str,  choices=None,help='output filename',metavar=None)
parser.add_argument('--layer_height',action='store', nargs=None, const=None,default=0.055, type=float,choices=None,help='Layer Height(mm)')
parser.add_argument('--image_width', action='store', nargs=None, const=None,default=0,     type=int,  choices=None,help='ImageFile Width(pixel)')
parser.add_argument('--image_height',action='store', nargs=None, const=None,default=0,     type=int,  choices=None,help='ImageFile Height(pixel)')
parser.add_argument('--xdpm',         action='store', nargs=None, const=None,default=0.0423,type=float,choices=None,help='pixel sizeX(mm)')
parser.add_argument('--ydpm',         action='store', nargs=None, const=None,default=0.0423,type=float,choices=None,help='pixel sizeY(mm)')


def conv_image(imageFile, sizeX=0, sizeY=0):
	u''' PNGﾌｧｲﾙを加工する
		imageFile: 画像ﾌｧｲﾙ名
		    sizeX: 画像のXｻｲｽﾞ(ﾋﾟｸｾﾙ数)
		           画像ｻｲｽﾞが指定ｻｲｽﾞより大きい場合は分割し
		           画像ｻｲｽﾞが指定ｻｲｽﾞより小さい場合は余白を追加
		           0 の場合は分割、拡張は行わない
		    sizeY: 画像のYｻｲｽﾞ(ﾋﾟｸｾﾙ数)
		           画像ｻｲｽﾞが指定ｻｲｽﾞより大きい場合は分割し
		           画像ｻｲｽﾞが指定ｻｲｽﾞより小さい場合は余白を追加
		           0 の場合は分割、拡張は行わない
	'''
	#白黒反転用のﾙｯｸｱｯﾌﾟﾃｰﾌﾞﾙ
	lookup_tbl = np.ones((256,1),dtype='uint8')

	for i in range(256):
		lookup_tbl[i][0] = 255 - i

	src_im = cv2.imread(imageFile)
	height, width, channels = src_im.shape

	#LUT を使用して白黒反転
	im = cv2.LUT(src_im,lookup_tbl)

	# 左右反転
	imm = cv2.flip(im,1)

	#ｸﾞﾚｰｽｹｰﾙに変換して二値化(大津法)
	gray = cv2.cvtColor(imm, cv2.COLOR_BGR2GRAY)
	ret,th = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

	#白黒反転、左右反転の画像を元画像とする
	cv2.imwrite(imageFile,th)

	#画像のｻｲｽﾞ調整
	if sizeX == 0 and sizeY == 0:
		#ｻｲｽﾞ指定が無い
		cv2.imwrite(imageFile,th)
	else:
		#ﾌｧｲﾙ名生成のために名前と拡張子を分離
		name,ext = os.path.splitext(imageFile)

		if sizeX == 0:
			sizeX = width
		if sizeY == 0:
			sizeY = height

		tmp_img = np.zeros((sizeY,sizeX), dtype=np.uint8)
		tmp_img.fill(255)	#背景は白

		if sizeY > height:
			if sizeX > width:
				#指定されたｻｲｽﾞの方が大きいため、元の画像は内部に収まる
				#ﾌｧｲﾙ分割をしないのでﾌｧｲﾙ名も変換しない
				tmp_img[0:height,0:width] = th
				cv2.imwrite(imageFile,tmp_img)
			else:
				#Y方向の指定ｻｲｽﾞの方が大きいので元画像はXのみ分割する
				cnt = width / sizeX
				for nx in range(cnt):
					x = nx * sizeX
					tmp_img.fill(255)
					tmp_img[0:height,x:x+sizeX] = th[0:, x:x+sizeX]
					cv2.imwrite('{0}_X{1}_Y0{2}'.format(name,nx,ext),tmp_img)
					print 'Created::{0}_X{1}_Y0{2}'.format(name,nx,ext)

				#X余り部分
				if width % sizeX != 0:
					tmp_img.fill(255)
					tmp_img[0:height,:width%sizeX] = th[0:,sizeX*cnt:]
					cv2.imwrite('{0}_X{1}_Y0{2}'.format(name,cnt,ext),tmp_img)
					print 'Created::{0}_X{1}_Y0{2}'.format(name,cnt,ext)
		else:
			# 指定されたYｻｲｽﾞが元画像より小さいのでY方向の分割
			ycnt = height / sizeY
			xcnt = width / sizeX
			for ny in range(ycnt):
				y = ny * sizeY
				if width > sizeX:
					# 指定されたXｻｲｽﾞが元画像より小さいのでX方向の分割
					cnt = width / sizeX
					for nx in range(cnt):
						x = nx * sizeX
						cv2.imwrite('{0}_X{1}_Y{2}{3}'.format(name,nx,ny,ext),th[y:y+sizeY, x:x+sizeX])
						print 'Created::{0}_X{1}_Y{2}{3}'.format(name,nx,ny,ext)

					#余り部分
					if width % sizeX != 0:
						tmp_img[0:,:width%sizeX] = th[y:y+sizeY,sizeX*cnt:]
						cv2.imwrite('{0}_X{1}_Y{2}{3}'.format(name,cnt,ny,ext),tmp_img)
						print 'Created::{0}_X{1}_Y{2}{3}'.format(name,cnt,ny,ext)
				else:
					#X指定ｻｲｽﾞに元画像は収まる
					tmp_img.fill(255)
					tmp_img[0:,:width] = th[y:y+sizeY, 0:]
					cv2.imwrite('{0}_X0_Y{1}{2}'.format(name,ny,ext),tmp_img)
					print 'Created::{0}_X0_Y{1}{2}'.format(name,ny,ext)

			if height % sizeY != 0:
				#Y方向の余り
				tmp_img.fill(255)

				if width > sizeX:
					# 指定されたXｻｲｽﾞが元画像より小さいのでX方向の分割
					for nx in range(xcnt):
						x = nx * sizeX
						cv2.imwrite('{0}_X{1}_Y{2}{3}'.format(name,nx,ycnt,ext),th[sizeY*ycnt:, x:x+sizeX])
						print 'Created::{0}_X{1}_Y{2}{3}'.format(name,nx,ycnt,ext)

					#余り部分
					if width % sizeX != 0:
						tmp_img[0:height%sizeY,:width%sizeX] = th[sizeY*ycnt:,sizeX*xcnt:]
						cv2.imwrite('{0}_X{1}_Y{2}{3}'.format(name,xcnt,ycnt,ext),tmp_img)
						print 'Created::{0}_X{1}_Y{2}{3}'.format(name,xcnt,ycnt,ext)
				else:
					#X指定ｻｲｽﾞに元画像は収まる
					tmp_img[0:height%sizeY,:width] = th[sizeY*ycnt:, 0:]
					cv2.imwrite('{0}_X0_Y{1}{2}'.format(name,ycnt,ext),tmp_img)
					print 'Created::{0}_X0_Y{1}{2}'.format(name,ycnt,ext)


def exec_slic3r(stl_file, output_file, layer_height=0.055):
	cmd = 'Slic3r-console.exe --no-gui --export-svg --fill-density 99'

	height = ' --layer-height {0} --first_layer_height {0}'.format(layer_height)
	output = ' -o {0} {1}'.format(output_file,stl_file)

	#print cmd+height+output
	subprocess.call(cmd + height + output)

###################################################################
#
#
#
if __name__ == '__main__':
	#conv_image('f:\\yoko0.png',300,800)

	args = parser.parse_args()

	#print args
	name,ext = os.path.splitext(args.stl_file)

	if args.output == None:
		#出力ﾌｧｲﾙの指定がない場合
		args.output = name + '.svg'

	#ｽﾗｲｽﾃﾞｰﾀを生成(SVGﾌｫｰﾏｯﾄ)
	exec_slic3r(args.stl_file,args.output,args.layer_height)

	if os.path.exists('Images') == False:
		os.mkdir('Images')

	# SVG を PNG へ変換(Images ﾌｫﾙﾀﾞ下へ生成する)
	svg2png.svg_to_png(args.output,'Images\\{0}.png'.format(name),args.xdpm,args.ydpm)

	# png ﾌｧｲﾙを加工する
	files = glob.glob('Images\\*.png')

	for file in files:
		print file
		conv_image(file,args.image_size)
