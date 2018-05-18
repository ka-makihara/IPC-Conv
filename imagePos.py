#-*- coding:utf-8 -*-

import os
import sys

import numpy as np
import cv2


def main(imageFile, outFile, isDraw=True):
	src_img = cv2.imread(imageFile)

	gray = cv2.cvtColor(src_img,cv2.COLOR_BGR2GRAY)
	#cnts = cv2.findContours(gray,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
	cnts = cv2.findContours(gray,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[1]
	#cnts.sort(key=cv2.contourArea,reverse=True)

	img_tmp = src_img.copy()

	for i,c in enumerate(cnts):
		#輪郭を直線近似
		arclen = cv2.arcLength(c,True)
		hull = cv2.convexHull(c)		#座標を整列(時計まわり:右下、左下、左上、右上)
		approx = cv2.approxPolyDP(hull,0.02*arclen,True)

		if len(approx) == 4:
			#近似が4線(四角)
			if isDraw == True:
				#cv2.drawContours(img_tmp,[approx],-1,(0,255,0),1)	#輪郭描画
				x1 = approx[2][0][0]
				y1 = approx[2][0][1]
				x2 = approx[0][0][0]
				y2 = approx[0][0][1]

				img = gray[y1:y2,x1:x2			#領域をｲﾒｰｼﾞとして取り出す
				#cv2.imwrite('f:\\tt.png',img)	#領域をﾌｧｲﾙ保存
				#area = cv2.countNonZero(img)	#領域の0以外のﾋﾟｸｾﾙを数える
				area = cv2.contourArea(cnts[i])	#面積
				mu = cv2.moments(approx)		#ﾓｰﾒﾝﾄ計測
				cx = int(mu['m10'] / mu['m00'])	#重心X
				cy = int(mu['m01'] / mu['m00'])	#重心Y
				cv2.line(img_tmp,(cx-1,cy),(cx+1,cy),(0,0,0),1)
				cv2.line(img_tmp,(cx,cy-1),(cx,cy+1),(0,0,0),1)

				#cenStr = '({0},{1})'.format(cx,cy)
				#cv2.putText(img_tmp,cenStr,(x1,y1+8),cv2.FONT_HERSHEY_PLAIN,0.7,(0,0,255))
				cv2.putText(img_tmp,str(area),(x1,y1+8),cv2.FONT_HERSHEY_PLAIN,0.7,(0,0,255))

		else:
			#外接四角形
			x,y,w,h = cv2.boundingRect(approx)
			if isDraw == True:
				cv2.drawContours(img_tmp,[approx],-1,(255,0,0),2)
				cv2.rectangle(img_tmp,(x,y),(x+w, y+h),(255,0,0),2)
				cv2.putText(img_tmp,str(i),(x,y),cv2.FONT_HERSHEY_PLAIN,1.0,(255,255,0))

		'''
		if isDraw == True:
			for pos in approx:
				cv2.circle(img_tmp,tuple(pos[0]),4,(0,0,255))
		'''

	cv2.imwrite(outFile,img_tmp)

if __name__ == '__main__':
	main('f:\\pad.png','f:\\pad_info.png')
	main('f:\\pad2.png','f:\\pad2_info.png')
