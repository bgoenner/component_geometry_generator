

class ComponentGenerator:

    def __init__(self):
        
        self.component_name = None
        
        ## lef definitions
        self.ports = {}
        self.geometry_bounds = []


        ## scad definitions
        self.px = None
        self.layer = None

    def convert_px_2_boundary(self, num_px, num_layers):
        pass
