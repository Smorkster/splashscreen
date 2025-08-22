# SplashScreen

A powerful and flexible Python splash screen library built with tkinter. Create customizable splash screens for your applications with advanced positioning, threading support, and both standalone and attached modes.

## Features

- **Easy to use**: Create splash screens with just one line of code
- **Flexible positioning**: 9 predefined positions plus custom coordinates
- **Auto-close functionality**: Automatically close after a specified time
- **Customizable appearance**: Custom fonts, colors, messages, and titles
- **Thread-safe**: Non-blocking operation that doesn't freeze your main application
- **Dynamic updates**: Update message and colors while the splash screen is running
- **Standalone or attached**: Run independently or attach to existing tkinter windows
- **Blocking modes**: Support for both blocking and non-blocking operation
- **Close button**: Optional close button for user interaction
- **Main window blocking**: Option to disable main window while splash is shown
- **Smart positioning**: Automatic screen boundary detection and adjustment

## Installation

```bash
pip install tksplashscreen
```

## Quick Start

```python
from splashscreen import SplashScreen

# Simple splash screen that closes after 3 seconds
splash = SplashScreen("Loading application...", close_after=3.0)

# Your application initialization code here
import time
time.sleep(5)  # Simulate work

# Splash will automatically close after 3 seconds
```

## Basic Usage

### Creating a Splash Screen

```python
from splashscreen import SplashScreen

# Basic splash screen
splash = SplashScreen("Welcome to MyApp!")

# With auto-close
splash = SplashScreen("Loading...", close_after=5.0)

# Custom positioning
splash = SplashScreen("Please wait...", placement="C")  # Center

# Custom colors and font
splash = SplashScreen(
    message="Initializing...",
    placement="TR",              # Top Right
    font="Arial, 24, bold",      # Font specification
    bg="#2E3440",               # Background color
    fg="#ECEFF4",               # Text color
    close_button=True,          # Add close button
    title="Loading"             # Optional title
)
```

### Attached vs Standalone Mode

```python
import tkinter as tk
from splashscreen import SplashScreen

# Create main window
root = tk.Tk()

# Attached to main window (default behavior when mainwindow is provided)
splash = SplashScreen(
    "Loading...",
    mainwindow=root,
    placement="C"
)

# Standalone mode (independent window)
splash = SplashScreen(
    "Standalone splash",
    mainwindow=None,  # or simply omit this parameter
    standalone_blocking=True  # Blocks until closed
)

# Standalone non-blocking
splash = SplashScreen(
    "Non-blocking standalone",
    standalone_blocking=False
)
```

### Placement Options

The `placement` parameter accepts the following values:

| Code | Position |
|------|----------|
| `'TL'` | Top Left |
| `'TC'` | Top Center |
| `'TR'` | Top Right |
| `'CL'` | Center Left |
| `'C'`  | Center |
| `'CR'` | Center Right |
| `'BL'` | Bottom Left |
| `'BC'` | Bottom Center |
| `'BR'` | Bottom Right (default) |

### Custom Coordinates

```python
# Using dictionary for exact positioning
splash = SplashScreen(
    "Custom position",
    placement={'x': 100, 'y': 200}
)

# Dynamic positioning
import random
splash = SplashScreen(
    "Random position",
    placement={
        'x': random.randint(50, 800),
        'y': random.randint(50, 600)
    }
)
```

### Font Specification

Fonts can be specified in two ways:

```python
# As a string: "family, size, style"
font="Arial, 16, normal"
font="Times New Roman, 20, bold"
font="Courier, 14, italic"

# As a tuple
font=("Helvetica", 18, "bold")
```

### Color Specification

Colors can be specified as:

```python
# Named colors
bg="red"
fg="white"

# Hex colors
bg="#FF5733"
fg="#FFFFFF"

# RGB tuples (will be converted to hex)
bg=(255, 87, 51)    # Converts to #FF5733
```

## Advanced Usage

### Blocking Main Window

```python
# Block main window while splash is shown
splash = SplashScreen(
    "Please wait...",
    mainwindow=root,
    block_main=True  # Main window becomes unresponsive
)
```

### True Blocking Mode

