from .. import scheduler

from collections import namedtuple
from io import StringIO
import unittest
from unittest.mock import patch

class TestPrefReader(unittest.TestCase):
    """ Tests for the functions to read preferences. """

    def test_combine_lines(self):
        """ Test combine_lines() properly combines lines. """

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
        expected = [Employee('Some Employee', 'XXXXXXXXXXXXDDDDDDDDPPPPPPCCCCCCCCCCCCCCCCXXXXXX'),
                    Employee('Test Student', 'XXXXXXCCCCCCCCCCCCCCCCXXPPPPPPPPPPPPPPPPXXXXXXXX')]


        assert actual_prefs == expected


class TestPrefsLineConversion(unittest.TestCase):
    """ Tests for the functions that convert prefs lines to strings. """

    def test_simple_uncolored_conversion(self):
        """ Test a conversion from one tb(..) piece. """
        line = 'tb(0,4);'
        expected = 'XXXX'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_green_conversion(self):
        """ Test a conversion for a green tc(..) piece. """
        line = 'tc(4,8,"1");'
        expected = 'PPPPPPPP'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_pink_conversion(self):
        """ Test a conversion for a pink tc(..) piece. """
        line = 'tc(4,6,"2");'
        expected = 'DDDDDD'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_simple_red_conversion(self):
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


class TestConvertTime(unittest.TestCase):
    """ Tests for time conversion. """

    def test_one(self):
        """ Test time conversion #1. """
        assert scheduler.convert_time(8.00) == "8:00"

    def test_two(self):
        """ Test time conversion #2. """
        assert scheduler.convert_time(8.50) == "8:30"

    def test_three(self):
        """ Test time conversion #3. """
        assert scheduler.convert_time(12.50) == "12:30"

    def test_four(self):
        """ Test time conversion #4. """
        assert scheduler.convert_time(13.00) == "1:00"

    def test_five(self):
        """ Test time conversion #5. """
        assert scheduler.convert_time(14.25) == "2:15"


class TestPrefsStringReader(unittest.TestCase):
    """ Tests for the prefs string reader. """

    def test_simple_prefers(self):
        """ Test get_day_prefs() with a 6-char prefers to work string. """
        
        pstring = 'PPPPPP'
        expected = 'Prefers to work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_simple_can_work(self):
        """ Test get_day_prefs() with a 6-char can work string. """
        
        pstring = 'XXXXXX'
        expected = 'Can work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_simple_both(self):
        """ Test get_day_prefs() with a 6-char mixed string. """

        pstring = 'XXPPPP'
        expected = 'Can work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_dislikes(self):
        """ Test get_day_prefs() with a 6-char string including dislikes. """

        pstring = 'XXDDPP'
        expected = ''

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_longer(self):
        """ Test get_day_prefs() with a longer string. """

        pstring = 'XXXXXXCCCCCCCCCCCCPPCCCCCCCCCCCCCCCCCCCCCCXXXXXX'
        expected = 'Can work: 8:00 - 9:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_using_file(self):
        """ Test get_day_prefs() from the test_prefs file. """

        employees = scheduler.get_day_prefs("tests/test_prefs")
        
        expected1 = 'Can work: 8:00 - 9:30\nCan work: 8:30 - 10:00\n' \
                    'Can work: 9:00 - 10:30\nCan work: 9:30 - 11:00\n' \
                    'Prefers to work: 1:00 - 2:30\nCan work: 6:30 - 8:00'

        expected2 = 'Can work: 8:00 - 9:30\nCan work: 1:30 - 3:00\n' \
                    'Prefers to work: 2:00 - 3:30\nPrefers to work: 2:30 - 4:00\n' \
                    'Prefers to work: 3:00 - 4:30\nPrefers to work: 3:30 - 5:00\n' \
                    'Prefers to work: 4:00 - 5:30\nPrefers to work: 4:30 - 6:00\n' \
                    'Can work: 5:00 - 6:30\nCan work: 5:30 - 7:00\n' \
                    'Can work: 6:00 - 7:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(employees[0].prefs)
            assert test_output.getvalue().strip() == expected1

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(employees[1].prefs)
            assert test_output.getvalue().strip() == expected2


class TestWhenAvailable(unittest.TestCase):
    """ Test when_employee_available() and all_available() """

    def test_when_employee_available_one(self):
        """ Test when_employee_available() on first empl in test_prefs. """

        expected1 = 'Some Employee\n' \
                    'Can work: 8:00 - 9:30\nCan work: 8:30 - 10:00\n' \
                    'Can work: 9:00 - 10:30\nCan work: 9:30 - 11:00\n' \
                    'Prefers to work: 1:00 - 2:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.when_employee_available('tests/test_prefs', 'Some Employee')
            assert test_output.getvalue().strip() == expected1

    def test_when_employee_available_two(self):
        """ Test when_employee_available() on second empl in test_prefs. """

        expected2 = 'Test Student\n' \
                    'Can work: 8:00 - 9:30\nCan work: 1:30 - 3:00\n' \
                    'Prefers to work: 2:00 - 3:30\nPrefers to work: 2:30 - 4:00\n' \
                    'Prefers to work: 3:00 - 4:30\nPrefers to work: 3:30 - 5:00\n' \
                    'Prefers to work: 4:00 - 5:30\nPrefers to work: 4:30 - 6:00\n' \
                    'Can work: 5:00 - 6:30\nCan work: 5:30 - 7:00\n' \
                    'Can work: 6:00 - 7:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.when_employee_available('tests/test_prefs', 'Test Student')
            assert test_output.getvalue().strip() == expected2

    def test_all_available(self):
        """ Test all_available() on the test prefs. """

        expected = 'Some Employee\n' \
                   'Can work: 8:00 - 9:30\nCan work: 8:30 - 10:00\n' \
                   'Can work: 9:00 - 10:30\nCan work: 9:30 - 11:00\n' \
                   'Prefers to work: 1:00 - 2:30\nCan work: 6:30 - 8:00\n\n' \
                   'Test Student\n' \
                   'Can work: 8:00 - 9:30\nCan work: 1:30 - 3:00\n' \
                   'Prefers to work: 2:00 - 3:30\nPrefers to work: 2:30 - 4:00\n' \
                   'Prefers to work: 3:00 - 4:30\nPrefers to work: 3:30 - 5:00\n' \
                   'Prefers to work: 4:00 - 5:30\nPrefers to work: 4:30 - 6:00\n' \
                   'Can work: 5:00 - 6:30\nCan work: 5:30 - 7:00\n' \
                   'Can work: 6:00 - 7:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.all_available('tests/test_prefs')
            assert test_output.getvalue().strip() == expected
