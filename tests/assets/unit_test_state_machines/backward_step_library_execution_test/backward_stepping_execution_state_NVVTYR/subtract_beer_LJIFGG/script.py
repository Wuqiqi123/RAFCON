from __future__ import print_function

def execute(self, inputs, outputs, gvm):
    self.logger.debug("subtract beer")
    outputs['beer_value'] = inputs['beer_value'] -50
    return 0
    
    
def backward_execute(self, inputs, outputs, gvm):
    print("Backward execute ", self.name)
