# -*- coding: utf-8 -*-

'''
Copyright (c) 2019 Colin Curtain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Colin Curtain (ccbogel)
https://github.com/ccbogel/QualCoder
https://qualcoder.wordpress.com/
'''

from collections import Counter
from copy import deepcopy
import logging
import math
import os
import sys
import traceback

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog

from GUI.ui_visualise_graph import Ui_Dialog_visualiseGraph
from information import DialogInformation
from memo import DialogMemo

path = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


def exception_handler(exception_type, value, tb_obj):
    """ Global exception handler useful in GUIs.
    tb_obj: exception.__traceback__ """
    tb = '\n'.join(traceback.format_tb(tb_obj))
    text = 'Traceback (most recent call last):\n' + tb + '\n' + exception_type.__name__ + ': ' + str(value)
    print(text)
    logger.error(_("Uncaught exception: ") + text)
    QtWidgets.QMessageBox.critical(None, _('Uncaught Exception'), text)


def msecs_to_mins_and_secs(msecs):
    """ Convert milliseconds to minutes and seconds.
    msecs is an integer. Minutes and seconds output is a string."""

    secs = int(msecs / 1000)
    mins = int(secs / 60)
    remainder_secs = str(secs - mins * 60)
    if len(remainder_secs) == 1:
        remainder_secs = "0" + remainder_secs
    return str(mins) + "." + remainder_secs


