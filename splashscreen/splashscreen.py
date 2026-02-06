"""
SplashScreen - A flexible Python splash screen library

Author: Smorkster
GitHub: https://github.com/Smorkster/splashscreen
License: MIT
Version: 2.0
"""

import logging
import tkinter as tk

from tkinter import Canvas, Event, Label, Tk, Toplevel, StringVar
from tkinter.ttk import Progressbar

logging.basicConfig( level = logging.INFO )

EnumPlacement = {
    'BR': lambda w, h, sw, sh: ( sw - w - 10, sh - h - 50 ),         # Bottom Right
    'BL': lambda w, h, sw, sh: ( 10, sh - h - 50 ),                  # Bottom Left
    'TR': lambda w, h, sw, sh: ( sw - w - 10, 10 ),                  # Top Right
    'TL': lambda w, h, sw, sh: ( 10, 10 ),                           # Top Left
    'C':  lambda w, h, sw, sh: ( ( sw - w ) // 2, ( sh - h ) // 2 ), # Center
    'CL': lambda w, h, sw, sh: ( 10, ( sh - h ) // 2 ),              # Center Left
    'CR': lambda w, h, sw, sh: ( sw - w - 10, ( sh - h ) // 2 ),     # Center Right
    'BC': lambda w, h, sw, sh: ( ( sw - w ) // 2, sh - h - 50 ),     # Bottom Center
    'TC': lambda w, h, sw, sh: ( ( sw - w ) // 2, 10 ),              # Top Center
}


class Placement:
    """ Handles placement logic for the splash screen """

    def __init__( self, placement: str | dict ) -> None:
        """ Initialize placement with either a string or a dict

        Args:
            placement (str|dict): Specifications for the new placement
        """

        if isinstance( placement, dict ):
            self._placement = placement
            self._is_dict = True

        elif isinstance( placement, str ):
            try:
                self._placement = EnumPlacement[ placement.upper() ]
                self._is_dict = False

            except KeyError:
                logging.warning( 'Invalid placement "%s"; defaulting to BR', placement )
                self._placement = EnumPlacement[ 'BR' ]
                self._is_dict = False

        else:
            logging.warning( 'Unsupported placement type %s; defaulting to BR', type( placement ) )
            self._placement = EnumPlacement[ 'BR' ]
            self._is_dict = False


    def compute_geometry( self, root: Tk | Toplevel, *, has_progressbar: bool = False, has_title: bool = False ) -> str:
        """ Compute the geometry string for the splash screen

        Args:
            root (Tk): Root window to update
            has_progressbar (bool): Is the progressbar present
            has_title (bool): Is the title present

        Returns:
            (str): Geometry formated string for current size
        """

        root.update_idletasks()

        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()

        min_width = 200
        min_height = 100

        if has_title:
            min_height = max( min_height, 120 )

        if has_progressbar:
            min_height = max( min_height, 150 )

        width = max( width, min_width )
        height = max( height, min_height )

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()

        if self._is_dict:
            x = self._placement.get( 'x', 100 )
            y = self._placement.get( 'y', 100 )

        else:
            x, y = self._placement( width, height, sw, sh )

        if ( x + width ) > sw:
            x = sw - width
            logging.warning( 'Too far right, moving inside screen' )

        if ( y + height + 40 ) > sh:
            y = sh - height - 40
            logging.warning( 'Too far down, moving inside screen' )

        return f'{ width }x{ height }+{ x }+{ y }'


class SplashScreen:
    """ A flexible splash screen that doesn't block until explicitly shown """

    def __init__( self,
                 message: str,
                 close_after: float | None = None,
                 placement: str | dict = 'BR',
                 font: str | tuple | None = None,
                 bg: str = '#00538F',
                 fg: str = 'white',
                 mainwindow: Tk | None = None,
                 close_button: bool = False,
                 title: str = '',
                 progressbar: dict | None = None,
                 block_main: bool = False
                 ):
        """ Initialize splash screen configuration (doesn't create window yet)

        Args:
            message (str): The message to display on the splash screen
            close_after (float): Time in seconds after which splash will auto-close
            placement (str|dict): Placement of splash screen ('BR', 'TL', 'C', etc. or dict with x,y)
            font (str|tuple[ str, str, str ]): Font specification (tuple or comma-separated string)
            bg (str): Background color
            fg (str): Foreground/text color
            mainwindow (Tk): Parent window (if None, creates standalone)
            close_button (bool): Whether to show close button
            title (str): Title text displayed above message
            progressbar (dict): Dict with 'max' and 'mode' keys for progress bar
            block_main (bool): Whether to disable main window while splash is shown
        """

        if not message:
            raise ValueError( 'Message cannot be empty' )

        # Store configuration
        self._message: str = message
        self._auto_close_after: float | None = close_after
        self._bg_color: str = bg
        self._fg_color: str = fg
        self._block_mainwindow: bool = block_main
        self._close_button: bool = close_button
        self._title_text: str = title
        self._progressbar_spec = progressbar
        self._placement: Placement = Placement( placement )

        if font is None:
            self._font_spec = ( 'Calibri', 12, 'normal' )

        else:
            self._font_spec: str | tuple = font

        self.rootwindow: Tk | None = mainwindow
        self._is_standalone: bool = mainwindow is None

        # Runtime state
        self.root: Tk | Toplevel | None
        self.label: Label
        self.title: Label
        self.progressbar: Progressbar
        self.close_btn: Canvas
        self._bg: StringVar
        self._fg: StringVar
        self._is_shown: bool = False
        self._auto_close_id: str
        self._owns_root: bool = False


    def show( self, blocking: bool = False ) -> 'SplashScreen':
        """ Create and show the splash screen window

        Args:
            blocking: If True and standalone, runs mainloop (blocks until closed)

        Returns:
            self for method chaining
        """

        if self._is_shown:
            logging.warning('Splash screen already shown')

            return self

        self._create_window()
        self._is_shown = True

        if blocking and self._is_standalone and self._owns_root and self.root is not None:
            self.root.mainloop()

        return self


    def _create_window( self ) -> None:
        """ Create the splash screen window """

        try:
            # Create root window
            if self.rootwindow:
                # Attached mode
                self.root = Toplevel( master = self.rootwindow )
                self._owns_root = False

            else:
                # Standalone mode
                default_root = getattr( tk, '_default_root', None )

                if default_root is not None:
                    self.root = Toplevel( master = default_root )
                    self._owns_root = False

                else:
                    self.root = Tk()
                    self._owns_root = True

            self.root.transient( None )
            self.root.attributes( '-topmost', True )
            self.root.overrideredirect( True )

            # Setup colors
            self._fg = self._normalize_color( self._fg_color, 'white' )
            self._bg = self._normalize_color( self._bg_color, '#00538F' )
            self._bg.trace_add( 'write', self._update_background )

            # Parse font
            self._font = self._parse_font( self._font_spec )

            try:
                sw = self.root.winfo_screenmmwidth()
                font_size = int( self._font[ 1 ] ) if len( self._font)  >= 2 else 12
                wrap = max( 240, min( 700, font_size * 22 ) )
                wrap = min( wrap, int( sw * 0.60 ) )

            except:
                wrap = 400

            # Create title if specified
            if self._title_text:
                self.title = Label(
                    self.root,
                    text = self._title_text,
                    font = self._font,
                    fg = self._fg.get(),
                    bg = self._bg.get(),
                    justify = 'left',
                    anchor = 'nw'
                )
                self.title.grid( column = 0,
                                columnspan = 2,
                                row = 0,
                                padx = 20,
                                pady = ( 20, 5 ),
                                sticky = 'nw'
                                )

            # Create message label
            self.label = Label(
                self.root,
                text = self._message,
                font = self._font,
                fg = self._fg.get(),
                bg = self._bg.get(),
                justify = 'left',
                wraplength = wrap,
                anchor = 'nw'
            )
            label_row = 1 if self._title_text else 0
            self.label.grid( column = 0,
                            columnspan = 2,
                            row = label_row,
                            padx = 20,
                            pady = 20,
                            sticky = 'nw'
                            )

            # Create progress bar if specified
            if self._progressbar_spec:
                self.progressbar = Progressbar(
                    master = self.root,
                    mode = self._progressbar_spec.get( 'mode', 'determinate' ),
                    maximum = self._progressbar_spec.get( 'max', 100 )
                )
                if self._progressbar_spec.get( 'mode' ) == 'indeterminate':
                    self.progressbar.start( interval = 10 )

                pb_row = 2 if self._title_text else 1
                self.progressbar.grid( column = 0,
                                      columnspan = 2,
                                      row = pb_row,
                                      padx = 20,
                                      pady = 10,
                                      sticky = 'nswe'
                                      )

            # Create close button if specified
            if self._close_button:
                self._create_custom_flat_button()

            # Configure grid
            self.root.grid_columnconfigure( index = 0, weight = 1 )
            self.root.grid_columnconfigure( index = 1, weight = 0 )

            for i in range( 3 ):
                self.root.grid_rowconfigure( index = i, weight = 1 if i > 0 else 0 )

            # Position window
            self._resize_and_position()
            self.root.config( bg = self._bg.get() )

            # Block main window if requested
            if self._block_mainwindow and self.rootwindow:
                self.root.transient( self.rootwindow )
                self.root.lift()

                try:
                    self.root.focus_force()

                except:
                    pass

                self.root.update_idletasks()
                self.root.update()

                try:
                    self.rootwindow.wm_attributes( '-disabled', True )

                except:
                    pass

                try:
                    self.root.grab_set_global()

                except:

                    try:
                        self.root.grab_set()

                    except:
                        pass

                self.root.protocol( 'WM_DELETE_WINDOW', self.close )

            # Schedule auto-close if specified
            if self._auto_close_after:
                self._auto_close_id = self.root.after(
                    int( self._auto_close_after * 1000 ),
                    self.close
                )

            # Update to ensure window is visible
            self.root.update_idletasks()

        except Exception as e:
            logging.exception( 'Failed to create splash screen: %s', e )

            raise


    def _parse_font( self, font_spec ) -> tuple[ str, int, str ]:
        """ Parse font specification into tuple format

        Args:
            font_spec (str|tuple): If string transform into tuple

        Returns:
            (tuple[ str, str, str ]): Font formated tuple, if font_spec is not
                string or tuple, return default font specification
        """

        if isinstance( font_spec, tuple ):

            return font_spec

        elif isinstance( font_spec, str ):
            try:
                parts = [ p.strip() for p in font_spec.split( ',' ) ]

                if len( parts ) >= 3:

                    return ( parts[ 0 ], int( parts[ 1 ] ), parts[ 2 ] )

                elif len( parts ) == 2:

                    return ( parts[ 0 ], int( parts[ 1 ] ), 'normal' )

                elif len( parts ) == 1:

                    return ( parts[ 0 ], 12, 'normal' )

            except ( ValueError, IndexError ):
                logging.warning( 'Invalid font format "%s"; using default', font_spec )

        return ( 'Calibri', 12, 'normal' )


    def _normalize_color( self, value: str | tuple | StringVar, default: str ) -> StringVar:
        """ Return a valid Tkinter color as a StringVar

        Args:
            value (str|tuple|StringVar): Requested font specification
            default (str): A default font specification

        Returns:
            result (StringVar): Transformed input as a StringVar
        """

        if isinstance( value, StringVar ):
            value = value.get()

        if isinstance( value, str ):
            if not self._is_valid_color( value ):
                logging.warning( 'Invalid color "%s"; using default "%s"', value, default )
                value = default

        elif isinstance( value, tuple ) and len( value ) == 3:
            if all( isinstance( c, int ) and 0 <= c <= 255 for c in value ):
                value = f'#{ value[ 0 ]:02x }{ value[ 1 ]:02x }{ value[ 2 ]:02x }'

            else:
                value = default

        else:
            value = default

        # Create a temporary root if needed for color validation
        temp_root = self.root if self.root else tk.Tk()

        if temp_root != self.root:
            temp_root.withdraw()

        result = StringVar( master = temp_root, value = value )

        if temp_root != self.root:
            temp_root.destroy()

        return result


    def _is_valid_color( self, color: str ) -> bool:
        """ Check if the given color is valid

        Args:
            color (str): Name or hex of requested color

        Returns:
            (bool): True if color is a valid specification
        """

        try:
            temp_root = self.root if self.root else tk.Tk()

            if temp_root != self.root:
                temp_root.withdraw()

            temp_root.winfo_rgb( color )

            if temp_root != self.root:
                temp_root.destroy()

            return True

        except ( tk.TclError, Exception ):

            return False


    def _resize_and_position( self ) -> None:
        """ Resize and position the splash screen """

        if self.label and self.root:
            self.label.update_idletasks()

        if self.root:
            self.root.update_idletasks()

            if self._progressbar_spec:
                self.progressbar.update_idletasks()

            geom = self._placement.compute_geometry( root = self.root, has_progressbar = ( self._progressbar_spec is not None ), has_title = bool( self._title_text ) )
            self.root.geometry( newGeometry = geom )

            self.root.update_idletasks()


    def _create_custom_flat_button( self ) -> None:
        """ Create a flat custom close button using Canvas """

        button_size = 24
        self.close_btn = Canvas(
            self.root,
            width = button_size,
            height = button_size,
            highlightthickness = 0,
            borderwidth = 0,
            bg = self._bg.get()
        )

        self.close_btn.create_line( 6, 6, 18, 18, fill = self._fg.get(), width = 2, tags = 'x_line' )
        self.close_btn.create_line( 18, 6, 6, 18, fill = self._fg.get(), width = 2, tags = 'x_line' )

        self.close_btn.bind( '<Button-1>', lambda e: self.close() )
        self.close_btn.bind( '<Enter>', self._on_canvas_button_hover )
        self.close_btn.bind( '<Leave>', self._on_canvas_button_leave )

        title_row = 0 if self._title_text else 0
        self.close_btn.grid( column = 1, row = title_row, padx = 5, pady = 5, sticky = 'ne' )


    def _lighten_color( self, color: str, factor: float ) -> str:
        """ Lighten a color by a given factor

        Args:
            color (str): Color to transform
            factor (float): Factor to transform by

        Returns:
            (str): New lighter color, or input if error
        """

        if not self.root:

            raise ValueError( 'Root has been closed' )

        try:
            if color.startswith( '#' ):
                r = int( color[ 1:3 ], 16 )
                g = int( color[ 3:5 ], 16 )
                b = int( color[ 5:7 ], 16 )

            else:
                rgb = self.root.winfo_rgb( color )
                r, g, b = [ x // 256 for x in rgb ]

            r = min( 255, int( r + ( 255 - r ) * factor ) )
            g = min( 255, int( g + ( 255 - g ) * factor ) )
            b = min( 255, int( b + ( 255 - b ) * factor ) )

            return f'#{ r:02x }{ g:02x }{ b:02x }'

        except Exception:

            return color


    def _on_canvas_button_hover( self, event: Event ) -> None:
        """ Handle canvas button hover

        Args:
            event (Event): Event triggering this handler
        """

        hover_color = self._lighten_color( self._bg.get(), 0.3 )
        self.close_btn.configure( bg = hover_color )
        self.close_btn.itemconfig( 'x_line', width = 3 )


    def _on_canvas_button_leave( self, event: Event ) -> None:
        """ Handle canvas button leave

        Args:
            event (Event): Event triggering this handler
        """

        self.close_btn.configure( bg = self._bg.get() )
        self.close_btn.itemconfig( 'x_line', width = 2 )


    def _update_background( self, *args ) -> None:
        """ Update background color for all widgets """

        if not self.root:

            raise ValueError( 'Root has been closed' )

        bg_color = self._bg.get()
        self.root.config( bg = bg_color )

        if self.label:
            self.label.config( bg = bg_color )

        if self.title:
            self.title.config( bg = bg_color )

        if self.close_btn:
            self.close_btn.config( bg = bg_color )


    def update_message( self, new_text: str, append: bool = False) -> None:
        """ Update the splash screen message

        Args:
            new_text (str): New message text
            append (bool): If True, append to existing text instead of replacing
        """

        if not self._is_shown or not self.label:
            raise RuntimeError( 'Splash screen not shown yet. Call show() first.' )


        def do_update() -> None:
            """ Worker to do the update """

            if not self.root:

                raise ValueError( 'Root has been closed' )

            try:
                if append:
                    current = self.label.cget( 'text' )
                    self.label.config( text = current + new_text )

                else:
                    self.label.config( text = new_text )

                self.label.update_idletasks()
                self.root.update_idletasks()
                self._resize_and_position()

            except tk.TclError as e:
                logging.warning( 'Error updating message: %s', e )

        if self.rootwindow:
            self.rootwindow.after( 0, do_update )

        else:
            do_update()


    def update_color( self, new_color: str ) -> None:
        """Update the splash screen background color

        Args:
            new_color (str): The color to set
        """

        if not self._is_shown:
            raise RuntimeError( 'Splash screen not shown yet. Call show() first.' )

        normalized = self._normalize_color( value = new_color, default = self._bg.get() )

        def do_update() -> None:
            """ Worker to do the update """

            if not self.root:

                raise ValueError( 'Root has been closed' )

            self._bg.set( normalized.get() )
            self.root.update_idletasks()

        if self.rootwindow:
            self.rootwindow.after( 0, do_update )

        else:
            do_update()


    def step_progressbar( self, step_count: float = 1.0 ) -> None:
        """Increment progress bar by step_count

        Args:
            step_count: Amount to increment (default 1.0)
        """

        if not self.progressbar:
            logging.warning( 'No progress bar configured' )

            return

        current = self.progressbar.cget( 'value' )
        maximum = self.progressbar.cget( 'maximum' )

        if current + step_count >= maximum:
            # Leave tiny gap to show it's not quite done
            self.progressbar.config( value = maximum - 0.001 )

        else:
            self.progressbar.step( amount = step_count )

        self.progressbar.update_idletasks()


    def set_progress( self, value: float ) -> None:
        """ Set progress bar to specific value

        Args:
            value (float): Progress value (0 to max)
        """

        if not self.progressbar:
            logging.warning( 'No progress bar configured' )

            return

        maximum = self.progressbar.cget( 'maximum' )
        value = max( 0, min( value, maximum - 0.001 ) )
        self.progressbar.config( value = value )
        self.progressbar.update_idletasks()


    def close( self, delay: float = 0 ) -> None:
        """ Close the splash screen

        Args:
            delay: Seconds to wait before closing (default 0)
        """

        if not self._is_shown or not self.root:

            return

        def do_close():
            """ Worker to close the splash window """

            if not self.root:

                raise ValueError( 'Root has been closed' )

            try:
                # Cancel auto-close if scheduled
                if hasattr( self, '_auto_close_id' ):
                    self.root.after_cancel( self._auto_close_id )
                    self._auto_close_id = ''

                # Stop indeterminate progress bar
                if self._progressbar_spec:
                    try:
                        self.progressbar.stop()

                    except:
                        pass

                # Re-enable main window if blocked
                if self._block_mainwindow and self.rootwindow:
                    try:
                        self.rootwindow.wm_attributes( '-disabled', False )
                        self.rootwindow.deiconify()

                    except:
                        pass

                # Quit mainloop if standalone
                if self._is_standalone and self._owns_root:
                    try:
                        self.root.quit()

                    except:
                        pass

                # Destroy window
                if self.root:
                    self.root.destroy()
                    self.root = None
                    self._is_shown = False

            except Exception as e:
                logging.warning( 'Error closing splash screen: %s', e )

        if delay > 0:
            self.root.after( int( delay * 1000 ), do_close )

        else:
            do_close()


    def is_shown( self ) -> bool:
        """ Check if splash screen is currently shown

        Returns:
            (bool): True if splash screen is displayed
        """

        return self._is_shown


    def __enter__( self ) -> 'SplashScreen':
        """ Enter the context manager and show the splash screen.

        Called automatically at the start of a ``with`` block.

        Returns:
            SplashScreen: The splash screen instance.
        """

        self.show()

        return self


    def __exit__( self, exc_type, exc_val, exc_tb ) -> bool:
        """ Exit the context manager and close the splash screen.

        Called automatically when leaving a ``with`` block. The splash
        screen is always closed, and any exception raised inside the block
        is propagated.

        Args:
            exc_type: Exception type, if raised.
            exc_val: Exception instance, if raised.
            exc_tb: Traceback, if raised.

        Returns:
            bool: Always ``False`` to indicate exceptions are not suppressed.
        """

        self.close()

        return False
