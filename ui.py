import math
import platform

import psutil
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from Cpu import CpuMonitor


WINDOW_W = 560
WINDOW_H = 840
WINDOW_RADIUS = 26

BG_DEEP = QColor(6, 8, 16)
BG_PANEL = QColor(15, 20, 34)
BG_CARD = QColor(255, 255, 255, 16)
BORDER = QColor(255, 255, 255, 28)
WHITE = QColor(255, 255, 255)
MUTED = QColor(170, 178, 205)
DIMMED = QColor(92, 104, 134)


def cpu_palette(value):
    if value > 80:
        return QColor(255, 78, 112), QColor(255, 42, 80), QColor(255, 72, 110, 135)
    if value >= 50:
        return QColor(255, 190, 66), QColor(255, 142, 36), QColor(255, 180, 58, 120)
    return QColor(42, 214, 255), QColor(58, 132, 255), QColor(56, 210, 255, 120)


def status_copy(value):
    if value > 80:
        return "HIGH LOAD", "Performance is under pressure"
    if value >= 50:
        return "ACTIVE LOAD", "System is working steadily"
    return "HEALTHY", "Realtime telemetry looks stable"


def short_cpu_name():
    name = platform.processor() or platform.uname().processor or platform.machine() or "Desktop CPU"
    name = " ".join(name.split())
    if len(name) > 48:
        return name[:45] + "..."
    return name


def make_app_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    rect = QRectF(4, 4, 56, 56)
    base = QLinearGradient(4, 4, 60, 60)
    base.setColorAt(0.0, QColor(36, 214, 255))
    base.setColorAt(0.5, QColor(147, 112, 255))
    base.setColorAt(1.0, QColor(255, 84, 126))
    painter.setBrush(QBrush(base))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(rect, 16, 16)

    painter.setBrush(QColor(8, 10, 20, 220))
    painter.drawRoundedRect(QRectF(11, 11, 42, 42), 12, 12)
    painter.setPen(QPen(QColor(255, 255, 255), 3, Qt.SolidLine, Qt.RoundCap))
    painter.drawArc(QRectF(19, 19, 26, 26), 210 * 16, -250 * 16)
    painter.end()
    return QIcon(pixmap)


