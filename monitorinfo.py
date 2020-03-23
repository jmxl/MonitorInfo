#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中
from PyQt5.QtWidgets import QApplication, \
                                                               QMainWindow, \
                                                               QDesktopWidget, \
                                                               QInputDialog, \
                                                               QLineEdit, \
                                                               QMessageBox, \
                                                               QPushButton
#导入Qt Designer工具生成的MainWindow
from MainWindow import Ui_MainWindow

class MonitorInfo(QMainWindow, Ui_MainWindow):
   edidBytes = b'\x00'

   def __init__(self, parent=None):
      super(MonitorInfo, self).__init__(parent)
      self.setupUi(self)
      self.center()
      self.pushButton_CheckDevice.clicked.connect(self.updateInfo)
      self.pushButton_AboutMe.clicked.connect(self.showAboutMe)

   #窗口居中
   def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())
   
      #获取EDID  
   def getEDID(self):
      pwdInputDialog = QInputDialog()
      pwdInputDialog.setFixedSize(250, 150)
      pwdInputDialog.setWindowTitle('权限申请')
      pwdInputDialog.setLabelText('请输入root账户密码:')
      pwdInputDialog.setOkButtonText('确认')
      pwdInputDialog.setCancelButtonText('取消')
      pwdInputDialog.setTextEchoMode(QLineEdit.Password)
      pwdInputDialog.setInputMode(QInputDialog.TextInput)
      okPressed = pwdInputDialog.exec_()
      pwd = pwdInputDialog.textValue()
      if okPressed and pwd != '':
         os.system('echo ' + pwd +' | sudo -S get-edid > edid.bin')
         edidFile = open('edid.bin', 'rb')
         self.edidBytes = edidFile.read()
         edidFile.close()
         os.remove('edid.bin')
      else:
         messageBox = QMessageBox()
         messageBox.setWindowTitle('警告')
         messageBox.setText('获取屏幕信息需要root权限, 请正确输入密码!')
         messageBox.addButton(QMessageBox.Yes)
         buttonY = messageBox.button(QMessageBox.Yes)
         buttonY.setText('确定')
         messageBox.exec_()

   #更新显示器信息
   def updateInfo(self):
      self.comboBox_Device.clear()
      self.getEDID()
      self.label_ProductDate.setText(str(self.edidBytes[0x11] + 1990)+"年")
      self.label_EdidVersion.setText(str(self.edidBytes[0x12])+"."+str(self.edidBytes[0x13]))
      deviceString = self.getMonitorDataString()
      self.label_ProductModel.setText(deviceString[1])
      self.comboBox_Device.addItem(deviceString[0])
      colorInfo = self.getClolorInfo()
      self.label_RedX.setText(colorInfo[0])
      self.label_RedY.setText(colorInfo[1])
      self.label_GreenX.setText(colorInfo[2])
      self.label_GreenY.setText(colorInfo[3])
      self.label_BlueX.setText(colorInfo[4])
      self.label_BlueY.setText(colorInfo[5])
      self.label_WhiteX.setText(colorInfo[6])
      self.label_WhiteY.setText(colorInfo[7])
      self.label_Gamut.setText(colorInfo[8])

   def getMonitorDataString(self):
      name = "Unknown"
      serial = "Unknown"
      for i in range(3):
         if self.edidBytes[(0x48 + i*18+3)] == 0xFC:
            name = self.edidBytes[(0x48 + i*18) + 5 : (0x48 + i*18 + 17)].decode('ascii')
         elif self.edidBytes[(0x48 + i*18)+3] == 0xFE:
            serial = self.edidBytes[(0x48 + i*18) + 5 : (0x48 + i*18 + 17)].decode('ascii')
         else:
            continue
         if name == "Unknown":
            name = self.getVendorID()
      return [name, serial]
   
   def getVendorID(self):
      return chr(((self.edidBytes[8] & 0x7C) >> 2) + 0x40) + chr(((self.edidBytes[8] & 0x03) << 3) + ((self.edidBytes[9] & 0xE0) >> 5) + 0x40) + chr((self.edidBytes[9] & 0x1F) + 0x40)

   def getClolorInfo(self):
      redX =  (4 * self.edidBytes[0x1b] + (self.edidBytes[0x19] & 0xC0 >> 6)) / 1023.0
      redY =  (4 * self.edidBytes[0x1c] + (self.edidBytes[0x19] & 0x30 >> 4)) / 1023.0
      greenX =  (4 * self.edidBytes[0x1d] + (self.edidBytes[0x19] & 0x0C >> 2)) / 1023.0
      greenY =  (4 * self.edidBytes[0x1e] + (self.edidBytes[0x19] & 0x03)) / 1023.0
      blueX =  (4 * self.edidBytes[0x1f] + (self.edidBytes[0x1a] & 0xC0 >> 6)) / 1023.0
      blueY =  (4 * self.edidBytes[0x20] + (self.edidBytes[0x1a] & 0x30 >> 4)) / 1023.0
      whiteX =  (4 * self.edidBytes[0x21] + (self.edidBytes[0x1a] & 0x0C >> 2)) / 1023.0
      whiteY =  (4 * self.edidBytes[0x22] + (self.edidBytes[0x1a] & 0x03)) / 1023.0
      ntscGamut = abs(redX * greenY + greenX * blueY + blueX * redY - redX * blueY - greenX * redY - blueX * greenY) / 2 / 0.1582
      return [ '{:.3f}'.format(redX),  '{:.3f}'.format(redY),  '{:.3f}'.format(greenX),  '{:.3f}'.format(greenY),  '{:.3f}'.format(blueX),  '{:.3f}'.format(blueY), '{:.3f}'.format(whiteX), '{:.3f}'.format(whiteY), '{:.2f}% NTSC'.format(ntscGamut*100)]
   def showAboutMe(self):
      messageBox = QMessageBox()
      messageBox.setWindowTitle('关于')
      messageBox.setText("软件: 色域检测\r\n版本: 1.0.0\r\n作者: 九面相柳    ")
      messageBox.addButton(QMessageBox.Yes)
      buttonY = messageBox.button(QMessageBox.Yes)
      buttonY.setText('确定')
      messageBox.exec_()  

if __name__ == "__main__":
   #PyQt5程序需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
   app = QApplication(sys.argv)
   #仅支持Linux
   if (sys.platform == 'linux'):
      qMonitorInfo = MonitorInfo()
      #将窗口控件显示在屏幕上
      qMonitorInfo.show()
   #程序运行，sys.exit方法确保程序完整退出。
   sys.exit(app.exec_())

