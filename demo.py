"""
SplashScreen - A flexible Python splash screen library

Author: Smorkster
GitHub: https://github.com/Smorkster/splashscreen
License: MIT
Version: 1.3
Created: 2025-08-11
"""

import logging
import random
import time
from tkinter import Tk, N, E, W
from tkinter.ttk import Button, Label, Separator

from splashscreen import SplashScreen

logging.basicConfig( level = logging.INFO )

class NonBlockingSplashDemo:
    def __init__( self, root: Tk ):
        self.root = root
        self.current_splash = None
        self.demo_running = False


    def run_single_demo( self, placement = 'BR', standalone = False, blocking = False, block_main = False, progressbar: dict = None ):
        """ Run a single splash screen demo """

        if self.demo_running:
            logging.info( 'Demo already running, please wait...' )

            return

        self.demo_running = True
        logging.info( f'Starting splash demo at { placement } (standalone={ standalone }, blocking={ blocking })' )

        try:
            mainwindow_param = None if standalone else self.root

            # Create splash screen
            self.current_splash = SplashScreen(
                message = 'Test',
                mainwindow = mainwindow_param,
                placement = placement,
                font = 'Calibri, 25, bold',
                bg = '#00538F',
                fg = 'white',
                close_button = True,
                title = 'Testing',
                progressbar = progressbar,
                block_main = block_main
            )

            self.current_splash.show()

            if standalone and blocking:
                # For blocking standalone, we need to handle updates differently
                # since the mainloop will block
                logging.info( 'Starting blocking standalone splash screen...' )
                self._run_blocking_demo()

            elif progressbar != None and progressbar.get( 'mode', False ) == 'determinate':
                self._schedule_demo_progressbar( progress_spec = progressbar )

            else:
                # For non-blocking, schedule updates
                self._schedule_demo_updates()

        except Exception as e:
            logging.error( f'Error creating splash screen: { e }' )
            self.demo_running = False


    def _schedule_demo_updates( self ):
        """ Schedule demo updates for non-blocking mode """

        try:
            if self.current_splash and hasattr( self.current_splash, 'root' ) and self.current_splash.root:
                # Use splash's root for standalone, or main root for attached
                scheduler = self.current_splash.root if self.current_splash._is_standalone else self.root

                scheduler.after( 500, lambda: self.update_message( 'Initializing modules...' ) )
                scheduler.after( 1000, lambda: self.change_color( '#8B0000' ) )
                scheduler.after( 1500, lambda: self.update_message( 'Loading resources...' ) )
                scheduler.after( 2000, lambda: self.update_message( 'Almost ready...' ) )
                scheduler.after( 2500, self.close_splash )

            else:
                # Fallback to main root
                self.root.after( 500, lambda: self.update_message( 'Initializing modules...' ) )
                self.root.after( 1000, lambda: self.change_color( '#8B0000' ) )
                self.root.after( 1500, lambda: self.update_message( 'Loading resources...' ) )
                self.root.after( 2000, lambda: self.update_message( 'Almost ready...' ) )
                self.root.after( 2500, self.close_splash )

        except Exception as e:
            logging.error( f'Error scheduling demo updates: { e }' )
            self.demo_running = False


    def _schedule_demo_progressbar( self, progress_spec ):
        """ Demo progressbar """

        def operate( i ):
            scheduler.after( i * 1000, lambda: self.current_splash.step_progressbar( step_count = float( 1 ) ) )
            scheduler.after( i * 1000, lambda: self.update_message( f'Step { i }' ) )

        scheduler = self.current_splash.root if self.current_splash._is_standalone else self.root

        for i in range( 1, progress_spec[ 'max' ] + 1 ):
            operate( i )

        closing_time = ( progress_spec[ 'max' ] + 2 ) * 1000
        scheduler.after( closing_time, lambda: self.close_splash() )


    def _run_blocking_demo( self ):
        """ Run demo for blocking standalone mode """

        def _close_splash() -> None:
            """ Worker function to close the splash """

            self.current_splash.close( delay = 1 )
            logging.info( 'Splash screen closed, continuing...' )
            self.current_splash = None
            self.demo_running = False

        # For blocking mode, we need to run updates in a separate thread
        # or schedule them before the mainloop blocks
        if self.current_splash and self.current_splash.root:
            # Schedule updates before mainloop blocks
            self.current_splash.root.after( 500, lambda: self.update_message( 'Initializing modules...' ) )
            self.current_splash.root.after( 1000, lambda: self.change_color( '#8B0000' ) )
            self.current_splash.root.after( 1500, lambda: self.update_message( 'Loading resources...' ) )
            self.current_splash.root.after( 2000, lambda: self.update_message( 'Almost ready...' ) )
            self.current_splash.root.after( 2500, _close_splash )


    def update_message( self, message = None, append = None ):
        """ Update message """

        if not self.current_splash:
            self.demo_running = False
            return

        logging.info( f'Updating message: { message }' )
        try:
            self.current_splash.update_message( message, append )

        except Exception as e:
            logging.error( f'Error updating message: { e }' )


    def change_color( self, color ):
        """ Change background color """

        if not self.current_splash:
            self.demo_running = False

            return

        logging.info( f'Changing color to { color }' )

        try:
            self.current_splash.update_color( color )

        except Exception as e:
            logging.error( f'Error changing color: { e }' )


    def close_splash( self ):
        """ Close the splash screen """

        if self.current_splash:
            logging.info( 'Closing splash screen' )

            try:
                self.current_splash.close( delay = 1 )
                self.current_splash = None

            except Exception as e:
                logging.error( f'Error closing splash: { e }' )

            finally:
                self.demo_running = False
                logging.info( 'Demo completed' )


