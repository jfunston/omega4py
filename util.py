from PyQt5 import QtWidgets


def ui_methods(cls):
    def add_qt_action(self, name, callback, shortcut, button=None):
        action = QtWidgets.QAction(name, self)
        if shortcut != "":
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        if button != None:
            button.clicked.connect(callback)
        self.addAction(action)

    setattr(cls, "add_qt_action", add_qt_action)
    return cls


def pretty_bool(inval):
    if inval is None:
        inval = ""
    elif inval == 1:
        inval = "y"
    else:
        inval = "n"
    return inval


def pretty_int(inval):
    if inval is None:
        return ""
    return str(inval)
