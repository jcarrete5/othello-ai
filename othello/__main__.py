import logging
from othello import ui

try:
    ui.loop()
finally:
    logging.shutdown()

###- Some Notes -###
# 3 kinds of players: NetworkPlayer, AIPlayer, ControlledPlayer
# Each player has their own overriden loop method that determines how their move will be set
# Remove the ai.loop method as that will not be how player moves are set
