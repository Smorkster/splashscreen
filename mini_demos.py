"""
SplashScreen mini demo - A minimalistic demo of SplashScreen
displaying how progressbar can be used

Author: Smorkster
GitHub: https://github.com/Smorkster/splashscreen
License: MIT
Version: 1.3
Created: 2025-08-11
"""

import time
from splashscreen import SplashScreen


def determinate( steps: int = 5 ) -> None:
    """ Demonstrate one progress step per second

    Args:
        steps (int): The number of step the progressbar should take
    """

    splash: SplashScreen = SplashScreen(
        message = 'Starting...',
        progressbar = { 'max': steps, 'mode': 'determinate' },
        close_button = True
    )

    # Show first (creates the root window)
    splash.show()

    def do_step( current_step: int ) -> None:
        """ Worker function to update progressbar

        Args:
            current_step (int): Step index to take
        """

        if current_step <= steps:
            splash.update_message( f'Step { current_step } of { steps }' )
            splash.step_progressbar( 1 )

            # Schedule next step
            if current_step < steps:
                splash.root.after( 1000, lambda: do_step( current_step + 1 ) )

            else:
                # Close after final step
                splash.root.after( 1000, splash.close )

    # Now we can schedule (root exists after show())
    splash.root.after( 2000, lambda: do_step( 1 ) )

    # Enter mainloop to keep program alive
    splash.root.mainloop()


def indeterminate():
    """ Demonstrate an indeterminate progressbar """

    splash: SplashScreen = SplashScreen( message = 'Test',
                 placement = 'CR',
                 progressbar = { 'mode': 'indeterminate' },
                 close_after = 3
                 )
    splash.show()
    splash.root.mainloop()

if __name__ == '__main__':
    indeterminate()

    time.sleep( 1 )

    #determinate( 5 )