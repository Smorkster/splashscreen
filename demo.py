import time
import logging
import random
from tkinter import Tk, N, S, E, W
from tkinter.ttk import Button, Label

import tk
from splashscreen import SplashScreen

logging.basicConfig( level = logging.INFO )

class NonBlockingSplashDemo:
    def __init__( self, root: Tk ):
        self.root = root
        self.current_splash = None
        self.demo_running = False

    def run_single_demo( self, placement = 'BR' ):
        """Run a single non-blocking splash screen demo"""
        if self.demo_running:
            logging.info( "Demo already running, please wait..." )
            return

        self.demo_running = True
        logging.info( f"Starting non-blocking splash demo at { placement }" )

        try:
            # Create splash screen
            self.current_splash = SplashScreen(
                message = "Test",
                mainwindow = self.root,
                placement = placement,
                font = "Calibri, 25, bold",
                bg = "#00538F",
                fg = "white",
                close_button = True,
                title = 'Testing'
            )
        except Exception as e:
            logging.error( f"Error creating splash screen: { e }" )
            self.demo_running = False

        try:
            # Schedule the demo steps using after() - this keeps everything non-blocking
            self.root.after( 1000, self.update_message( message = 'Initializing modules...' ) )
            self.root.after( 1200, self.change_color( "#8B0000" ) )
            self.root.after( 1300, self.update_message( message = 'Loading resources...' ) )
            self.root.after( 2000, self.update_message( message = 'Almost ready...' ) )
            self.root.after( 2200, self.close_splash )
        except Exception as e:
            logging.error( f'Error occured using splash screen: { e }' )
            self.demo_running = False

    def update_message( self , message = None, append = None ):
        """Update message"""
        if not self.current_splash:
            self.demo_running = False
            return

        logging.info( fr"Updating message: { message }" )
        if message == 'Loading resources...':
            self.current_splash.update_message( message, append )
        else:
            self.current_splash.update_message( message, append )

        if hasattr( self.current_splash, 'progress_bar' ):
            self.current_splash.progress_bar.update( 1 )

    def change_color( self, color ):
        """Change background color"""
        if not self.current_splash:
            self.demo_running = False
            return

        logging.info( "Changing color" )
        self.current_splash.update_color( color )  # Dark red

    def close_splash( self ):
        """Close the splash screen"""
        if self.current_splash:
            logging.info( "Closing splash screen" )
            try:
                self.current_splash.close( close_after_sec = 1 )
                self.current_splash = None
            except Exception as e:
                logging.error( f"Error closing splash: { e }" )
            finally:
                self.demo_running = False
                logging.info( "Demo completed" )

class MultiDemoRunner:
    def __init__( self, root ):
        self.root = root
        self.demo = NonBlockingSplashDemo( root )
        self.placements = [
            'BR', 'BC', 'BL',
            'CL', 'CR', 'C',
            'TL', 'TC', 'TR',
            { 'x': 100, 'y': 444 }, 
            { 'x': 200, 'y': 300 },
            { 'x': random.randint( 10, 800 ), 'y': random.randint( 10, 600 ) },
            { 'x': random.randint( 10, 800 ), 'y': random.randint( 10, 600 ) },
        ]
        self.current_demo_index = 0
        self.running_sequence = False

    def run_demo_sequence( self ):
        """Run all demos in sequence, non-blocking"""
        if self.running_sequence:
            logging.info( "Demo sequence already running" )
            return

        self.running_sequence = True
        self.current_demo_index = 0
        logging.info( "Starting demo sequence..." )
        self._run_next_demo()

    def _run_next_demo( self ):
        """Run the next demo in the sequence"""
        if self.current_demo_index < len( self.placements ):
            placement = self.placements[ self.current_demo_index ]
            logging.info( f"Running demo { self.current_demo_index + 1 }/{ len( self.placements ) }: { placement }" )

            # Run the demo
            self.demo.run_single_demo( placement )

            # Schedule the next demo (wait 6 seconds for current demo to complete)
            self.current_demo_index += 1
            self.root.after( 6000, self._run_next_demo )
        else:
            logging.info( "All demos completed!" )
            self.running_sequence = False

def main():
    root = Tk()
    root.title( "Splash Screen Demo" )
    #root.geometry( "400x350" )

    # Create demo runner
    demo_runner = MultiDemoRunner( root )

    # Add UI elements
    title_label = Label( root, text = "Splash Screen Demo", font = ( "Calibri", 14, "bold" ) )
    title_label.grid( column = 0, columnspan = 2, row = 0 )
    #title_label.pack( pady = 10 )

    # Buttons for different demo types
    single_demo_btn = Button( root, text = "Run Single Demo (BR)", 
                            command = lambda: demo_runner.demo.run_single_demo( 'BR' ) )
    single_demo_btn.grid( column = 0, row = 1, padx = 5, sticky = ( N, W ) )

    random_demo_btn = Button( root, text = "Run Random Position Demo", 
                            command = lambda: demo_runner.demo.run_single_demo( {
                                'x': random.randint( 10, 800 ), 
                                'y': random.randint( 10, 600 )
                            } ) )
    random_demo_btn.grid( column = 1, row = 1, padx = 5, sticky = ( N, W ) )

    sequence_demo_btn = Button( root, text = "Run All Demo Sequence", 
                              command = demo_runner.run_demo_sequence )
    sequence_demo_btn.grid( column = 0, row = 2, padx = 5, sticky = ( N, W ) )

    # Close button
    close_btn = Button( root, text = "Close Application", command = root.destroy )
    close_btn.grid( column = 0, row = 3, padx = 5, pady = 10,sticky = ( N, W ) )

    logging.info( "Application started - main window is responsive" )
    root.columnconfigure( index = 0, weight = 1 )
    root.columnconfigure( index = 1, weight = 1 )
    root.rowconfigure( index = 0, weight = 0 )
    root.rowconfigure( index = 1, weight = 0 )
    root.rowconfigure( index = 2, weight = 0 )
    root.rowconfigure( index = 3, weight = 0 )
    root.mainloop()

if __name__ == "__main__":
    main()
