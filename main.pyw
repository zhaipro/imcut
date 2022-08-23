import sys

import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtUiTools import loadUiType
from PySide6.QtGui import QPixmap, QImage

import utils


def debug(*args):
    print(*args, flush=True)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        Ui_MainWindow, _ = loadUiType('dialog.ui')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.pixmap_label = self.ui.pixmap_label
        self.setAcceptDrops(True)   # 必须设置，不然无法接收拖放事件
        self.ui.thresholdSlider.valueChanged.connect(self.threshold_changed)
        self.ui.thresholdBox.valueChanged.connect(self.threshold_changed)

        self.menu_init()

    def threshold_changed(self, value):
        debug('threshold_changed:', value)
        self.ui.thresholdSlider.setValue(value)
        self.ui.thresholdBox.setValue(value)
        self._fit()

    def menu_init(self):
        self.ui.menu.triggered.connect(self.menu_file)

    def menu_file(self, action):
        if action.objectName() == 'actionOpen':
            self.menu_file_open()
        elif action.objectName() == 'actionSave':
            self.menu_file_save()

    def menu_file_open(self):
        fn, _ = QFileDialog.getOpenFileName(self)
        if fn:
            self.fit(fn)

    def menu_file_save(self):
        filter = 'Images (*.jpg *.png)'
        fn, _ = QFileDialog.getSaveFileName(self, filter=filter)
        debug('save:', fn)
        if fn:
            cv2.imwrite(fn, self.cropped_image)

    def menu_exit(self):
        self.close()

    def imshow(self, label, im):
        h, w, c = im.shape
        qim = QImage(im, w, h, w * c, QImage.Format_BGR888)
        pixmap = QPixmap(qim)
        label.setPixmap(pixmap)

    def _fit(self):
        if not hasattr(self, 'im'):
            return
        threshold = self.ui.thresholdSlider.value()
        im = self.im.copy()
        w, s, a, d = utils._capture_detect_1(im, threshold, q=0.2)
        self.cropped_image = self.im[w:s, a:d]
        im = cv2.rectangle(im, (a - 2, w - 2), (d + 1, s + 1), (0, 0, 255), 2)

        self.imshow(self.pixmap_label, im)
        self.ui.actionSave.setEnabled(True)

    def fit(self, fn):
        self.im = cv2.imread(fn)
        self._fit()

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):  # noqa
        fn = evn.mimeData().text()
        debug('dragEnterEvent:', fn)
        if fn.endswith('.jpg') or fn.endswith('.png'):
            # 鼠标放开函数事件
            evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):       # noqa
        fn = evn.mimeData().text()[8:]
        debug('dropEvent:', fn)
        self.fit(fn)

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
