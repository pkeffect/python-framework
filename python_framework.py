"""
Internode Bare Metal Python Framework Generator

A single-file, zero-dependency Python project generator that creates
production-ready project structures using only the Python standard library.

Author: pkeffect
License: MIT
Repository: https://github.com/pkeffect/internode-framework
"""

import json
import configparser
import argparse
import venv
import secrets
import logging
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# =============================================================================
# Script Metadata
# =============================================================================

__version__ = "1.3.1"
__author__ = "pkeffect"
__project__ = "Internode Bare Metal Framework"

MIN_PYTHON = (3, 11)

# Check Python version early
if sys.version_info < MIN_PYTHON:
    sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# Path Constants
# =============================================================================

CONFIG_FILE = Path.home() / ".internode.toml"
PLUGINS_DIR = Path.home() / ".internode" / "plugins"

# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_AUTHOR_EMAIL = "your-email@example.com"
DEFAULT_AUTHOR_HANDLE = "@your-handle"

# =============================================================================
# GUI Theme Constants
# =============================================================================

FONT_FAMILY = "Segoe UI"

THEME = {
    "bg": "#1e1e1e",
    "bg_secondary": "#2d2d2d",
    "bg_input": "#3d3d3d",
    "fg": "#ffffff",
    "fg_secondary": "#b0b0b0",
    "accent": "#ff6b35",
    "accent_hover": "#ff8c5a",
    "border": "#4d4d4d",
    "success": "#4caf50",
}

# Style name constants (for DRY compliance)
STYLE_ACCENT_BTN = "Accent.TButton"
STYLE_SECONDARY_BTN = "Secondary.TButton"
CONTENT_TYPE_HTML = "text/html; charset=utf-8"

# =============================================================================
# Configuration File Parser
# =============================================================================


def _parse_toml_line(line: str, current_section: str, config: Dict[str, Any]) -> str:
    """
    Parse a single line of TOML-like config.
    
    Args:
        line: The line to parse (already stripped).
        current_section: The current section name.
        config: The config dict to update.
    
    Returns:
        The new current section name.
    """
    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return current_section
    
    # Section header
    if line.startswith("[") and line.endswith("]"):
        section = line[1:-1]
        if section not in config:
            config[section] = {}
        return section
    
    # Key-value pair
    if "=" in line:
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        
        if current_section == "default":
            config[key] = value
        else:
            if current_section not in config:
                config[current_section] = {}
            config[current_section][key] = value
    
    return current_section


def load_config_file() -> Dict[str, Any]:
    """
    Load user defaults from ~/.internode.toml if it exists.
    
    Returns:
        Dictionary of configuration values.
    """
    config: Dict[str, Any] = {}
    
    if not CONFIG_FILE.exists():
        return config
    
    try:
        content = CONFIG_FILE.read_text(encoding="utf-8")
        current_section = "default"
        
        for line in content.splitlines():
            current_section = _parse_toml_line(line.strip(), current_section, config)
        
        logger.info("Loaded config from %s", CONFIG_FILE)
    except Exception as e:
        logger.warning("Could not parse config file: %s", e)
    
    return config


# =============================================================================
# Plugin System
# =============================================================================


def load_plugins() -> List[Dict[str, Any]]:
    """
    Load user-defined plugins from ~/.internode/plugins/.
    
    Plugins must define a register() function that returns plugin metadata.
    Optional hooks: post_generate(generator), post_update(generator).
    
    Returns:
        List of loaded plugin dictionaries.
    """
    plugins: List[Dict[str, Any]] = []
    
    if not PLUGINS_DIR.exists():
        return plugins
    
    for plugin_file in PLUGINS_DIR.glob("*.py"):
        try:
            plugin_code = plugin_file.read_text(encoding="utf-8")
            plugin_module: Dict[str, Any] = {
                "__name__": plugin_file.stem,
                "__file__": str(plugin_file),
            }
            exec(compile(plugin_code, plugin_file, "exec"), plugin_module)
            
            if "register" in plugin_module:
                plugin_info = plugin_module["register"]()
                if plugin_info:
                    plugins.append({
                        "name": plugin_file.stem,
                        "path": plugin_file,
                        "module": plugin_module,
                        "info": plugin_info,
                    })
                    logger.info("Loaded plugin: %s", plugin_file.stem)
        except Exception as e:
            logger.warning("Failed to load plugin %s: %s", plugin_file, e)
    
    return plugins




TEMPLATES = {
    "default": {
        "description": "Full-featured project with configs, tests, and documentation",
        "include_configs": True,
        "include_tests": True,
        "include_docs": True,
    },
    "minimal": {
        "description": "Bare minimum: src, README, LICENSE only",
        "include_configs": False,
        "include_tests": False,
        "include_docs": False,
    },
    "api": {
        "description": "API project with configs and tests",
        "include_configs": True,
        "include_tests": True,
        "include_docs": True,
    },
    "cli": {
        "description": "CLI tool project",
        "include_configs": True,
        "include_tests": True,
        "include_docs": True,
    },
    "library": {
        "description": "Reusable library package",
        "include_configs": False,
        "include_tests": True,
        "include_docs": True,
    },
}


# =============================================================================
# GUI Class
# =============================================================================


