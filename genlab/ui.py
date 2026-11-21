# -*- coding: utf-8 -*-
"""Главное окно «Генераторной станции» на PySide6."""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import APP_NAME, VARIANT
from .exceptions import GenLabError
from .generators import default_workers
from .models import (
    MAX_BENCH_ADDRESSES,
    MAX_EMAILS,
    format_number,
    parse_int,
)


def apply_theme(app):
    """Включаю Fusion и спокойную светлую палитру до создания окна."""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#eef2f6"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8fafc"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#fde7c4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#7c2d12"))
    app.setPalette(palette)
    app.setFont(QFont("Segoe UI", 10))


# спокойный графитовый фон, янтарный акцент и белые карточки
STYLE_SHEET = """
QMainWindow, QWidget {
    background: #eef2f6;
    color: #1f2933;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QLabel {
    background: transparent;
}
QMenuBar {
    background: #ffffff;
    padding: 2px 10px;
    border-bottom: 1px solid #d7dee6;
}
QMenuBar::item {
    padding: 5px 11px;
    border-radius: 5px;
}
QMenuBar::item:selected {
    background: #eef2f6;
}
QMenu {
    background: #ffffff;
    border: 1px solid #d7dee6;
    border-radius: 8px;
    padding: 5px;
}
QMenu::item {
    padding: 6px 26px 6px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #fdf1df;
    color: #7c2d12;
}
QMenu::separator {
    height: 1px;
    background: #e2e8f0;
    margin: 5px 8px;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #d7dee6;
    border-radius: 10px;
    margin-top: 16px;
    padding: 16px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #64748b;
}
QLineEdit, QSpinBox, QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 6px 8px;
    selection-background-color: #fde7c4;
    selection-color: #7c2d12;
}
QLineEdit:focus, QSpinBox:focus, QPlainTextEdit:focus {
    border: 1px solid #b45309;
}
QSpinBox {
    padding-right: 18px;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 0;
    height: 0;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 15px;
}
QPushButton:hover {
    background: #f1f5f9;
}
QPushButton:pressed {
    background: #e2e8f0;
}
QPushButton#primaryButton {
    background: #b45309;
    color: #fffaf2;
    border: none;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: #c2610c;
}
QPushButton#primaryButton:pressed {
    background: #92400e;
}
QPushButton#primaryButton:disabled {
    background: #d6b28e;
    color: #fffaf2;
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #64748b;
    padding: 10px 18px;
    margin-right: 4px;
    border-bottom: 3px solid transparent;
    font-weight: 600;
}
QTabBar::tab:hover {
    color: #1f2933;
}
QTabBar::tab:selected {
    color: #7c2d12;
    border-bottom: 3px solid #b45309;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    border: 1px solid #d7dee6;
    border-radius: 8px;
    gridline-color: transparent;
}
QTableWidget::item {
    padding: 6px;
}
QTableWidget::item:selected {
    background: #fde7c4;
    color: #7c2d12;
}
QHeaderView::section {
    background: #e8eef4;
    color: #52606d;
    border: none;
    padding: 8px 6px;
    font-weight: 600;
}
QLabel#appTitle {
    font-family: "Georgia";
    font-size: 22pt;
    font-weight: 600;
    color: #1f2933;
}
QLabel#appSubtitle {
    color: #64748b;
}
QLabel#variantChip {
    background: #ffffff;
    border: 1px solid #d7dee6;
    border-radius: 12px;
    padding: 6px 14px;
    color: #7c2d12;
    font-weight: 600;
}
QLabel#fieldLabel {
    color: #64748b;
    font-size: 9pt;
}
QLabel#summary {
    color: #52606d;
}
QLabel#hint {
    color: #94a3b8;
    font-size: 9pt;
}
QProgressBar {
    background: #e2e8f0;
    border: none;
    border-radius: 4px;
    max-height: 8px;
}
QProgressBar::chunk {
    background: #b45309;
    border-radius: 4px;
}
QStatusBar {
    color: #64748b;
    background: #eef2f6;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px 4px 0;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0 4px 2px 4px;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 4px;
    min-width: 32px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}
QWidget#titleBar {
    background: #1f2933;
}
QLabel#titleMark {
    background: #b45309;
    color: #ffffff;
    border-radius: 13px;
    font-family: "Georgia";
    font-size: 12pt;
}
QLabel#titleText {
    color: #ffffff;
    font-size: 10pt;
    font-weight: 600;
}
QPushButton#minBtn, QPushButton#maxBtn, QPushButton#closeBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: #f1f5f9;
    font-size: 12pt;
    padding: 0;
}
QPushButton#minBtn:hover, QPushButton#maxBtn:hover {
    background: #334155;
    color: #ffffff;
}
QPushButton#closeBtn:hover {
    background: #b91c1c;
    color: #ffffff;
}
QToolTip {
    background: #1f2933;
    color: #f8fafc;
    border: none;
    padding: 4px 8px;
}
"""


