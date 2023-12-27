
import regex


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

    def parse_lef_template(self, template_file):

        # regex for template %(.*?)%
        # matches .*%PIN_#%(?=.*\n)[^}]+%PIN_#%
        # matches .*%PIN_#\[%(?=.*\n)[^}]+%PIN_#\]%

        # parse template
        with open(template_file, 'r+') as f:
            data = mmap.mmap(f.fileno(), 0)
            mo = regex.finditer(module_re, data)

        if mo:
            newFile.write('\n'.join([ x.group().decode('utf-8') for x in mo ]))
            print("found module", mo)#.decode('utf-8'))


if __name__ == "__main__":
    pass