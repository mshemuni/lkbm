from logging import getLogger


from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QDialog, QVBoxLayout, \
    QComboBox, QTextEdit, QPushButton, QLabel

from pardus import SSHConnector

SCHEMA = {"primary": "#F5AE71"}

from PyQt5 import QtCore, QtWidgets, QtGui
import sys

class QToaster(QtWidgets.QFrame):
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QToaster, self).__init__(*args, **kwargs)
        QtWidgets.QHBoxLayout(self)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)

        self.setStyleSheet('''
            QToaster {
                border: 1px solid black;
                border-radius: 0px; 
                color: rgb(255, 255, 255);
                background-color: rgb(57, 66, 81);
            }
        ''')
        # alternatively:
        # self.setAutoFillBackground(True)
        # self.setFrameShape(self.Box)

        self.timer = QtCore.QTimer(singleShot=True, timeout=self.hide)

        if self.parent():
            self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
            self.setGraphicsEffect(self.opacityEffect)
            self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b'opacity')
            # we have a parent, install an eventFilter so that when it's resized
            # the notification will be correctly moved to the right corner
            self.parent().installEventFilter(self)
        else:
            # there's no parent, use the window opacity property, assuming that
            # the window manager supports it; if it doesn't, this won'd do
            # anything (besides making the hiding a bit longer by half a second)
            self.opacityAni = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(100)
        self.opacityAni.finished.connect(self.checkClosed)

        self.corner = QtCore.Qt.TopLeftCorner
        self.margin = 10

    def checkClosed(self):
        # if we have been fading out, we're closing the notification
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.close()

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacityAni.stop()
        # ...and restore the opacity
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacityAni.setDirection(self.opacityAni.Backward)
        self.opacityAni.setDuration(500)
        self.opacityAni.start()

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacityAni.stop()
            parentRect = self.parent().rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.TopLeftCorner:
                geo.moveTopLeft(
                    parentRect.topLeft() + QtCore.QPoint(self.margin, self.margin))
            elif self.corner == QtCore.Qt.TopRightCorner:
                geo.moveTopRight(
                    parentRect.topRight() + QtCore.QPoint(-self.margin, self.margin))
            elif self.corner == QtCore.Qt.BottomRightCorner:
                geo.moveBottomRight(
                    parentRect.bottomRight() + QtCore.QPoint(-self.margin, -self.margin))
            else:
                geo.moveBottomLeft(
                    parentRect.bottomLeft() + QtCore.QPoint(self.margin, -self.margin))
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).eventFilter(source, event)

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.deleteLater()

    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        # if you don't set a stylesheet, you don't need any of the following!
        if not self.parent():
            # there's no parent, so we need to update the mask
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()).translated(-.5, -.5), 4, 4)
            self.setMask(QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon()))
        else:
            self.clearMask()

    @staticmethod
    def show_message(parent, message,
                     icon=QtWidgets.QStyle.SP_MessageBoxInformation,
                     corner=QtCore.Qt.TopLeftCorner, margin=10, closable=True,
                     timeout=5000, desktop=False, parentWindow=True):

        if parent and parentWindow:
            parent = parent.window()

        if not parent or desktop:
            self = QToaster(None)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.BypassWindowManagerHint)
            # This is a dirty hack!
            # parentless objects are garbage collected, so the widget will be
            # deleted as soon as the function that calls it returns, but if an
            # object is referenced to *any* other object it will not, at least
            # for PyQt (I didn't test it to a deeper level)
            self.__self = self

            currentScreen = QtWidgets.QApplication.primaryScreen()
            if parent and parent.window().geometry().size().isValid():
                # the notification is to be shown on the desktop, but there is a
                # parent that is (theoretically) visible and mapped, we'll try to
                # use its geometry as a reference to guess which desktop shows
                # most of its area; if the parent is not a top level window, use
                # that as a reference
                reference = parent.window().geometry()
            else:
                # the parent has not been mapped yet, let's use the cursor as a
                # reference for the screen
                reference = QtCore.QRect(
                    QtGui.QCursor.pos() - QtCore.QPoint(1, 1),
                    QtCore.QSize(3, 3))
            maxArea = 0
            for screen in QtWidgets.QApplication.screens():
                intersected = screen.geometry().intersected(reference)
                area = intersected.width() * intersected.height()
                if area > maxArea:
                    maxArea = area
                    currentScreen = screen
            parentRect = currentScreen.availableGeometry()
        else:
            self = QToaster(parent)
            parentRect = parent.rect()

        self.timer.setInterval(timeout)


        self.label = QtWidgets.QLabel(message)
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        font = QtGui.QFont()
        font.setFamily("IRANYekanWeb")
        font.setPointSize(10)
        font.setWeight(100)
        self.label.setFont(font)
        self.layout().addWidget(self.label)

        if closable:
            self.closeButton = QtWidgets.QToolButton()
            self.layout().addWidget(self.closeButton)
            closeIcon = self.style().standardIcon(
                QtWidgets.QStyle.SP_TitleBarCloseButton)
            self.closeButton.setIcon(closeIcon)
            self.closeButton.setAutoRaise(True)
            self.closeButton.clicked.connect(self.close)

        self.timer.start()

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.adjustSize()

        self.corner = corner
        self.margin = margin

        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        if corner == QtCore.Qt.TopLeftCorner:
            geo.moveTopLeft(
                parentRect.topLeft() + QtCore.QPoint(margin, margin))
        elif corner == QtCore.Qt.TopRightCorner:
            geo.moveTopRight(
                parentRect.topRight() + QtCore.QPoint(-margin, margin))
        elif corner == QtCore.Qt.BottomRightCorner:
            geo.moveBottomRight(
                parentRect.bottomRight() + QtCore.QPoint(-margin, -margin))
        else:
            geo.moveBottomLeft(
                parentRect.bottomLeft() + QtCore.QPoint(margin, -margin))

        self.setGeometry(geo)
        self.show()
        self.opacityAni.start()


