BOARD_MULT_INFO = "boardMultiplierInfo"
MULTIPLIER_LANDED = "multiplierLanded"


def send_multiplier_landed_event(gamestate):
    """Emit event when multiplier symbols land on the board during free spins."""
    if gamestate.gametype != gamestate.config.freegame_type:
        return  # Only emit in free spins

    multipliers = []
    total_mult_sum = 0

    # Check all positions on the board for M symbols
    for reel_idx, reel in enumerate(gamestate.board):
        for row_idx, symbol in enumerate(reel):
            if hasattr(symbol, 'name') and symbol.name == 'M':
                mult_value = getattr(symbol, 'multiplier', 0)
                if mult_value > 0:
                    # Add padding offset if needed
                    row_pos = row_idx + 1 if gamestate.config.include_padding else row_idx
                    multipliers.append({
                        "reel": reel_idx,
                        "row": row_pos,
                        "value": float(mult_value)
                    })
                    total_mult_sum += mult_value

    # Only emit event if multipliers were found
    if multipliers:
        event = {
            "index": len(gamestate.book.events),
            "type": MULTIPLIER_LANDED,
            "multipliers": multipliers,
            "totalMultipliers": len(multipliers),
            "boardMultiplierSum": float(total_mult_sum)
        }
        gamestate.book.add_event(event)


def send_mult_info_event(gamestate, board_mult: int, mult_info: dict, base_win: float, updatedWin: float):
    multiplier_info, winInfo = {}, {}
    multiplier_info["positions"] = []
    if gamestate.config.include_padding:
        for m in range(len(mult_info)):
            multiplier_info["positions"].append(
                {"reel": mult_info[m]["reel"], "row": mult_info[m]["row"] + 1, "multiplier": mult_info[m]["value"]}
            )
    else:
        for m in range(mult_info):
            multiplier_info["positions"].append(
                {"reel": mult_info[m]["reel"], "row": mult_info[m]["row"], "multiplier": mult_info[m]["value"]}
            )

    winInfo["tumbleWin"] = int(round(min(base_win, gamestate.config.wincap) * 100))
    winInfo["boardMult"] = board_mult
    winInfo["totalWin"] = int(round(min(updatedWin, gamestate.config.wincap) * 100))

    assert round(updatedWin, 1) == round(base_win * board_mult, 1)
    event = {
        "index": len(gamestate.book.events),
        "type": BOARD_MULT_INFO,
        "multInfo": multiplier_info,
        "winInfo": winInfo,
    }
    gamestate.book.add_event(event)