class ViewGraph(QDialog):
    """ Dialog to view code and categories in an acyclic graph. Provides options for
    colors and amount of nodes to display (based on category selection).
    """

    settings = None
    categories = []
    code_names = []

    def __init__(self, settings):
        """ Set up the dialog. """

        sys.excepthook = exception_handler
        QDialog.__init__(self)
        self.settings = settings
        self.get_data()
        combobox_list = ['All']
        for c in self.categories:
            combobox_list.append(c['name'])
        # Set up the user interface from Designer.
        self.ui = Ui_Dialog_visualiseGraph()
        self.ui.setupUi(self)
        self.ui.comboBox.addItems(combobox_list)
        # set the scene
        self.scene = GraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.ui.pushButton_view.pressed.connect(self.do_graph)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        menu.addAction('sample')
        menu.exec_(event.globalPos())

    def get_data(self):
        """ Called from init and gets all the codes and categories. """

        self.categories = []
        cur = self.settings['conn'].cursor()
        cur.execute("select name, catid, owner, date, memo, supercatid from code_cat order by name")
        result = cur.fetchall()
        for row in result:
            self.categories.append({'name': row[0], 'catid': row[1], 'owner': row[2],
            'date': row[3], 'memo': row[4], 'supercatid': row[5]})
        self.code_names = []
        cur = self.settings['conn'].cursor()
        cur.execute("select name, memo, owner, date, cid, catid, color from code_name")
        result = cur.fetchall()
        for row in result:
            self.code_names.append({'name': row[0], 'memo': row[1], 'owner': row[2], 'date': row[3],
            'cid': row[4], 'catid': row[5], 'color': row[6]})

    def do_graph(self):
        """ Create a circular acyclic graph
        default font size is 8.  """

        self.scene.clear()
        cats = deepcopy(self.categories)
        codes = deepcopy(self.code_names)

        for c in codes:
            c['depth'] = 0
            c['x'] = None
            c['y'] = None
            c['supercatid'] = c['catid']
            c['angle'] = None
            if self.ui.checkBox_blackandwhite.isChecked():
                c['color'] = "#FFFFFF"
            c['fontsize'] = 8
        for c in cats:
            c['depth'] = 0
            c['x'] = None
            c['y'] = None
            c['cid'] = None
            c['angle'] = None
            c['color'] = '#FFFFFF'
            c['fontsize'] = 8
            if self.ui.checkBox_fontsize.isChecked():
                c['fontsize'] = 9
                if c['depth'] == 0:
                    c['fontsize'] = 10
        model = cats + codes

        # Default is all categories and codes
        top_node = self.ui.comboBox.currentText()
        if top_node == "All":
            top_node = None
        for c in cats:
            if c['name'] == top_node:
                top_node = c
        model = self.get_node_with_children(top_node, model)

        ''' Look at each category and determine the depth.
        Also determine the number of children for each catid. '''
        supercatid_list = []
        for c in model:
            supercatid = 0
            depth = 0
            supercatid = c['supercatid']
            supercatid_list.append(c['supercatid'])
            while supercatid is not None:
                for s in cats:
                    if supercatid == s['catid']:
                        depth += 1
                        supercatid = s['supercatid']
                c['depth'] = depth
        catid_counts = Counter(supercatid_list)

        # assign angles to each item segment
        for cat_key in catid_counts.keys():
            #logger.debug("cat_key:" + cat_key + "", catid_counts[cat_key]:" + str(catid_counts[cat_key]))
            segment = 1
            for m in model:
                if m['angle'] is None and m['supercatid'] == cat_key:
                    m['angle'] = (2 * math.pi / catid_counts[m['supercatid']]) * (segment + 1)
                    segment += 1
        ''' Calculate x y positions from central point outwards.
        The 'central' x value is towards the left side rather than true center, because
        the text boxes will draw to the right-hand side.
        '''
        c_x = self.scene.getWidth() / 3
        c_y = self.scene.getHeight() / 2
        r = 180
        rx_expander = c_x / c_y  # screen is landscape, so stretch x position
        x_is_none = True
        i = 0
        while x_is_none and i < 1000:
            x_is_none = False
            for m in model:
                if m['x'] is None and m['supercatid'] is None:
                    m['x'] = c_x + (math.cos(m['angle']) * (r * rx_expander))
                    m['y'] = c_y + (math.sin(m['angle']) * r)
                if m['x'] is None and m['supercatid'] is not None:
                    for super_m in model:
                        if super_m['catid'] == m['supercatid'] and super_m['x'] is not None:
                            m['x'] = super_m['x'] + (math.cos(m['angle']) * (r * rx_expander) / (m['depth'] + 2))
                            m['y'] = super_m['y'] + (math.sin(m['angle']) * r / (m['depth'] + 2))
                            if abs(super_m['x'] - m['x']) < 20 and abs(super_m['y'] - m['y']) < 20:
                                m['x'] += 20
                                m['y'] += 20
                if m['x'] is None:
                    x_is_none = True
            i += 1

        # Fix out of view items
        for m in model:
            if m['x'] < 2:
                m['x'] = 2
            if m['y'] < 2:
                m['y'] = 2
            if m['x'] > c_x * 2 - 20:
                m['x'] = c_x * 2 - 20
            if m['y'] > c_y * 2 - 20:
                m['y'] = c_y * 2 - 20

        # Add text items to the scene
        for m in model:
            self.scene.addItem(TextGraphicsItem(self.settings, m))
        # Add link which includes the scene text items and associated data, add links before text_items
        for m in self.scene.items():
            if isinstance(m, TextGraphicsItem):
                for n in self.scene.items():
                    if isinstance(n, TextGraphicsItem) and m.data['supercatid'] is not None and m.data['supercatid'] == n.data['catid'] and n.data['depth'] < m.data['depth']:
                        #item = QtWidgets.QGraphicsLineItem(m['x'], m['y'], super_m['x'], super_m['y'])  # xy xy
                        item = LinkGraphicsItem(m, n)
                        self.scene.addItem(item)

    def get_node_with_children(self, node, model):
        """ Return a short list of this top node and all its children.
        Note, maximum depth of 10. """
        if node is None:
            return model
        new_model = [node]
        i = 0  # not really needed, but keep for ensuring an exit from while loop
        new_model_changed = True
        while model != [] and new_model_changed and i < 10:
            new_model_changed = False
            append_list = []
            for n in new_model:
                for m in model:
                    if m['supercatid'] == n['catid']:
                        append_list.append(m)
            for n in append_list:
                new_model.append(n)
                model.remove(n)
                new_model_changed = True
            i += 1
        return new_model

    def reject(self):

        self.dialog_list = []
        super(ViewGraph, self).reject()

    def accept(self):

        self.dialog_list = []
        super(ViewGraph, self).accept()


