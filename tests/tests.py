from .. import scheduler

from collections import namedtuple
from io import StringIO
import unittest
from unittest.mock import patch

class TestPrefsReader(unittest.TestCase):
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

        actual_prefs = scheduler.get_day_prefs("test_prefs")
        expected = [Employee('Some Employee', 'XXXXXXXXXXXXDDDDDDDDPPPPPPCCCCCCCCCCCCCCCCXXXXXX'),
                    Employee('Test Student', 'XXXXXXCCCCCCCCCCCCCCCCXXPPPPPPPPPPPPPPPPXXXXXXXX')]


        assert actual_prefs == expected


class TestPrefsLineConversion(unittest.TestCase):
    """ Tests the conversion function prefs_line_to_string(). """

    def test_prefs_conversion_simple_uncolored(self):
        """ Test prefs_line_to_string() from one tb(..) piece. """
        line = 'tb(0,4);'
        expected = 'XXXX'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_prefs_conversion_simple_green(self):
        """ Test prefs_line_to_string() for a green tc(..) piece. """
        line = 'tc(4,8,"1");'
        expected = 'PPPPPPPP'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_prefs_conversion_simple_pink(self):
        """ Test prefs_line_to_string() for a pink tc(..) piece. """
        line = 'tc(4,6,"2");'
        expected = 'DDDDDD'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_prefs_conversion_simple_red(self):
        """ Test prefs_line_to_string() for a red tc(..) piece. """
        line = 'tc(4,4,"3");'
        expected = 'CCCC'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_prefs_conversion_double(self):
        """ Test prefs_line_to_string() with two pieces. """
        line = 'tc(2,4,"1");tb(0,8);'
        expected = 'PPPPXXXXXXXX'

        assert scheduler.prefs_line_to_string(line) == expected

    def test_prefs_conversion_multiple(self):
        """ Test prefs_line_to_string() with multiple pieces. """
        line = 'tb(0,4);tc(0,14,"3");tc(2,2,"1");tc(0,26,"3");tb(2,6);etr();'
        expected = 'XXXXCCCCCCCCCCCCCCPPCCCCCCCCCCCCCCCCCCCCCCCCCCXXXXXX'

        assert scheduler.prefs_line_to_string(line) == expected


class TestTimeConversions(unittest.TestCase):
    """ Tests for time conversion. """

    def test_decimal_to_time_one(self):
        """ Test decimal_to_time() conversion #1. """
        assert scheduler.decimal_to_time(8.00) == "8:00"

    def test_decimal_to_time_two(self):
        """ Test decimal_to_time() conversion #2. """
        assert scheduler.decimal_to_time(8.50) == "8:30"

    def test_decimal_to_time_three(self):
        """ Test decimal_to_time() conversion #3. """
        assert scheduler.decimal_to_time(12.50) == "12:30"

    def test_decimal_to_time_four(self):
        """ Test decimal_to_time() conversion #4. """
        assert scheduler.decimal_to_time(13.00) == "1:00"

    def test_decimal_to_time_five(self):
        """ Test decimal_to_time() conversion #5. """
        assert scheduler.decimal_to_time(14.25) == "2:15"

    def test_time_to_decimal_one(self):
        """ Test time_to_decimal() conversion #1. """
        assert scheduler.time_to_decimal('8:30') == 8.5

    def test_time_to_decimal_two(self):
        """ Test time_to_decimal() conversion #2. """
        assert scheduler.time_to_decimal('1:30') == 13.5

    def test_time_to_decimal_three(self):
        """ Test time_to_decimal() conversion #3. """
        assert scheduler.time_to_decimal('12:00') == 12

    def test_time_to_decimal_four(self):
        """ Test time_to_decimal() conversion #4. """
        assert scheduler.time_to_decimal('4:30') == 16.5

    def test_time_to_decimal_five(self):
        """ Test time_to_decimal() conversion #5. """
        assert scheduler.time_to_decimal('1:00') == 13