class TitleButton(QLabel):
    def __init__(self, text, danger=False, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(28, 26)
        hover = "rgba(255, 82, 116, 0.86)" if danger else "rgba(255, 255, 255, 0.14)"
        self.setStyleSheet(
            f"""
            QLabel {{
                color: rgba(255,255,255,0.62);
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 9px;
                font-size: 13px;
                font-weight: 700;
            }}
            QLabel:hover {{
                color: white;
                background: {hover};
            }}
            """
        )
        self.setCursor(Qt.PointingHandCursor)


class CPUCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(252, 252)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._value = 0.0
        self._displayed = 0.0
        self._pulse = 0.0

        timer = QTimer(self)
        timer.timeout.connect(self._step)
        timer.start(16)

    def set_value(self, value):
        self._value = float(max(0, min(100, value)))

    def _step(self):
        self._displayed += (self._value - self._displayed) * 0.09
        self._pulse = (self._pulse + 2.0) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        value = self._displayed
        primary, secondary, glow = cpu_palette(value)

        outer = QPainterPath()
        outer.addEllipse(QRectF(7, 7, w - 14, h - 14))
        body = QRadialGradient(cx, cy, cx)
        body.setColorAt(0.0, QColor(255, 255, 255, 20))
        body.setColorAt(0.55, QColor(19, 25, 42, 220))
        body.setColorAt(1.0, QColor(7, 10, 22, 235))
        painter.fillPath(outer, QBrush(body))

        pulse = (math.sin(math.radians(self._pulse)) + 1) / 2
        painter.setPen(QPen(QColor(glow.red(), glow.green(), glow.blue(), int(46 + 32 * pulse)), 18))
        painter.drawEllipse(QRectF(16, 16, w - 32, h - 32))

        arc_rect = QRectF(31, 31, w - 62, h - 62)
        span = int(-270 * 16 * (value / 100))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, 225 * 16, -270 * 16)

        if span:
            arc = QConicalGradient(cx, cy, 225)
            arc.setColorAt(0.0, secondary)
            arc.setColorAt(0.45, primary)
            arc.setColorAt(1.0, secondary)
            painter.setPen(QPen(QBrush(arc), 9, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(arc_rect, 225 * 16, span)

        for index in range(36):
            angle = math.radians(225 - (270 / 35) * index)
            active = (index / 35) <= value / 100
            radius_outer = 106
            radius_inner = 100 if index % 3 == 0 else 103
            x1 = cx + radius_outer * math.cos(angle)
            y1 = cy - radius_outer * math.sin(angle)
            x2 = cx + radius_inner * math.cos(angle)
            y2 = cy - radius_inner * math.sin(angle)
            color = QColor(primary.red(), primary.green(), primary.blue(), 160) if active else QColor(255, 255, 255, 24)
            painter.setPen(QPen(color, 1.2 if index % 3 == 0 else 0.7, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        painter.setFont(QFont("Arial", 58, QFont.DemiBold))
        painter.setPen(WHITE)
        painter.drawText(QRectF(cx - 88, cy - 57, 176, 72), Qt.AlignCenter, f"{int(value)}")

        painter.setFont(QFont("Arial", 18, QFont.Medium))
        painter.setPen(QColor(210, 218, 240, 190))
        painter.drawText(QRectF(cx + 35, cy - 43, 34, 38), Qt.AlignLeft | Qt.AlignVCenter, "%")

        label_font = QFont("Arial", 9, QFont.Medium)
        label_font.setLetterSpacing(QFont.AbsoluteSpacing, 2.4)
        painter.setFont(label_font)
        painter.setPen(QColor(170, 178, 205, 130))
        painter.drawText(QRectF(cx - 85, cy + 30, 170, 22), Qt.AlignCenter, "REALTIME CPU")
        painter.end()


class StatusBadge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self._title = "INITIALIZING"
        self._detail = "Reading system telemetry"
        self._value = 0
        self._color = QColor(42, 214, 255)
        self._pulse = 0

        timer = QTimer(self)
        timer.timeout.connect(self._step)
        timer.start(30)

    def set_status(self, title, detail, value, color):
        self._title = title
        self._detail = detail
        self._value = int(value)
        self._color = color
        self.update()

    def _step(self):
        self._pulse = (self._pulse + 3) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        path = QPainterPath()
        path.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 17, 17)
        fill = QLinearGradient(0, 0, w, h)
        fill.setColorAt(0.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 38))
        fill.setColorAt(1.0, QColor(255, 255, 255, 8))
        painter.fillPath(path, QBrush(fill))
        painter.setPen(QPen(QColor(self._color.red(), self._color.green(), self._color.blue(), 80), 0.9))
        painter.drawPath(path)

        pulse = (math.sin(math.radians(self._pulse)) + 1) / 2
        painter.setBrush(QColor(self._color.red(), self._color.green(), self._color.blue(), int(150 + pulse * 100)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(24, h / 2), 5.5, 5.5)

        painter.setFont(QFont("Arial", 11, QFont.DemiBold))
        painter.setPen(WHITE)
        painter.drawText(QRectF(42, 7, w - 140, 17), Qt.AlignLeft | Qt.AlignVCenter, self._title)

        painter.setFont(QFont("Arial", 9, QFont.Medium))
        painter.setPen(QColor(220, 228, 246, 150))
        painter.drawText(QRectF(42, 24, w - 140, 15), Qt.AlignLeft | Qt.AlignVCenter, self._detail)

        painter.setFont(QFont("Arial", 20, QFont.DemiBold))
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(w - 90, 0, 58, h), Qt.AlignRight | Qt.AlignVCenter, f"{self._value}")
        painter.setFont(QFont("Arial", 11, QFont.Medium))
        painter.setPen(QColor(220, 228, 246, 150))
        painter.drawText(QRectF(w - 31, 2, 22, h), Qt.AlignLeft | Qt.AlignVCenter, "%")
        painter.end()


class SlimBar(QWidget):
    def __init__(self, label="", parent=None):
        super().__init__(parent)
        self.label = label
        self.setFixedHeight(26)
        self._fill = 0.0
        self._target = 0.0

        timer = QTimer(self)
        timer.timeout.connect(self._step)
        timer.start(16)

    def set_value(self, value):
        self._target = max(0, min(100, value)) / 100.0

    def _step(self):
        self._fill += (self._target - self._fill) * 0.12
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        value = self._fill
        primary, secondary, _ = cpu_palette(value * 100)

        painter.setFont(QFont("Arial", 9, QFont.Medium))
        painter.setPen(QColor(170, 178, 205, 145))
        label_w = 58
        painter.drawText(QRectF(0, 0, label_w, h), Qt.AlignLeft | Qt.AlignVCenter, self.label.upper())

        bar_x = label_w
        bar_w = w - label_w - 45
        bar_h = 5
        bar_y = (h - bar_h) / 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 3, 3)

        fill_w = bar_w * value
        if fill_w > 2:
            gradient = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            gradient.setColorAt(0.0, secondary)
            gradient.setColorAt(1.0, primary)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 3, 3)

        painter.setFont(QFont("Arial", 10, QFont.DemiBold))
        painter.setPen(WHITE if value > 0.02 else MUTED)
        painter.drawText(QRectF(w - 42, 0, 42, h), Qt.AlignRight | Qt.AlignVCenter, f"{int(value * 100)}%")
        painter.end()


class TrendGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(82)
        self._values = [0] * 54
        self._current = 0

    def add_value(self, value):
        self._current = max(0, min(100, int(value)))
        self._values = self._values[1:] + [self._current]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        frame = QPainterPath()
        frame.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 18, 18)
        panel = QLinearGradient(0, 0, w, h)
        panel.setColorAt(0.0, QColor(255, 255, 255, 18))
        panel.setColorAt(1.0, QColor(255, 255, 255, 6))
        painter.fillPath(frame, QBrush(panel))
        painter.setPen(QPen(QColor(255, 255, 255, 24), 0.8))
        painter.drawPath(frame)

        painter.setClipPath(frame)
        left, top, right, bottom = 18, 25, w - 18, h - 15
        for index in range(1, 4):
            y = top + (bottom - top) * index / 4
            painter.setPen(QPen(QColor(255, 255, 255, 13), 0.6))
            painter.drawLine(left, y, right, y)

        step = (right - left) / (len(self._values) - 1)
        points = []
        for index, value in enumerate(self._values):
            x = left + step * index
            y = bottom - (bottom - top) * (value / 100)
            points.append((x, y))

        graph = QPainterPath()
        graph.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            graph.lineTo(x, y)

        fill = QPainterPath()
        fill.moveTo(left, bottom)
        for x, y in points:
            fill.lineTo(x, y)
        fill.lineTo(right, bottom)
        fill.closeSubpath()

        area = QLinearGradient(0, top, 0, bottom)
        area.setColorAt(0.0, QColor(52, 211, 255, 62))
        area.setColorAt(1.0, QColor(52, 211, 255, 0))
        painter.fillPath(fill, QBrush(area))

        line = QLinearGradient(left, 0, right, 0)
        line.setColorAt(0.0, QColor(42, 214, 255))
        line.setColorAt(0.52, QColor(150, 116, 255))
        line.setColorAt(1.0, QColor(255, 88, 128))
        painter.setPen(QPen(QBrush(line), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(graph)

        painter.setClipping(False)
        painter.setFont(QFont("Arial", 9, QFont.DemiBold))
        painter.setPen(QColor(170, 178, 205, 175))
        painter.drawText(QRectF(18, 7, w - 90, 16), Qt.AlignLeft | Qt.AlignVCenter, "LIVE CPU TREND")

        painter.setFont(QFont("Arial", 10, QFont.DemiBold))
        painter.setPen(QColor(255, 255, 255, 210))
        painter.drawText(QRectF(w - 70, 7, 52, 16), Qt.AlignRight | Qt.AlignVCenter, f"{self._current}%")
        painter.end()


class MetricCard(QWidget):
    def __init__(self, title, value="--", subtitle="", parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._accent = QColor(42, 214, 255)

    def set_value(self, value, subtitle=None, accent=None):
        self._value = value
        if subtitle is not None:
            self._subtitle = subtitle
        if accent is not None:
            self._accent = accent
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        path = QPainterPath()
        path.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 16, 16)
        fill = QLinearGradient(0, 0, w, h)
        fill.setColorAt(0.0, QColor(255, 255, 255, 18))
        fill.setColorAt(1.0, QColor(255, 255, 255, 6))
        painter.fillPath(path, QBrush(fill))
        painter.setPen(QPen(QColor(255, 255, 255, 26), 0.8))
        painter.drawPath(path)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 150))
        painter.drawRoundedRect(QRectF(12, 13, 4, h - 26), 2, 2)

        painter.setFont(QFont("Arial", 8, QFont.DemiBold))
        painter.setPen(QColor(170, 178, 205, 150))
        painter.drawText(QRectF(25, 9, w - 35, 14), Qt.AlignLeft | Qt.AlignVCenter, self._title.upper())

        painter.setFont(QFont("Arial", 16, QFont.DemiBold))
        painter.setPen(WHITE)
        painter.drawText(QRectF(25, 25, w - 35, 20), Qt.AlignLeft | Qt.AlignVCenter, self._value)

        if self._subtitle:
            painter.setFont(QFont("Arial", 8, QFont.Medium))
            painter.setPen(QColor(170, 178, 205, 120))
            painter.drawText(QRectF(25, 43, w - 35, 13), Qt.AlignLeft | Qt.AlignVCenter, self._subtitle)
        painter.end()


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cpu = 0
        self._phase = 0.0

        timer = QTimer(self)
        timer.timeout.connect(self._step)
        timer.start(33)

    def set_cpu(self, value):
        self._cpu = value
        self.update()

    def _step(self):
        self._phase = (self._phase + 0.01) % (math.pi * 2)
        self.update()

    def _draw_glow(self, painter, x, y, radius, color, alpha):
        gradient = QRadialGradient(x, y, radius)
        gradient.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), alpha))
        gradient.setColorAt(0.45, QColor(color.red(), color.green(), color.blue(), int(alpha * 0.35)))
        gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        painter.fillRect(0, 0, self.width(), self.height(), gradient)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        phase = self._phase

        shell = QPainterPath()
        shell.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), WINDOW_RADIUS, WINDOW_RADIUS)
        painter.setClipPath(shell)

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor(7, 8, 18))
        base.setColorAt(0.45, QColor(9, 14, 30))
        base.setColorAt(1.0, QColor(6, 8, 18))
        painter.fillRect(0, 0, w, h, base)

        painter.setCompositionMode(QPainter.CompositionMode_Screen)
        size = max(w, h) * 0.52
        self._draw_glow(
            painter,
            w * (0.22 + 0.10 * math.sin(phase * 0.9)),
            h * (0.18 + 0.06 * math.cos(phase)),
            size,
            QColor(28, 126, 255),
            72,
        )
        self._draw_glow(
            painter,
            w * (0.78 + 0.08 * math.cos(phase * 0.8)),
            h * (0.24 + 0.08 * math.sin(phase * 1.1)),
            size * 0.95,
            QColor(212, 70, 255),
            58,
        )
        self._draw_glow(
            painter,
            w * (0.50 + 0.14 * math.sin(phase * 0.7 + 1.2)),
            h * (0.62 + 0.09 * math.cos(phase * 0.85)),
            size * 1.05,
            QColor(46, 229, 195),
            46,
        )

        primary, _, _ = cpu_palette(self._cpu)
        self._draw_glow(
            painter,
            w * (0.55 + 0.12 * math.sin(phase * 1.35)),
            h * (0.45 + 0.10 * math.cos(phase)),
            size * 0.72,
            primary,
            28 + int(min(44, self._cpu * 0.3)),
        )

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        shade = QLinearGradient(0, 0, 0, h)
        shade.setColorAt(0.0, QColor(0, 0, 0, 18))
        shade.setColorAt(0.58, QColor(0, 0, 0, 46))
        shade.setColorAt(1.0, QColor(0, 0, 0, 82))
        painter.fillRect(0, 0, w, h, shade)

        painter.setClipping(False)
        painter.setPen(QPen(QColor(255, 255, 255, 34), 1))
        painter.drawPath(shell)
        painter.end()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor = CpuMonitor()
        self._drag_pos = None
        self._build()

        timer = QTimer(self)
        timer.timeout.connect(self._refresh)
        timer.start(1000)
        self._refresh()

    def _build(self):
        self.setWindowTitle("CPU Monitor Pro")
        self.setWindowIcon(make_app_icon())
        self.setFixedSize(WINDOW_W, WINDOW_H)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.bg = BackgroundWidget(self)
        self.bg.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        self.bg.lower()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(10)

        logo = QLabel("CP")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(36, 36)
        logo.setStyleSheet(
            """
            QLabel {
                color: white;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 12px;
                font-size: 13px;
                font-weight: 800;
            }
            """
        )
        top.addWidget(logo)

        brand = QVBoxLayout()
        brand.setSpacing(1)
        title = QLabel("CPU MONITOR PRO")
        title.setStyleSheet("color: rgba(245,248,255,0.95); font-size: 13px; font-weight: 800; letter-spacing: 3px;")
        subtitle = QLabel("Realtime desktop telemetry")
        subtitle.setStyleSheet("color: rgba(185,195,220,0.58); font-size: 10px; font-weight: 500;")
        brand.addWidget(title)
        brand.addWidget(subtitle)
        top.addLayout(brand)
        top.addStretch()

        minimize = TitleButton("-")
        minimize.mousePressEvent = lambda _: self.showMinimized()
        close = TitleButton("X", danger=True)
        close.mousePressEvent = lambda _: self.close()
        top.addWidget(minimize)
        top.addWidget(close)
        root.addLayout(top)
        root.addSpacing(12)

        summary = QWidget()
        summary.setFixedHeight(56)
        summary.setStyleSheet(
            """
            QWidget {
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 18px;
            }
            QLabel { border: none; background: transparent; }
            """
        )
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(16, 8, 16, 8)
        summary_layout.setSpacing(12)
        summary_text = QVBoxLayout()
        summary_text.setSpacing(1)
        self.cpu_name = QLabel(short_cpu_name())
        self.cpu_name.setStyleSheet("color: rgba(255,255,255,0.92); font-size: 12px; font-weight: 700;")
        self.summary_meta = QLabel("Starting sensors")
        self.summary_meta.setStyleSheet("color: rgba(185,195,220,0.58); font-size: 10px; font-weight: 500;")
        summary_text.addWidget(self.cpu_name)
        summary_text.addWidget(self.summary_meta)
        summary_layout.addLayout(summary_text)
        summary_layout.addStretch()
        self.live_label = QLabel("LIVE")
        self.live_label.setAlignment(Qt.AlignCenter)
        self.live_label.setFixedSize(54, 26)
        self.live_label.setStyleSheet(
            "color: rgba(170,255,235,0.95); background: rgba(45,245,190,0.11); "
            "border: 1px solid rgba(90,255,220,0.20); border-radius: 13px; font-size: 10px; font-weight: 800;"
        )
        summary_layout.addWidget(self.live_label)
        root.addWidget(summary)
        root.addSpacing(10)

        self.canvas = CPUCanvas()
        root.addWidget(self.canvas, alignment=Qt.AlignCenter)
        root.addSpacing(8)

        self.badge = StatusBadge()
        root.addWidget(self.badge)
        root.addSpacing(10)

        self.trend = TrendGraph()
        root.addWidget(self.trend)
        root.addSpacing(10)

        section = QLabel("CORE ACTIVITY")
        section.setStyleSheet("color: rgba(170,178,205,0.62); font-size: 10px; font-weight: 800; letter-spacing: 2px;")
        root.addWidget(section)
        root.addSpacing(5)

        core_count = psutil.cpu_count(logical=True) or 1
        self._bars = []
        for index in range(min(core_count, 4)):
            bar = SlimBar(f"Core {index}")
            self._bars.append(bar)
            root.addWidget(bar)
            root.addSpacing(1)

        root.addSpacing(9)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(10)
        metrics.setVerticalSpacing(10)
        self.freq_card = MetricCard("Frequency")
        self.memory_card = MetricCard("Memory")
        self.temp_card = MetricCard("Temperature")
        self.boot_card = MetricCard("Boot Time")
        metrics.addWidget(self.freq_card, 0, 0)
        metrics.addWidget(self.memory_card, 0, 1)
        metrics.addWidget(self.temp_card, 1, 0)
        metrics.addWidget(self.boot_card, 1, 1)
        root.addLayout(metrics)

    def _refresh(self):
        cpu_total = self.monitor.get_cpu_usage()
        primary, _, _ = cpu_palette(cpu_total)
        title, detail = status_copy(cpu_total)

        self.canvas.set_value(cpu_total)
        self.bg.set_cpu(cpu_total)
        self.badge.set_status(title, detail, cpu_total, primary)
        self.trend.add_value(cpu_total)

        per_core = psutil.cpu_percent(percpu=True)
        for index, bar in enumerate(self._bars):
            if index < len(per_core):
                bar.set_value(per_core[index])

        freq = psutil.cpu_freq()
        if freq:
            self.freq_card.set_value(f"{freq.current / 1000:.1f} GHz", "current clock", primary)
        else:
            self.freq_card.set_value("N/A", "clock unavailable", primary)

        memory = psutil.virtual_memory()
        used_gb = (memory.total - memory.available) / (1024 ** 3)
        total_gb = memory.total / (1024 ** 3)
        self.memory_card.set_value(f"{memory.percent:.1f} %", f"{used_gb:.1f}/{total_gb:.1f} GB", primary)

        temp = self.monitor.get_temperature()
        if temp is not None:
            temp_color = cpu_palette(85 if temp > 80 else 55 if temp > 65 else 20)[0]
            self.temp_card.set_value(f"{temp:.1f} C", "estimated sensor", temp_color)
        else:
            self.temp_card.set_value("N/A", "sensor unavailable", primary)

        self.boot_card.set_value(self.monitor.get_boot_time(), self.monitor.get_uptime(), primary)

        process_count = self.monitor.get_process_count()
        cores = psutil.cpu_count(logical=True) or 1
        physical = psutil.cpu_count(logical=False) or cores
        self.summary_meta.setText(f"{physical} physical / {cores} logical cores | {process_count} processes")

    def resizeEvent(self, event):
        if hasattr(self, "bg"):
            self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