```python
# This will block code execution until splash is closed
splash = SplashScreen(
    "Blocking splash - click X to continue",
    close_button=True,
    standalone_blocking=True,
    close_after=10  # Auto-close after 10 seconds
)

# This line won't execute until splash is closed
print("Splash closed - continuing execution")
```

### Dynamic Updates

```python
splash = SplashScreen("Initializing...")

# Update the message
splash.update_message("Loading modules...")

# Append to existing message
splash.update_message("\nPlease wait...", append=True)

# Change background color
splash.update_color("#4CAF50")  # Green

# Close manually
splash.close()

# Close after delay
splash.close(close_after_sec=2.0)
```

### Progress Indication with Updates

```python
import time
from splashscreen import SplashScreen

def loading_sequence():
    splash = SplashScreen(
        "Starting application...",
        placement="C",
        font="Calibri, 18, bold",
        bg="#2C3E50",
        fg="#ECF0F1"
    )
    
    steps = [
        ("Loading configuration...", "#E74C3C"),
        ("Connecting to database...", "#F39C12"), 
        ("Initializing modules...", "#3498DB"),
        ("Loading user interface...", "#27AE60"),
        ("Ready!", "#16A085")
    ]
    
    for i, (step, color) in enumerate(steps):
        splash.update_message(f"Step {i+1}/{len(steps)}: {step}")
        splash.update_color(color)
        time.sleep(1.5)  # Simulate work
    
    splash.close(close_after_sec=1.0)

loading_sequence()
```

### Multiple Sequential Splash Screens

```python
import time

def show_splash_sequence():
    positions = ['TL', 'TR', 'C', 'BL', 'BR']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for pos, color in zip(positions, colors):
        splash = SplashScreen(
            f"Position: {pos}",
            placement=pos,
            bg=color,
            fg="white",
            font="Arial, 16, bold",
            close_after=2.0
        )
        time.sleep(2.2)  # Wait for auto-close

show_splash_sequence()
```

## API Reference

### SplashScreen Class

#### Constructor

```python
SplashScreen(
    message: str,
    close_after: Optional[float] = None,
    placement: Union[str, Dict] = "BR",
    font: Optional[Union[str, Tuple]] = None,
    bg: str = "#00538F",
    fg: str = "white",
    mainwindow: Optional[tk.Tk] = None,
    close_button: bool = False,
    title: Optional[str] = None,
    standalone_blocking: bool = True,
    block_main: bool = False
)
```

**Parameters:**
- `message` (str): The text to display on the splash screen
- `close_after` (float, optional): Time in seconds before auto-closing
- `placement` (str|dict, optional): Position on screen or custom coordinates (default: "BR")
- `font` (str|tuple, optional): Font specification (default: Calibri, 18, bold)
- `bg` (str, optional): Background color (default: "#00538F")
- `fg` (str, optional): Text color (default: "white")
- `mainwindow` (tk.Tk, optional): Parent window to attach to (None for standalone)
- `close_button` (bool, optional): Show close button in top-right corner (default: False)
- `title` (str, optional): Optional title text displayed above main message
- `standalone_blocking` (bool, optional): Whether standalone splash blocks execution (default: True)
- `block_main` (bool, optional): Whether to disable main window while splash is shown (default: False)

#### Methods

##### `update_message(new_text: str, append: bool = False)`
Update the displayed message.

**Parameters:**
- `new_text` (str): New text to display
- `append` (bool): If True, append to existing text instead of replacing

**Raises:**
- `ReferenceError`: If splash screen has been closed

##### `update_color(new_color: str)`
Change the background color of the splash screen.

**Parameters:**
- `new_color` (str): New background color (hex, named color, or RGB tuple)

##### `close(close_after_sec: float = 0)`
Close the splash screen.

**Parameters:**
- `close_after_sec` (float): Delay in seconds before closing (default: immediate)

## Complete Examples

### Application Startup with Progress