# http://stackoverflow.com/questions/17891613/pyqt-mouse-events-for-qgraphicsview
class GraphicsScene(QtWidgets.QGraphicsScene):
    """ set the scene for the graphics objects and re-draw events. """

    # matches the initial designer file graphics view
    sceneWidth = 982
    sceneHeight = 647

    def __init__ (self, parent=None):
        super(GraphicsScene, self).__init__ (parent)
        self.setSceneRect(QtCore.QRectF(0, 0, self.sceneWidth, self.sceneHeight))

    def setWidth(self, width):
        """ Resize scene width. """

        self.sceneWidth = width
        self.setSceneRect(QtCore.QRectF(0, 0, self.sceneWidth, self.sceneHeight))

    def setHeight(self, height):
        """ Resize scene height. """

        self.sceneHeight = height
        self.setSceneRect(QtCore.QRectF(0, 0, self.sceneWidth, self.sceneHeight))

    def getWidth(self):
        """ Return scene width. """

        return self.sceneWidth

    def getHeight(self):
        """ Return scene height. """

        return self.sceneHeight

    def mouseMoveEvent(self, mouseEvent):
        """ On mouse move, an item might be repositioned so need to redraw all the link_items.
        This slows re-drawing down, but is more dynamic. """

        super(GraphicsScene, self).mousePressEvent(mouseEvent)

        for item in self.items():
            if isinstance(item, TextGraphicsItem):
                item.data['x'] = item.pos().x()
                item.data['y'] = item.pos().y()
                #logger.debug("item pos:" + str(item.pos()))
        for item in self.items():
            if isinstance(item, LinkGraphicsItem):
                item.redraw()
        self.update()

        '''def mousePressEvent(self, mouseEvent):
        super(GraphicsScene, self).mousePressEvent(mouseEvent)
        #position = QtCore.QPointF(event.scenePos())
        #logger.debug("pressed here: " + str(position.x()) + ", " + str(position.y()))
        for item in self.items(): # item is QGraphicsProxyWidget
            if isinstance(item, LinkItem):
                item.redraw()
        self.update(self.sceneRect())'''

    """def mouseReleaseEvent(self, mouseEvent):
        ''' On mouse release, an item might be repositioned so need to redraw all the
        link_items '''

        super(GraphicsScene, self).mouseReleaseEvent(mouseEvent)
        for item in self.items():
            if isinstance(item, LinkGraphicsItem):
                item.redraw()
        self.update(self.sceneRect())"""


