import sys
import types

import main


def test_resolver_headless_en_macos(monkeypatch):
    monkeypatch.setattr(main.platform, "system", lambda: "Darwin")
    assert main.resolver_headless("manual") is False
    assert main.resolver_headless("auto") is True


def test_resolver_headless_en_windows(monkeypatch):
    monkeypatch.setattr(main.platform, "system", lambda: "Windows")
    assert main.resolver_headless("manual") is False
    assert main.resolver_headless("auto") is False


def test_parse_args_default_es_manual(monkeypatch):
    monkeypatch.setattr(main.sys, "argv", ["main.py"])
    assert main.parse_args().mode == "manual"


def test_parse_args_acepta_auto(monkeypatch):
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--mode", "auto"])
    assert main.parse_args().mode == "auto"


def test_notificar_windows_no_hace_nada_fuera_de_windows(monkeypatch):
    monkeypatch.setattr(main.platform, "system", lambda: "Darwin")
    main.notificar_windows(True)
    main.notificar_windows(False)


def test_notificar_windows_muestra_beep_y_messagebox(monkeypatch):
    monkeypatch.setattr(main.platform, "system", lambda: "Windows")

    eventos = {"beep": [], "msg": []}

    fake_winsound = types.SimpleNamespace(
        MB_ICONASTERISK=0x40,
        MB_ICONHAND=0x10,
        MessageBeep=lambda code: eventos["beep"].append(code),
    )
    monkeypatch.setitem(sys.modules, "winsound", fake_winsound)

    class FakeUser32:
        @staticmethod
        def MessageBoxW(hwnd, text, title, style):
            eventos["msg"].append((hwnd, text, title, style))
            return 1

    monkeypatch.setattr(
        main.ctypes,
        "windll",
        types.SimpleNamespace(user32=FakeUser32()),
        raising=False,
    )

    main.notificar_windows(True)
    main.notificar_windows(False)

    assert eventos["beep"] == [fake_winsound.MB_ICONASTERISK, fake_winsound.MB_ICONHAND]
    assert eventos["msg"][0] == (0, "Proceso finalizado correctamente", "Grupo2000", 0x00000040)
    assert eventos["msg"][1] == (0, "Error en la ejecución. Revisar log.", "Grupo2000", 0x00000010)