class TestReadPrefsString(unittest.TestCase):
    """ Tests for read_prefs_string(), the prefs string reader. """

    def test_read_prefs_string_simple_prefers(self):
        """ Test read_prefs_string() with a 6-char prefers to work string. """
        
        pstring = 'PPPPPP'
        expected = 'Prefers to work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_read_prefs_string_simple_can_work(self):
        """ Test read_prefs_string() with a 6-char can work string. """
        
        pstring = 'XXXXXX'
        expected = 'Can work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_read_prefs_string_simple_mixed(self):
        """ Test read_prefs_string() with a 6-char mixed string. """

        pstring = 'XXPPPP'
        expected = 'Can work: 8:00 - 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_read_prefs_string_dislikes(self):
        """ Test read_prefs_string() with a 6-char string including dislikes. """

        pstring = 'XXDDPP'
        expected = ''

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_read_prefs_string_longer(self):
        """ Test read_prefs_string() with a longer string. """

        pstring = 'XXXXXXCCCCCCCCCCCCPPCCCCCCCCCCCCCCCCCCCCCCXXXXXX'
        expected = 'Can work: 8:00 - 9:30\nCan work: 6:30 - 8:00'

        print (scheduler.read_prefs_string(pstring))
        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(pstring)
            assert test_output.getvalue().strip() == expected

    def test_read_prefs_string_using_file(self):
        """ Test read_prefs_string() from the test_prefs file. """

        employees = scheduler.get_day_prefs("test_prefs")
        
        expected1 = 'Can work: 8:00 - 9:30\nCan work: 8:30 - 10:00\n' \
                    'Can work: 9:00 - 10:30\nCan work: 9:30 - 11:00\n' \
                    'Prefers to work: 1:00 - 2:30\nCan work: 6:30 - 8:00'

        expected2 = 'Can work: 8:00 - 9:30\nCan work: 1:30 - 3:00\n' \
                    'Prefers to work: 2:00 - 3:30\nPrefers to work: 2:30 - 4:00\n' \
                    'Prefers to work: 3:00 - 4:30\nPrefers to work: 3:30 - 5:00\n' \
                    'Prefers to work: 4:00 - 5:30\nPrefers to work: 4:30 - 6:00\n' \
                    'Can work: 5:00 - 6:30\nCan work: 5:30 - 7:00\n' \
                    'Can work: 6:00 - 7:30\nCan work: 6:30 - 8:00'

        print (scheduler.read_prefs_string(employees[0].prefs))
        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(employees[0].prefs)
            assert test_output.getvalue().strip() == expected1

        print (scheduler.read_prefs_string(employees[1].prefs))
        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.read_prefs_string(employees[1].prefs)
            assert test_output.getvalue().strip() == expected2


class TestCanWork(unittest.TestCase):
    """ Tests for can_work(). """

    def test_can_work_simple(self):
        """ Test can_work() with a six-char string. """

        pstring = 'XXXXXX'
        assert scheduler.can_work(pstring, '8:00') == 1.5

    def test_can_work_longer(self):
        """ Test can_work() with a longer string. """

        pstring = 'XXXXXXXX'
        assert scheduler.can_work(pstring, '8:00') == 2

    def test_can_work_cannot_work(self):
        """ Test can_work() when someone can't work. """

        pstring = 'XXXXDDCC'
        assert scheduler.can_work(pstring, '8:00') == 0

    def test_can_work_not_end(self):
        """ Test can_work() on an interval that doesn't reach the end. """

        pstring = 'XXXXPPDD'
        assert scheduler.can_work(pstring, '8:00') == 1.5

    def test_can_work_other_time(self):
        """ Test can_work() with a time that's not 8:00. """

        pstring = 'XXXXPPPPXXXXPPPPXXXXPPPPPPPP'
        assert scheduler.can_work(pstring, '1:00') == 2


class TestWhenAvailable(unittest.TestCase):
    """ Test when_employee_available() and day_available_by_empl() """

    def test_when_employee_available_one(self):
        """ Test when_employee_available() on first empl in test_prefs. """

        expected1 = 'Can work: 8:00 - 9:30\nCan work: 8:30 - 10:00\n' \
                    'Can work: 9:00 - 10:30\nCan work: 9:30 - 11:00\n' \
                    'Prefers to work: 1:00 - 2:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.when_employee_available('test_prefs', 'Some Employee')
            assert test_output.getvalue().strip() == expected1

    def test_when_employee_available_two(self):
        """ Test when_employee_available() on second empl in test_prefs. """

        expected2 = 'Can work: 8:00 - 9:30\nCan work: 1:30 - 3:00\n' \
                    'Prefers to work: 2:00 - 3:30\nPrefers to work: 2:30 - 4:00\n' \
                    'Prefers to work: 3:00 - 4:30\nPrefers to work: 3:30 - 5:00\n' \
                    'Prefers to work: 4:00 - 5:30\nPrefers to work: 4:30 - 6:00\n' \
                    'Can work: 5:00 - 6:30\nCan work: 5:30 - 7:00\n' \
                    'Can work: 6:00 - 7:30\nCan work: 6:30 - 8:00'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.when_employee_available('test_prefs', 'Test Student')
            assert test_output.getvalue().strip() == expected2

    def test_day_available_by_empl(self):
        """ Test day_available_by_empl() on the test prefs. """

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
            scheduler.day_available_by_empl('test_prefs')
            assert test_output.getvalue().strip() == expected

    def test_who_can_work(self):
        """ Test who_can_work() on the test prefs. """
        expected = 'Some Employee, from 8:00 until 11:00\n' \
                   'Test Student, from 8:00 until 9:30'

        with patch('sys.stdout', new=StringIO()) as test_output:
            scheduler.who_can_work('test_prefs', '8:00')
            assert test_output.getvalue().strip() == expected        