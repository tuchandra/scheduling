from collections import namedtuple

""" Scheduling tool for Northwestern IT.

Follow the instructions in README.md to make sure that the prefs files are
properly configured. This assumes they are located in prefs/ and named
monday.txt, tuesday.txt, etc.

...
"""


def read_prefs_file(day):
    """ Reads the prefs file for 'day' and returns the line-by-line text. """

    fname = day + ".txt"
    with open(fname) as f:
        return f.read().splitlines()


def combine_lines(lines):
    """ Combine pref file lines for the same employee.

    Details: The prefs file is structured as in tests/test_prefs.txt. Each 
    employee has two lines; one is their name, other info, and max hours; and
    the second immediately follows with their prefs.

    This takes in a list of lines (i.e., the output of a splitlines() call)
    that is itself taken directly from the WhenToWork source.

    This function combines lines for the same employee, outputting a list of
    namedtuples ("name", "prefs).
    """

    # Some lines have <script> or </script> tags, so get rid of those
    for i, line in enumerate(lines):
        lines[i] = line.replace("<script>", "").replace("</script>", "")

    # Create Employee struct, and list of employees
    Employee = namedtuple("Employee", ["name", "prefs"])
    empls = []

    for line in lines:
        # Lines with names are always followed by lines with prefs, so 
        # we can keep the 'name' var from one iteration to the next.
        if line[:3] == "nm2":
            # Lines that start with nm2 are an employee, in the form
            #   nm2("First Last","",2,"id");sc("40");stuff();
            # Splitting at ; lets us get contents of nm2() as the 0th entry.
            # -> ['nm2("First Last","",2,"id")', 'sc("40")', 'stuff()']
            # -> 'nm2("First Last","",2,"id")'
            # Splitting again at " lets us get the name itself as the 1st entry
            # -> ['nm2(', 'First Last', ',', '', ',2,', 'id', ')']
            # -> 'First Last'
            line_parts = line.split(";")
            name = line_parts[0].split('"')[1]

        if line[:2] == "tb" or line[:2] == "tc":
            # Lines that start with tb or tc are the prefs string.
            # We have 'name' from the previous loop iteration.
            empls.append(Employee(name, line))

    return empls


def get_all_prefs(day):
    """ Get all of the employees' prefs for a 'day'.

    ...
    """

    # See tests/test_prefs.txt for structure of the prefs file
    # Get file; first three lines are garbage; last three lines are garbage
    lines = read_prefs_file(day)[3:-4]
    empls = combine_lines(lines)

    # Lines that start with tb or tc are a prefs line, in the form
    #   tb(0, 6);tc(3, 5, "1");other();things();etr();
    # Each of these tb() and tc() segments denotes an interval on their prefs.
    #
    # tb(x, y) are "no preference" intervals (i.e., white) that last for 
    # y 15-minute intervals (e.g., tb(0, 4) is an hour of white)
    #
    # tc(x, y, "z") are colored intervals, where z denotes the color
    # (1 = green, 2 = pink, 3 = red), and they last for y 15-minute intervals

    return


def when_employee_available(day, name):
    """ Prints availability of a given employee 'name' on 'day'.

    ...
    """

    ...


def all_available(day):
    """ Prints availability of all employees on 'day'.

    ...
    """

    ...


def who_can_work(day, time):
    """ Prints employees who can work on 'day' at 'time' for > 1.5 hours.

    ...
    """

    ...


def count_available_hours(day, name):
    """ Prints number of hours employee 'name' is available on 'day'.

    ...
    """

    ...