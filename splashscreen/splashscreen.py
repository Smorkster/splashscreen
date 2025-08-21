import logging
import threading
import tkinter as tk
from tkinter.ttk import Style
from typing import Dict, Optional, Tuple, Union

logging.basicConfig( level = logging.INFO )

EnumPlacement = {
    'BR': lambda w, h, sw, sh: ( sw - w - 10, sh - h - 50 ),         # Bottom Right
    'BL': lambda w, h, sw, sh: ( 10, sh - h - 50 ),                  # Bottom Left
    'TR': lambda w, h, sw, sh: ( sw - w - 10, 10 ),                  # Top Right
    'TL': lambda w, h, sw, sh: ( 10, 10 ),                           # Top Left
    'C':  lambda w, h, sw, sh: ( ( sw - w) // 2, ( sh - h ) // 2 ),  # Center
    'CL': lambda w, h, sw, sh: ( 10, ( sh - h) // 2 ),               # Center Left
    'CR': lambda w, h, sw, sh: ( sw - w - 10, (sh - h ) // 2 ),      # Center Right
    'BC': lambda w, h, sw, sh: ( ( sw - w ) // 2, sh - h - 50 ),     # Bottom Center
    'TC': lambda w, h, sw, sh: ( ( sw - w ) // 2, 10 ),              # Top Center
}

class Placement:
    """ Handles placement logic for the splash screen """
    def __init__( self, placement: Union[ str, Dict ] ):
        """ Initialize placement with either a string or a dict """
        if isinstance( placement, dict ):
            # For dictionary placement, store it directly
            self._placement = placement
            self._is_dict = True
        elif isinstance( placement, str ):
            try:
                self._placement = EnumPlacement[ placement.upper() ]
                self._is_dict = False
            except KeyError:
                logging.warning( "Invalid placement '%s'; defaulting to BR", placement )
                self._placement = EnumPlacement[ 'BR' ]
                self._is_dict = False
        else:
            logging.warning( "Unsupported placement type %s; defaulting to BR", type( placement ) )
            self._placement = EnumPlacement[ 'BR' ]
            self._is_dict = False

    def compute_geometry( self, root: tk.Tk, label: tk.Label ):
        """ Compute the geometry string for the splash screen """
        root.update_idletasks()
        label.update_idletasks()  # Ensure label has calculated its size

        # Get the actual required size of the label
        width = label.winfo_reqwidth() + 60
        height = label.winfo_reqheight() + 80

        # Ensure minimum size for readability
        min_width = 200
        min_height = 100
        width = max( width, min_width )
        height = max( height, min_height )

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()

        if self._is_dict:
            # For dictionary placement, extract x and y directly
            x = self._placement.get( 'x', 100 )  # Default to 100 if x not found
            y = self._placement.get( 'y', 100 )  # Default to 100 if y not found
        else:
            # For function placement, call the function
            x, y = self._placement( width, height, sw, sh )

        return f"{ width }x{ height }+{ x }+{ y }"

class SplashScreen:
    """ A simple splash screen class using tkinter """
    def __init__( self,
                 message: str,
                 close_after: Optional[ float ] = None,
                 placement: Optional[ str ] = "BR",
                 font: Optional[ Union[ str, Tuple ] ] = None,
                 bg: str = "#00538F",
                 fg: str = "white",
                 mainwindow: Optional[ tk.Tk ] = None,
                 close_button: Optional[ bool ] = False,
                 title: Optional[ str ] = None
                ):
        """ Initialize the splash screen

            * message (str): The message to display on the splash screen.
            * close_after (float): Time in seconds after which the splash screen will close automatically.
            * placement (str): Placement of the splash screen on the screen.
            * font (str | tuple): Font specification for the message.
            * bg (str): Background color of the splash screen.
            * fg (str): Foreground color of the message text.
            * mainwindow (tk.TK): A window to which the splashscreen belongs to
            * close_button (bool): Should a closebutton be available in upper right corner
            * title (str): A title to be displayed at top of the splashscreen
        """

        if len( message ) == 0 or message == None:
            raise ValueError( 'There must be a message defined' )
        else:
            self._message = message

        self.rootwindow = mainwindow
        self._auto_close_after = close_after
        self._bg = bg
        self._fg = fg

        self._main_window = mainwindow
        self._close_button = close_button
        self._title = title
        self._is_standalone = mainwindow is None  # Track if this is a standalone splash

        self.root = None
        self.label = None
        self._placement = Placement( placement )
        self._font = font

        if self.rootwindow:
            self.rootwindow.after( 0, self._create_window )
            self.rootwindow.update()
            self.rootwindow.update_idletasks()
            #self._create_window()
        else:
            self._create_window()

    def _close_window( self ):
        """ Close the splash screen window safely """
        if self.root:
            try:
                # Attached splash screens, just destroy the window
                if self._is_standalone:
                    self.root.quit()

                # Always destroy the splash window
                self.root.destroy()
                self.root = None

            except tk.TclError as e:
                logging.warning( f"Error closing splash screen: { e }" )

    def _create_custom_flat_button( self ):
        """Create a completely flat custom button using Canvas"""
        button_size = 24

        self.close_btn = tk.Canvas( self.root, 
                                width = button_size, 
                                height = button_size,
                                highlightthickness = 0,
                                borderwidth = 0 )

        # Draw the X symbol
        self.close_btn.create_line( 6, 6, 18, 18, fill = self._fg.get(), width = 2, tags = "x_line" )
        self.close_btn.create_line( 18, 6, 6, 18, fill = self._fg.get(), width = 2, tags = "x_line" )

        # Bind events
        self.close_btn.bind( "<Button-1>", lambda e: self.close() )
        self.close_btn.bind( "<Enter>", self._on_canvas_button_hover )
        self.close_btn.bind( "<Leave>", self._on_canvas_button_leave )

        self.close_btn.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = ( tk.N, tk.E ) )

    def _lighten_color( self, color: str, factor: float ) -> str:
        """Lighten a color by a given factor"""
        try:
            # Convert hex to RGB
            if color.startswith( '#' ):
                r = int( color[ 1:3 ], 16 )
                g = int( color[ 3:5 ], 16 )
                b = int( color[ 5:7 ], 16 )
            else:
                # Try to get RGB values from color name
                rgb = self.root.winfo_rgb( color )
                r, g, b = [ x // 256 for x in rgb ]

            # Lighten by moving towards white
            r = min( 255, int( r + ( 255 - r ) * factor ) )
            g = min( 255, int( g + ( 255 - g ) * factor ) )
            b = min( 255, int( b + ( 255 - b ) * factor ) )

            return f'#{ r:02x }{ g:02x }{ b:02x }'
        except Exception as e:
            return color  # Return original if conversion fails

    def _on_canvas_button_hover( self, event ):
        """Handle canvas button hover"""
        # Change to a slightly lighter background
        hover_color = self._lighten_color( self._bg.get(), 0.3 )
        self.close_btn.configure( bg = hover_color )
        # Make the X slightly larger/bolder
        self.close_btn.itemconfig( "x_line", width = 4 )

    def _on_canvas_button_leave( self, event ):
        """Handle canvas button leave"""
        # Return to original background
        self.close_btn.configure( bg = self._bg.get() )
        # Return X to original size
        self.close_btn.itemconfig( "x_line", width = 2 )

    def _create_window( self ):
        """ Create the splash screen window in a separate thread """
        try:
            if self.rootwindow:
                self.root = tk.Toplevel( self.rootwindow )
            else:
                self.root = tk.Tk()
            self.root.attributes( "-topmost", True )
            self.root.overrideredirect( True )
            self.root.update_idletasks()

            self._fg = self._normalize_color( self._fg, "white" )
            self._bg = self._normalize_color( self._bg, "#00538F" )
            self._bg.trace_add( 'write', self._update_background )

            self._resize_and_position()
            self.update_color( self._bg )

            if isinstance( self._font, str ):
                try:
                    temptup =  tuple( self._font.split( ',' ) )
                    if len( temptup ) < 3:
                        raise
                    font = temptup[0].strip()
                    size = int( temptup[1].strip() ) or 18
                    style = temptup[2].strip() or "normal"
                    self._font = ( font, size, style )
                except:
                    logging.warning( "Invalid font format '%s'; using default", self._font )
                    temptup = ( "Calibri", 18, "bold" )
            elif isinstance( self._font, tuple ):
                temptup = self._font

            if self._title:
                self.title = tk.Label( self.root,
                                      text = self._message,
                                      font = self._font,
                                      fg = self._fg.get(),
                                      justify = "left",
                                      anchor = "nw"
                                     )
                self.title.grid( sticky = ( tk.N, tk.W ) )

            self.label = tk.Label( self.root, text = self._message,
                                  font = self._font,
                                  fg = self._fg.get(),
                                  justify = "left",
                                  wraplength = 400,
                                  anchor = "nw" )
            self.label.grid( column = 0, columnspan = 2, row = 1, padx = 20, pady = 20, sticky = ( tk.N, tk.W ) )

            if self._close_button:
                self._create_custom_flat_button()

            self._resize_and_position()
            self.update_color( self._bg )

            if self._auto_close_after:
                # Schedule the close from the main thread safely
                def close_wrapper():
                    self.close()
                self.root.after( int( self._auto_close_after * 1000 ), close_wrapper )

            self.root.grid_columnconfigure( index = 0, weight = 1 )
            self.root.grid_columnconfigure( index = 1, weight = 0 )
            self.root.grid_rowconfigure( index = 0, weight = 0 )
            self.root.grid_rowconfigure( index = 1, weight = 1 )

            if not self.rootwindow:
                self.root.mainloop()
        except Exception as e:
            logging.exception( "Failed to create splash screen: %s", e )

    def _normalize_color( self, value: str | tuple | tk.StringVar, default: str ) -> tk.StringVar:
        """ Return a valid Tkinter color as a StringVar, or default if invalid.

            * value (str | tuple): Color value as a string or RGB tuple.
            * default (str): Default color value to return if the input is invalid.
        Returns:
            * tk.StringVar: Valid Tkinter color
        """

        if isinstance( value , tk.StringVar ):
            value = value.get()

        if isinstance( value, str ):
            if self._is_valid_color( value ):
                pass
            else:
                logging.warning( "Invalid color '%s'; using default '%s'", value, default )
                value = default
        elif isinstance( value, tuple ) and len( value ) == 3 and all( isinstance( c, int ) for c in value ):
            value = f'#{ value[ 0 ]:02x }{ value[ 1 ]:02x }{ value[ 2 ]:02x }'
        else:
            value = default
        return tk.StringVar( self.root, value )

    def _resize_and_position( self ):
        """ Resize and position the splash screen based on the current placement """
        if self.label and self.root:
            # Force the label to update its size calculation
            self.label.update_idletasks()
            self.root.update_idletasks()

            geom = self._placement.compute_geometry( self.root, self.label )
            self.root.geometry( geom )
            self.root.update_idletasks()

    def _is_valid_color( self, color: str) -> bool:
        """ Check if the given color is valid """
        try:
            self.root.winfo_rgb( color )
            return True
        except tk.TclError:
            return False

    def update_message( self, new_text: str, append: Optional[ bool ] = False ):
        """ Update the splash screen message """
        try:
            if self.root and self.rootwindow:
                self.label.update()
                self.root.update()
                self.rootwindow.after( 0, lambda: self._update_text( new_text, append ) )
            elif self.root:
                # For standalone splash screens, update directly
                self._update_text( new_text, append )
        except Exception as e:
            if self.root == None:
                raise ReferenceError( 'SplashScreen has closed' )
            else:
                raise Exception( f'Error updating text: { e }' )

    def _update_text( self, new_text: str, append: Optional[ bool ] = False ):
        """ Update the label text in the main thread """
        if self.label:
            try:
                if append:
                    current_text = self.label.cget( "text" )
                    self.label.config( text = current_text + new_text )
                else:
                    self.label.config( text = new_text )

                self.label.update()
                self.label.update_idletasks()
                self.root.update()
                self.root.update_idletasks()

                self._resize_and_position()

            except tk.TclError as e:
                logging.warning( f"Error updating text: { e }" )
            except Exception as e:
                logging.warning( f'Error updating text: { e }' )
                if self.root == None:
                    logging.warning( 'SplashScreen was closed' )

    def _update_background( self, a, b, c ):
        """ """
        self.root.config( bg = self._bg.get() )
        if self.label:
            self.label.config( bg = self._bg.get() )
        if hasattr( self, 'title' ):
            self.title.config( bg = self._bg.get() )
        if hasattr( self, 'close_btn' ):
            self.close_btn.config( bg = self._bg.get() )

    def update_color( self, new_color: str ):
        """ Update the splash screen background color """
        if self.root:
            new_color = ( self._normalize_color( value = new_color, default = self._bg.get() ) ).get()
            if self.rootwindow:
                self.rootwindow.after( 0, self._bg.set( new_color ) )
            else:
                self.root.after( 0, self._bg.set( new_color ) )

            self.root.update()
            self.root.update_idletasks()

            if self.label:
                self.label.update()
                self.label.update_idletasks()
            if hasattr( self, 'title' ):
                self.title.update()
                self.title.update_idletasks()

    def close( self, close_after_sec: float = 0 ):
        """ Close the splash screen after a specified time """
        if self.root:
            delay = int( close_after_sec * 1000 )
            self.root.after( delay, self._close_window )