class MultiDemoRunner:
    def __init__( self, root: Tk ):

        self.root = root
        self.demo = NonBlockingSplashDemo( root )
        self.placements = [
            'BR', 'BC', 'BL',
            'CL', 'CR', 'C',
            'TL', 'TC', 'TR',
            { 'x': 100, 'y': 444 },
            { 'x': random.randint( 0, self.root.winfo_screenwidth() ), 'y': random.randint( 0, self.root.winfo_screenheight() ) },
            { 'x': 2000, 'y': 100 },
            { 'x': 100, 'y': 2000 },
        ]
        self.current_demo_index = 0
        self.running_sequence = False

    def run_demo_sequence( self ):
        """ Run all demos in sequence, non-blocking """

        if self.running_sequence:
            logging.info( 'Demo sequence already running' )

            return

        self.running_sequence = True
        self.current_demo_index = 0
        logging.info( 'Starting demo sequence...' )
        self._run_next_demo()


    def _run_next_demo( self ):
        """ Run the next demo in the sequence """

        if self.current_demo_index < len( self.placements ):
            placement = self.placements[ self.current_demo_index ]
            logging.info( f'Running demo { self.current_demo_index + 1 }/{ len( self.placements ) }: { placement }' )

            # Run the demo
            self.demo.run_single_demo( placement )

            # Schedule the next demo (wait 6 seconds for current demo to complete)
            self.current_demo_index += 1
            self.root.after( 6000, self._run_next_demo )

        else:
            logging.info(' All demos completed!' )
            self.running_sequence = False


def test_true_blocking():
    """ Test function to demonstrate true blocking behavior """

    logging.info( '=== TESTING TRUE BLOCKING BEHAVIOR ===' )
    logging.info( 'Creating blocking standalone splash...' )

    splash = SplashScreen(
        message = 'Blocking splash screen\nThis blocks until closed!',
        placement = 'C',
        font = 'Calibri, 16, bold',
        bg ='#FF6B35',
        fg = 'white',
        close_after = 5  # Auto-close after 5 seconds
    )

    # This line will NOT execute until the splash is closed!
    logging.info( '=== SPLASH HAS BEEN CLOSED ===' )


