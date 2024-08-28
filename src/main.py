# -*- coding: utf-8 -*-
"""
@author: msh, yk
"""
import argparse
from logging import getLogger, basicConfig
from pathlib import Path
from sys import argv

from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtCore import QSize

from pardus import SSHConnector, Service, Apt, Config, ConfigRaw
from pardus.gui import Ui_MainWindow, Ui_FormAdd, GUIFunctions, Ui_FormServices, Ui_FormLog, Ui_FormApt, \
    Ui_FormPackageInfo, Ui_FormConfig
from pardus.gui.functions import CustomQTreeWidgetItem


def paginate_dict(d, items_per_page):
    items = list(d.items())
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    return [
        dict(items[i * items_per_page: (i + 1) * items_per_page])
        for i in range(total_pages)
    ]


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, logger_level="DEBUG", log_file=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        if log_file is None:
            self.log_file = Path("pardus.log")
        else:
            self.log_file = log_file

        log_format = "[%(asctime)s, %(levelname)s], [%(filename)s, %(funcName)s, %(lineno)s]: %(message)s"
        basicConfig(filename=self.log_file, level=logger_level, format=log_format)

        self.logger = getLogger("MYRaf")

        getLogger('matplotlib.font_manager').disabled = True
        getLogger('libGL').disabled = True

        self.actionAdd.triggered.connect(lambda: self.show_window(AddForm(self)))
        self.actionDelete.triggered.connect(lambda: self.gui_functions.remove_from_connections(self.treeWidget))

        self.gui_functions = GUIFunctions(self.logger)

        self.connections = {}
        self.mdiArea.subWindowList()

        self.treeWidget.installEventFilter(self)

    def load_it(self):
        connection = SSHConnector("172.16.102.241", 22, "dns", "landofcanaan", self.logger)
        self.gui_functions.add_to_connections(self, connection, self.treeWidget)
        connection = SSHConnector("172.16.102.130", 22, "samba", "landofcanaan", self.logger)
        self.gui_functions.add_to_connections(self, connection, self.treeWidget)

    def show_window(self, window):
        self.mdiArea.addSubWindow(window)
        window.show()

    def services(self):
        connections_to_use = []
        connections = self.gui_functions.get_selected_connections(self.treeWidget)
        for key, values in connections.items():
            host = key.text(0)
            port = int(values[0].text(1))
            user_name = values[1].text(1)
            passwd = key.password
            connection = SSHConnector(host, port, user_name, passwd, self.logger)
            connections_to_use.append(connection)
        self.show_window(ServicesForm(self, connections_to_use))

    def apt(self):
        connections_to_use = []
        connections = self.gui_functions.get_selected_connections(self.treeWidget)
        for key, values in connections.items():
            host = key.text(0)
            port = int(values[0].text(1))
            user_name = values[1].text(1)
            passwd = key.password
            connection = SSHConnector(host, port, user_name, passwd, self.logger)
            connections_to_use.append(connection)
        # {'package': 'zziplib-bin', 'repo': 'jammy',
        # 'version': '0.13.72+dfsg.1-1.1', 'arch': 'i386', 'tags': []}
        self.show_window(AptForm(self, connections_to_use))

    def conf(self):
        connections_to_use = []
        connections = self.gui_functions.get_selected_connections(self.treeWidget)
        for key, values in connections.items():
            host = key.text(0)
            port = int(values[0].text(1))
            user_name = values[1].text(1)
            passwd = key.password
            connection = SSHConnector(host, port, user_name, passwd, self.logger)
            connections_to_use.append(connection)
        self.show_window(ConfigureForm(self, connections_to_use))

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self.treeWidget:

            selected = self.gui_functions.get_selected_connections(self.treeWidget)

            menu = QtWidgets.QMenu()
            menu.addAction('Add...', lambda: (self.show_window(AddForm(self))))
            menu.addAction('Remove', lambda: (self.gui_functions.remove_from_connections(self.treeWidget)))

            menu.addSeparator()

            services = menu.addAction('Services...', lambda: (self.services()))
            if len(selected) < 1:
                services.setEnabled(False)

            apt = menu.addAction('Apt...', lambda: (self.apt()))
            if len(selected) < 1:
                apt.setEnabled(False)

            conf = menu.addAction('Config...', lambda: (self.conf()))
            if len(selected) < 1:
                conf.setEnabled(False)

            # menu.addMenu(apt)
            menu.exec_(event.globalPos())
            return True

        return super(MainWindow, self).eventFilter(source, event)