class FrameworkGUI:
    """
    Modern Tkinter GUI for the Internode Bare Metal Framework Generator.
    
    Features a dark gray theme with orange accents, scrollable content area,
    and all configuration options accessible in a single window.
    """
    
    def __init__(self) -> None:
        """Initialize the GUI application."""
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        
        self.tk = tk
        self.ttk = ttk
        self.filedialog = filedialog
        self.messagebox = messagebox
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"{__project__} v{__version__}")
        self.root.geometry("650x750")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(True, True)
        self.root.minsize(500, 600)
        
        # Tkinter variables
        self.project_name = tk.StringVar(value="MyProject")
        self.output_dir = tk.StringVar(value=".")
        self.author_handle = tk.StringVar(value=DEFAULT_AUTHOR_HANDLE)
        self.author_email = tk.StringVar(value=DEFAULT_AUTHOR_EMAIL)
        self.template = tk.StringVar(value="default")
        self.enable_venv = tk.BooleanVar(value=True)
        self.update_mode = tk.BooleanVar(value=False)
        self.dry_run = tk.BooleanVar(value=False)
        
        self._apply_styles()
        self._create_widgets()
    
    def _apply_styles(self) -> None:
        """Apply custom ttk styles for the dark theme."""
        style = self.ttk.Style()
        style.theme_use("clam")
        
        # Accent button (orange)
        style.configure(
            STYLE_ACCENT_BTN,
            background=THEME["accent"],
            foreground=THEME["fg"],
            borderwidth=0,
            focuscolor=THEME["accent"],
            padding=(20, 14),
            font=(FONT_FAMILY, 11, "bold"),
        )
        style.map(
            STYLE_ACCENT_BTN,
            background=[("active", THEME["accent_hover"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"])],
        )
        
        # Secondary button (gray)
        style.configure(
            STYLE_SECONDARY_BTN,
            background=THEME["bg_secondary"],
            foreground=THEME["fg"],
            borderwidth=1,
            padding=(15, 10),
            font=(FONT_FAMILY, 10),
        )
        style.map(
            STYLE_SECONDARY_BTN,
            background=[("active", THEME["border"])],
        )
        
        # Radio buttons
        style.configure(
            "TRadiobutton",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=(FONT_FAMILY, 10),
        )
        
        # Checkbuttons
        style.configure(
            "TCheckbutton",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=(FONT_FAMILY, 10),
        )
    
    def _create_widgets(self) -> None:
        """Create all GUI widgets with scrollable content."""
        tk = self.tk
        ttk = self.ttk
        
        # Create main container
        container = tk.Frame(self.root, bg=THEME["bg"])
        container.pack(fill="both", expand=True)
        
        # Header (fixed at top)
        header_frame = tk.Frame(container, bg=THEME["bg"], padx=30, pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text="🐍 Internode Framework",
            font=(FONT_FAMILY, 22, "bold"),
            bg=THEME["bg"],
            fg=THEME["accent"],
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"Bare Metal Python Generator v{__version__}",
            font=(FONT_FAMILY, 10),
            bg=THEME["bg"],
            fg=THEME["fg_secondary"],
        ).pack(pady=(2, 0))
        
        # Separator
        tk.Frame(container, height=2, bg=THEME["border"]).pack(fill="x")
        
        # Scrollable content area
        canvas = tk.Canvas(container, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0))
        scrollbar.pack(side="right", fill="y")
        
        # Content padding frame
        content = tk.Frame(scrollable_frame, bg=THEME["bg"], padx=10, pady=20)
        content.pack(fill="both", expand=True)
        
        # === Project Settings Section ===
        self._create_section_header(content, "Project Settings")
        self._create_input_field(content, "Project Name", self.project_name)
        self._create_directory_field(content, "Output Directory", self.output_dir)
        
        # === Author Section ===
        self._create_section_header(content, "Author Information")
        self._create_input_field(content, "Author Handle", self.author_handle)
        self._create_input_field(content, "Author Email", self.author_email)
        
        # === Template Selection ===
        self._create_section_header(content, "Template")
        template_frame = tk.Frame(content, bg=THEME["bg"])
        template_frame.pack(fill="x", pady=5)
        
        for key, val in TEMPLATES.items():
            desc = val["description"]
            label = f"{key.capitalize()} - {desc[:45]}{'...' if len(desc) > 45 else ''}"
            ttk.Radiobutton(
                template_frame,
                text=label,
                variable=self.template,
                value=key,
            ).pack(anchor="w", pady=2)
        
        # === Options Section ===
        self._create_section_header(content, "Options")
        
        ttk.Checkbutton(
            content,
            text="Create Virtual Environment (.venv)",
            variable=self.enable_venv,
        ).pack(anchor="w", pady=3)
        
        ttk.Checkbutton(
            content,
            text="Update Mode (add missing files only)",
            variable=self.update_mode,
        ).pack(anchor="w", pady=3)
        
        ttk.Checkbutton(
            content,
            text="Dry Run (preview only, no files created)",
            variable=self.dry_run,
        ).pack(anchor="w", pady=3)
        
        # Spacer
        tk.Frame(content, height=30, bg=THEME["bg"]).pack()
        
        # === Generate Button ===
        ttk.Button(
            content,
            text="🚀  Generate Project",
            style=STYLE_ACCENT_BTN,
            command=self._generate,
        ).pack(fill="x", pady=(10, 20))
        
        # Footer (in scrollable area)
        tk.Label(
            content,
            text="Made with Python stdlib only • No external dependencies",
            font=(FONT_FAMILY, 9),
            bg=THEME["bg"],
            fg=THEME["fg_secondary"],
        ).pack(pady=(0, 10))
    
    def _create_section_header(self, parent, text: str) -> None:
        """Create a styled section header."""
        frame = self.tk.Frame(parent, bg=THEME["bg"])
        frame.pack(fill="x", pady=(15, 8))
        
        self.tk.Label(
            frame,
            text=text,
            font=(FONT_FAMILY, 12, "bold"),
            bg=THEME["bg"],
            fg=THEME["accent"],
        ).pack(anchor="w")
        
        self.tk.Frame(frame, height=1, bg=THEME["border"]).pack(fill="x", pady=(5, 0))
    
    def _create_input_field(self, parent, label: str, variable) -> None:
        """Create a styled text input field."""
        frame = self.tk.Frame(parent, bg=THEME["bg"])
        frame.pack(fill="x", pady=6)
        
        self.tk.Label(
            frame,
            text=label,
            font=(FONT_FAMILY, 10),
            bg=THEME["bg"],
            fg=THEME["fg"],
        ).pack(anchor="w")
        
        entry = self.tk.Entry(
            frame,
            textvariable=variable,
            font=(FONT_FAMILY, 11),
            bg=THEME["bg_input"],
            fg=THEME["fg"],
            insertbackground=THEME["fg"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
        )
        entry.pack(fill="x", ipady=8, pady=4)
    
    def _create_directory_field(self, parent, label: str, variable) -> None:
        """Create a directory input with browse button."""
        frame = self.tk.Frame(parent, bg=THEME["bg"])
        frame.pack(fill="x", pady=6)
        
        self.tk.Label(
            frame,
            text=label,
            font=(FONT_FAMILY, 10),
            bg=THEME["bg"],
            fg=THEME["fg"],
        ).pack(anchor="w")
        
        input_row = self.tk.Frame(frame, bg=THEME["bg"])
        input_row.pack(fill="x", pady=4)
        
        entry = self.tk.Entry(
            input_row,
            textvariable=variable,
            font=(FONT_FAMILY, 11),
            bg=THEME["bg_input"],
            fg=THEME["fg"],
            insertbackground=THEME["fg"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        
        self.ttk.Button(
            input_row,
            text="Browse",
            style=STYLE_SECONDARY_BTN,
            command=lambda: self._browse_directory(variable),
        ).pack(side="right")
    
    def _browse_directory(self, variable) -> None:
        """Open directory browser dialog."""
        directory = self.filedialog.askdirectory()
        if directory:
            variable.set(directory)
    
    def _generate(self) -> None:
        """Generate the project based on current settings."""
        name = self.project_name.get().strip()
        
        if not name:
            self.messagebox.showerror("Error", "Project name is required!")
            return
        
        try:
            output_path = Path(self.output_dir.get()) / name
            plugins = load_plugins()
            
            generator = ProjectGenerator(
                project_name=name,
                output_dir=output_path,
                enable_venv=self.enable_venv.get(),
                author_email=self.author_email.get(),
                author_handle=self.author_handle.get(),
                template=self.template.get(),
                dry_run=self.dry_run.get(),
                update_mode=self.update_mode.get(),
                plugins=plugins,
            )
            generator.generate()
            
            if self.dry_run.get():
                self.messagebox.showinfo(
                    "Dry Run Complete",
                    f"Preview for '{name}' complete.\nCheck console for details."
                )
            else:
                self.messagebox.showinfo(
                    "Success",
                    f"Project '{name}' generated!\n\nLocation:\n{output_path.absolute()}"
                )
        except Exception as e:
            self.messagebox.showerror("Error", f"Generation failed:\n{e}")
    
    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()

def launch_gui() -> None:
    """
    Launch the GUI application.
    
    Attempts to use Tkinter first. If Tkinter is unavailable or fails,
    falls back to a web-based UI served via http.server.
    """
    try:
        import tkinter
        logger.info("Tkinter available, launching native GUI...")
        gui = FrameworkGUI()
        gui.run()
    except ImportError:
        logger.warning("Tkinter not available, falling back to web UI...")
        _launch_web_gui()
    except Exception as e:
        logger.warning("Tkinter failed (%s), falling back to web UI...", e)
        _launch_web_gui()


def _launch_web_gui() -> None:
    """Launch the web-based fallback UI."""
    print("\n" + "=" * 60)
    print("  Tkinter GUI unavailable - Starting Web UI")
    print("  Your browser will open automatically.")
    print("  Press Ctrl+C in this terminal to stop.")
    print("=" * 60 + "\n")
    
    web_gui = WebGUI()
    web_gui.run()


# =============================================================================
# Web-Based GUI (Fallback)
# =============================================================================


class WebGUI:
    """
    Web-based fallback GUI using http.server.
    
    Provides the same functionality as the Tkinter GUI but rendered
    in the user's web browser. Used when Tkinter is unavailable.
    """
    
    PORT = 8765
    HOST = "localhost"
    
    def __init__(self) -> None:
        """Initialize the web GUI."""
        self.server = None
    
    def _get_html_page(self, message: str = "", message_type: str = "") -> str:
        """Generate the HTML page with current state."""
        templates_html = ""
        for key, val in TEMPLATES.items():
            desc = val["description"]
            templates_html += f'''
                <label class="radio-option">
                    <input type="radio" name="template" value="{key}" {"checked" if key == "default" else ""}>
                    <span class="radio-label">{key.capitalize()} - {desc}</span>
                </label>
            '''
        
        message_html = ""
        if message:
            color = THEME["success"] if message_type == "success" else THEME["accent"]
            message_html = f'<div class="message" style="background: {color}20; border-left: 4px solid {color}; padding: 12px; margin-bottom: 20px;">{message}</div>'
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{__project__} v{__version__}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: "{FONT_FAMILY}", -apple-system, BlinkMacSystemFont, sans-serif;
            background: {THEME["bg"]};
            color: {THEME["fg"]};
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 650px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 20px 0 30px;
            border-bottom: 2px solid {THEME["border"]};
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 28px;
            color: {THEME["accent"]};
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            color: {THEME["fg_secondary"]};
            font-size: 14px;
        }}
        
        .section {{
            margin-bottom: 25px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            color: {THEME["accent"]};
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid {THEME["border"]};
        }}
        
        label {{
            display: block;
            font-size: 13px;
            color: {THEME["fg"]};
            margin-bottom: 6px;
        }}
        
        input[type="text"], input[type="email"] {{
            width: 100%;
            padding: 12px 14px;
            font-size: 14px;
            background: {THEME["bg_input"]};
            border: 1px solid {THEME["border"]};
            border-radius: 4px;
            color: {THEME["fg"]};
            margin-bottom: 15px;
            transition: border-color 0.2s;
        }}
        
        input[type="text"]:focus, input[type="email"]:focus {{
            outline: none;
            border-color: {THEME["accent"]};
        }}
        
        .radio-option {{
            display: block;
            padding: 8px 0;
            cursor: pointer;
        }}
        
        .radio-option input {{
            margin-right: 10px;
            accent-color: {THEME["accent"]};
        }}
        
        .radio-label {{
            font-size: 13px;
        }}
        
        .checkbox-group {{
            margin-top: 10px;
        }}
        
        .checkbox-option {{
            display: flex;
            align-items: center;
            padding: 8px 0;
            cursor: pointer;
        }}
        
        .checkbox-option input {{
            margin-right: 10px;
            accent-color: {THEME["accent"]};
            width: 16px;
            height: 16px;
        }}
        
        .btn-primary {{
            width: 100%;
            padding: 16px 24px;
            font-size: 16px;
            font-weight: bold;
            background: {THEME["accent"]};
            color: {THEME["fg"]};
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 20px;
        }}
        
        .btn-primary:hover {{
            background: {THEME["accent_hover"]};
        }}
        
        footer {{
            text-align: center;
            padding: 20px 0;
            color: {THEME["fg_secondary"]};
            font-size: 12px;
            margin-top: 30px;
        }}
        
        .message {{
            border-radius: 4px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐍 Internode Framework</h1>
            <p class="subtitle">Bare Metal Python Generator v{__version__} (Web UI)</p>
        </header>
        
        {message_html}
        
        <form method="POST" action="/">
            <div class="section">
                <div class="section-title">Project Settings</div>
                <label>Project Name</label>
                <input type="text" name="project_name" value="MyProject" required>
                
                <label>Output Directory</label>
                <input type="text" name="output_dir" value=".">
            </div>
            
            <div class="section">
                <div class="section-title">Author Information</div>
                <label>Author Handle</label>
                <input type="text" name="author_handle" value="{DEFAULT_AUTHOR_HANDLE}">
                
                <label>Author Email</label>
                <input type="email" name="author_email" value="{DEFAULT_AUTHOR_EMAIL}">
            </div>
            
            <div class="section">
                <div class="section-title">Template</div>
                {templates_html}
            </div>
            
            <div class="section">
                <div class="section-title">Options</div>
                <div class="checkbox-group">
                    <label class="checkbox-option">
                        <input type="checkbox" name="enable_venv" value="1" checked>
                        Create Virtual Environment (.venv)
                    </label>
                    <label class="checkbox-option">
                        <input type="checkbox" name="update_mode" value="1">
                        Update Mode (add missing files only)
                    </label>
                    <label class="checkbox-option">
                        <input type="checkbox" name="dry_run" value="1">
                        Dry Run (preview only, no files created)
                    </label>
                </div>
            </div>
            
            <button type="submit" class="btn-primary">🚀 Generate Project</button>
        </form>
        
        <footer>
            Made with Python stdlib only • No external dependencies<br>
            <small>Close this tab and press Ctrl+C in terminal to stop</small>
        </footer>
    </div>
</body>
</html>'''
    
    def _create_handler(self) -> type:
        """Create a request handler class with access to self."""
        import http.server
        import urllib.parse
        
        web_gui = self
        
        class RequestHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default logging
                pass
            
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", CONTENT_TYPE_HTML)
                self.end_headers()
                self.wfile.write(web_gui._get_html_page().encode("utf-8"))
            
            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                params = urllib.parse.parse_qs(body)
                
                # Extract form values
                project_name = params.get("project_name", [""])[0].strip()
                output_dir = params.get("output_dir", ["."])[0].strip() or "."
                author_handle = params.get("author_handle", [DEFAULT_AUTHOR_HANDLE])[0]
                author_email = params.get("author_email", [DEFAULT_AUTHOR_EMAIL])[0]
                template = params.get("template", ["default"])[0]
                enable_venv = "enable_venv" in params
                update_mode = "update_mode" in params
                dry_run = "dry_run" in params
                
                if not project_name:
                    html = web_gui._get_html_page("Project name is required!", "error")
                    self.send_response(200)
                    self.send_header("Content-type", CONTENT_TYPE_HTML)
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))
                    return
                
                try:
                    output_path = Path(output_dir) / project_name
                    plugins = load_plugins()
                    
                    generator = ProjectGenerator(
                        project_name=project_name,
                        output_dir=output_path,
                        enable_venv=enable_venv,
                        author_email=author_email,
                        author_handle=author_handle,
                        template=template,
                        dry_run=dry_run,
                        update_mode=update_mode,
                        plugins=plugins,
                    )
                    generator.generate()
                    
                    if dry_run:
                        msg = f"Dry run complete for '{project_name}'. Check console."
                    else:
                        msg = f"Project '{project_name}' generated at {output_path.absolute()}"
                    
                    html = web_gui._get_html_page(msg, "success")
                except Exception as e:
                    html = web_gui._get_html_page(f"Error: {e}", "error")
                
                self.send_response(200)
                self.send_header("Content-type", CONTENT_TYPE_HTML)
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
        
        return RequestHandler
    
    def run(self) -> None:
        """Start the web server and open browser."""
        import http.server
        import socketserver
        import webbrowser
        import urllib.parse
        
        socketserver.TCPServer.allow_reuse_address = True
        handler = self._create_handler()
        
        with socketserver.TCPServer((self.HOST, self.PORT), handler) as httpd:
            url = f"http://{self.HOST}:{self.PORT}"
            logger.info("Web UI running at %s", url)
            webbrowser.open(url)
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("Web UI server stopped.")
                httpd.server_close()


class ProjectGenerator:
    def __init__(
        self,
        project_name: str,
        output_dir: Path,
        enable_venv: bool = True,
        author_email: str = DEFAULT_AUTHOR_EMAIL,
        author_handle: str = DEFAULT_AUTHOR_HANDLE,
        template: str = "default",
        dry_run: bool = False,
        update_mode: bool = False,
        plugins: list = None,
    ):
        self.project_name = project_name
        self.output_dir = output_dir
        self.enable_venv = enable_venv
        self.author_email = author_email
        self.author_handle = author_handle
        self.template = TEMPLATES.get(template, TEMPLATES["default"])
        self.template_name = template
        self.dry_run = dry_run
        self.update_mode = update_mode
        self.plugins = plugins or []
        self.src_dir = self.output_dir / "src" / self.project_name.lower().replace("-", "_")
        self.tests_dir = self.output_dir / "tests"

    def generate(self) -> None:
        """Main execution method to generate the project."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would generate project: {self.project_name}")
            self._print_dry_run_preview()
            return
        
        if self.update_mode:
            logger.info(f"Updating project: {self.project_name} (adding missing files only)")
            self._validate_project_name()
            self._update_project()
            return
        
        logger.info(f"Initializing project: {self.project_name} (template: {self.template_name})")
        self._validate_project_name()
        self._create_directories()
        
        if self.template["include_configs"]:
            self._create_config_files()
        
        self._create_gitignore()
        self._create_pyproject_toml()
        self._create_manage_py()
        self._create_source_code()
        
        if self.template["include_tests"]:
            self._create_tests()
        
        if self.template["include_docs"]:
            self._create_documentation()
        else:
            self._create_readme_minimal()
        
        self._create_license()
        self._create_github_actions()
        self._create_precommit_config()
        self._create_dockerfile()
        
        # Run plugin hooks
        self._run_plugin_hooks("post_generate")
        
        if self.enable_venv:
            self._create_venv()

        self._print_next_steps()
    
    def _update_project(self) -> None:
        """Update an existing project by adding missing files only."""
        if not self.output_dir.exists():
            logger.error(f"Project directory does not exist: {self.output_dir}")
            logger.info("Use without --update to create a new project.")
            sys.exit(1)
        
        files_added = 0
        
        # Define files to check/add
        files_to_check = [
            (self.output_dir / ".gitignore", self._create_gitignore),
            (self.output_dir / "pyproject.toml", self._create_pyproject_toml),
            (self.output_dir / "manage.py", self._create_manage_py),
            (self.output_dir / "LICENSE", self._create_license),
            (self.output_dir / ".github" / "workflows" / "ci.yml", self._create_github_actions),
            (self.output_dir / ".pre-commit-config.yaml", self._create_precommit_config),
            (self.output_dir / "Dockerfile", self._create_dockerfile),
        ]
        
        for file_path, create_func in files_to_check:
            if not file_path.exists():
                logger.info(f"Adding missing file: {file_path.name}")
                create_func()
                files_added += 1
        
        if files_added == 0:
            logger.info("No missing files found. Project is up to date.")
        else:
            logger.info(f"Added {files_added} missing file(s).")
        
        self._run_plugin_hooks("post_update")
    
    def _run_plugin_hooks(self, hook_name: str) -> None:
        """Run plugin hooks by name."""
        for plugin in self.plugins:
            module = plugin.get("module", {})
            if hook_name in module and callable(module[hook_name]):
                try:
                    logger.info(f"Running plugin hook: {plugin['name']}.{hook_name}")
                    module[hook_name](self)
                except Exception as e:
                    logger.warning(f"Plugin {plugin['name']} hook {hook_name} failed: {e}")

    def _print_dry_run_preview(self) -> None:
        """Prints a preview of what would be created in dry-run mode."""
        print(f"\n[DRY-RUN] Preview for project '{self.project_name}'")
        print(f"Template: {self.template_name}")
        print(f"Output: {self.output_dir.absolute()}")
        print("\nFiles that would be created:")
        print(f"  {self.output_dir}/")
        print(f"    src/{self.project_name.lower().replace('-', '_')}/")
        print("      __init__.py")
        print("      main.py")
        print("      utils.py")
        if self.template["include_tests"]:
            print("    tests/")
            print("      __init__.py")
            print("      test_main.py")
        if self.template["include_configs"]:
            print("    configs/")
            print("      config.toml, config.yaml, config.json, config.ini")
        print("    .gitignore, pyproject.toml, manage.py, LICENSE, README.md")
        if self.template["include_docs"]:
            print("    AUDIT.md, CHANGELOG.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md")
            print("    DEPENDENCIES.md, DEVELOPER.md, SECURITY.md, SUPPORT.md")
        if self.enable_venv:
            print("    .venv/")
        print()

    def _validate_project_name(self) -> None:
        """Validates the project name for invalid characters."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', self.project_name):
            raise ValueError(
                f"Invalid project name '{self.project_name}'. "
                "Name must start with a letter and contain only letters, numbers, hyphens, or underscores."
            )

    def _create_directories(self) -> None:
        """Creates the project directory structure."""
        logger.info("Creating directories...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.src_dir.mkdir(parents=True, exist_ok=True)
        if self.template["include_tests"]:
            self.tests_dir.mkdir(parents=True, exist_ok=True)
        if self.template["include_configs"]:
            (self.output_dir / "configs").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)

    def _create_readme_minimal(self) -> None:
        """Creates a minimal README for non-doc templates."""
        content = f"""# {self.project_name}

Generated by Bare Metal Python Framework v{__version__}.

## Usage
```bash
python manage.py run
```
"""
        (self.output_dir / "README.md").write_text(content, encoding="utf-8")


    def _create_config_files(self) -> None:
        """Creates configuration files using standard libraries and secure secrets."""
        logger.info("Creating configuration files...")
        
        config_dir = self.output_dir / "configs"
        comment = "For database settings, use this configuration."
        host = "localhost"
        port = 5432
        
        # Security: Generate a random API key instead of hardcoding
        api_key = secrets.token_urlsafe(32)

        # 1. TOML
        toml_content = f"""# {comment}
[database]
host = "{host}"
port = {port}
enabled = true

[security]
# Note: In production, consider loading this from environment variables
api_key_placeholder = "See .env file"
"""
        (config_dir / "config.toml").write_text(toml_content, encoding="utf-8")

        # 2. ENV
        env_content = f"""# Secrets
DB_URL=postgres://{host}:{port}/db
# Generated securely
API_KEY={api_key}
DEBUG=True
"""
        (self.output_dir / ".env").write_text(env_content, encoding="utf-8")
        (self.output_dir / ".env.example").write_text("# Secrets\nDB_URL=...\nAPI_KEY=...\nDEBUG=False\n", encoding="utf-8")

        # 3. YAML (Manual creation)
        yaml_content = f"""# {comment}
database:
    host: {host}
    port: {port}
    enabled: true
"""
        (config_dir / "config.yaml").write_text(yaml_content, encoding="utf-8")

        # 4. JSON
        data_json: Dict[str, Any] = {
            "database": {"host": host, "port": port, "enabled": True},
            "logging": {"level": "INFO"}
        }
        (config_dir / "config.json").write_text(json.dumps(data_json, indent=4), encoding="utf-8")

        # 5. INI
        config = configparser.ConfigParser()
        config['DATABASE'] = {'host': host, 'port': str(port), 'enabled': 'true'}
        with (config_dir / "config.ini").open("w", encoding="utf-8") as f:
            f.write(f"; {comment}\n")
            config.write(f)

    def _create_gitignore(self) -> None:
        """Creates a comprehensive .gitignore file."""
        logger.info("Creating .gitignore...")
        content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environments
.env
.venv
env/
venv/
ENV/

# IDEs
.idea/
.vscode/
*.swp

# Logs
logs/
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/
"""
        (self.output_dir / ".gitignore").write_text(content.strip(), encoding="utf-8")

    def _create_pyproject_toml(self) -> None:
        """Creates a modern pyproject.toml."""
        logger.info("Creating pyproject.toml...")
        content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.project_name}"
version = "0.1.0"
description = "A bare metal Python project"
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest",
    "flake8",
    "black",
    "mypy"
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
"""
        (self.output_dir / "pyproject.toml").write_text(content, encoding="utf-8")

    def _create_manage_py(self) -> None:
        """Creates a management script (Django-style but pure Python)."""
        logger.info("Creating manage.py...")
        pkg_name = self.project_name.lower().replace("-", "_")
        content = f"""#!/usr/bin/env python3
\"\"\"Project management script with common development commands.\"\"\"
import sys
import unittest
import subprocess
import os
import shutil
import ast
from pathlib import Path

# Add src to path so we can import the package
sys.path.insert(0, str(Path("src").resolve()))

def run_tests():
    \"\"\"Run unit tests.\"\"\"
    print("Running tests...")
    loader = unittest.TestLoader()
    start_dir = 'tests'
    if not Path(start_dir).exists():
        print("No tests directory found.")
        return
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

def run_app():
    \"\"\"Run the application.\"\"\"
    print("Starting application...")
    try:
        from {pkg_name} import main
        main.main()
    except ImportError as e:
        print(f"Error starting app: {{e}}")
        sys.exit(1)

def clean():
    \"\"\"Remove build artifacts and cache files.\"\"\"
    print("Cleaning project...")
    patterns = [
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        "*.pyo",
        "*.egg-info",
        "build",
        "dist",
        ".eggs",
        "htmlcov",
        ".coverage",
    ]
    removed = 0
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed: {{path}}")
                removed += 1
            elif path.is_file():
                path.unlink()
                print(f"  Removed: {{path}}")
                removed += 1
    print(f"Cleaned {{removed}} items.")

def lint():
    \"\"\"Run basic syntax check using ast module (stdlib only).\"\"\"
    print("Running lint (syntax check)...")
    errors = 0
    for py_file in Path("src").rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            print(f"  ✓ {{py_file}}")
        except SyntaxError as e:
            print(f"  ✗ {{py_file}}: {{e}}")
            errors += 1
    
    for py_file in Path("tests").rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            print(f"  ✓ {{py_file}}")
        except SyntaxError as e:
            print(f"  ✗ {{py_file}}: {{e}}")
            errors += 1
        except FileNotFoundError:
            pass
    
    if errors:
        print(f"\\nFound {{errors}} syntax error(s).")
        sys.exit(1)
    else:
        print("\\nNo syntax errors found.")

def build():
    \"\"\"Build the package using setuptools.\"\"\"
    print("Building package...")
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("Build complete. Check dist/ directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {{e}}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'build' module not found. Install with: pip install build")
        sys.exit(1)

def show_help():
    print("Usage: python manage.py [command]")
    print("Commands:")
    print("  test    - Run unit tests")
    print("  run     - Run the application")
    print("  clean   - Remove build artifacts and cache")
    print("  lint    - Check syntax of Python files")
    print("  build   - Build the package")
    print("  help    - Show this help message")

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    commands = {{
        "test": run_tests,
        "run": run_app,
        "clean": clean,
        "lint": lint,
        "build": build,
        "help": show_help,
    }}
    
    command = sys.argv[1]
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {{command}}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        manage_py_path = self.output_dir / "manage.py"
        manage_py_path.write_text(content, encoding="utf-8")
        
        # Try to make it executable on Unix systems
        try:
            current_mode = manage_py_path.stat().st_mode
            manage_py_path.chmod(current_mode | 0o111)
        except Exception:
            pass # Ignore on non-Unix or if fails

    def _create_source_code(self) -> None:
        """Creates the source code skeleton."""
        logger.info("Creating source code...")
        
        # __init__.py
        (self.src_dir / "__init__.py").touch()
        
        # main.py
        main_content = """import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started successfully.")
    print("Hello from the Bare Metal Framework!")

if __name__ == "__main__":
    main()
"""
        (self.src_dir / "main.py").write_text(main_content, encoding="utf-8")

        # config_loader.py
        config_loader = """import json
import configparser
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"

def load_json_config() -> Dict[str, Any]:
    with (CONFIG_DIR / "config.json").open() as f:
        return json.load(f)

def load_ini_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_DIR / "config.ini")
    return config
"""
        (self.src_dir / "utils.py").write_text(config_loader, encoding="utf-8")

    def _create_tests(self) -> None:
        """Creates unit tests scaffold."""
        logger.info("Creating tests...")
        (self.tests_dir / "__init__.py").touch()
        test_content = f"""import unittest
from {self.project_name.lower().replace("-", "_")} import utils

class TestBasic(unittest.TestCase):
    def test_example(self):
        self.assertTrue(True)

    def test_config_loader_structure(self):
        config = utils.load_ini_config()
        self.assertIsInstance(config, object)

if __name__ == '__main__':
    unittest.main()
"""
        (self.tests_dir / "test_main.py").write_text(test_content, encoding="utf-8")

    def _create_documentation(self) -> None:
        """Creates the complete set of project documentation."""
        logger.info("Creating documentation...")

        # 1. README.md
        readme_content = f"""# {self.project_name}

## Description
Generated by the Bare Metal Python Framework.

## Structure
- `src/`: Source code
- `tests/`: Unit tests
- `configs/`: Configuration files
- `manage.py`: Task runner script

## Usage
See `DEVELOPER.md` for detailed instructions.
"""
        (self.output_dir / "README.md").write_text(readme_content, encoding="utf-8")

        # 2. AUDIT.md
        audit_content = f"""# Project Audit Log

## {datetime.now().strftime('%Y-%m-%d')} - Initial Generation
- Project generated by Python Framework Script.
- Structure created.
- Dependencies initialized.
"""
        (self.output_dir / "AUDIT.md").write_text(audit_content, encoding="utf-8")

        # 3. CHANGELOG.md (Keep a Changelog 1.0.0 format)
        changelog_content = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - {date}
### Added
- Initial project structure.
""".format(date=datetime.now().strftime('%Y-%m-%d'))
        (self.output_dir / "CHANGELOG.md").write_text(changelog_content, encoding="utf-8")

        # 4. CODE_OF_CONDUCT.md
        coc_content = """# Code of Conduct

## Our Pledge

We as contributors and maintainers pledge to make participation in our project and community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Our Standards

### Positive Behavior

Examples of behavior that contributes to a positive environment:

- ✅ Using welcoming and inclusive language
- ✅ Being respectful of differing viewpoints and experiences
- ✅ Gracefully accepting constructive criticism
- ✅ Focusing on what is best for the community
- ✅ Showing empathy towards other community members
- ✅ Helping newcomers learn and contribute
- ✅ Crediting others for their work and ideas

### Unacceptable Behavior

Examples of unacceptable behavior:

- ❌ Trolling, insulting/derogatory comments, and personal or political attacks
- ❌ Public or private harassment
- ❌ Publishing others' private information without explicit permission
- ❌ The use of sexualized language or imagery
- ❌ Unwelcome sexual attention or advances
- ❌ Other conduct which could reasonably be considered inappropriate in a professional setting
- ❌ Spam, promotional content, or off-topic discussions

## Our Responsibilities

Project maintainers are responsible for clarifying standards of acceptable behavior and will take appropriate and fair corrective action in response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned with this Code of Conduct, or to ban temporarily or permanently any contributor for behaviors they deem inappropriate, threatening, offensive, or harmful.

## Scope

This Code of Conduct applies within all project spaces, including:

- GitHub repository (issues, pull requests, discussions)
- Code comments and documentation
- Project-related social media
- Events or meetups representing the project

It also applies when an individual is representing the project in public spaces.

## Enforcement

### Reporting

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by:

1. **GitHub:** Report content directly via GitHub's reporting tools
2. **Email:** {self.author_email}
3. **Private message:** Contact {self.author_handle} directly

All complaints will be reviewed and investigated promptly and fairly.

### What to Include

When reporting, please include:
- Your contact information
- Names (GitHub usernames) of people involved
- Description of the incident
- Links to relevant content (issues, comments, etc.)
- Any additional context or screenshots

### Confidentiality

All reports will be handled with discretion. We will not publicly share details without the reporter's consent, except where required by law.

## Enforcement Guidelines

Project maintainers will follow these Community Impact Guidelines:

### 1. Correction

**Community Impact:** Use of inappropriate language or unprofessional behavior.

**Consequence:** A private, written warning providing clarity around the violation and why it was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact:** A violation through a single incident or series of actions.

**Consequence:** A warning with consequences for continued behavior. No interaction with the people involved for a specified period. This includes avoiding interactions in community spaces as well as external channels like social media. Violating these terms may lead to a temporary or permanent ban.

### 3. Temporary Ban

**Community Impact:** A serious violation of community standards, including sustained inappropriate behavior.

**Consequence:** A temporary ban from any interaction or public communication with the community for a specified period. No public or private interaction with the people involved is allowed during this period. Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact:** Demonstrating a pattern of violation of community standards, including sustained inappropriate behavior, harassment, or aggression.

**Consequence:** A permanent ban from any public interaction within the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 2.1, available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct enforcement ladder](https://github.com/mozilla/diversity).

## Questions

If you have questions about this Code of Conduct, please open a discussion or contact the project maintainers.

---

**Last Updated:** January 11, 2026
"""
        (self.output_dir / "CODE_OF_CONDUCT.md").write_text(coc_content, encoding="utf-8")

        # 5. CONTRIBUTING.md
        contributing_content = """# Contributing

We welcome contributions! Please fork the repository, make your changes, and submit a pull request.

## How to Contribute
1. Fork the repo.
2. Create a new branch (`git checkout -b feature/cool-feature`).
3. Commit your changes (`git commit -am 'Add cool feature'`).
4. Push to the branch (`git push origin feature/cool-feature`).
5. Create a new Pull Request.

## Testing
Please ensure all tests pass before submitting.
`python manage.py test`
"""
        (self.output_dir / "CONTRIBUTING.md").write_text(contributing_content, encoding="utf-8")

        # 6. DEPENDENCIES.md
        deps_content = """# Dependencies

## Core
- Python >= 3.8

## Dev Dependencies (Install via `pip install -e .[dev]`)
- pytest
- flake8
- black
- mypy

## Production Dependencies
(Functionality provided by standard library mostly)
"""
        (self.output_dir / "DEPENDENCIES.md").write_text(deps_content, encoding="utf-8")

        # 7. DEVELOPER.md
        dev_content = f"""# Developer Context

**Project Name:** {self.project_name}

## Objective
This project is a bare metal Python application generated to minimize external dependencies.

## Architecture
- **Entry Point:** `src/{self.project_name.lower().replace("-", "_")}/main.py`
- **Task Runner:** `manage.py` located in root.
- **Config:** `configs/` directory containing TOML, JSON, and INI options.
- **Testing:** `unittest` based in `tests/`.

## Workflow
1. **Setup:**
   - Create venv: `python -m venv .venv`
   - Activate venv.
   - Install editable: `pip install -e .`

2. **Development:**
   - Run app: `python manage.py run`
   - Run tests: `python manage.py test`

## Style Guide
- Follow pep8.
- Use type hints for all functions.
"""
        (self.output_dir / "DEVELOPER.md").write_text(dev_content, encoding="utf-8")

        # 8. SECURITY.md
        security_content = """# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities to the maintainers via email (see CODE_OF_CONDUCT.md).
"""
        (self.output_dir / "SECURITY.md").write_text(security_content, encoding="utf-8")

        # 9. SUPPORT.md
        support_content = """# Support

## Channels
- **GitHub Issues:** For bugs and feature requests.
- **Email:** {self.author_email}

## FAQ
Q: How do I run this?
A: See README.md or DEVELOPER.md.
"""
        (self.output_dir / "SUPPORT.md").write_text(support_content, encoding="utf-8")

    def _create_license(self) -> None:
        """Creates LICENSE file."""
        logger.info("Creating LICENSE...")
        year = datetime.now().year
        content = f"""MIT License

Copyright (c) {year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
"""
        (self.output_dir / "LICENSE").write_text(content, encoding="utf-8")

    def _create_github_actions(self) -> None:
        """Creates GitHub Actions CI workflow."""
        logger.info("Creating GitHub Actions workflow...")
        workflows_dir = self.output_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        ci_content = f"""name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v5
      with:
        python-version: ${{{{ matrix.python-version }}}}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Lint check
      run: python manage.py lint

    - name: Run tests
      run: python manage.py test
"""
        (workflows_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    def _create_precommit_config(self) -> None:
        """Creates pre-commit configuration file."""
        logger.info("Creating pre-commit config...")
        content = """# Pre-commit configuration
# Install: pip install pre-commit && pre-commit install

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: []
"""
        (self.output_dir / ".pre-commit-config.yaml").write_text(content, encoding="utf-8")

    def _create_dockerfile(self) -> None:
        """Creates a Dockerfile for containerized deployment."""
        logger.info("Creating Dockerfile...")
        pkg_name = self.project_name.lower().replace("-", "_")
        content = f"""# Dockerfile for {self.project_name}
# Build: docker build -t {pkg_name} .
# Run:   docker run -it {pkg_name}

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source code
COPY . .

# Run the application
CMD ["python", "manage.py", "run"]
"""
        (self.output_dir / "Dockerfile").write_text(content, encoding="utf-8")
        
        # Also create .dockerignore
        dockerignore = """# Dockerignore
.git
.gitignore
.venv
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.env
.github
"""
        (self.output_dir / ".dockerignore").write_text(dockerignore, encoding="utf-8")

    def _create_venv(self) -> None:
        """Creates a virtual environment."""
        logger.info("Creating virtual environment (this may take a moment)...")
        venv_dir = self.output_dir / ".venv"
        try:
            venv.create(venv_dir, with_pip=True)
            logger.info("Virtual environment created successfully.")
        except Exception as e:
            logger.error(f"Failed to create venv: {e}")

    def _print_next_steps(self) -> None:
        """Prints helpful next steps for the user with cross-platform instructions."""
        print("\n" + "="*60)
        print(f"Project '{self.project_name}' generated successfully!")
        print("="*60)
        print(f"Location: {self.output_dir.absolute()}\n")
        
        print("NEXT STEPS:")
        print("1.  Navigate to the project directory:")
        print(f"    cd {self.output_dir}")
        
        if self.enable_venv:
            print("\n2.  Activate the virtual environment:")
            
            # Windows PowerShell
            print("    [Windows PowerShell]:")
            print(f"    .\\{self.output_dir.name}\\.venv\\Scripts\\Activate.ps1")
            
            # Windows Command Prompt
            print("    [Windows Command Prompt]:")
            print(f"    {self.output_dir.name}\\.venv\\Scripts\\activate.bat")
            
            # Unix (Bash/Zsh)
            print("    [Unix/MacOS]:")
            print(f"    source {self.output_dir.name}/.venv/bin/activate")
            
            print("\n    (To exit the environment later, simply type: deactivate)")
        
        print("\n3.  Install the project in editable mode:")
        print("    pip install -e .")
        
        print("\n4.  Run the application:")
        print("    python manage.py run")
        
        print("\n5.  Run tests:")
        print("    python manage.py test")
        print("="*60 + "\n")

def main() -> None:
    # Load user config file first
    user_config = load_config_file()
    
    # Load plugins
    plugins = load_plugins()
    
    # Set defaults from config file if available
    default_author = user_config.get("author", DEFAULT_AUTHOR_HANDLE)
    default_email = user_config.get("email", DEFAULT_AUTHOR_EMAIL)
    default_template = user_config.get("template", "default")
    
    parser = argparse.ArgumentParser(
        description=f"Bare Metal Python Framework Generator v{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python python_framework.py --name MyApp
  python python_framework.py --name MyApp --template minimal --no-venv
  python python_framework.py --interactive
  python python_framework.py --gui
  python python_framework.py --name TestProject --dry-run
  python python_framework.py --name ExistingProject --update
"""
    )
    parser.add_argument("--name", help="Name of the project")
    parser.add_argument("--out", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--author", help="Author name/handle for generated files")
    parser.add_argument("--email", help="Author email for generated files")
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default=default_template,
        help="Project template to use"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview files without creating them")
    parser.add_argument("--update", action="store_true", help="Update existing project (add missing files only)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--gui", action="store_true", help="Launch GUI (Tkinter with web fallback)")
    parser.add_argument("--gui2", action="store_true", help="Launch web-based GUI directly")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # GUI2 mode - launch web UI directly, bypass Tkinter
    if args.gui2:
        _launch_web_gui()
        return
    
    # GUI mode - try Tkinter first, fallback to web if unavailable
    if args.gui:
        launch_gui()
        return
    
    # Interactive mode
    if args.interactive or (not args.name and not args.update):
        print(f"\n=== Bare Metal Python Framework Generator v{__version__} ===")
        print("Interactive Mode (press Enter for defaults)\n")
        
        name = input("Project name [MyProject]: ").strip() or "MyProject"
        out = input("Output directory [.]: ").strip() or "."
        author = input(f"Author handle [{default_author}]: ").strip() or default_author
        email = input(f"Author email [{default_email}]: ").strip() or default_email
        
        print("\nAvailable templates:")
        for key, val in TEMPLATES.items():
            print(f"  {key}: {val['description']}")
        template = input(f"Template [{default_template}]: ").strip() or default_template
        
        create_venv = input("Create virtual environment? [Y/n]: ").strip().lower()
        enable_venv = create_venv != 'n'
        
        dry_run = input("Dry run (preview only)? [y/N]: ").strip().lower() == 'y'
        update_mode = input("Update existing project? [y/N]: ").strip().lower() == 'y'
        print()
    else:
        name = args.name
        out = args.out
        author = args.author or default_author
        email = args.email or default_email
        template = args.template
        enable_venv = not args.no_venv
        dry_run = args.dry_run
        update_mode = args.update
    
    if not name:
        print("Error: Project name is required. Use --name or --interactive.")
        sys.exit(1)
    
    output_path = Path(out) / name
    
    generator = ProjectGenerator(
        project_name=name,
        output_dir=output_path,
        enable_venv=enable_venv,
        author_email=email,
        author_handle=author,
        template=template,
        dry_run=dry_run,
        update_mode=update_mode,
        plugins=plugins,
    )
    generator.generate()

if __name__ == "__main__":
    main()
