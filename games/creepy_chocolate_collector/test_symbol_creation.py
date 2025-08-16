"""Test symbol creation directly"""

import sys
import os

# Add the paths we need
sys.path.append('.')
sys.path.append('..')

# Create a minimal symbol to test assignment
class MockConfig:
    def __init__(self):
        self.special_symbols = {
            "wild": ["W", "CW"],
            "scatter": ["JAR"], 
            "cash": ["CC"],
            "multiplier": ["CW"]
        }
        self.collector_multipliers = [1, 2, 3, 10]
        self.padding_symbol_values = {
            "CC": {"cash_value": {
                2: 50, 5: 30, 10: 15, 15: 8, 20: 5, 25: 3, 50: 2, 2000: 1
            }}
        }

class MockSymbol:
    def __init__(self, name):
        self.name = name
        
        # Simulate what Symbol.__init__ does
        config = MockConfig()
        for special_property in config.special_symbols.keys():
            if name in config.special_symbols[special_property]:
                setattr(self, special_property, True)
    
    def assign_attribute(self, attr_dict):
        for key, value in attr_dict.items():
            setattr(self, key, value)

# Test the assignment functions
def test_assignment():
    # Create mock gamestate
    class MockGameState:
        def __init__(self):
            self.current_multiplier_index = 0
            self.config = MockConfig()
        
        def assign_collector_properties(self, symbol):
            current_multiplier = self.config.collector_multipliers[self.current_multiplier_index]
            symbol.assign_attribute({
                "multiplier": current_multiplier,
                "collector": True
            })
    
    gamestate = MockGameState()
    
    # Test CW symbol
    print("Testing CW symbol:")
    cw_symbol = MockSymbol("CW")
    print(f"  Before assignment: {vars(cw_symbol)}")
    
    gamestate.assign_collector_properties(cw_symbol)
    print(f"  After assignment: {vars(cw_symbol)}")
    
    # Test CC symbol  
    print("\nTesting CC symbol:")
    cc_symbol = MockSymbol("CC")
    print(f"  Before assignment: {vars(cc_symbol)}")
    
    # Simulate CC assignment
    cc_symbol.assign_attribute({"cash_value": 25})
    print(f"  After assignment: {vars(cc_symbol)}")

if __name__ == "__main__":
    test_assignment()