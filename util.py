from PyQt5 import QtWidgets


def ui_methods(cls):
    def add_qt_action(self, name, callback, shortcut, button=None):
        action = QtWidgets.QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        if button != None:
            button.clicked.connect(callback)
        self.addAction(action)

    setattr(cls, "add_qt_action", add_qt_action)
    return cls
