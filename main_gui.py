"""
OMNI-AI Futuristic Python GUI
Built with Kivy - Purple-Dark Morphism + Neon Aesthetic
"""

import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.anchorlayout import AnchorLayout

import matplotlib.pyplot as plt
import numpy as np
import threading
import psutil
import json
from datetime import datetime

# Set window size
Window.size = (1400, 900)


class OmniAIGUI(App):
    """Main OMNI-AI Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "OMNI-AI - Futuristic Dashboard"
        self.settings = {
            'neon_effects': True,
            'sound_enabled': True,
            'animations_enabled': True
        }
        
    def build(self):
        """Build the main application"""
        self.root = ScreenManager()
        
        # Create main dashboard screen
        main_screen = MainDashboard(name='main')
        self.root.add_widget(main_screen)
        
        return self.root


class MainDashboard(Screen):
    """Main dashboard with tabbed interface"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_monitor = SystemMonitor()
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = self._create_header()
        self.main_layout.add_widget(header)
        
        # Tabbed panel for sections
        self.tabbed_panel = TabbedPanel(do_default_tab=False)
        
        # Create tabs for each section
        self._create_dashboard_tab()
        self._create_voice_tab()
        self._create_security_tab()
        self._create_monitor_tab()
        self._create_ai_tab()
        self._create_terminal_tab()
        
        self.main_layout.add_widget(self.tabbed_panel)
        
        self.add_widget(self.main_layout)
        
        # Schedule periodic updates
        Clock.schedule_interval(self.update_dashboard, 2)
        
    def _create_header(self):
        """Create header with title and controls"""
        header = BoxLayout(size_hint_y=0.1, spacing=10, padding=10)
        header.canvas.before.clear()
        
        with header.canvas.before:
            Color(0.05, 0.05, 0.18, 1)  # Dark purple background
            Rectangle(size=header.size, pos=header.pos)
            Color(0.85, 0.56, 0.94, 0.3)  # Neon purple border
            Line(rectangle=(header.x, header.y, header.width, header.height), width=2)
        
        # Title
        title = Label(
            text='[b][size=24]OMNI-AI[/size] - Futuristic Dashboard[/b]',
            markup=True,
            size_hint_x=0.7,
            color=(0.85, 0.56, 0.94, 1)  # Neon purple
        )
        header.add_widget(title)
        
        # Settings button
        settings_btn = Button(
            text='⚙ Settings',
            size_hint_x=0.15,
            background_color=(0.85, 0.56, 0.94, 0.7),  # Neon purple
            color=(0.05, 0.05, 0.18, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        header.add_widget(settings_btn)
        
        # Theme button
        theme_btn = Button(
            text='🌙 Theme',
            size_hint_x=0.15,
            background_color=(0, 0.73, 0.83, 0.7),  # Neon cyan
            color=(0.05, 0.05, 0.18, 1)
        )
        header.add_widget(theme_btn)
        
        return header
    
    def _create_dashboard_tab(self):
        """Dashboard section with system stats"""
        tab = TabbedPanelItem(text='📊 Dashboard')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # System stats grid
        stats_grid = GridLayout(cols=4, spacing=10, size_hint_y=0.4)
        stats_grid.canvas.before.clear()
        
        with stats_grid.canvas.before:
            Color(0.05, 0.05, 0.18, 0.8)
            Rectangle(size=stats_grid.size, pos=stats_grid.pos)
        
        # CPU
        cpu_stat = self._create_stat_card('CPU Usage', '0%', (0.85, 0.56, 0.94))
        stats_grid.add_widget(cpu_stat)
        
        # Memory
        mem_stat = self._create_stat_card('Memory Usage', '0%', (0, 0.73, 0.83))
        stats_grid.add_widget(mem_stat)
        
        # Disk
        disk_stat = self._create_stat_card('Disk Usage', '0%', (0.92, 0.56, 0.62))
        stats_grid.add_widget(disk_stat)
        
        # Network
        net_stat = self._create_stat_card('Network Status', 'Active', (0.06, 0.73, 0.5))
        stats_grid.add_widget(net_stat)
        
        layout.add_widget(stats_grid)
        
        # Quick actions
        actions_label = Label(text='Quick Actions', size_hint_y=0.1, bold=True,
                             color=(0.85, 0.56, 0.94, 1))
        layout.add_widget(actions_label)
        
        actions_grid = GridLayout(cols=3, spacing=10, size_hint_y=0.3)
        
        for action in ['System Health Check', 'Security Audit', 'Voice Test']:
            btn = Button(
                text=action,
                background_color=(0.85, 0.56, 0.94, 0.6),
                color=(0.05, 0.05, 0.18, 1)
            )
            btn.bind(on_press=lambda x, a=action: self.execute_action(a))
            actions_grid.add_widget(btn)
        
        layout.add_widget(actions_grid)
        
        # Info section
        info_label = Label(
            text='System Status: OPERATIONAL\nAll systems nominal\nLast check: Now',
            markup=True,
            size_hint_y=0.2,
            color=(0.06, 0.73, 0.5, 1)
        )
        layout.add_widget(info_label)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_voice_tab(self):
        """Voice interaction section"""
        tab = TabbedPanelItem(text='🎤 Voice')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Voice visualizer
        visualizer = self._create_voice_visualizer()
        layout.add_widget(visualizer)
        
        # Control buttons
        controls = GridLayout(cols=3, spacing=10, size_hint_y=0.2)
        
        start_btn = Button(
            text='🔴 Start Listening',
            background_color=(0.92, 0.56, 0.62, 0.7),
            color=(0.05, 0.05, 0.18, 1)
        )
        start_btn.bind(on_press=self.start_voice)
        controls.add_widget(start_btn)
        
        stop_btn = Button(
            text='⭕ Stop',
            background_color=(0.6, 0.3, 0.3, 0.7),
            color=(1, 1, 1, 1)
        )
        controls.add_widget(stop_btn)
        
        test_btn = Button(
            text='🔊 Test',
            background_color=(0.06, 0.73, 0.5, 0.7),
            color=(0.05, 0.05, 0.18, 1)
        )
        controls.add_widget(test_btn)
        
        layout.add_widget(controls)
        
        # Transcript display
        transcript = TextInput(
            text='[Voice input will appear here]',
            multiline=True,
            readonly=True,
            background_color=(0.05, 0.05, 0.18, 0.8),
            foreground_color=(0.06, 0.73, 0.5, 1),
            font_size='12sp'
        )
        layout.add_widget(transcript)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_security_tab(self):
        """Security & Encryption section"""
        tab = TabbedPanelItem(text='🔐 Security')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView()
        scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        
        # Encryption card
        enc_card = self._create_security_card(
            title='Data Encryption (Fernet)',
            subtitle='Encrypt sensitive data',
            color=(0.85, 0.56, 0.94)
        )
        scroll_layout.add_widget(enc_card)
        
        # Hash password card
        hash_card = self._create_security_card(
            title='Password Hashing (PBKDF2)',
            subtitle='Secure password hashing',
            color=(0, 0.73, 0.83)
        )
        scroll_layout.add_widget(hash_card)
        
        # Security audit card
        audit_card = self._create_security_card(
            title='Security Audit',
            subtitle='Run comprehensive security check',
            color=(0.92, 0.56, 0.62)
        )
        scroll_layout.add_widget(audit_card)
        
        scroll.add_widget(scroll_layout)
        layout.add_widget(scroll)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_monitor_tab(self):
        """System Monitoring section"""
        tab = TabbedPanelItem(text='📈 Monitor')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create matplotlib figure for CPU history
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # CPU chart
        ax1.set_title('CPU Usage Over Time', color='#d946ef', fontweight='bold')
        ax1.set_facecolor('#0f0f2e')
        ax1.grid(True, alpha=0.2, color='#d946ef')
        x = np.arange(0, 10)
        y_cpu = np.random.randint(10, 80, 10)
        ax1.plot(x, y_cpu, color='#d946ef', linewidth=2, label='CPU %')
        ax1.fill_between(x, y_cpu, alpha=0.3, color='#d946ef')
        ax1.set_ylabel('Usage %', color='#06b6d4')
        ax1.legend(loc='upper left')
        
        # Memory chart
        ax2.set_title('Memory Usage Over Time', color='#06b6d4', fontweight='bold')
        ax2.set_facecolor('#0f0f2e')
        ax2.grid(True, alpha=0.2, color='#06b6d4')
        y_mem = np.random.randint(20, 70, 10)
        ax2.plot(x, y_mem, color='#06b6d4', linewidth=2, label='Memory %')
        ax2.fill_between(x, y_mem, alpha=0.3, color='#06b6d4')
        ax2.set_xlabel('Time (seconds)', color='#66a3ff')
        ax2.set_ylabel('Usage %', color='#66a3ff')
        ax2.legend(loc='upper left')
        
        # Apply dark theme
        for ax in [ax1, ax2]:
            ax.spines['bottom'].set_color('#d946ef')
            ax.spines['left'].set_color('#06b6d4')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#66a3ff')
        
        fig.patch.set_facecolor('#0f0f2e')
        
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_ai_tab(self):
        """AI Models section"""
        tab = TabbedPanelItem(text='🤖 AI Models')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView()
        scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        
        # TensorFlow model
        tf_card = self._create_ai_card(
            title='TensorFlow',
            models='Intent Classification, Entity Extraction',
            status='OPERATIONAL',
            color=(1, 0.65, 0, 0.7)  # Orange
        )
        scroll_layout.add_widget(tf_card)
        
        # PyTorch model
        pt_card = self._create_ai_card(
            title='PyTorch',
            models='Advanced NLP, Transformers',
            status='OPERATIONAL',
            color=(0.85, 0.56, 0.94, 0.7)  # Neon purple
        )
        scroll_layout.add_widget(pt_card)
        
        # Hybrid AI
        hybrid_card = self._create_ai_card(
            title='Hybrid AI Engine',
            models='Intent + NLP + Entity Extraction',
            status='OPERATIONAL',
            color=(0, 0.73, 0.83, 0.7)  # Neon cyan
        )
        scroll_layout.add_widget(hybrid_card)
        
        scroll.add_widget(scroll_layout)
        layout.add_widget(scroll)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_terminal_tab(self):
        """Terminal emulator section"""
        tab = TabbedPanelItem(text='⌨ Terminal')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Display
        display = TextInput(
            text='OMNI-AI Terminal v1.0\nType "help" for commands\n\n>>> ',
            multiline=True,
            readonly=True,
            background_color=(0, 0, 0, 0.9),
            foreground_color=(0.06, 0.73, 0.5, 1),
            font_name='Courier',
            font_size='11sp'
        )
        layout.add_widget(display)
        
        # Input
        input_box = BoxLayout(size_hint_y=0.1, spacing=5)
        
        command_input = TextInput(
            multiline=False,
            background_color=(0, 0, 0, 0.9),
            foreground_color=(0.06, 0.73, 0.5, 1),
            font_name='Courier',
            font_size='11sp',
            hint_text='Enter command...'
        )
        input_box.add_widget(command_input)
        
        execute_btn = Button(
            text='Execute',
            size_hint_x=0.2,
            background_color=(0.06, 0.73, 0.5, 0.7),
            color=(0, 0, 0, 1)
        )
        
        def execute_cmd(btn):
            cmd = command_input.text
            if cmd:
                display.text += f'\n{cmd}\n[Command: {cmd} executed]\n>>> '
                command_input.text = ''
        
        execute_btn.bind(on_press=execute_cmd)
        input_box.add_widget(execute_btn)
        
        layout.add_widget(input_box)
        
        tab.content = layout
        self.tabbed_panel.add_widget(tab)
    
    def _create_stat_card(self, title, value, color):
        """Create a stat card widget"""
        card = BoxLayout(orientation='vertical', padding=10, spacing=5)
        card.canvas.before.clear()
        
        with card.canvas.before:
            Color(0.05, 0.05, 0.18, 0.7)
            Rectangle(size=card.size, pos=card.pos)
            Color(color[0], color[1], color[2], 0.4)
            Line(rectangle=(card.x, card.y, card.width, card.height), width=2)
        
        title_label = Label(text=title, size_hint_y=0.4, bold=True, color=color)
        card.add_widget(title_label)
        
        value_label = Label(text=value, size_hint_y=0.6, font_size='24sp', 
                           bold=True, color=color)
        card.add_widget(value_label)
        
        # Progress bar
        progress = ProgressBar(max=100, value=int(value.rstrip('%') or 0), 
                              size_hint_y=0.3)
        card.add_widget(progress)
        
        return card
    
    def _create_voice_visualizer(self):
        """Create voice visualizer with animated bars"""
        layout = BoxLayout(size_hint_y=0.6, spacing=5, padding=10)
        layout.canvas.before.clear()
        
        with layout.canvas.before:
            Color(0.05, 0.05, 0.18, 0.8)
            Rectangle(size=layout.size, pos=layout.pos)
            Color(0.85, 0.56, 0.94, 0.2)
            Line(rectangle=(layout.x, layout.y, layout.width, layout.height), width=2)
        
        # Add animated bars
        for i in range(20):
            bar = ProgressBar(max=100, value=np.random.randint(30, 90),
                            size_hint_x=1/20, orientation='vertical')
            layout.add_widget(bar)
        
        return layout
    
    def _create_security_card(self, title, subtitle, color):
        """Create security operation card"""
        card = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None, height=120)
        card.canvas.before.clear()
        
        with card.canvas.before:
            Color(0.05, 0.05, 0.18, 0.7)
            Rectangle(size=card.size, pos=card.pos)
            Color(color[0], color[1], color[2], 0.3)
            Line(rectangle=(card.x, card.y, card.width, card.height), width=2)
        
        title_label = Label(text=title, size_hint_y=0.4, bold=True, color=color)
        card.add_widget(title_label)
        
        subtitle_label = Label(text=subtitle, size_hint_y=0.3, color=(0.66, 0.66, 0.66, 1))
        card.add_widget(subtitle_label)
        
        btn = Button(text='Execute', size_hint_y=0.3, background_color=color,
                    color=(0.05, 0.05, 0.18, 1))
        card.add_widget(btn)
        
        return card
    
    def _create_ai_card(self, title, models, status, color):
        """Create AI model card"""
        card = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None, height=130)
        card.canvas.before.clear()
        
        with card.canvas.before:
            Color(0.05, 0.05, 0.18, 0.7)
            Rectangle(size=card.size, pos=card.pos)
            Color(color[0], color[1], color[2], 0.4)
            Line(rectangle=(card.x, card.y, card.width, card.height), width=2)
        
        title_label = Label(text=title, size_hint_y=0.25, bold=True, color=color)
        card.add_widget(title_label)
        
        models_label = Label(text=f'Models: {models}', size_hint_y=0.35, 
                            color=(0.66, 0.66, 0.66, 1), font_size='10sp')
        card.add_widget(models_label)
        
        status_label = Label(text=f'Status: {status}', size_hint_y=0.2, 
                            color=(0.06, 0.73, 0.5, 1), bold=True)
        card.add_widget(status_label)
        
        btn = Button(text='Analyze', size_hint_y=0.2, background_color=color)
        card.add_widget(btn)
        
        return card
    
    def start_voice(self, instance):
        """Start voice listening"""
        print("Voice listening started...")
    
    def execute_action(self, action):
        """Execute quick action"""
        print(f"Executing action: {action}")
    
    def update_dashboard(self, dt):
        """Update dashboard stats"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        # Update would happen here
        return True
    
    def open_settings(self, instance):
        """Open settings modal"""
        popup = Popup(
            title='Settings',
            size_hint=(0.8, 0.6),
            background_color=(0.05, 0.05, 0.18, 1)
        )
        
        settings_layout = GridLayout(cols=1, padding=10, spacing=10)
        
        # Settings options
        for setting in ['Neon Effects', 'Sound Effects', 'Animations']:
            setting_item = BoxLayout(size_hint_y=None, height=50)
            setting_item.add_widget(Label(text=setting, color=color))
            # Add toggle here
            setting_item.add_widget(Button(text='ON', width=100))
            settings_layout.add_widget(setting_item)
        
        close_btn = Button(text='Close', size_hint_y=0.2, 
                          background_color=(0.85, 0.56, 0.94, 0.7))
        close_btn.bind(on_press=popup.dismiss)
        settings_layout.add_widget(close_btn)
        
        popup.content = settings_layout
        popup.open()


class SystemMonitor:
    """System monitoring utilities"""
    
    def get_stats(self):
        """Get system stats"""
        return {
            'cpu': psutil.cpu_percent(interval=0.1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'network': 'Active'
        }


if __name__ == '__main__':
    app = OmniAIGUI()
    app.run()
