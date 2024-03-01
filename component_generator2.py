

class ComponentGenerator:

    class Port:

        def __init__(self, location=None, direction=None, name=None, layer=None):
            self.location = None
            self.name = None
            self.layer = None
            self.direction = None

            self.size = 1

        def set_location(self, location):
            self.location = location

        def set_name(self, name):
            self.name = name

        def set_layer(self, layer):
            self.layer = layer

        def set_size(self, size):
            self.size = size

        def get_location(self):
            return self.location

        def get_name(self):
            return self.name

        def get_layer(self):
            return self.layer
        
        def get_size(self):
            return self.size

    def __init__(self, name=None, ports={}, geometry_bounds=[]):
        self.component_name = name
        
        ## lef definitions
        self.ports = ports
        self.size = geometry_bounds


        ## scad definitions
        self.px = None
        self.layer = None

        ## SCAD LEF ##
        self.scad_lef = None

        self.ports = {}

        #self.size = [0,0]
        self.size_layer = 0

        self.pitch = None

    def write_lef(self, o_file_name):

        o_file = open(o_file_name, "w")

        o_file.write("\n")

        adj_size = [
            self.size[0] + self.pitch*2,
            self.size[1] + self.pitch*2
        ]

        o_file.write("""
        MACRO {self.component_name}
          CLASS CORE ;
          ORIGIN 0 0 ;
          FOREIGN {self.component_name} ;
          SIZE {adj_size[0]} {adj_size[1]} ;
          SYMMETRY X Y ;
          SITE CoreSite ;
        """)

        for p in self.ports:
            p_x1 = p.location[0] - p.size/2
            p_x2 = p.location[0] + p.size/2

            p_y1 = p.location[1] - p.size/2
            p_y2 = p.location[1] + p.size/2
            
            o_file.wirte("""
              PIN {p.name}
                DIRECTION {p.direction} ;
                USE SIGNAL ;
                PORT
                  LAYER {p.layer} ;
                    RECT {p_x1} {p_y1} {p_x2} {p_y2} ;
                END
              END {p.name} ;
            """)

        o_file.write("""
          OBS
        """)

        for l in self.layer:
            obs_size = [
                self.pitch,
                self.pitch,
                self.size[0] + self.pitch,
                self.size[1] + self.pitch,
            ]
            
            o_file.write("""
                LAYER {l} ;
                  RECT {obs_size[0]} {obs_size[1]} {obs_size[2]} {obs_size[3]} 
            """)