class ItemDescriptionDialog(QDialog):
    def __init__(self, parent, caption, label, items_with_descriptions):
        super().__init__(parent)
        self.setWindowTitle(caption)
        self.resize(400, 150)

        # Main layout
        main_layout = QVBoxLayout()

        # Dropdown (QComboBox) and text area side-by-side (horizontal layout)
        dropdown_layout = QVBoxLayout()

        self.label = QLabel(label)

        # Dropdown widget
        self.combo_box = QComboBox()
        self.combo_box.addItems(items_with_descriptions.keys())
        self.combo_box.currentIndexChanged.connect(self.display_description)

        # Text area for description
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)

        # Ok button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        # Adding widgets to the dropdown layout
        dropdown_layout.addWidget(self.label)
        dropdown_layout.addWidget(self.combo_box)
        dropdown_layout.addWidget(self.description_text)

        # Adding dropdown layout and ok button to main layout
        main_layout.addLayout(dropdown_layout)
        main_layout.addWidget(ok_button)

        self.setLayout(main_layout)

        self.items_with_descriptions = items_with_descriptions

        # Display description for the first item initially
        self.display_description()

    def display_description(self):
        current_item_text = self.combo_box.currentText()
        description = self.items_with_descriptions.get(current_item_text, "")
        self.description_text.setText(description)


class CustomQTreeWidgetItem(QTreeWidgetItem):
    def __hash__(self):
        return id(self)


