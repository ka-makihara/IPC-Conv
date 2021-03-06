#-*- coding:utf-8 -*-

"""Subclass of StlPng, which is generated by wxFormBuilder."""

import os
import wx
import glob
import subprocess
import stl_png

import stl2png
import svg2png

def delete_imageFiles(dirName):
	files = glob.glob( dirName + '\\*.png')
	for file in files:
		os.remove(file)
		print 'delete {0}'.format(file)

# Implementing StlPng
class StlPngDlg( stl_png.StlPng ):
	def __init__( self, parent ):
		stl_png.StlPng.__init__( self, parent )

	# Handlers for StlPng events.
	def OnFileChanged( self, event ):
		# TODO: Implement OnFileChanged
		pass
	
	def OnExecute( self, event ):
		# TODO: Implement OnExecute
		stl_file = self.m_filePicker2.GetPath()					# STL ﾌｧｲﾙ名
		layer_height = float(self.m_layerHeight.GetValue())		# ｽﾗｲｽ高さ
		xdpm = float(self.m_pixelSizeX.GetValue())				# Xﾄﾞｯﾄ/mm
		ydpm = float(self.m_pixelSizeY.GetValue())				# Yﾄﾞｯﾄ/mm
		img_width = int(self.m_img_width.GetValue())			# 生成するPNGﾌｧｲﾙの幅
		img_height= int(self.m_img_height.GetValue())			# 生成するPNGﾌｧｲﾙの高さ

		name,ext = os.path.splitext(stl_file)

		#ｽﾗｲｽﾃﾞｰﾀを生成(SVGﾌｫｰﾏｯﾄ)
		stl2png.exec_slic3r(stl_file, name + '.svg', layer_height)

		# SVG から PNG を生成するﾌｫﾙﾀﾞを新規に作成する(STLﾌｧｲﾙのﾌｫﾙﾀﾞ下に生成)
		dirName = os.path.dirname(stl_file) + '\\Images'
		if os.path.exists(dirName) == False:
			os.mkdir(dirName)
		else:
			delete_imageFiles(dirName)

		# SVG を PNG へ変換(Images ﾌｫﾙﾀﾞ下へ生成する)
		print u'SVG から PNGを作成します'
		output_name = os.path.splitext( os.path.basename(stl_file) )
		outFile = dirName + '\\' + output_name[0] + '.png'
		svg2png.svg_to_png(name+'.svg',outFile,xdpm=xdpm, ydpm=ydpm)

		# png ﾌｧｲﾙを加工する
		files = glob.glob('{0}\\*.png'.format(dirName))

		for file in files:
			print file
			stl2png.conv_image(file,img_width,img_height)

		# PNGﾌｧｲﾙを分割します
		print u'PNGﾌｧｲﾙを分割します'
		cmd_exe = 'bitmapbunkatsu.exe'
		opt_mask = ' /mask={0},{1}'.format(self.m_maskX.GetValue(), self.m_maskY.GetValue())
		opt_block= ' /block={0},{1}'.format(self.m_blockX.GetValue(),self.m_blockY.GetValue())
		opt_out = ' /output={0}'.format(dirName)

		files = glob.glob('{0}\\*.png'.format(dirName))
		for file in files:
			print file
			opt_img = ' /image={0}'.format(file)
			cmd_str = cmd_exe + opt_mask + opt_block + opt_img + opt_out
			subprocess.call(cmd_str)

		wx.MessageBox(u'完了しました',u'確認')
		print u'完了しました'


if __name__ == '__main__':

	app = wx.App()

	dialog = StlPngDlg(None)
	result = dialog.ShowModal()

	dialog.Destroy()