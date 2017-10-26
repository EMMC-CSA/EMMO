# -*- coding: utf-8 -*-
"""

"""
import os
import sys
import itertools

if sys.version_info < (3, 2):
    raise RuntimeError('emmo requires Python 3.2 or later')

import owlready2


thisdir = os.path.abspath(os.path.dirname(__file__))
owldir = os.path.abspath(os.path.join(thisdir, '..', 'owl'))
owlready2.onto_path.append(owldir)

categories = (
    #'annotation_properties',
    'classes',
    #'data_properties',
    'individuals',
    'properties',
)


def get_ontology(base_iri):
    """Returns a new Ontology from `base_iri`."""
    #if thisdir not in owlready2.onto_path:
    #    owlready2.onto_path.append(thisdir)
    if (not base_iri.endswith('/')) and (not base_iri.endswith('#')):
        base_iri = '%s#' % base_iri
    if base_iri in owlready2.default_world.ontologies:
        return owlready2.default_world.ontologies[base_iri]
    else:
        return Ontology(owlready2.default_world, base_iri)



class ThingClass(owlready2.ThingClass):
    """Extension of the owlready2.ThingClass with some additional properties
    and methods.
    """
    pass


# Inject our ThingClass into the owlready2.namespace module
owlready2.namespace.ThingClass = ThingClass



class Ontology(owlready2.Ontology):
    """A generic class extending owlready2.Ontology.

    If desireble, the methods defined here may be moved to
    owlready2.Ontology,
    """

    def get_dot_graph(self, root=None, graph=None, taxonomy=False,
                      reflexions=False, **kw):
        """Returns a pydot graph object for visualising the ontology.

        Parameters
        ----------
        root : None | string | owlready2.ThingClass
            Name or owlready2 entity of root node to plot subgraph
            below.  If None, all classes will be included in the
            subgraph.
        graph : None | pydot.Dot instance
            Pydot graph object to plot into.  If None, a new graph object
            is created using the keyword arguments.
        taxonomy : bool
            Whether to only visualise the taxonomy (i.e. only include
            is_a relations).
        reflexions : bool
            Whether to visualise reflective relations both ways.

        Keyword arguments are passed to pydot.Dot().

        Note: This method requires pydot.
        """
        import pydot

        if graph is None:
            kw.setdefault('graph_type', 'digraph')
            kw.setdefault('rankdir', 'BT')
            #kw.setdefault('fontname', 'Bitstream Vera Sans')
            kw.setdefault('fontsize', 8)
            #kw.setdefault('splines', 'ortho')
            graph = pydot.Dot(**kw)

        if root is None:
            for root in self.get_root_classes():
                self.get_dot_graph(root=root, graph=graph, taxonomy=taxonomy,
                                   reflexions=reflexions)
            return graph
        elif isinstance(root, str):
            root = self.get_by_label(root)

        label = root.label.first()
        nodes = graph.get_node(label)
        if nodes:
            node, = nodes
        else:
            node = pydot.Node(label)
            graph.add_node(node)

        for subclass in root.subclasses():
            subnode = pydot.Node(subclass.label.first())
            edge = pydot.Edge(subnode, node, label='is_a')
            graph.add_edge(edge)
            self.get_dot_graph(root=subclass, graph=graph, taxonomy=taxonomy,
                               reflexions=reflexions)

        if not taxonomy:
            pass

        return graph

    def get_root_classes(self):
        """Returns a list or root classes."""
        return [cls for cls in self.classes()
                if not cls.ancestors().difference(set([cls, owlready2.Thing]))]

    def get_by_label(self, label):
        """Returns entity by label.

        If several entities have the same label, only the one that if
        first found is returned.  A KeyError is raised if `label`
        cannot be found.
        """
        for category in categories:
            method = getattr(self, category)
            for entity in method():
                if label in entity.label:
                    return entity
        raise KeyError('No such label in ontology "%s": %s' % (
            onto.name, label))

    def get_by_label_all(self, label):
        """Like get_by_label(), but returns a list of all matching labels."""
        return [entity for entity in
                itertools.chain(*(getattr(self, c)() for c in categories))
                if label in entity.label]

    def sync_reasoner(self):
        """Update current ontology by running the HermiT reasoner."""
        with self:
            owlready2.sync_reasoner()

    def get_annotations(self, entity):
        """Returns a dict with annotations for `entity`.  Entity may be given
        either as a ThingClass object or a label."""
        if isinstance(entity, str):
            entity = self.get_by_label(entity)
        return {
            a.label.first(): [
                o.strip('"') for s, p, o in
                self.get_triples(entity.storid, a.storid, None)]
            for a in self.annotation_properties()}






if __name__ == '__main__':
    #owlready2.onto_path.append(thisdir)

    emmo = get_ontology('emmo-0.3_2017-10-26.owl')
    emmo.load()

    onto = owlready2.get_ontology('emmo-0.2_2017-10-11_fix.owl')
    onto.load()
    onto.sync_reasoner()

    graph = onto.get_dot_graph()
    graph.write_pdf('aaa.pdf')

    entity_graph = onto.get_dot_graph('entity')
    entity_graph.write_png('entity_graph.png')

    material_entity_graph = onto.get_dot_graph('material_entity')
    material_entity_graph.write_png('material_entity_graph.png')

    material_entity_graph2 = onto.get_dot_graph('material_entity', rankdir='RL')
    material_entity_graph2.write_png('material_entity_graph2.png')

    quality_graph = onto.get_dot_graph('quality')
    quality_graph.write_png('quality_graph.png')

    quality_graph2 = onto.get_dot_graph('quality', rankdir='RL')
    quality_graph2.write_png('quality_graph2.png')
