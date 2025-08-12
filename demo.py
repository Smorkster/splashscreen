import time
import logging
from splashscreen import SplashScreen

logging.basicConfig( level = logging.INFO )

def main( placement = 'BR' ):
    """ Main function to demonstrate the splash screen functionality """
    close_after = 1
    change_wait = close_after / 4
    splash = SplashScreen( message = "Test",
                          placement = placement,
                          font = "Calibri, 25, bold",
                          close_after = close_after,
                           bg = "#00538F",
                           fg = "white" )
    logging.info( f"Splash screen displayed at { placement }." )

    # Simulate some loading steps
    time.sleep( change_wait )
    splash.update_message( "Initializing modules..." )
    logging.info( "Updated message: Initializing modules..." )

    time.sleep( change_wait )
    splash.update_color( "#8B0000" )  # Dark red
    splash.update_message( "\nLoading resources...", append = True )
    logging.info( "Changed color and appended message." )

    time.sleep( change_wait )
    splash.update_message( "Almost ready..." )

    time.sleep( change_wait )

    # Small delay before creating next splash screen
    time.sleep( 0.1 )

    # If close_after is not set, the splash screen is closed with:
    # splash.close( close_after_sec = 0.1 )

if __name__ == "__main__":
    """ Run the main function, iterating all possible positions """
    placements = [ 'BR', 'BC', 'BL', 'CL', 'TL', 'TC', 'TR', 'CR', 'C' ]

    for i, p in enumerate( placements ):
        logging.info( f"Starting splash { i + 1 }/{ len( placements ) }: { p }" )
        main( placement = p )
        logging.info( f"Completed splash { i + 1 }/{ len( placements ) }: { p }" )

    logging.info( "All splash screens completed!" )