class TextGraphicsItem(QtWidgets.QGraphicsTextItem):
    """ The item show the name and color of the code or category
    Categories are typically shown white, and category font sizes can be enlarged using a
    checkbox and code colours can be ignores using a check box. A custom context menu
    allows selection of a code/category memo an displaying the information.
    """

    data = None
    border_rect = None
    font = None
    settings = None

    def __init__(self, settings, data):
        super(TextGraphicsItem, self).__init__(None)

        self.settings = settings
        self.data = data
        self.setFlags (QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsFocusable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.font = QtGui.QFont(self.settings['font'], self.data['fontsize'], QtGui.QFont.Normal)
        self.setFont(self.font)
        self.setPlainText(self.data['name'])
        if self.data['cid'] is None:
            self.setPlainText(self.data['name'])
        self.setPos(self.data['x'], self.data['y'])
        self.document().contentsChanged.connect(self.text_changed)
        #self.border_rect = QtWidgets.QGraphicsRectItem(0, 0, rect.width(), rect.height())
        #self.border_rect.setParentItem(self)

    def paint(self, painter, option, widget):
        """ see paint override method here:
            https://github.com/jsdir/giza/blob/master/giza/widgets/nodeview/node.py
            see:
            https://doc.qt.io/qt-5/qpainter.html """

        color = QtGui.QColor(self.data['color'])
        painter.setBrush(QtGui.QBrush(color, style=QtCore.Qt.SolidPattern))
        painter.drawRect(self.boundingRect())
        #logger.debug("bounding rect:" + str(self.boundingRect()))
        painter.setFont(self.font)
        #fi = painter.fontInfo()
        #logger.debug("Font:", fi.family(), " Pixelsize:",fi.pixelSize(), " Pointsize:", fi.pointSize(), " Style:", fi.style())
        fm = painter.fontMetrics()
        #logger.debug("Font height: ", fm.height())
        painter.setPen(QtCore.Qt.black)
        lines = self.data['name'].split('\n')
        for row in range(0, len(lines)):
            #painter.drawText(5,fm.height(),self.data['name'])
            painter.drawText(5, fm.height() * (row + 1), lines[row])

    def text_changed(self):
        """ Text changed in a node. Redraw the border rectangle item to match. """

        #rect = self.boundingRect()
        #self.border_rect.setRect(0, 0, rect.width(), rect.height())
        self.data['name'] = self.toPlainText()
        #logger.debug("self.data[name]:" + self.data['name'])

    def contextMenuEvent(self, event):
        """
        # https://riverbankcomputing.com/pipermail/pyqt/2010-July/027094.html
        I was not able to mapToGlobal position so, the menu maps to scene position plus
        the Dialog screen position.
        """

        menu = QtWidgets.QMenu()
        menu.addAction('Memo')
        if self.data['cid'] is not None:
            menu.addAction('Coded text and media')
            menu.addAction('Case text and media')
        action = menu.exec_(QtGui.QCursor.pos())
        if action is None:
            return
        if action.text() == 'Memo':
            self.add_edit_memo(self.data)
        if action.text() == 'Coded text and media':
            self.coded_media(self.data)
        if action.text() == 'Case text and media':
            self.case_media(self.data)

    def add_edit_memo(self, data):
        """ Add or edit memos for codes and categories. """

        if data['cid'] is not None:
            ui = DialogMemo(self.settings, "Memo for Code " + data['name'], data['memo'])
            ui.exec_()
            self.data['memo'] = ui.memo
            cur = self.settings['conn'].cursor()
            cur.execute("update code_name set memo=? where cid=?", (self.data['memo'], self.data['cid']))
            self.settings['conn'].commit()
        if data['catid'] is not None and data['cid'] is None:
            ui = DialogMemo(self.settings, "Memo for Category " + data['name'], data['memo'])
            ui.exec_()
            self.data['memo'] = ui.memo
            cur = self.settings['conn'].cursor()
            cur.execute("update code_cat set memo=? where catid=?", (self.data['memo'], self.data['catid']))
            self.settings['conn'].commit()

    def case_media(self, data):
        """ Display all coded text and media for this code.
        Codings come from ALL files and ALL coders. """

        ui = DialogInformation("Coded media for cases: " + self.data['name'], "")
        cur = self.settings['conn'].cursor()
        CODENAME = 0
        COLOR = 1
        CASE_NAME = 2
        POS0 = 3
        POS1 = 4
        SELTEXT = 5
        OWNER = 6
        # Text
        sql = "select code_name.name, color, cases.name, "
        sql += "code_text.pos0, code_text.pos1, seltext, code_text.owner from code_text "
        sql += " join code_name on code_name.cid = code_text.cid "
        sql += " join (case_text join cases on cases.caseid = case_text.caseid) on "
        sql += " code_text.fid = case_text.fid "
        sql += "and (code_text.pos0 between case_text.pos0 and case_text.pos1) "
        sql += "and (code_text.pos1 between case_text.pos0 and case_text.pos1) "
        sql += " where code_name.cid=" + str(self.data['cid'])
        sql += " order by cases.name, code_text.pos0, code_text.owner "

        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            color = row[COLOR]
            title = '<br /><span style=\"background-color:' + color + '\">'
            title += " Case: <em>" + row[CASE_NAME] + "</em></span>"
            title += ", Coder: <em>" + row[OWNER] + "</em> "
            title += ", " + str(row[POS0]) + " - " + str(row[POS1])
            title += "<br />"
            tmp_html = row[SELTEXT].replace("&", "&amp;")
            tmp_html = tmp_html.replace("<", "&lt;")
            tmp_html = tmp_html.replace(">", "&gt;")
            html = title + tmp_html + "</p><br />"
            ui.ui.textEdit.insertHtml(html)

        # Images
        sql = "select code_name.name, color, cases.name, "
        sql += "x1, y1, width, height, code_image.owner,source.mediapath, source.id, "
        sql += "code_image.memo from "
        sql += "code_image join code_name on code_name.cid = code_image.cid "
        sql += "join (case_text join cases on cases.caseid = case_text.caseid) on "
        sql += "code_image.id = case_text.fid "
        sql += " join source on case_text.fid = source.id "
        sql += "where code_name.cid = " + str(self.data['cid']) + " "
        sql += " order by cases.name, code_image.owner "
        cur.execute(sql)
        results = cur.fetchall()
        for counter, row in enumerate(results):
            color = row[COLOR]
            title = '<br /><span style=\"background-color:' + color + '\">'
            title += " Case: <em>" + row[CASE_NAME] + "</em></span>, File:" + row[8] + ", "
            title += "Coder: " + row[7]
            ui.ui.textEdit.insertHtml(title)
            img = {'mediapath': row[8], 'x1': row[3], 'y1': row[4], 'width': row[5], 'height': row[6]}
            self.put_image_into_textedit(img, counter, ui.ui.textEdit)
            ui.ui.textEdit.append("Memo: " + row[10] + "\n\n")

        # A/V Media
        sql = "select code_name.name, color, cases.name, "
        sql += "code_av.pos0, code_av.pos1, code_av.memo, code_av.owner,source.mediapath, "
        sql += "source.id from "
        sql += "code_av join code_name on code_name.cid = code_av.cid "
        sql += "join (case_text join cases on cases.caseid = case_text.caseid) on "
        sql += "code_av.id = case_text.fid "
        sql += " join source on case_text.fid = source.id "
        sql += "where code_name.cid = " + str(self.data['cid'])
        sql += " order by source.name, code_av.owner "
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            html = '<span style=\"background-color:' + row[COLOR] + '\">Case: ' + row[CASE_NAME]
            html += ', File: ' + row[7] + '</span>'
            ui.ui.textEdit.insertHtml(html)
            start = msecs_to_mins_and_secs(row[3])
            end = msecs_to_mins_and_secs(row[4])
            ui.ui.textEdit.insertHtml('<br />[' + start + ' - ' + end + '] Coder: ' + row[6])
            ui.ui.textEdit.append("Memo: " + row[5] + "\n\n")

        ui.exec_()

    def put_image_into_textedit(self, img, counter, text_edit):
        """ Scale image, add resource to document, insert image.
        A counter is important as each image slice needs a unique name, counter adds
        the uniqueness to the name.
        """

        path = self.settings['path'] + img['mediapath']
        document = text_edit.document()
        image = QtGui.QImageReader(path).read()
        image = image.copy(img['x1'], img['y1'], img['width'], img['height'])
        # scale to max 300 wide or high. perhaps add option to change maximum limit?
        scaler = 1.0
        scaler_w = 1.0
        scaler_h = 1.0
        if image.width() > 300:
            scaler_w = 300 / image.width()
        if image.height() > 300:
            scaler_h = 300 / image.height()
        if scaler_w < scaler_h:
            scaler = scaler_w
        else:
            scaler = scaler_h
        # need unique image names or the same image from the same path is reproduced
        imagename = self.settings['path'] + '/images/' + str(counter) + '-' + img['mediapath']
        url = QtCore.QUrl(imagename)
        document.addResource(QtGui.QTextDocument.ImageResource, url, QtCore.QVariant(image))
        cursor = text_edit.textCursor()
        image_format = QtGui.QTextImageFormat()
        image_format.setWidth(image.width() * scaler)
        image_format.setHeight(image.height() * scaler)
        image_format.setName(url.toString())
        cursor.insertImage(image_format)
        text_edit.insertHtml("<br />")

    def coded_media(self, data):
        """ Display all coded media for this code.
        Coded media comes from ALL files and ALL coders. """

        ui = DialogInformation("Coded text : " + self.data['name'], "")
        cur = self.settings['conn'].cursor()
        CODENAME = 0
        COLOR = 1
        SOURCE_NAME = 2
        POS0 = 3
        POS1 = 4
        SELTEXT = 5
        OWNER = 6
        sql = "select code_name.name, color, source.name, pos0, pos1, seltext, code_text.owner from "
        sql += "code_text "
        sql += " join code_name on code_name.cid = code_text.cid join source on fid = source.id "
        sql += " where code_name.cid =" + str(self.data['cid']) + " "
        sql += " order by source.name, pos0, code_text.owner "
        cur.execute(sql)
        results = cur.fetchall()
        # Text
        for row in results:
            title = '<span style=\"background-color:' + row[COLOR] + '\">'
            title += " File: <em>" + row[SOURCE_NAME] + "</em></span>"
            title += ", Coder: <em>" + row[OWNER] + "</em> "
            title += ", " + str(row[POS0]) + " - " + str(row[POS1])
            ui.ui.textEdit.insertHtml(title)
            ui.ui.textEdit.append(row[SELTEXT] + "\n\n")

        # Images
        sql = "select code_name.name, color, source.name, x1, y1, width, height,"
        sql += "code_image.owner, source.mediapath, source.id, code_image.memo "
        sql += " from code_image join code_name "
        sql += "on code_name.cid = code_image.cid join source on code_image.id = source.id "
        sql += "where code_name.cid =" + str(self.data['cid']) + " "
        sql += " order by source.name, code_image.owner "
        cur.execute(sql)
        results = cur.fetchall()
        for counter, row in enumerate(results):
            ui.ui.textEdit.insertHtml('<span style=\"background-color:' + row[COLOR] + '\">File: ' + row[8] + '</span>')
            ui.ui.textEdit.insertHtml('<br />Coder: ' + row[7]  + '<br />')
            img = {'mediapath': row[8], 'x1': row[3], 'y1': row[4], 'width': row[5], 'height': row[6]}
            self.put_image_into_textedit(img, counter, ui.ui.textEdit)
            ui.ui.textEdit.append("Memo: " + row[10] + "\n\n")

        # Media
        sql = "select code_name.name, color, source.name, pos0, pos1, code_av.memo, "
        sql += "code_av.owner, source.mediapath, source.id from code_av join code_name "
        sql += "on code_name.cid = code_av.cid join source on code_av.id = source.id "
        sql += "where code_name.cid = " + str(self.data['cid']) + " "
        sql += " order by source.name, code_av.owner "
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            ui.ui.textEdit.insertHtml('<span style=\"background-color:' + row[COLOR] + '\">File: ' + row[7] + '</span>')
            start = msecs_to_mins_and_secs(row[3])
            end = msecs_to_mins_and_secs(row[4])
            ui.ui.textEdit.insertHtml('<br />[' + start + ' - ' + end + '] Coder: ' + row[6])
            ui.ui.textEdit.append("Memo: " + row[5] + "\n\n")
        ui.exec_()


class LinkGraphicsItem(QtWidgets.QGraphicsLineItem):
    """ Takes the coordinate from the two TextGraphicsItems. """

    from_widget = None
    from_pos = None
    to_widget = None
    to_pos = None

    def __init__(self, from_widget, to_widget):
        super(LinkGraphicsItem, self).__init__(None)

        self.from_widget = from_widget
        self.to_widget = to_widget
        self.setFlag(self.ItemIsSelectable, True)
        self.calculatePointsAndDraw()

    def redraw(self):
        """ Called from mouse move and release events. """

        self.calculatePointsAndDraw()

    def calculatePointsAndDraw(self):
        """ Calculate the to x and y and from x and y points. Draw line between the
        widgets. Join the line to appropriate side of widget. """

        to_x = self.to_widget.pos().x()
        to_y = self.to_widget.pos().y()
        from_x = self.from_widget.pos().x()
        from_y = self.from_widget.pos().y()

        x_overlap = False
        # fix from_x value to middle of from widget if to_widget overlaps in x position
        if to_x > from_x and to_x < from_x + self.from_widget.boundingRect().width():
            from_x = from_x + self.from_widget.boundingRect().width() / 2
            x_overlap = True
        # fix to_x value to middle of to widget if from_widget overlaps in x position
        if from_x > to_x and from_x < to_x + self.to_widget.boundingRect().width():
            to_x = to_x + self.to_widget.boundingRect().width() / 2
            x_overlap = True

        # fix from_x value to right-hand side of from widget if to_widget on the right of the from_widget
        if not x_overlap and to_x > from_x + self.from_widget.boundingRect().width():
            from_x = from_x + self.from_widget.boundingRect().width()
        # fix to_x value to right-hand side if from_widget on the right of the to widget
        elif not x_overlap and from_x > to_x + self.to_widget.boundingRect().width():
            to_x = to_x + self.to_widget.boundingRect().width()

        y_overlap = False
        # fix from_y value to middle of from widget if to_widget overlaps in y position
        if to_y > from_y and to_y < from_y + self.from_widget.boundingRect().height():
            from_y = from_y + self.from_widget.boundingRect().height() / 2
            y_overlap = True
        # fix from_y value to middle of to widget if from_widget overlaps in y position
        if from_y > to_y and from_y < to_y + self.to_widget.boundingRect().height():
            to_y = to_y + self.to_widget.boundingRect().height() / 2
            y_overlap = True

        # fix from_y value if to_widget is above the from_widget
        if not y_overlap and to_y > from_y:
            from_y = from_y + self.from_widget.boundingRect().height()
        # fix to_y value if from_widget is below the to widget
        elif not y_overlap and from_y > to_y:
            to_y = to_y + self.to_widget.boundingRect().height()

        linkWidth = 1
        self.setPen(QtGui.QPen(QtCore.Qt.black, linkWidth, QtCore.Qt.SolidLine))
        self.setLine(from_x, from_y, to_x, to_y)


