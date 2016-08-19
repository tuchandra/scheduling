from .. import scheduler

from collections import namedtuple
import unittest

class TestPrefReader(unittest.TestCase):
    """ Tests for the functions to read preferences. """

    def test_employee_names(self):
        """ Test that get_all_prefs() gets the right employee names. """

        assert scheduler.get_all_prefs("tests/test_prefs") == 2

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