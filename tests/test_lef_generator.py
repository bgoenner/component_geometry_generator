

def test_load_template():

    # variables
    lef_template_file = './templates/base_mfda_component_1.lef'

    # imports
    from component_generator import ComponentGenerator 


    # test code
    test_gen = ComponentGenerator()

    print(test_gen.parse_lef_template_re(lef_template_file))


def test_parse_template():

    # variables
    lef_template_file = './templates/base_mfda_component_1.lef'

    # imports
    from component_generator import ComponentGenerator 


    # test code
    test_gen = ComponentGenerator()
    test_gen.parse_lef_template(lef_template_file)

    print(test_gen.template)

def test_extract_scad_lef():

    # variables
    mscad_file = './tests/full_geom/test_full_serpentine_50px_0.mscad'

    # imports
    from component_generator import ComponentGenerator

    test_gen  = ComponentGenerator()
    lef_block = test_gen.extract_scad_lef(mscad_file)

    print(lef_block)

def test_parse_lef_block():

    # variables
    mscad_file = './tests/full_geom/test_full_serpentine_50px_0.mscad'

    # imports
    from component_generator import ComponentGenerator

    test_gen  = ComponentGenerator()
    lef_block = test_gen.extract_scad_lef(mscad_file)
    test_gen.parse_scad_lef(lef_block)

    print(test_gen.scad_lef)

def test_build():

    # variables
    mscad_file = './tests/full_geom/test_full_serpentine_50px_0.mscad'
    lef_template_file = './templates/base_mfda_component_1.lef'

    # imports
    from component_generator import ComponentGenerator

    # load scad and lef
    test_gen  = ComponentGenerator()
    test_gen.parse_lef_template(lef_template_file)
    lef_block = test_gen.extract_scad_lef(mscad_file)
    test_gen.parse_scad_lef(lef_block)

    test_gen.build_component_file(mscad_file, lef_template_file)