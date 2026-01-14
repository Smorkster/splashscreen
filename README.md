# tksplashscreen

A lightweight, flexible **tkinter** splash screen helper for Python apps.

* **PyPI package name:** `tksplashscreen`
* **License:** MIT
* **Python:** 3.6+

> **Lifecycle note:** Creating a `SplashScreen(...)` only configures it. Call **`show()`** to display it.



## Installation

```bash
pip install tksplashscreen
```



## Quick usage

See `demo.py` and `mini_demos.py` in the repo for full runnable examples.

```python
from splashscreen import SplashScreen

splash = SplashScreen("Loading…", close_after=3)
splash.show()
```



## What you can do

* Preset placement (`TL`, `TC`, `TR`, `CL`, `C`, `CR`, `BL`, `BC`, `BR`) or `{ "x": 100, "y": 200 }`
    * T* - Top
    * C* - Center
    * B* - Bottom
    * *L - Left
    * *C - Center
    * *R - Right
* Standalone splash (no main window) or attached to an existing `tk.Tk`
* Optional progress bar (determinate / indeterminate)
* Update text/colors while running
* Optional close button
* Optional main-window blocking (modal behavior)



## API (short reference)

### Constructor

```python
SplashScreen(
    message: str,
    close_after: float | None = None,
    placement: str | dict = "BR",
    font: str | tuple | None = None,
    bg: str = "#00538F",
    fg: str = "white",
    mainwindow: "tk.Tk" | None = None,
    close_button: bool = False,
    title: str | None = None,
    progressbar: dict | None = None,
    block_main: bool = False,
)
```

### Methods

* `show(blocking: bool = False)` - Display the splashscreen
* `update_message(text: str, append: bool = False)` - Update text in the splash screen, with or without appending
* `update_color(color: str)` - Change the background color of the splash screen
* `step_progressbar(step_count: float = 1.0)` - Step progressbar specified number of steps
* `set_progress(value: float)` - Set progressbar to specific value
* `close(delay: float = 0)` - Close the splash screen
* `is_shown() -> bool` - Check if splash screen is displayed

---

## Common pitfalls / FAQ

### Why do I get "Splash screen not shown yet. Call show() first."?

You created the object but never displayed it.

✅ Do this:

```python
splash = SplashScreen("Loading…")
splash.show()
```

### My splash appears and then immediately disappears

If your program exits right after calling `show()`, the process ends and the window closes.

* If you’re using a standalone splash in a short script, keep the process alive (see `mini_demos.py`).
* If you’re attached to a `tk.Tk()` app, make sure your app’s mainloop continues running.

### “Standalone non-blocking” closes my main window / app

Standalone means the splash is **not** the app’s main root window. If you create a `Tk()` for the splash and then quit/destroy it incorrectly, you might terminate the program.

Tips:

* Prefer attaching to your app’s `root` when you already have one.
* For standalone usage, rely on `SplashScreen(...).show(blocking=True)` if you want the splash to drive the event loop.

### Progress bar doesn’t move

For determinate mode you must advance it:

* call `step_progressbar(...)` per step, or
* call `set_progress(value)`.

### My UI freezes while the splash is visible

If you do long work on the tkinter/UI thread, everything freezes.

* Do heavy work in a worker thread/process, and only schedule UI updates back onto tkinter.
* Use the demo files for patterns (`demo.py`, `mini_demos.py`).

### The splash size/position seems off

Text size, wrapping, and progress bars affect geometry.

* Use a larger `wraplength` (or shorter text) for better sizing.
* Try a different placement, or provide explicit `{x, y}`.



## Contributing

Issues and PRs are welcome.
