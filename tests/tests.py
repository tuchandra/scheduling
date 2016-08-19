from .. import scheduler

from collections import namedtuple
import unittest

class TestPrefReader(unittest.TestCase):
    """ Tests for the functions to read preferences. """

    def test_combine_lines(self):
        """ Test that combine_lines() properly combines lines. """

        lines = ['nm2("Test Employee","",2,"id");sc("40");', 
                 'tb(0,4);lorem;ipsum;',
                 'nm2("Test Another","",3,"id");sc("50");',
                 'tc(0,5,"3");'
                 ]

        Employee = namedtuple("Employee", ["name", "prefs"])
        expected_empls = [Employee('Test Employee', 'tb(0,4);lorem;ipsum;'),
                          Employee('Test Another', 'tc(0,5,"3");')]

        combined = scheduler.combine_lines(lines)
        print (combined)
        assert combined == expected_empls

    def test_combine_lines_removes_script_tags(self):
        """ Test combine_lines() removes script tags. """

        lines = ['<script>nm2("Test Employee","",2,"id");sc("40");', 
                 'tb(0,4);lorem;ipsum;',
                 '</script>',
                 'nm2("Test Another","",3,"id");sc("50");',
                 'tc(0,5,"3");'
                 ]

        Employee = namedtuple("Employee", ["name", "prefs"])
        expected_empls = [Employee('Test Employee', 'tb(0,4);lorem;ipsum;'),
                          Employee('Test Another', 'tc(0,5,"3");')]

        combined = scheduler.combine_lines(lines)
        print (combined)
        assert combined == expected_empls

    def test_get_day_prefs_simple(self):
        """ Test get_day_prefs() on the dummy set of prefs. """

        Employee = namedtuple("Employee", ["name", "prefs"])

        actual_prefs = scheduler.get_day_prefs("tests/test_prefs")
        expected = [Employee('Some Employee', 'XXXXXXXXXXXXDDDDDDDDPPPPPPCCCCCCCCCCCCCCCCXXXXXXXXXX'),
                    Employee('Test Student', 'XXXXXXCCCCCCCCCCCCCCCCCCCCXXPPPPPPPPPPPPPPPPXXXXXXXX')]


        assert actual_prefs == expected

    def test_its_fine_if_this_fails(self):
        """ Intentionally failing so I can get printed stuff. """

        assert 1
        #assert scheduler.get_day_prefs("tests/test_prefs") == 0

class TestPrefsLineConversion(unittest.TestCase):
    """ Tests for the functions that convert prefs lines to strings. """

    def test_simple_uncolored_conversion(self):
        """ Test a conversion from one tb(..) piece. """
        line = 'tb(0,4);'
        expected = 'XXXX'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_colored_conversion(self):
        """ Test a conversion for a green tc(..) piece. """
        line = 'tc(4,8,"1");'
        expected = 'PPPPPPPP'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_colored_conversion(self):
        """ Test a conversion for a pink tc(..) piece. """
        line = 'tc(4,6,"2");'
        expected = 'DDDDDD'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_colored_conversion(self):
        """ Test a conversion for a red tc(..) piece. """
        line = 'tc(4,4,"3");'
        expected = 'CCCC'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_double_conversion(self):
        """ Test a conversion with two pieces. """
        line = 'tc(2,4,"1");tb(0,8);'
        expected = 'PPPPXXXXXXXX'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_multiple_conversion(self):
        """ Test a conversion with multiple pieces. """
        line = 'tb(0,4);tc(0,14,"3");tc(2,2,"1");tc(0,26,"3");tb(2,6);etr();'
        expected = 'XXXXCCCCCCCCCCCCCCPPCCCCCCCCCCCCCCCCCCCCCCCCCCXXXXXX'

        assert scheduler.prefs_line_to_string(line) == expected