class TitleBar(QWidget):
    """Своя тёмная полоса заголовка вместо стандартной рамки Windows."""

    def __init__(self, window, title):
        super().__init__(window)
        self.window = window
        self._offset = None
        self.setObjectName("titleBar")
        # без этого атрибута QWidget не рисует фон из таблицы стилей
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(10)

        mark = QLabel("Г")
        mark.setObjectName("titleMark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(26, 26)
        layout.addWidget(mark)

        text = QLabel(title)
        text.setObjectName("titleText")
        layout.addWidget(text)
        layout.addStretch(1)

        for symbol, slot, name in (("–", window.showMinimized, "minBtn"),
                                   ("□", window.toggle_max, "maxBtn"),
                                   ("✕", window.close, "closeBtn")):
            button = QPushButton(symbol)
            button.setObjectName(name)
            button.setFixedSize(34, 26)
            button.clicked.connect(slot)
            layout.addWidget(button)

    def mousePressEvent(self, event):
        """Запоминаю точку захвата, чтобы окно можно было перетаскивать."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._offset = (event.globalPosition().toPoint()
                            - self.window.frameGeometry().topLeft())
            event.accept()

    def mouseMoveEvent(self, event):
        """Двигаю окно вместе с мышью, пока кнопка нажата."""
        if self._offset is not None and not self.window.isMaximized():
            self.window.move(event.globalPosition().toPoint() - self._offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._offset = None

    def mouseDoubleClickEvent(self, event):
        self.window.toggle_max()


class BenchmarkWorker(QThread):
    """Считаю замер в отдельном потоке, чтобы окно не замирало."""

    done = Signal(object)
    failed = Signal(str)

    def __init__(self, service, count, workers, parent=None):
        super().__init__(parent)
        self.service = service
        self.count = count
        self.workers = workers

    def run(self):
        try:
            result = self.service.benchmark_report(
                count=self.count, length=8, workers=self.workers
            )
        except GenLabError as error:
            self.failed.emit(str(error))
        except Exception as error:  # поток не должен молча падать
            self.failed.emit(f"непредвиденная ошибка: {error}")
        else:
            self.done.emit(result)


def field(label_text, widget):
    """Собираю подпись и поле в один небольшой вертикальный блок."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    label = QLabel(label_text)
    label.setObjectName("fieldLabel")
    layout.addWidget(label)
    layout.addWidget(widget)
    return box


def make_table():
    """Создаю таблицу только для чтения с чередованием строк."""
    table = QTableWidget(0, 0)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setHighlightSections(False)
    table.setShowGrid(False)
    table.setWordWrap(False)
    return table


def fill_table(table, columns, rows, stretch=None):
    """Заполняю таблицу строками и подгоняю ширину столбцов."""
    table.clear()
    table.setColumnCount(len(columns))
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(list(columns))
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            if column_index == 0:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_index, column_index, item)
    table.resizeColumnsToContents()
    header = table.horizontalHeader()
    header.setStretchLastSection(stretch is None)
    if stretch is not None and 0 <= stretch < table.columnCount():
        header.setSectionResizeMode(stretch, QHeaderView.ResizeMode.Stretch)