class ConfigureForm(QtWidgets.QWidget, Ui_FormConfig):
    def __init__(self, parent, connections):
        super(ConfigureForm, self).__init__(parent)
        self.parent = parent
        self.connections = connections
        self.setupUi(self)

        self.configs = []

        self.comboBoxKind.setEnabled(False)

        self.loads = {
            "Samba": "/etc/samba/smb.conf",
            "Kerberos": "/etc/krb5.conf",
        }

        self.comboBoxLoad.currentTextChanged.connect(self.load_file_path)
        self.pushButtonOpen.clicked.connect(self.open_files)

        self.pushButtonSave.clicked.connect(self.save)

    def save(self):
        for conf in self.configs:
            text = self.plainTextEditConfig.toPlainText()
            try:
                conf.data = text
            except Exception as e:
                print(e)
                self.parent.logger.warning(e)
                self.parent.gui_functions.toast(str(e))

    def load_file_path(self):
        load = self.comboBoxLoad.currentText()
        path = self.loads.get(load, "")
        self.lineEdiPath.setText(path)

    def open_files(self):
        path = self.lineEdiPath.text()

        self.configs = []
        for connection in self.connections:
            try:
                self.configs.append(
                    ConfigRaw(connection, path=path, create=True, backup=True, force=True, logger=self.parent.logger)
                )
            except Exception as e:
                print(e)
                self.parent.logger.warning(e)
                self.parent.gui_functions.toast(self, str(e))

        print([len(conf) for conf in self.configs])

        if any(len(conf) > 0 for conf in self.configs):
            options = {
                "_": ""
            }
            for conf in self.configs:
                try:
                    options[conf.connector.address] = conf.read()
                except Exception as e:
                    self.parent.logger.warning(e)
                    self.parent.gui_functions.toast(self, str(e))

            index = self.parent.gui_functions.get_item_description(
                self, "Select Configuration",
                "There are some configuration in at least one of the files.",
                options
            )

            data_to_load = ""
            if index > 0:
                data_to_load = self.configs[index - 1].data

            self.plainTextEditConfig.setPlainText(data_to_load)


class LogForm(QtWidgets.QWidget, Ui_FormLog):
    def __init__(self, parent, services, service_name):
        super(LogForm, self).__init__(parent)
        self.parent = parent
        self.services = services
        self.service_name = service_name
        self.setupUi(self)

        self.load()
        self.tableWidget.installEventFilter(self)

    def load(self):
        data = []
        for service in self.services:
            try:
                logs = service.logs(self.service_name)
                for l in logs:
                    data.append([service.connector.address] + list(l.values()))
            except Exception as e:
                self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.parent.gui_functions.clear_table(self.tableWidget)
        self.parent.gui_functions.add_to_table(data, self.tableWidget)
        self.tableWidget.sortItems(1)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self.tableWidgetLog:
            menu = QtWidgets.QMenu()
            menu.addAction('Refresh', lambda: (self.load()))

            menu.exec_(event.globalPos())
            return True

        return super(LogForm, self).eventFilter(source, event)


