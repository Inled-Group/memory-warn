#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify
import psutil
import os

class MemoryMonitorApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Monitor de Memoria")
        self.set_default_size(400, 200)
        self.set_border_width(10)
        self.connect("destroy", Gtk.main_quit)
        
        # Inicializar notificaciones
        Notify.init("Monitor de Memoria")
        
        # Variables de configuración
        self.threshold = 80  # Porcentaje por defecto
        self.check_interval = 5  # Segundos
        self.notification_sent = False
        
        # Crear layout principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Mostrar uso actual de memoria
        self.memory_label = Gtk.Label()
        vbox.pack_start(self.memory_label, True, True, 0)
        
        # Crear slider para ajustar el umbral
        threshold_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        threshold_label = Gtk.Label(label="Umbral de alerta (%): ")
        threshold_box.pack_start(threshold_label, False, False, 0)
        
        self.threshold_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 10, 100, 5)
        self.threshold_slider.set_value(self.threshold)
        self.threshold_slider.connect("value-changed", self.on_threshold_changed)
        threshold_box.pack_start(self.threshold_slider, True, True, 0)
        
        vbox.pack_start(threshold_box, False, False, 0)
        
        # Intervalo de comprobación
        interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        interval_label = Gtk.Label(label="Intervalo de comprobación (s): ")
        interval_box.pack_start(interval_label, False, False, 0)
        
        # Aquí está la corrección - usar argumentos con nombre en lugar de posicionales
        self.interval_spinner = Gtk.SpinButton()
        adjustment = Gtk.Adjustment(
            value=self.check_interval,
            lower=1,
            upper=60,
            step_increment=1,
            page_increment=5,
            page_size=0
        )
        self.interval_spinner.set_adjustment(adjustment)
        self.interval_spinner.connect("value-changed", self.on_interval_changed)
        interval_box.pack_start(self.interval_spinner, False, False, 0)
        
        vbox.pack_start(interval_box, False, False, 0)
        
        # Botones
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.start_button = Gtk.Button(label="Iniciar Monitoreo")
        self.start_button.connect("clicked", self.on_start_clicked)
        button_box.pack_start(self.start_button, True, True, 0)
        
        self.stop_button = Gtk.Button(label="Detener")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        self.stop_button.set_sensitive(False)
        button_box.pack_start(self.stop_button, True, True, 0)
        
        vbox.pack_start(button_box, False, False, 0)
        
        self.status_label = Gtk.Label(label="Estado: Detenido")
        vbox.pack_start(self.status_label, False, False, 0)
        
        # ID del temporizador
        self.timer_id = None
        
        # Actualizar la información de memoria al inicio
        self.update_memory_info()
    
    def on_threshold_changed(self, slider):
        self.threshold = slider.get_value()
        self.notification_sent = False
    
    def on_interval_changed(self, spinner):
        self.check_interval = spinner.get_value_as_int()
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = GLib.timeout_add_seconds(self.check_interval, self.check_memory)
    
    def on_start_clicked(self, button):
        if self.timer_id is None:
            self.timer_id = GLib.timeout_add_seconds(self.check_interval, self.check_memory)
            self.status_label.set_text("Estado: Monitoreando")
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(True)
    
    def on_stop_clicked(self, button):
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
            self.status_label.set_text("Estado: Detenido")
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
    
    def check_memory(self):
        memory_percent = self.update_memory_info()
        
        if memory_percent >= self.threshold and not self.notification_sent:
            self.show_notification(memory_percent)
            self.notification_sent = True
        elif memory_percent < self.threshold:
            self.notification_sent = False
        
        return True
    
    def update_memory_info(self):
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024 * 1024 * 1024)  # En GB
        memory_total = memory.total / (1024 * 1024 * 1024)  # En GB
        
        self.memory_label.set_text(
            f"Uso de memoria: {memory_percent:.1f}%\n"
            f"Utilizado: {memory_used:.2f} GB / Total: {memory_total:.2f} GB"
        )
        
        return memory_percent
    
    def show_notification(self, memory_percent):
        notification = Notify.Notification.new(
            "¡Alerta de uso de memoria!",
            f"El uso de memoria ha alcanzado {memory_percent:.1f}%, "
            f"superando el umbral establecido de {self.threshold:.1f}%",
            "dialog-warning"
        )
        notification.set_urgency(2)  # Urgencia crítica
        notification.show()

def main():
    app = MemoryMonitorApp()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()