class MainWindow(QMainWindow):
    """Окно с вкладками для трёх задач, замера скорости и журнала."""

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self._worker = None
        self._normal_geometry = None
        self.setWindowTitle(f"{APP_NAME} — вариант {VARIANT}")
        # рисую свою полосу заголовка, системная рамка не нужна
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setMinimumSize(980, 680)
        self._place_window()
        self.setStyleSheet(STYLE_SHEET)
        self._build_menu()
        self._build_ui()
        self.refresh_history()

    def _place_window(self):
        """Подгоняю размер под экран и ставлю окно по центру."""
        screen = QApplication.primaryScreen().availableGeometry()
        width = min(max(1120, screen.width() - 180), 1280)
        height = min(max(720, screen.height() - 150), 850)
        self.resize(width, height)
        self.move(screen.x() + (screen.width() - width) // 2,
                  screen.y() + (screen.height() - height) // 2)

    def toggle_max(self):
        """Разворачиваю окно на весь экран или возвращаю прежний размер."""
        if self._normal_geometry is None:
            self._normal_geometry = self.geometry()
            self.setGeometry(QApplication.primaryScreen().availableGeometry())
        else:
            self.setGeometry(self._normal_geometry)
            self._normal_geometry = None

    def _build_menu(self):
        """Создаю меню «Файл», «Вид» и «Справка»."""
        file_menu = self.menuBar().addMenu("Файл")
        export_action = QAction("Экспорт журнала в CSV...", self)
        export_action.triggered.connect(self.export_history)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = self.menuBar().addMenu("Вид")
        refresh_action = QAction("Обновить журнал", self)
        refresh_action.triggered.connect(self.refresh_history)
        view_menu.addAction(refresh_action)

        help_menu = self.menuBar().addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _build_ui(self):
        """Собираю шапку, вкладки и строку состояния."""
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.addWidget(
            TitleBar(self, f"{APP_NAME} — лабораторная работа №4"))
        header_layout.addWidget(self.menuBar())
        self.setMenuWidget(header)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 14, 18, 8)
        layout.setSpacing(10)

        title_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        subtitle = QLabel("Генераторы, встроенные функции и параллельный расчёт")
        subtitle.setObjectName("appSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        title_row.addLayout(title_box)
        title_row.addStretch(1)
        chip = QLabel(f"ЛР №4 · вариант {VARIANT}")
        chip.setObjectName("variantChip")
        title_row.addWidget(chip, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(title_row)

        self.tabs = QTabWidget()
        self.tabs.setUsesScrollButtons(False)
        self.tabs.addTab(self._make_circle_tab(), "Площади кругов")
        self.tabs.addTab(self._make_email_tab(), "Email-адреса")
        self.tabs.addTab(self._make_numbers_tab(), "Двузначные")
        self.tabs.addTab(self._make_benchmark_tab(), "Скорость")
        self.tabs.addTab(self._make_history_tab(), "Журнал")
        layout.addWidget(self.tabs, 1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Готово")
        self.statusBar().addPermanentWidget(QSizeGrip(self))

    def _make_circle_tab(self):
        """Собираю вкладку с площадями кругов."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        card = QGroupBox("Параметры расчёта")
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 18, 14, 12)
        row.setSpacing(14)

        self.circle_start = QLineEdit("10")
        self.circle_end = QLineEdit("100")
        self.circle_step = QLineEdit("1")
        self.circle_limit = QSpinBox()
        self.circle_limit.setRange(1, 50)
        self.circle_limit.setValue(5)
        for widget in (self.circle_start, self.circle_end, self.circle_step):
            widget.setMaximumWidth(110)
        self.circle_limit.setMaximumWidth(90)
        row.addWidget(field("Радиус от", self.circle_start))
        row.addWidget(field("Радиус до", self.circle_end))
        row.addWidget(field("Шаг", self.circle_step))
        row.addWidget(field("Сколько показать", self.circle_limit))
        self.circle_button = QPushButton("Посчитать площади")
        self.circle_button.setObjectName("primaryButton")
        self.circle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.circle_button.clicked.connect(self.run_circle)
        row.addWidget(self.circle_button, 0, Qt.AlignmentFlag.AlignBottom)
        row.addStretch(1)
        hint = QLabel("Площадь круга: S = πr²")
        hint.setObjectName("hint")
        row.addWidget(hint, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(card)

        result_card = QGroupBox("Первые значения генератора")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(12, 18, 12, 10)
        self.circle_table = make_table()
        result_layout.addWidget(self.circle_table)
        self.circle_summary = QLabel("Нажмите «Посчитать площади»")
        self.circle_summary.setObjectName("summary")
        result_layout.addWidget(self.circle_summary)
        layout.addWidget(result_card, 1)
        return page

    def _make_email_tab(self):
        """Собираю вкладку с бесконечным генератором адресов."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        card = QGroupBox("Параметры генератора")
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 18, 14, 12)
        row.setSpacing(14)
        self.email_length = QLineEdit("8")
        self.email_length.setMaximumWidth(110)
        self.email_count = QSpinBox()
        self.email_count.setRange(1, MAX_EMAILS)
        self.email_count.setValue(7)
        self.email_count.setMaximumWidth(110)
        row.addWidget(field("Длина имени", self.email_length))
        row.addWidget(field("Сколько адресов", self.email_count))
        self.email_button = QPushButton("Сгенерировать")
        self.email_button.setObjectName("primaryButton")
        self.email_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.email_button.clicked.connect(self.run_email)
        row.addWidget(self.email_button, 0, Qt.AlignmentFlag.AlignBottom)
        row.addStretch(1)
        hint = QLabel("Символы: латиница, цифры и «_», домен mail.ru")
        hint.setObjectName("hint")
        row.addWidget(hint, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(card)

        result_card = QGroupBox("Сгенерированные адреса")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(12, 18, 12, 10)
        self.email_table = make_table()
        self.email_table.setFont(QFont("Consolas", 10))
        result_layout.addWidget(self.email_table)
        self.email_summary = QLabel("Нажмите «Сгенерировать»")
        self.email_summary.setObjectName("summary")
        result_layout.addWidget(self.email_summary)
        layout.addWidget(result_card, 1)
        return page

    def _make_numbers_tab(self):
        """Собираю вкладку с фильтром двузначных чисел."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        card = QGroupBox("Список чисел")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 18, 14, 12)
        self.numbers_input = QPlainTextEdit()
        self.numbers_input.setPlaceholderText(
            "Например: 5 12 999 -34 100 7 56"
        )
        self.numbers_input.setFixedHeight(76)
        card_layout.addWidget(self.numbers_input)
        row = QHBoxLayout()
        row.addStretch(1)
        self.numbers_button = QPushButton("Оставить двузначные")
        self.numbers_button.setObjectName("primaryButton")
        self.numbers_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.numbers_button.clicked.connect(self.run_numbers)
        row.addWidget(self.numbers_button)
        card_layout.addLayout(row)
        layout.addWidget(card)

        result_card = QGroupBox("Результат filter")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(12, 18, 12, 10)
        self.numbers_table = make_table()
        result_layout.addWidget(self.numbers_table)
        self.numbers_summary = QLabel("Введите числа через пробел")
        self.numbers_summary.setObjectName("summary")
        result_layout.addWidget(self.numbers_summary)
        layout.addWidget(result_card, 1)
        return page

    def _make_benchmark_tab(self):
        """Собираю вкладку сравнения обычного и параллельного генераторов."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        card = QGroupBox("Замер производительности")
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 18, 14, 12)
        row.setSpacing(14)
        self.bench_count = QSpinBox()
        self.bench_count.setRange(10_000, MAX_BENCH_ADDRESSES)
        self.bench_count.setSingleStep(100_000)
        self.bench_count.setValue(1_000_000)
        self.bench_count.setGroupSeparatorShown(True)
        self.bench_count.setMaximumWidth(150)
        self.bench_workers = QSpinBox()
        self.bench_workers.setRange(1, 16)
        self.bench_workers.setValue(default_workers())
        self.bench_workers.setMaximumWidth(90)
        row.addWidget(field("Сгенерировать адресов", self.bench_count))
        row.addWidget(field("Процессов", self.bench_workers))
        self.bench_button = QPushButton("Сравнить скорость")
        self.bench_button.setObjectName("primaryButton")
        self.bench_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bench_button.clicked.connect(self.run_benchmark)
        row.addWidget(self.bench_button, 0, Qt.AlignmentFlag.AlignBottom)
        row.addStretch(1)
        hint = QLabel("ProcessPoolExecutor: процессов не больше числа ядер")
        hint.setObjectName("hint")
        row.addWidget(hint, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(card)

        result_card = QGroupBox("Результат сравнения")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(12, 18, 12, 10)
        self.bench_progress = QProgressBar()
        self.bench_progress.setRange(0, 0)
        self.bench_progress.setVisible(False)
        result_layout.addWidget(self.bench_progress)
        self.bench_table = make_table()
        result_layout.addWidget(self.bench_table)
        self.bench_summary = QLabel("Замер выполняется в отдельном потоке")
        self.bench_summary.setObjectName("summary")
        result_layout.addWidget(self.bench_summary)
        layout.addWidget(result_card, 1)
        return page

    def _make_history_tab(self):
        """Собираю вкладку журнала запусков."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        card = QGroupBox("Последние запуски")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 18, 12, 10)
        self.history_table = make_table()
        card_layout.addWidget(self.history_table)
        row = QHBoxLayout()
        self.history_refresh = QPushButton("Обновить")
        self.history_refresh.clicked.connect(self.refresh_history)
        self.history_export = QPushButton("Экспорт в CSV")
        self.history_export.clicked.connect(self.export_history)
        self.history_clear = QPushButton("Очистить журнал")
        self.history_clear.clicked.connect(self.clear_history)
        row.addWidget(self.history_refresh)
        row.addWidget(self.history_export)
        row.addWidget(self.history_clear)
        row.addStretch(1)
        self.history_summary = QLabel("Записей в журнале: 0")
        self.history_summary.setObjectName("summary")
        row.addWidget(self.history_summary)
        card_layout.addLayout(row)
        layout.addWidget(card, 1)
        return page

    def _show_error(self, error):
        """Показываю понятное сообщение об ошибке и не роняю окно."""
        QMessageBox.warning(self, "Ошибка", str(error))

    def _show_result(self, table, result, stretch=None):
        """Вывожу результат в таблицу и показываю время расчёта."""
        fill_table(table, result.columns, result.rows, stretch=stretch)
        return (f"{result.summary}. Время: "
                f"{format_number(result.duration_ms, 2)} мс.")

    def run_circle(self):
        """Считаю площади кругов по данным формы."""
        try:
            result = self.service.circle_report(
                self.circle_start.text(),
                self.circle_end.text(),
                self.circle_step.text(),
                self.circle_limit.value(),
            )
        except GenLabError as error:
            self._show_error(error)
            return
        self.circle_summary.setText(
            self._show_result(self.circle_table, result)
        )
        self.statusBar().showMessage("Площади посчитаны")
        self.refresh_history()

    def run_email(self):
        """Генерирую адреса по данным формы."""
        try:
            result = self.service.email_report(
                self.email_length.text(), self.email_count.value()
            )
        except GenLabError as error:
            self._show_error(error)
            return
        self.email_summary.setText(
            self._show_result(self.email_table, result, stretch=1)
        )
        self.statusBar().showMessage("Адреса сгенерированы")
        self.refresh_history()

    def run_numbers(self):
        """Фильтрую двузначные числа из текстового поля."""
        try:
            result = self.service.two_digit_report(
                self.numbers_input.toPlainText()
            )
        except GenLabError as error:
            self._show_error(error)
            return
        self.numbers_summary.setText(
            self._show_result(self.numbers_table, result, stretch=1)
        )
        self.statusBar().showMessage("Список отфильтрован")
        self.refresh_history()

    def run_benchmark(self):
        """Запускаю замер в отдельном потоке."""
        if self._worker is not None and self._worker.isRunning():
            return
        try:
            count = parse_int(
                self.bench_count.value(), "Количество адресов", 1000,
                MAX_BENCH_ADDRESSES,
            )
            workers = parse_int(
                self.bench_workers.value(), "Количество процессов", 1, 16
            )
        except GenLabError as error:
            self._show_error(error)
            return

        self.bench_button.setEnabled(False)
        self.bench_progress.setVisible(True)
        self.bench_summary.setText("Считаю обычный и параллельный варианты...")
        self._worker = BenchmarkWorker(self.service, count, workers)
        self._worker.done.connect(self._benchmark_done)
        self._worker.failed.connect(self._benchmark_failed)
        self._worker.finished.connect(self._benchmark_finished)
        self._worker.start()

    def _benchmark_done(self, result):
        """Показываю результат замера после завершения потока."""
        self.bench_summary.setText(
            self._show_result(self.bench_table, result, stretch=2)
        )
        self.statusBar().showMessage("Замер завершён")
        self.refresh_history()

    def _benchmark_failed(self, message):
        """Показываю ошибку замера."""
        self.bench_summary.setText("Замер не выполнен")
        QMessageBox.warning(self, "Ошибка замера", message)

    def _benchmark_finished(self):
        """Возвращаю кнопку и прячу индикатор после потока."""
        self.bench_button.setEnabled(True)
        self.bench_progress.setVisible(False)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def refresh_history(self):
        """Обновляю таблицу журнала из SQLite."""
        try:
            records = self.service.history(50)
        except GenLabError as error:
            self.history_summary.setText(f"Журнал недоступен: {error}")
            return
        rows = [
            (record.run_id, record.task, record.summary, record.created,
             format_number(record.duration_ms, 1))
            for record in records
        ]
        fill_table(
            self.history_table,
            ("ID", "Задача", "Итог", "Начало", "Время, мс"),
            rows,
            stretch=2,
        )
        self.history_summary.setText(f"Записей в журнале: {len(records)}")

    def export_history(self):
        """Сохраняю журнал в выбранный CSV-файл."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт журнала", "genlab_history.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            count = self.service.export_history(path)
        except GenLabError as error:
            self._show_error(error)
            return
        QMessageBox.information(self, "Экспорт", f"Сохранено записей: {count}")

    def clear_history(self):
        """Удаляю журнал после подтверждения."""
        answer = QMessageBox.question(
            self, "Очистка журнала", "Удалить все записи журнала?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            removed = self.service.clear_history()
        except GenLabError as error:
            self._show_error(error)
            return
        self.refresh_history()
        self.statusBar().showMessage(f"Удалено записей: {removed}")

    def show_about(self):
        """Показываю краткие сведения о программе."""
        QMessageBox.about(
            self, "О программе",
            f"«{APP_NAME}» — лабораторная работа №4 по теории алгоритмов.\n"
            f"Вариант {VARIANT}: генераторы, filter и параллельный расчёт.\n\n"
            "Панов Артём Андреевич, группа Б.ПИН.РИС-24.06, ТвГТУ, 2026.",
        )

    def closeEvent(self, event):
        """Жду завершения замера, чтобы не оставить висящий процесс."""
        if self._worker is not None and self._worker.isRunning():
            self._worker.wait(10_000)
        super().closeEvent(event)