```python
import tkinter as tk
import time
from splashscreen import SplashScreen

def startup_application():
    # Create main window (hidden initially)
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Show splash screen
    splash = SplashScreen(
        "MyApp is starting...",
        mainwindow=root,
        placement="C",
        font="Arial, 20, bold",
        bg="#34495E",
        fg="#ECF0F1",
        close_button=True,
        title="Application Startup"
    )
    
    # Simulate application startup
    startup_steps = [
        ("Loading configuration files...", "#E74C3C"),
        ("Initializing database connection...", "#F39C12"),
        ("Loading user interface components...", "#3498DB"),
        ("Preparing workspace...", "#9B59B6"),
        ("Starting services...", "#27AE60"),
        ("Application ready!", "#16A085")
    ]
    
    for i, (step, color) in enumerate(startup_steps):
        splash.update_message(f"{step}\n({i+1}/{len(startup_steps)} complete)")
        splash.update_color(color)
        time.sleep(1.2)  # Simulate work
    
    # Show completion and close
    splash.update_message("Startup complete! Opening application...")
    time.sleep(1)
    splash.close()
    
    # Show main window
    root.deiconify()
    root.title("MyApp")
    root.geometry("800x600")
    
    # Add some basic UI
    label = tk.Label(root, text="Application Started Successfully!", 
                    font=("Arial", 16), pady=50)
    label.pack()
    
    root.mainloop()

if __name__ == "__main__":
    startup_application()
```

### Multi-Position Demo

```python
import tkinter as tk
from splashscreen import SplashScreen
import time
import random

class SplashDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Splash Screen Demo")
        self.root.geometry("400x300")
        
        # Create demo buttons
        self.create_ui()
    
    def create_ui(self):
        tk.Label(self.root, text="Splash Screen Demo", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Demo buttons
        demos = [
            ("Basic Splash", self.basic_demo),
            ("All Positions", self.position_demo),
            ("Random Positions", self.random_demo),
            ("Blocking Demo", self.blocking_demo),
            ("Color Animation", self.color_demo)
        ]
        
        for name, command in demos:
            tk.Button(self.root, text=name, command=command, 
                     width=20, pady=5).pack(pady=2)
    
    def basic_demo(self):
        SplashScreen("Basic splash screen demo!", close_after=2.0)
    
    def position_demo(self):
        positions = ['TL', 'TC', 'TR', 'CL', 'C', 'CR', 'BL', 'BC', 'BR']
        for pos in positions:
            splash = SplashScreen(f"Position: {pos}", placement=pos, 
                                close_after=1.0)
            time.sleep(1.2)
    
    def random_demo(self):
        for i in range(5):
            x = random.randint(50, 800)
            y = random.randint(50, 500)
            SplashScreen(f"Random {i+1}: ({x}, {y})", 
                        placement={'x': x, 'y': y}, close_after=1.0)
            time.sleep(1.2)
    
    def blocking_demo(self):
        # This will block until user closes splash
        SplashScreen("Blocking splash - click X to continue",
                    close_button=True, standalone_blocking=True)
        print("Blocking splash closed!")
    
    def color_demo(self):
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        splash = SplashScreen("Color animation demo", placement='C')
        
        for i, color in enumerate(colors):
            splash.update_message(f"Color {i+1}/{len(colors)}")
            splash.update_color(color)
            time.sleep(0.8)
        
        splash.close(close_after_sec=1.0)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    demo = SplashDemo()
    demo.run()
```

## Error Handling

The library includes robust error handling:

- Invalid colors default to the specified default color
- Invalid placements default to "BR" (Bottom Right)
- Screen boundary detection prevents windows from appearing off-screen
- Automatic fallbacks for malformed font specifications
- Thread-safe operations with proper cleanup

## Threading and Thread Safety

The splash screen operates in a thread-safe manner:
- Attached splash screens use the main window's thread
- Standalone splash screens will run in their own thread
- All UI updates are properly scheduled on the main thread
- No risk of UI freezing in the parent application

## Requirements

- Python 3.6+
- tkinter (usually included with Python)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Latest Version Features
- Added support for custom coordinate positioning
- Implemented standalone blocking and non-blocking modes
- Added close button functionality with custom styling
- Enhanced thread safety and error handling
- Added main window blocking capability
- Improved smart positioning with screen boundary detection
- Added title support for splash screens
- Enhanced color handling with RGB tuple support
- Improved font specification parsing