class AptForm(QtWidgets.QWidget, Ui_FormApt):
    def __init__(self, parent, connections):
        super(AptForm, self).__init__(parent)
        self.parent = parent
        self.connections = connections
        self.apts = [
            Apt(connection, logger=self.parent.logger)
            for connection in self.connections
        ]
        self.setupUi(self)

        self.lineEditSearch.textChanged.connect(self.search)

        self.current_page = 0
        self.elements_per_page = 100

        self.packages = self.load()
        self.filtered_packages = self.packages

        self.fill()
        self.pushButtonNext.clicked.connect(self.next_page)
        self.pushButtonPrevious.clicked.connect(self.previous_page)

        self.treeWidget.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self.treeWidget:
            selected = self.parent.gui_functions.get_selected_connections(self.treeWidget)

            menu = QtWidgets.QMenu()
            menu.addAction('Refresh', lambda: (self.load(), self.fill()))
            menu.addSeparator()

            install = menu.addAction('Install', lambda: (self.install()))
            remove = menu.addAction('Remove', lambda: (self.remove()))
            reinstall = menu.addAction('Reinstall', lambda: (self.reinstall()))
            purge = menu.addAction('Purge', lambda: (self.purge()))
            menu.addSeparator()
            show = menu.addAction('Show', lambda: (self.show_package()))

            if len(selected) < 1:
                install.setEnabled(False)
                remove.setEnabled(False)
                reinstall.setEnabled(False)
                purge.setEnabled(False)
                show.setEnabled(False)

            menu.exec_(event.globalPos())
            return True

        return super(AptForm, self).eventFilter(source, event)

    def install(self):
        selected = self.parent.gui_functions.get_selected_packages(self.treeWidget)

        progress = QtWidgets.QProgressDialog("Installing ...", "Abort", 0, len(self.apts), self)

        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint() + QSize(400, 0))
        progress.setWindowTitle('Pardus: Please Wait')
        progress.setAutoClose(True)

        for package_name in selected.keys():
            for iteration, apt in enumerate(self.apts):
                try:
                    progress.setLabelText(f"Operating on {apt.connector.address}")
                    apt.install(package_name.text(0))

                    if progress.wasCanceled():
                        progress.setLabelText("ABORT!")
                        break

                    progress.setValue(iteration)

                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{package_name.connector.address}")

        progress.close()
        self.load()
        self.fill()

    def remove(self):
        selected = self.parent.gui_functions.get_selected_packages(self.treeWidget)

        progress = QtWidgets.QProgressDialog("Removing ...", "Abort", 0, len(self.apts), self)

        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint() + QSize(400, 0))
        progress.setWindowTitle('Pardus: Please Wait')
        progress.setAutoClose(True)

        for package_name in selected.keys():
            for iteration, apt in enumerate(self.apts):
                try:
                    progress.setLabelText(f"Operating on {apt.connector.address}")
                    apt.remove(package_name.text(0))

                    if progress.wasCanceled():
                        progress.setLabelText("ABORT!")
                        break

                    progress.setValue(iteration)

                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{apt.connector.address}")

        progress.close()
        self.load()
        self.fill()

    def reinstall(self):
        selected = self.parent.gui_functions.get_selected_packages(self.treeWidget)

        progress = QtWidgets.QProgressDialog("Removing ...", "Abort", 0, len(self.apts), self)

        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint() + QSize(400, 0))
        progress.setWindowTitle('Pardus: Please Wait')
        progress.setAutoClose(True)

        for package_name in selected.keys():
            for iteration, apt in enumerate(self.apts):
                try:
                    progress.setLabelText(f"Operating on {apt.connector.address}")
                    apt.reinstall(package_name.text(0))

                    if progress.wasCanceled():
                        progress.setLabelText("ABORT!")
                        break

                    progress.setValue(iteration)

                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{package_name.connector.address}")

        progress.close()
        self.load()
        self.fill()

    def purge(self):
        selected = self.parent.gui_functions.get_selected_packages(self.treeWidget)

        progress = QtWidgets.QProgressDialog("Removing ...", "Abort", 0, len(self.apts), self)

        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint() + QSize(400, 0))
        progress.setWindowTitle('Pardus: Please Wait')
        progress.setAutoClose(True)

        for package_name in selected.keys():
            for iteration, apt in enumerate(self.apts):
                try:
                    progress.setLabelText(f"Operating on {apt.connector.address}")
                    apt.purge(package_name.text(0))

                    if progress.wasCanceled():
                        progress.setLabelText("ABORT!")
                        break

                    progress.setValue(iteration)

                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{package_name.connector.address}")

        progress.close()
        self.load()
        self.fill()

    def show_package(self):
        selected = self.parent.gui_functions.get_selected_packages(self.treeWidget)

        for package_name in selected.keys():
            for apt in self.apts:
                try:
                    self.parent.show_window(PackageInformationForm(self.parent, apt, package_name.text(0)))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{apt.connector.address}")

    def fill(self):
        try:
            packages = self.filtered_packages[self.current_page]
        except Exception as e:
            packages = {}
        self.treeWidget.clear()
        self.label_2.setText(f"{self.current_page + 1} / {len(self.filtered_packages)}")
        self.parent.gui_functions.add_to_packages(self, packages, self.treeWidget)

    def next_page(self):
        self.current_page += 1
        if self.current_page >= len(self.filtered_packages):
            self.current_page = 0

        self.fill()

    def previous_page(self):
        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = len(self.filtered_packages) - 1

        self.fill()

    def load(self):
        self.treeWidget.clear()
        result = {}
        for apt in self.apts:
            for packages in apt.list():
                packages["domain"] = apt.connector.address

                package = packages['package']
                domain = packages['domain']

                others = {k: str(v) for k, v in packages.items() if k not in ['package', 'domain']}
                if package not in result:
                    result[package] = {}
                result[package][domain] = others

        return paginate_dict(result, self.elements_per_page)

    def search(self):
        search_text = self.lineEditSearch.text().lower()
        found_package = {}
        for packages in self.packages:
            for package in packages.keys():
                if search_text in package:
                    found_package[package] = packages[package]

        self.current_page = 0
        self.filtered_packages = paginate_dict(found_package, self.elements_per_page)
        self.fill()