class GUIFunctions:
    def __init__(self, logger=None):

        if logger is None:
            self.logger = getLogger(__file__)
        else:
            self.logger = logger

    def error(self, parent, text):
        QMessageBox.critical(parent, "Pardus", text)

    def warning(self, parent, text):
        QMessageBox.warning(parent, "Pardus", text)

    def information(self, parent, text):
        QMessageBox.information(parent, "Pardus", text)

    def get_file(self, parent, caption, file_type=None):
        try:
            if file_type is not None:
                file_type_to_use = file_type
            else:
                file_type_to_use = "fits, fit, fts (*.fits *.fit *.fts)"

            file, _ = QtWidgets.QFileDialog.getOpenFileName(parent, caption, '', file_type_to_use)
            return file
        except Exception as e:
            self.logger.error(e)
            return ""

    def get_files(self, parent, caption, file_type=None):
        try:
            if file_type is not None:
                file_type_to_use = file_type
            else:
                file_type_to_use = "fits, fit, fts (*.fits *.fit *.fts)"

            files, _ = QtWidgets.QFileDialog.getOpenFileNames(parent, caption, '', file_type_to_use)
            return files
        except Exception as e:
            self.logger.error(e)
            return []

    def get_directory(self, parent, caption):
        try:
            directory = QtWidgets.QFileDialog.getExistingDirectory(parent, caption)
            return directory
        except Exception as e:
            self.logger.error(e)
            return ""

    def save_file(self, parent, caption, file_type_to_use):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(parent, caption, filter=file_type_to_use)

        return file

    def get_selected_connections(self, tree_widget):
        selected_items_dict = {}

        def traverse_item(item: QTreeWidgetItem):
            if item.isSelected():
                selected_items_dict[item] = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    selected_items_dict[item].append(child)
            else:
                child_selected = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    if child.isSelected():
                        child_selected.append(child)
                if child_selected:
                    selected_items_dict[item] = child_selected

        root_count = tree_widget.topLevelItemCount()
        for i in range(root_count):
            root = tree_widget.topLevelItem(i)
            traverse_item(root)

        return selected_items_dict

    def remove_from_files(self, tree_widget):
        selected_items_dict = self.get_selected_connections(tree_widget)
        for parent, children in selected_items_dict.items():
            for child in children:
                parent.removeChild(child)

            if parent.childCount() == 0:
                tree_widget.takeTopLevelItem(tree_widget.indexOfTopLevelItem(parent))

    def get_number(self, parent, caption, text, min_val=0, max_val=100, step_val=1, default=0):
        number, ok = QtWidgets.QInputDialog.getInt(
            parent, caption, text, min=min_val, max=max_val, step=step_val, value=default
        )
        return number, ok

    def get_text(self, parent, caption, text, default=None):
        text, ok = QtWidgets.QInputDialog.getText(parent, caption, text, text=default)
        return text, ok

    def get_item(self, parent, caption, label, items):
        item, ok = QtWidgets.QInputDialog.getItem(parent, caption, label, items)
        return item, ok

    def get_item_description(self, parent, caption, label, items):
        dialog = ItemDescriptionDialog(parent, caption, label, items)
        if dialog.exec_() == QDialog.Accepted:
            selected_item = dialog.combo_box.currentIndex()

        return selected_item


    def ask(self, parent, caption, question):
        answer = QtWidgets.QMessageBox.question(parent, caption, question,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)

        return answer == QtWidgets.QMessageBox.Yes

    def add_to_combo(self, combo_widget, items):
        combo_widget.addItems(items)

    def clear_table(self, table_widget):
        while table_widget.rowCount() > 0:
            table_widget.removeRow(0)

    def get_from_table(self, table_widget):
        number_of_rows = table_widget.rowCount()
        number_of_columns = table_widget.columnCount()
        ret = []
        if number_of_rows > 0 and number_of_columns > 0:
            for i in range(number_of_rows):
                row = []
                for j in range(number_of_columns):
                    row.append(table_widget.item(i, j).text())

                ret.append(row)

            return ret

        return []

    def get_from_table_selected(self, table_widget):
        ret = []
        for i in table_widget.selectionModel().selectedRows():
            row = []
            for j in range(table_widget.columnCount()):
                row.append(table_widget.item(i.row(), j).text())
            ret.append(row)

        return ret

    def add_to_table(self, data, table_widget):
        for line in data:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            for it, value in enumerate(line):
                table_widget.setItem(row_position, it, QtWidgets.QTableWidgetItem(str(value)))

    def remove_from_table(self, table_widget):
        selected_rows = list(set([index.row() for index in table_widget.selectedIndexes()]))
        selected_rows.sort(reverse=True)
        for row in selected_rows:
            table_widget.removeRow(row)

    def add_to_list(self, list_widget, data):
        it = list_widget.count() - 1
        for x in data:
            it = it + 1
            item = QtWidgets.QListWidgetItem()
            list_widget.addItem(item)
            item = list_widget.item(it)
            item.setText(x)

    def get_from_list(self, list_widget):
        return [
            list_widget.item(x).text()
            for x in range(list_widget.count())
        ]

    def get_from_list_selected(self, list_widget):
        return [
            x.text()
            for x in list_widget.selectedItems()
        ]

    def remove_from_list(self, list_widget):
        for x in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(x))

    def add_to_connections(self, parent, connection: SSHConnector, tree_widget):
        connection_layer = CustomQTreeWidgetItem(tree_widget, [connection.address])
        connection_layer.setFirstColumnSpanned(True)

        item_port = CustomQTreeWidgetItem(connection_layer, ["port", connection.port.__str__()])
        item_port.setFlags(QtCore.Qt.ItemIsEnabled)
        item_user_name = CustomQTreeWidgetItem(connection_layer, ["username", connection.user.__str__()])
        item_user_name.setFlags(QtCore.Qt.ItemIsEnabled)
        item_password = CustomQTreeWidgetItem(connection_layer, ["password", "*" * 12])
        item_password.setFlags(QtCore.Qt.ItemIsEnabled)
        connection_layer.password = connection.passwd

    def remove_from_connections(self, tree_widget):
        selected_items_dict = self.get_selected_connections(tree_widget)
        for parent, children in selected_items_dict.items():
            for child in children:
                parent.removeChild(child)

            if parent.childCount() == 0:
                tree_widget.takeTopLevelItem(tree_widget.indexOfTopLevelItem(parent))

    def add_to_services(self, parent, data, tree_widget):
        tree_widget.clear()
        for unit, values in data.items():
            unit_layer = CustomQTreeWidgetItem(tree_widget, [unit])
            unit_layer.setFirstColumnSpanned(True)
            for address, val in values.items():
                item = CustomQTreeWidgetItem(unit_layer, [address] + list(val.values()))
                item.setFlags(QtCore.Qt.ItemIsEnabled)

                if val["active"] in ["active"]:
                    unit_layer.setBackground(0, QBrush(QColor("lightgreen")))
                elif val["active"] in ["inactive"]:
                    unit_layer.setBackground(0, QBrush(QColor("pink")))
                elif val["active"] == "dead":
                    unit_layer.setBackground(0, QBrush(QColor("pink")))

        tree_widget.sortItems(0, 0)

    def get_selected_services(self, tree_widget):
        selected_items_dict = {}

        def traverse_item(item: QTreeWidgetItem):
            if item.isSelected():
                selected_items_dict[item] = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    selected_items_dict[item].append(child)
            else:
                child_selected = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    if child.isSelected():
                        child_selected.append(child)
                if child_selected:
                    selected_items_dict[item] = child_selected

        root_count = tree_widget.topLevelItemCount()
        for i in range(root_count):
            root = tree_widget.topLevelItem(i)
            traverse_item(root)

        return selected_items_dict

    def add_to_packages(self, parent, data, tree_widget):
        tree_widget.clear()
        for package, values in data.items():
            package_layer = CustomQTreeWidgetItem(tree_widget, [package])
            package_layer.setFirstColumnSpanned(True)
            for address, val in values.items():
                v = list(val.values())
                item = CustomQTreeWidgetItem(package_layer, [address] + v)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                if "installed" in v[3]:
                    package_layer.setBackground(0, QBrush(QColor("lightgreen")))
                    item.setBackground(0, QBrush(QColor("lightgreen")))
                    item.setBackground(1, QBrush(QColor("lightgreen")))
                    item.setBackground(2, QBrush(QColor("lightgreen")))
                    item.setBackground(3, QBrush(QColor("lightgreen")))
                    item.setBackground(4, QBrush(QColor("lightgreen")))

        tree_widget.sortItems(0, 0)


    def get_selected_packages(self, tree_widget):
        selected_items_dict = {}

        def traverse_item(item: QTreeWidgetItem):
            if item.isSelected():
                selected_items_dict[item] = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    selected_items_dict[item].append(child)
            else:
                child_selected = []
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    if child.isSelected():
                        child_selected.append(child)
                if child_selected:
                    selected_items_dict[item] = child_selected

        root_count = tree_widget.topLevelItemCount()
        for i in range(root_count):
            root = tree_widget.topLevelItem(i)
            traverse_item(root)

        return selected_items_dict

    @staticmethod
    def toast(parent, message,
                     icon=QtWidgets.QStyle.SP_MessageBoxInformation,
                     corner=QtCore.Qt.BottomRightCorner, margin=10, closable=True,
                     timeout=5000, desktop=False, parentWindow=True):

        if parent and parentWindow:
            parent = parent.window()

        if not parent or desktop:
            self = QToaster(None)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint |
                                QtCore.Qt.BypassWindowManagerHint)
            # This is a dirty hack!
            # parentless objects are garbage collected, so the widget will be
            # deleted as soon as the function that calls it returns, but if an
            # object is referenced to *any* other object it will not, at least
            # for PyQt (I didn't test it to a deeper level)
            self.__self = self

            currentScreen = QtWidgets.QApplication.primaryScreen()
            if parent and parent.window().geometry().size().isValid():
                # the notification is to be shown on the desktop, but there is a
                # parent that is (theoretically) visible and mapped, we'll try to
                # use its geometry as a reference to guess which desktop shows
                # most of its area; if the parent is not a top level window, use
                # that as a reference
                reference = parent.window().geometry()
            else:
                # the parent has not been mapped yet, let's use the cursor as a
                # reference for the screen
                reference = QtCore.QRect(
                    QtGui.QCursor.pos() - QtCore.QPoint(1, 1),
                    QtCore.QSize(3, 3))
            maxArea = 0
            for screen in QtWidgets.QApplication.screens():
                intersected = screen.geometry().intersected(reference)
                area = intersected.width() * intersected.height()
                if area > maxArea:
                    maxArea = area
                    currentScreen = screen
            parentRect = currentScreen.availableGeometry()
        else:
            self = QToaster(parent)
            parentRect = parent.rect()

        self.timer.setInterval(timeout)

        self.label = QtWidgets.QLabel(message)
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        font = QtGui.QFont()
        font.setFamily("IRANYekanWeb")
        font.setPointSize(10)
        font.setWeight(100)
        self.label.setFont(font)
        self.layout().addWidget(self.label)

        if closable:
            self.closeButton = QtWidgets.QToolButton()
            self.layout().addWidget(self.closeButton)
            closeIcon = self.style().standardIcon(
                QtWidgets.QStyle.SP_TitleBarCloseButton)
            self.closeButton.setIcon(closeIcon)
            self.closeButton.setAutoRaise(True)
            self.closeButton.clicked.connect(self.close)

        self.timer.start()

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.adjustSize()

        self.corner = corner
        self.margin = margin

        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        if corner == QtCore.Qt.TopLeftCorner:
            geo.moveTopLeft(
                parentRect.topLeft() + QtCore.QPoint(margin, margin))
        elif corner == QtCore.Qt.TopRightCorner:
            geo.moveTopRight(
                parentRect.topRight() + QtCore.QPoint(-margin, margin))
        elif corner == QtCore.Qt.BottomRightCorner:
            geo.moveBottomRight(
                parentRect.bottomRight() + QtCore.QPoint(-margin, -margin))
        else:
            geo.moveBottomLeft(
                parentRect.bottomLeft() + QtCore.QPoint(margin, -margin))

        self.setGeometry(geo)
        self.show()
        self.opacityAni.start()