# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class StlPng
###########################################################################

class StlPng ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"STL-PNG", pos = wx.DefaultPosition, size = wx.Size( 530,245 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		if int( wx.__version__.split('.')[0]) == 3:
			self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		else:
			self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"STLﾌｧｲﾙ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		self.m_staticText1.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer2.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_filePicker2 = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a STL file", u"*.stl", wx.DefaultPosition, wx.Size( 500,-1 ), wx.FLP_DEFAULT_STYLE )
		bSizer2.Add( self.m_filePicker2, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"ｽﾗｲｽ解像度(mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		self.m_staticText2.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer3.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		self.m_staticText3.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer3.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_pixelSizeX = wx.TextCtrl( self, wx.ID_ANY, u"0.0423", wx.DefaultPosition, wx.Size( 50,-1 ), wx.TE_RIGHT )
		bSizer3.Add( self.m_pixelSizeX, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		self.m_staticText4.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_pixelSizeY = wx.TextCtrl( self, wx.ID_ANY, u"0.0423", wx.DefaultPosition, wx.Size( 50,-1 ), wx.TE_RIGHT )
		bSizer3.Add( self.m_pixelSizeY, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Z:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		self.m_staticText5.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer3.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_layerHeight = wx.TextCtrl( self, wx.ID_ANY, u"0.055", wx.DefaultPosition, wx.Size( 50,-1 ), wx.TE_RIGHT )
		bSizer3.Add( self.m_layerHeight, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"ｲﾒｰｼﾞｻｲｽﾞ(ﾋﾟｸｾﾙ)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		self.m_staticText12.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer6.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		self.m_staticText13.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer6.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_img_width = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( 58,-1 ), 0 )
		bSizer6.Add( self.m_img_width, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		self.m_staticText14.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer6.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_img_height = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( 58,-1 ), 0 )
		bSizer6.Add( self.m_img_height, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer6, 1, 0, 5 )
		
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"        ﾏｽｸ  分割数", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		self.m_staticText6.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer4.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		self.m_staticText7.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer4.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_maskX = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, 0, 30, 1 )
		bSizer4.Add( self.m_maskX, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		self.m_staticText8.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer4.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_maskY = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, 0, 30, 1 )
		bSizer4.Add( self.m_maskY, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"        ﾌﾞﾛｯｸ分割数", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		self.m_staticText9.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		self.m_staticText10.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_blockX = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, 0, 30, 4 )
		bSizer5.Add( self.m_blockX, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		self.m_staticText11.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_blockY = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, 0, 30, 4 )
		bSizer5.Add( self.m_blockY, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		if int( wx.__version__.split('.')[0]) == 3:
			bSizer5.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		else:
			bSizer5.AddSpacer( 60 )
		
		self.m_button5 = wx.Button( self, wx.ID_ANY, u"実  行", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button5.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_button5, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_filePicker2.Bind( wx.EVT_FILEPICKER_CHANGED, self.OnFileChanged )
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnExecute )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnFileChanged( self, event ):
		event.Skip()
	
	def OnExecute( self, event ):
		event.Skip()
	

