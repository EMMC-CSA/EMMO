import sys
import os

# Add emmo to sys path
thisdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(1, os.path.abspath(os.path.join(thisdir, '..', '..')))
import emmo




onto = emmo.get_ontology('emmo-0.3_2017-10-26.owl')
onto.load()
onto.sync_reasoner()


entity_graph = onto.get_dot_graph('entity')
entity_graph.write_png('entity_graph.png')

material_entity_graph = onto.get_dot_graph('material_entity', rankdir='RL')
material_entity_graph.write_png('material_entity_graph.png')

quality_graph = onto.get_dot_graph('quality', rankdir='RL')
quality_graph.write_png('quality_graph.png')
