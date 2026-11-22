"""Проверки главного окна PySide6."""

from PySide6.QtWidgets import QMessageBox

from genlab.ui import MainWindow


def test_window_has_five_tabs(qtbot, service):
    window = MainWindow(service)
    qtbot.addWidget(window)
    assert window.tabs.count() == 5
    assert window.tabs.tabText(0) == "Площади кругов"
    assert "вариант 16" in window.windowTitle()


def test_circle_tab(qtbot, service):
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.circle_start.setText("10")
    window.circle_end.setText("100")
    window.circle_step.setText("1")
    window.circle_limit.setValue(5)
    window.run_circle()

    assert window.circle_table.rowCount() == 5
    assert window.circle_table.item(0, 2).text() == "314,16"
    assert "5 из 91" in window.circle_summary.text()
    assert window.history_table.rowCount() == 1


def test_email_tab(qtbot, service):
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.email_length.setText("8")
    window.email_count.setValue(7)
    window.run_email()

    assert window.email_table.rowCount() == 7
    assert window.email_table.item(0, 1).text().endswith("@mail.ru")
    assert "7 адресов" in window.email_summary.text()


def test_numbers_tab(qtbot, service):
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.numbers_input.setPlainText("5 12 999 -34 100 7 56")
    window.run_numbers()

    assert window.numbers_table.rowCount() == 3
    assert window.numbers_table.item(0, 1).text() == "12"
    assert window.numbers_table.item(1, 1).text() == "-34"
    assert "двузначных: 3" in window.numbers_summary.text()


def test_error_is_shown(qtbot, service, monkeypatch):
    window = MainWindow(service)
    qtbot.addWidget(window)
    calls = []
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *args, **kwargs: calls.append(args))
    window.circle_start.setText("abc")
    window.run_circle()

    assert calls
    assert window.circle_table.rowCount() == 0


def test_history_table_updates(qtbot, service):
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.run_circle()
    window.run_email()
    window.refresh_history()

    assert window.history_table.rowCount() == 2
    assert "Записей в журнале: 2" in window.history_summary.text()
