import pytest

from ..parser import Parser, RelationGraph


def assert_relations_sets(rg, node1, node2, expected_relations):
    assert rg.get_relations(node1, node2) == set(expected_relations)


class TestParser:
    def test_no_relation(self):
        ps = Parser()
        text = "life is good"  # 'is' supposed to be relation, but leading dot is missing
        with pytest.raises(RuntimeError):
            rg = ps.parse_relations(text)

    def test_empty_relation(self):
        ps = Parser()
        text = "life . is good"  # extra space between leading dot and relation
        with pytest.raises(RuntimeError):
            rg = ps.parse_relations(text)

    @pytest.fixture()
    def get_simple_relation_graph(self):
        text = """
            # comment for A
            A 1, A 2 .is A

            # comment for B
            B 1, B 2, B 3 .is B

            # relations between A and B
            A 1 .relatedTo B 1
            A 2 .relatedTo B 2
        """
        ps = Parser()
        rg = ps.parse_relations(text)

        return rg

    def test_simple_relations(self):
        rg = self.get_simple_relation_graph()
        assert_relations_sets(rg, 'A 1', 'A', ['is'])
        assert_relations_sets(rg, 'A 2', 'A', ['is'])

        assert_relations_sets(rg, 'B 1', 'B', ['is'])
        assert_relations_sets(rg, 'B 2', 'B', ['is'])
        assert_relations_sets(rg, 'B 3', 'B', ['is'])

        assert_relations_sets(rg, 'A 1', 'B 1', ['relatedTo'])
        assert_relations_sets(rg, 'A 1', 'B 2', [])
        assert_relations_sets(rg, 'A 1', 'B 3', [])
        assert_relations_sets(rg, 'A 1', 'B', [])
        assert_relations_sets(rg, 'A 2', 'B 1', [])
        assert_relations_sets(rg, 'A 2', 'B 2', ['relatedTo'])
        assert_relations_sets(rg, 'A 2', 'B 3', [])
        assert_relations_sets(rg, 'A 2', 'B', [])

    def test_simple_nodes(self):
        rg = self.get_simple_relation_graph()
        assert set(rg.get_nodes()) == {'A', 'B', 'A 1', 'A 2', 'B 1', 'B 2', 'B 3'}