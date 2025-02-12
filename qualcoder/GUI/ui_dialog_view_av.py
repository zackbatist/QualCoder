# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialog_view_av.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_view_av(object):
    def setupUi(self, Dialog_view_av):
        Dialog_view_av.setObjectName("Dialog_view_av")
        Dialog_view_av.resize(1021, 368)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_view_av)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QTextEdit(Dialog_view_av)
        self.textEdit.setMinimumSize(QtCore.QSize(0, 80))
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 80))
        self.textEdit.setTabChangesFocus(True)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 7, 0, 1, 1)
        self.textEdit_transcription = QtWidgets.QTextEdit(Dialog_view_av)
        self.textEdit_transcription.setMinimumSize(QtCore.QSize(0, 40))
        self.textEdit_transcription.setMaximumSize(QtCore.QSize(16777215, 167700))
        self.textEdit_transcription.setTabChangesFocus(True)
        self.textEdit_transcription.setObjectName("textEdit_transcription")
        self.gridLayout.addWidget(self.textEdit_transcription, 5, 0, 1, 1)
        self.label_memo = QtWidgets.QLabel(Dialog_view_av)
        self.label_memo.setObjectName("label_memo")
        self.gridLayout.addWidget(self.label_memo, 6, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog_view_av)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 90))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 70))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButton_play = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_play.setGeometry(QtCore.QRect(10, 30, 85, 27))
        self.pushButton_play.setObjectName("pushButton_play")
        self.pushButton_stop = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_stop.setGeometry(QtCore.QRect(110, 30, 85, 27))
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.horizontalSlider_vol = QtWidgets.QSlider(self.groupBox_2)
        self.horizontalSlider_vol.setGeometry(QtCore.QRect(640, 40, 160, 18))
        self.horizontalSlider_vol.setMaximum(100)
        self.horizontalSlider_vol.setProperty("value", 100)
        self.horizontalSlider_vol.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_vol.setObjectName("horizontalSlider_vol")
        self.label_volume = QtWidgets.QLabel(self.groupBox_2)
        self.label_volume.setGeometry(QtCore.QRect(570, 40, 61, 20))
        self.label_volume.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_volume.setObjectName("label_volume")
        self.label_time = QtWidgets.QLabel(self.groupBox_2)
        self.label_time.setGeometry(QtCore.QRect(220, 40, 161, 21))
        self.label_time.setObjectName("label_time")
        self.label_time_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_time_2.setGeometry(QtCore.QRect(410, 40, 161, 21))
        self.label_time_2.setObjectName("label_time_2")
        self.horizontalSlider = QtWidgets.QSlider(self.groupBox_2)
        self.horizontalSlider.setGeometry(QtCore.QRect(0, -10, 1003, 34))
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(1000)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setProperty("value", 0)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(10)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.comboBox_tracks = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_tracks.setGeometry(QtCore.QRect(938, 33, 61, 28))
        self.comboBox_tracks.setObjectName("comboBox_tracks")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(840, 40, 91, 20))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.checkBox_scroll_transcript = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_scroll_transcript.setGeometry(QtCore.QRect(10, 61, 511, 22))
        self.checkBox_scroll_transcript.setObjectName("checkBox_scroll_transcript")
        self.gridLayout.addWidget(self.groupBox_2, 3, 0, 1, 1)
        self.label_transcription = QtWidgets.QLabel(Dialog_view_av)
        self.label_transcription.setObjectName("label_transcription")
        self.gridLayout.addWidget(self.label_transcription, 4, 0, 1, 1)

        self.retranslateUi(Dialog_view_av)
        QtCore.QMetaObject.connectSlotsByName(Dialog_view_av)
        Dialog_view_av.setTabOrder(self.pushButton_play, self.pushButton_stop)
        Dialog_view_av.setTabOrder(self.pushButton_stop, self.horizontalSlider_vol)
        Dialog_view_av.setTabOrder(self.horizontalSlider_vol, self.textEdit)

    def retranslateUi(self, Dialog_view_av):
        _translate = QtCore.QCoreApplication.translate
        Dialog_view_av.setWindowTitle(_translate("Dialog_view_av", "View Audio Video"))
        self.textEdit.setToolTip(_translate("Dialog_view_av", "<html><head/><body><p>Memo</p></body></html>"))
        self.label_memo.setText(_translate("Dialog_view_av", "Memo:"))
        self.pushButton_play.setText(_translate("Dialog_view_av", "Play"))
        self.pushButton_stop.setText(_translate("Dialog_view_av", "Stop"))
        self.label_volume.setText(_translate("Dialog_view_av", "Volume"))
        self.label_time.setText(_translate("Dialog_view_av", "Time:"))
        self.label_time_2.setText(_translate("Dialog_view_av", "Duration: "))
        self.horizontalSlider.setToolTip(_translate("Dialog_view_av", "<html><head/><body><p>Left click on the slider button and drag left or right to change video position.</p></body></html>"))
        self.label.setText(_translate("Dialog_view_av", "Audio:"))
        self.checkBox_scroll_transcript.setText(_translate("Dialog_view_av", "Scroll transcript while playing. (Transcript is read only)"))
        self.label_transcription.setText(_translate("Dialog_view_av", "Transcription:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_view_av = QtWidgets.QDialog()
    ui = Ui_Dialog_view_av()
    ui.setupUi(Dialog_view_av)
    Dialog_view_av.show()
    sys.exit(app.exec_())

