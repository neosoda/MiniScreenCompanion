from unittest.mock import MagicMock, patch
from mini_screen_companion.screens.geekmagic_serial import GeekMagicSerialScreen

def test_geekmagic_serial_update_hud():
    screen = GeekMagicSerialScreen(port="COM7", baudrate=115200)

    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.readline.return_value = b'{"status":"ok"}\r\n'

    with patch.object(screen, "_get_serial", return_value=mock_serial):
        ok = screen.update_hud(
            claude=92,
            codex=85,
            gemini=70,
            act="desk",
            mood="Dans le flow",
            msg="Systeme pret",
            rot=4
        )
        assert ok is True
        assert mock_serial.write.called
        written = mock_serial.write.call_args[0][0]
        assert b'"claude": 92' in written
        assert b'"act": "desk"' in written
        assert b'"rot": 4' in written

def test_geekmagic_serial_is_reachable():
    screen = GeekMagicSerialScreen(port="COM7", baudrate=115200)

    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.readline.return_value = b'{"status":"pong"}\r\n'

    with patch.object(screen, "_get_serial", return_value=mock_serial):
        assert screen.is_reachable() is True
