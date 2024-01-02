
import regex, mmap

class ComponentGenerator:

    def __init__(self):
        
        self.component_name = None
        
        ## lef definitions
        self.ports = {}
        self.geometry_bounds = []


        ## scad definitions
        self.px = None
        self.layer = None

        ## SCAD LEF ##
        self.scad_lef = None


        ## template definitions
        self.template = {}
        #   explicit values in template
        self.template['values'] = []
        #   list strings in template
        self.template['list'] = []
        #   value strings under dictionary
        self.template['dictionaries'] = {}

        self.template['blocks'] = {}

    def convert_px_2_boundary(self, num_px, num_layers):
        pass

    def parse_lef_template(self, template_file):

        matches = self.parse_lef_template_re(template_file)
        self.parse_lef_template_grammer(matches, template_file)

    def add_to_template(self, value, list_key):
        if value.replace('%','') not in self.template[list_key]:
            self.template[list_key].append(value.replace('%',''))

    def parse_lef_template_re(self, template_file):

        # regex for template %(.*?)%
        # matches .*%PIN_#%(?=.*\n)[^}]+%PIN_#%
        # matches .*%PIN_#\[%(?=.*\n)[^}]+%PIN_#\]%
        #         .*%Pin_#\[+%\[%(?=.*\n)[^}]+%Pin_#\]+%

        module_re = r'%(.*?)%'
        module_re = bytes(module_re, 'utf-8')


        # parse template
        with open(template_file, 'r+') as f:
            data = mmap.mmap(f.fileno(), 0)
            mo = regex.finditer(module_re, data)

        if mo:
            template_values = [ x.group().decode('utf-8') for x in mo ]
            #print("found module", mo)#.decode('utf-8'))

        return template_values

    def parse_lef_template_grammer(self, values, template_file):
        exception_chars      = ['+', '=']
        exception_pass_throu = ['[+', ']+']
        important_chars      = ['.', '#', '[', ']']

        for v in values:
            if any([x in v for x in exception_chars]):
                if any([x in v for x in exception_pass_throu]):
                    pass
                else:
                    raise ValueError(v+' not a valid variable name')

            if any([x in v for x in important_chars]):
                #print(str(v)+':'+str([x in v for x in important_chars]))
                if '.' in v:
                    # check for single depth dictionaries
                    # TODO

                    # create a dictionary
                    # create value in dictionary
                    dict_name = v.split('.')[0] \
                        .replace('%','')
                    
                    if dict_name not in self.template['dictionaries']:
                        self.template['dictionaries'][dict_name] = []

                    dict_value = v.split('.')[1] \
                        .replace('%','')

                    if dict_value in self.template['dictionaries'][dict_name]:
                        # raise error
                        raise ValueError(dict_value+" exists in "+dict_name)
                    self.template['dictionaries'][dict_name].append(dict_value)

                    pass
                if '#' in v:
                    # create list in values
                    if '.' in v:
                        if '#' in v.split('.')[0]:
                            v_list_name = v.split('.')[0]+'%'
                        elif '#' in v.split('.')[1]:
                            v_list_name = v.split('.')[1]+'%'
                        else:
                            raise ValueError('Issue with # parser')

                        self.add_to_template(v_list_name, 'list')

                    else:
                        if ']' not in v:
                            v_list_name = v.split('[')[0]+'%'


                            self.add_to_template(v_list_name, 'list')
                            self.add_to_template(v_list_name, 'values')
                        #if v_list_name not in self.template['list']:
                        #    self.template['list'].append(v_list_name)
                        #if v_list_name not in self.template['values']:
                        #    self.template['values'].append(v_list_name)
                    pass
                if '[' in v:
                    # search for template block
                    # .*%PIN_#\[%(?=.*\n)[^}]+%PIN_#\]%
                    reg_pat_temp = [r'.*',
                        r'(?=.*\n)[^}]+', 
                        r''
                        ]

                    reg_pat = reg_pat_temp[0] + v.replace('[',r'\[') +\
                            reg_pat_temp[1] + v.replace('[',r'\]') +\
                            reg_pat_temp[2]
                    #print('Reg pat: '+reg_pat)
                    reg_pat = bytes(reg_pat, 'utf-8')
                    
                    with open(template_file, 'r+') as f:
                        data = mmap.mmap(f.fileno(), 0)
                        mo = regex.finditer(reg_pat, data)

                    # create value block
                    v_block_name = v \
                        .replace('[','') \
                        .replace('+','') \
                        .replace('%','')

                    self.template['blocks'][v_block_name] = \
                        [ x.group().decode('utf-8') for x in mo ]

                    
                if ']' in v: 
                    # check or matching ]
                    if v.replace(']','') in self.template['blocks']:
                        pass
                    else:
                        ValueError('No matching [ for '+v)
                    pass
                #else:
                #    raise ValueError('No missing rule for '+v)
            else:
                #create value
                self.add_to_template(v, 'values')
                #if v not in self.template['values']: 
                #    self.template['values'].append(v)
                
    
    def template_struct():
        pass

    # module\s*LEF\s*\(\s*\)\s*\{(?:[^}{]+|(?R))*+\}

    def extract_scad_lef(self, scad_file):

        module_re = r'module\s*LEF\s*\(\s*\)\s*\{(?:[^}{]+|(?R))*+\}'
        module_re = bytes(module_re, 'utf-8')


        # parse template
        with open(scad_file, 'r+') as f:
            data = mmap.mmap(f.fileno(), 0)
            mo = regex.finditer(module_re, data)

        if mo:
            lef_scad_block = [ x.group().decode('utf-8') for x in mo ][0]

        return lef_scad_block

    #\w*\s*?=(?:.*?\r?\n?)*?;      - parse into variables
    #\[\s*"[\w ]*"\s*,\s*[\w."]*\] - scad dictionary
    #\[\s*"[\w ]*"\s*,[\w." ]*\]

    def parse_scad_lef(self, lef_block, scad_transform_file=None):

        module_re = r'\w*\s*?=(?:.*?\r?\n?)*?;'
        module_re = bytes(module_re, 'utf-8')

        self.scad_lef = {}

        # parse template
        #with open(lef_block, 'r+') as f:
        #data = mmap.mmap(f.fileno(), 0)
        mo = regex.finditer(module_re, 
            bytes(lef_block, 'utf-8'))

        if mo:
            variables = [ x.group().decode('utf-8') for x in mo ]

        for v in variables:
            var_name = v.split('=')[0].lstrip().rstrip()
            var_val  = v.split('=')[1].replace(';','').replace('\n','')

            p = regex.compile(r'(\[\s*"[\w ]*"\s*),([\w." ]*\])')

            # \s*(\[\s*"[\w ]*"\s*:[\w." ]*\]|[\w"]*)
            #

            p1= regex.compile(r'.*/w(.*".*".*)')
            var_val = p.sub('\\1 : \\2', var_val).lstrip()

            if '[' in var_val:
                var_vals = var_val.split(',')
                var_dict = {}
                for vv in var_vals:
                    chars_to_remove = ['[',']','"',"'"]

                    #print(vv)
                    if ':' not in vv and '"' in vv:
                        var_dict[''] = vv \
                            .replace('[','') \
                            .replace(']','') \
                            .replace('"','') \
                            .lstrip().rstrip()
                    elif ':' in vv:
                        vv_name = vv.split(':')[0] \
                            .replace('[','') \
                            .replace(']','') \
                            .replace('"','') \
                            .lstrip().rstrip()
                        vv_val  = vv.split(':')[1] \
                            .replace('[','') \
                            .replace(']','') \
                            .replace('"','') \
                            .lstrip().rstrip()

                        var_dict[vv_name] = str(vv_val)
                var_val = var_dict

            self.scad_lef[var_name] = var_val

    def build_component_file(self, src_scad, template_file):
        
        # get block keys
        #bl = self.template['blocks'].keys()
        print('Scad build scad_lef:')
        print(self.scad_lef)

        s = self.scad_lef.keys()
        block_count = {}

        for k in self.template['blocks'].keys():
            # sum('foo' in s for s in data)
            block_count[k] = sum(k.replace('#', '') in x for x in s)
            #block_count[k] = [k.replace('#', '') in self.scad_lef.keys()].count(True)

        print(block_count)

        temp_f = open(template_file, 'r+')
        o_file = open('/'.join(src_scad.split('/')[:-1])+'/comp_out.lef', 'w' )

        block_local = {}
        block_track = {}

        def write_blocks(layer=0):

            # iterate through

            l_key = list(block_local.keys())[layer]

            print(block_local[l_key])

            for scad_bl in [s for s in self.scad_lef if l_key.replace('#','') in s]:
            #self.scad_lef
                scad_bl_dict = self.scad_lef[scad_bl]
                print(scad_bl_dict)

                # go through each block line
                for bl in block_local[l_key].split('\n')[:-1]: # \n ends all squences
                    bl += '\n'
                    mod_re = r'%[\w\[\]#.]*%'
                    mo_bl = regex.finditer(mod_re, bl)
                    # go through each key
                    for mo_bl_item in [ x.group() for x in mo_bl ]:
                        mo_bl_item_cl = mo_bl_item \
                            .replace(l_key, scad_bl) \
                            .replace('%','') \
                            .replace('[','') \
                            .replace(']','')
                        print(mo_bl_item)
                        if '.' in mo_bl_item:
                            mo_key1 = mo_bl_item_cl.split('.')[0]
                            mo_key2 = mo_bl_item_cl.split('.')[1]
                            val = scad_bl_dict[mo_key2]
                        else:
                            val = scad_bl_dict['']
                        # replace key with val
                        bl = bl.replace(mo_bl_item, val)

                    o_file.write(bl)


            # get scad_lefs with matching key

        def open_block(mo_item_ob):
            # block begin
            block_key = mo_item_ob.split('[')[0].replace('%','')
            if block_key not in block_track or \
                not block_track[block_key]: # = False
                block_track[block_key] = True
                block_local[block_key] = ''
            else:
                raise ValueError("Issue with block "+block_key)
            if '[+' in mo_item_ob:
                block_local[block_key] += l
            elif '[-' in mo_item_ob:
                block_local[block_key] += l.replace(mo_item_ob,'')
            else:
                #TODO start at identifier
                block_local[block_key] += l
        
        def close_block(mo_item_cb):
            # close block
            block_key = mo_item_cb.split(']')[0].replace('%', '')
            block_track[block_key] = False
            # add line
            if ']+' in mo_item_cb:
                block_local[block_key] += l
            elif ']-' in mo_item_cb:
                block_local[block_key] += l.replace(mo_item_cb,'')
            else:
                #TODO start at identifier
                block_local[block_key] += l
            
                if not any(block_track.values()):
                    write_blocks()
            


        

        for l in temp_f:
            print(block_track)

            if any(block_track.values()):
                for bk, bv in block_track.items():
                    if bv:
                        if ']' not in l:
                            block_local[bk] += l

                        mod_re = r'%[\w\[\]#.]*%'
                        mo = regex.finditer(mod_re, l)

                        for mo_item in [ x.group() for x in mo ]:
                            mo_i_cl = mo_item.replace('%', '')
                            if '[' in mo_item:
                                # block begin
                                open_block(mo_item)
                            if ']' in mo_item:
                                close_block(mo_item)
                continue


            if '%' in l:
                # %[\w\[\]#.]*%
                mod_re = r'%[\w\[\]#.]*%'
                mo = regex.finditer(mod_re, l)
                #if any(block_track.values()):
                #    for bk, bv in block_track.items():
                #        if bv:
                #            block_local[bk] += l
                #            for mo_item in [ x.group() for x in mo ]:
                #                mo_i_cl = mo_item.replace('%', '')
                #                if '[' in mo_item:
                #                    # block begin
                #                    open_block(mo_item)
                #                if ']' in mo_item:
                #                    close_block(mo_item)
                
                for mo_item in [ x.group() for x in mo ]:
                    mo_i_cl = mo_item.replace('%', '')
                    if '[' in mo_item:
                        open_block(mo_item)

                    if ']' in mo_item:
                        # block end
                        continue
                    if any(block_track.values()):
                        continue
                    # if not inside a block
                    else:
                        if '.' in mo_i_cl:
                            mo_key1 = mo_i_cl.split('.')[0]
                            mo_key2 = mo_i_cl.split('.')[1]
                            val = self.scad_lef[mo_key1][mo_key2]
                        else:
                            val = self.scad_lef[mo_i_cl]

                        print(mo_item+' -> '+val)
                        l = l.replace(mo_item, val)
                if not any(block_track.values()):
                    o_file.write(l)
            else:
                if not any(block_track.values()):
                    o_file.write(l)

if __name__ == "__main__":
    pass