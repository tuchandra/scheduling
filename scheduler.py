from collections import namedtuple

""" Scheduling tool for Northwestern IT.

Follow the instructions in README.md to make sure that the prefs files are
properly configured. This assumes they are located in prefs/ and named
monday.txt, tuesday.txt, etc.

Definitions:
    W2W: WhenToWork
    prefs: On W2W, each employee can enter preferences for when they want to
           work. Each 15-minute interval (e.g., 7 to 7:15) is assigned a color
           (green, pink, red, white) denoting their availability.
    prefs string: A string representation of an employee's prefs. Each
                  character in the string represents one 15-minute interval,
                  starting at 8am and continuing until 8pm. The four characters
                  represent the availability (X = no preference, P = prefers
                  to work, D = dislikes working, C = cannot work)
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


def prefs_line_to_string(line):
    """ Converts a prefs line to a string.

    Prefs line is in the format tb(..);tc(..);..;..;.

    tb(x, y) are "no preference" intervals (i.e., white) that last for
    y 15-minute intervals (x has no meaning):
        e.g., tb(0, 4) is an hour of white; tb(2, 8) is two hours.

    tc(x, y, "z") are colored intervals, where z denotes the color, and they
    last for y 15-minute intervals (x has no meaning):
        z-values: 1 = green, 2 = pink, 3 = red
        e.g., tc(0, 10, "3") is an hour and a half of red.
        e.g., tc(0, 20, "1") is three hours of green.

    It gets sent to a string of XPDC characters, where:
        X - no preference (white)
        P - prefers to work (green)
        D - dislikes working (pink)
        C - cannot work (red)
    And each character represents 15 minutes of that color,
        e.g., XXXX = hour of white; RRDD = half hour of red, half hour of pink
    """

    prefs_pieces = line.split(';')
    prefs_string = ''

    # Mapping between prefs line code and actual color character
    codes = {1: "P", 2: "D", 3: "C"}

    for piece in prefs_pieces:
        if piece[:2] == "tb":
            # Format: tb(x,y) where y denotes the number of 15-minute intervals
            # Split at comma, -> [ 'tb(x', 'y)']
            # Extract y as second entry, remove last char (close paren)
            # and cast to int
            piece = piece.split(',')[1]
            length = int(piece[:-1])

            # Length tells how many X characters there should be
            prefs_string += ('X' * length)

        if piece[:2] == "tc":
            # Format: tc(x,y,"z")
            # x is worthless; y is the length; z is the color
            # Split at comma, -> [ 'tc(x', 'y', '"z")')]
            # Length, y is the second entry
            # Extract z as the third entry, stripping first and last two chars
            # (open quote, and close quote + close paren), and cast to int
            piece = piece.split(',')
            length = int(piece[1])
            code = int(piece[2][1:-2])

            # Lookup which character to add in codes; length tells how many
            prefs_string += (codes[code] * length)

    return prefs_string


def get_day_prefs(day):
    """ Get all of the employees' prefs for a 'day'.

    Given a day of the week, this function reads the prefs file for that day,
    parses it into employees and prefs, and converts each set of prefs to a
    prefs string.
    """

    # See tests/test_prefs.txt for structure of the prefs file
    # Get file; first three lines are garbage; last three lines are garbage
    lines = read_prefs_file(day)[3:-4]
    empls = combine_lines(lines)

    # Replace each entry in empls with a new namedtuple; we can't modify the
    # tuples directly.
    Employee = namedtuple("Employee", ["name", "prefs"])
    for i, empl in enumerate(empls):
        empls[i] = Employee(empl.name, prefs_line_to_string(empl.prefs))

    return empls


def decimal_to_time(time):
    """ Takes HH.MM (24 hours) as decimal, converts to HH:MM (12 hours).

    >>> decimal_to_time(13.50)
    '1:30'

    >>> decimal_to_time(8.75)
    '8:45'
    """

    time = str(time).split(".")

    # Get hour, convert to 12-hour format
    temp_hr = int(time[0]) - 1
    hpart = str(temp_hr % 12 + 1)

    # Get minutes, convert from decimal
    minutes = {0: "00", 15: "15", 3: "30", 45: "45"}
    mpart = minutes[int(0.60 * float(time[1]))]

    return "{0}:{1}".format(hpart, mpart)


def time_to_decimal(time):
    """ Takes HH:MM and converts to decimal (24 hour format).

    Times after 12:00 and before 8:00 are assumed to be PM.

    >>> time_to_decimal('8:30')
    8.5

    >>> time_to_decimal('1:30')
    13.5
    """

    time = time.split(":")
    new_time = int(time[0])

    # Times after 12:00 but before 8:00 are PM
    if new_time < 8:
        new_time += 12

    new_time += int(time[1]) / 60

    return new_time


def read_prefs_string(pstring):
    """ Read an employee prefs string to print their availability.

    This looks for periods of 1.5 hours (minimum shift length) where an
    employee prefers or has no preference working, ignoring times they dislike
    or cannot work. The results are printed out.

    Shifts also start on the half hour, so this iterates through the string
    in increments of two 15-minute elements.

    While the minimum shift length defaults to 1.5 hours (6 chars), but
    this can be changed if it is necessary to fill a longer shift.
    """

    # Configure minimum shift length
    MIN_SHIFT_LENGTH_HOURS = 1.5
    num_chars = int(MIN_SHIFT_LENGTH_HOURS * 4)

    time = 8.00

    for i, char in enumerate(pstring):
        # Iterate by two characters, so skip odd indices
        if i % 2 == 1:
            continue

        # When we reach 6 chars from the end of the string, break
        if i + 6 > len(pstring):
            break

        time1 = decimal_to_time(time)
        time2 = decimal_to_time(time + 1.5)

        # Check if they prefer this time
        if pstring[i : i+num_chars] == 'PPPPPP':
            print("Prefers to work: {0} - {1}".format(time1, time2))

        # Check that they can work this time (ignoring dislikes / cannot)
        elif can_work(pstring, decimal_to_time(time)):
            print("Can work: {0} - {1}".format(time1, time2))

        time += 0.5

    return 


def can_work(pstring, time):
    """ Checks if employee can work at 'time'.

    Returns how long they can work, in hours (or 0 if they cannot).
    """

    # Get time as a decimal; index obtained by remembering string starts at
    # 8:00, with each char being 0.25 hours
    time = time_to_decimal(time)
    index = int((time - 8.00) * 4)

    # Check if they cannot work; return 0 if so
    if "C" in pstring[index : index+6] or "D" in pstring[index : index+6]:
        return 0

    # Otherwise, figure out how long they can work for; once a cannot / dislike
    # is hit, terminate and return the difference in hours.
    # Start the iteration through the prefs string at the relevant time, and
    # for simplicity, also start the counter at the same index.
    for ind, char in enumerate(pstring[index:], start=index):
        if char == "C" or char == "D":
            return (ind - index + 1) * 0.25

    # If we exhaust the string, return difference in hours as well
    return (ind - index + 1) * 0.25


def when_employee_available(day, name):
    """ Prints availability of a given employee 'name' on 'day'. """

    employees = get_day_prefs(day)

    for empl in employees:
        if empl.name == name:
            print(name)
            read_prefs_string(empl.prefs)
            print()


def all_available(day):
    """ Prints availability of all employees on 'day'. """

    employees = get_day_prefs(day)

    for empl in employees:
        print(empl.name)
        read_prefs_string(empl.prefs)
        print()


def who_can_work(day, time):
    """ Prints those who can work on 'day' at 'time', and how long they can.

    ...
    """

    ...


def count_available_hours(day, name):
    """ Prints number of hours employee 'name' is available on 'day'.

    ...
    """

    ...