def main():
    root = Tk()
    root.title( 'Splash Screen Demo - Fixed' )

    # Create demo runner
    demo_runner = MultiDemoRunner( root )
    gui_row = 0

    # Add UI elements
    title_label = Label( root, text = ' Splash Screen Demo', font = ( 'Calibri', 15, 'bold' ) )
    title_label.grid( column = 0, columnspan = 2, row = gui_row, pady = 10 )
    gui_row += 1

    separator = Separator( root, orient = 'horizontal' )
    separator.grid( columnspan = 2, row = gui_row, pady = 10, sticky = ( E, W ) )
    gui_row += 1

    # Attached demos
    title_label = Label( root, text = ' Splash Screens \'attached\' to main window', font = ( 'Calibri', 12, 'bold' ) )
    title_label.grid( columnspan = 2, row = gui_row, pady = 10 )
    gui_row += 1

    # Buttons for different demo types
    single_demo_btn = Button( root,
                             text = 'Run Attached Demo (BR)',
                             command = lambda: demo_runner.demo.run_single_demo( 'BR' ) )
    single_demo_btn.grid( column = 0, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )

    random_demo_btn = Button( root,
                             text = 'Run Random Position Demo',
                             command = lambda: demo_runner.demo.run_single_demo( {
                                'x': random.randint( 10, 800 ),
                                'y': random.randint( 10, 600 )
                            } ) )
    random_demo_btn.grid( column = 1, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )
    gui_row += 1

    sequence_demo_btn = Button( root,
                               text = 'Run Sequence All Positions',
                               command = demo_runner.run_demo_sequence )
    sequence_demo_btn.grid( column = 0, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )

    main_blocking_demo_btn = Button( root,
                                    text = 'Blocking main window',
                                    command = lambda: demo_runner.demo.run_single_demo( 'CR', block_main = True ) )
    main_blocking_demo_btn.grid( column = 1, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )
    gui_row += 1

    basic_10s_progressbar_demo_btn = Button( root,
                                            text = 'Attached, 10 seconds progressbar, (BR)',
                                            command = lambda: demo_runner.demo.run_single_demo( 'BR', block_main = False, progressbar = { 'max': 10, 'mode': 'determinate' } ) )
    basic_10s_progressbar_demo_btn.grid( column = 0, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )

    basic_indet_progressbar_demo_btn = Button( root,
                                              text = 'Attached, indeterminate (BR)',
                                              command = lambda: demo_runner.demo.run_single_demo( 'BR', progressbar = { 'mode': 'indeterminate' } ) )
    basic_indet_progressbar_demo_btn.grid( column = 1, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )
    gui_row += 1

    separator = Separator( root, orient = 'horizontal' )
    separator.grid( columnspan = 2, row = gui_row, pady = 10, sticky = ( E, W ) )
    gui_row += 1

    # Standalone demos
    title_label = Label( root,
                        text = ' Splash Screens \'standalone\' from main window',
                        font = ( 'Calibri', 12, 'bold' )
                        )
    title_label.grid( columnspan = 2, row = gui_row, pady = 10 )
    gui_row += 1

    standalone_demo_btn = Button( root,
                                 text = 'Standalone Non-blocking',
                                 command = lambda: demo_runner.demo.run_single_demo( 'CR', standalone = True, blocking = False ) )
    standalone_demo_btn.grid( column = 0, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )

    standalone_blocking_demo_btn = Button( root,
                                          text = 'Standalone Blocking code',
                                          command = lambda: demo_runner.demo.run_single_demo( 'CR', standalone = True, blocking = True ) )
    standalone_blocking_demo_btn.grid( column = 1, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )
    gui_row += 1

    blocking_test_btn = Button( root, text = 'Test TRUE Blocking (standalone)',
                              command = test_true_blocking )
    blocking_test_btn.grid( column = 0, row = gui_row, padx = 5, pady = 5, sticky = ( N, W ) )
    gui_row += 1

    separator = Separator( root, orient = 'horizontal' )
    separator.grid( columnspan = 2, row = gui_row, pady = 10, sticky = ( E, W ) )
    gui_row += 1

    # Close button
    close_btn = Button( root, text = 'Close Application', command = root.destroy )
    close_btn.grid( column = 0, row = gui_row, padx = 5, pady = 10, sticky = ( N, W ) )

    logging.info( 'Application started - main window is responsive' )

    # Configure grid
    root.columnconfigure( 0, weight = 1 )
    root.columnconfigure( 1, weight = 1 )
    for i in range( 7 ):
        root.rowconfigure( i, weight = 0 )

    root.mainloop()

if __name__ == '__main__':
    main()