class PackageInformationForm(QtWidgets.QWidget, Ui_FormPackageInfo):
    def __init__(self, parent, apt, package_name):
        super(PackageInformationForm, self).__init__(parent)
        self.parent = parent
        self.apt = apt
        self.package_name = package_name

        self.setupUi(self)

        self.setWindowTitle(f"Package Information @ {self.apt.connector.address}")

        self.load()

        self.pushButtonReload.clicked.connect(self.load)

    def load(self):
        information = self.apt.show(self.package_name)
        description = information.pop('Description', "")
        self.plainTextEditDescription.setPlainText(description)
        data = [
            [key, str(value)]
            for key, value in information.items()
        ]

        self.parent.gui_functions.clear_table(self.tableWidgetInformation)
        self.parent.gui_functions.add_to_table(data, self.tableWidgetInformation)


class ServicesForm(QtWidgets.QWidget, Ui_FormServices):
    def __init__(self, parent, connections):
        super(ServicesForm, self).__init__(parent)
        self.parent = parent
        self.connections = connections
        self.services = [
            Service(connection, logger=self.parent.logger)
            for connection in self.connections
        ]
        self.setupUi(self)

        self.load()

        self.lineEditSearch.textChanged.connect(self.search)
        self.treeWidget.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self.treeWidget:
            selected = self.parent.gui_functions.get_selected_connections(self.treeWidget)

            menu = QtWidgets.QMenu()
            menu.addAction('Refresh', lambda: (self.load()))
            menu.addSeparator()
            start = menu.addAction('Start', lambda: (self.start()))
            stop = menu.addAction('Stop', lambda: (self.stop()))
            restart = menu.addAction('Restart', lambda: (self.restart()))
            enable = menu.addAction('Enable', lambda: (self.enable()))
            disable = menu.addAction('Disable', lambda: (self.disable()))
            logs = menu.addAction('Logs...', lambda: (self.log()))

            if len(selected) < 1:
                start.setEnabled(False)
                stop.setEnabled(False)
                restart.setEnabled(False)
                enable.setEnabled(False)
                disable.setEnabled(False)
                logs.setEnabled(False)

            menu.exec_(event.globalPos())
            return True

        return super(ServicesForm, self).eventFilter(source, event)

    def start(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        for service_name in selected.keys():
            for service in self.services:
                try:
                    service.start(service_name.text(0))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.load()
        self.search()

    def stop(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        for service_name in selected.keys():
            for service in self.services:
                try:
                    service.stop(service_name.text(0))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.load()
        self.search()

    def restart(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        for service_name in selected.keys():
            for service in self.services:
                try:
                    service.restart(service_name.text(0))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.load()
        self.search()

    def enable(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        for service_name in selected.keys():
            for service in self.services:
                try:
                    service.enable(service_name.text(0))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.load()
        self.search()

    def disable(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        for service_name in selected.keys():
            for service in self.services:
                try:
                    service.disable(service_name.text(0))
                except Exception as e:
                    self.parent.gui_functions.toast(self, f"{str(e)}@{service.connector.address}")

        self.load()
        self.search()

    def log(self):
        selected = self.parent.gui_functions.get_selected_services(self.treeWidget)
        service_name = list(selected.keys())[0].text(0)
        self.parent.show_window(LogForm(self.parent, self.services, service_name))

    def load(self):
        self.treeWidget.clear()
        result = {}
        for service in self.services:
            for ser in service.list():
                ser["domain"] = service.connector.address

                unit = ser['unit']
                domain = ser['domain']

                others = {k: v for k, v in ser.items() if k not in ['unit', 'domain']}
                if unit not in result:
                    result[unit] = {}
                result[unit][domain] = others

        self.parent.gui_functions.add_to_services(self, result, self.treeWidget)
        self.search()

    def search(self):
        search_text = self.lineEditSearch.text().lower()

        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            item_text = item.text(0).lower()

            # Check if the item text contains the search text
            if search_text in item_text:
                item.setHidden(False)  # Show the item
            else:
                item.setHidden(True)  # Hide the item


class AddForm(QtWidgets.QWidget, Ui_FormAdd):
    def __init__(self, parent):
        super(AddForm, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self.pushButtonTest.clicked.connect(self.test)
        self.pushButtonAdd.clicked.connect(self.add)

    def add(self):
        address = self.lineEditAddress.text()
        port = self.spinBoxPort.value()
        username = self.lineEditUserName.text()
        password = self.lineEditPassword.text()

        try:
            connection = SSHConnector(address, port, username, password, self.parent.logger)
            self.parent.gui_functions.add_to_connections(self, connection, self.parent.treeWidget)
            self.close()
        except Exception as e:
            self.parent.gui_functions.error(self, str(e))

    def test(self):
        address = self.lineEditAddress.text()
        port = self.spinBoxPort.value()
        username = self.lineEditUserName.text()
        password = self.lineEditPassword.text()

        try:
            _ = SSHConnector(address, port, username, password, self.parent.logger)
            self.parent.gui_functions.information(self, "Connection Established")
        except Exception as e:
            self.parent.gui_functions.error(self, str(e))

    def closeEvent(self, event):
        for i in self.parent.mdiArea.subWindowList():
            if i.widget() == self:
                i.close()


def main():
    parser = argparse.ArgumentParser(description='MYRaf V3 Beta')
    parser.add_argument("--logger", "-ll", default=10, type=int,
                        help="Logger level: CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0")
    parser.add_argument("--logfile", "-lf", default=None, type=str, help="Path to log file")

    args = parser.parse_args()

    app = QtWidgets.QApplication(argv)
    window = MainWindow(logger_level=args.logger, log_file=args.logfile)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
