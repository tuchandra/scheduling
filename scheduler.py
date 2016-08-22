"""Scheduling tool for Northwestern IT.

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

Usage:
    scheduler.py -h | --help
    scheduler.py --day <day>
    scheduler.py --day <day> --byempl
    scheduler.py --day <day> --time <time>
    scheduler.py --day <day> --name <name>
    scheduler.py --count (--day <day>)
    scheduler.py --name <name>

Options:
    --help, -h              Show this message
    --day, -d <day>         Get availabilities for day, by time
    --byempl, -e            Get availabilities by empl (requires --day)
    --time, -t <time>       Get availabilities for a time (requires --day)
    --name, -n <name>       Get availabilities for employee 'name'
    --count, -c             Count hours each empl is available (--day optional)

Detailed explanation of options:
    Runing the script without any options will only display the help message.
    More specification is needed for the script to be useful.

    Running the script with a --day option will let you see all of the
    availabilities for that day, by time.. This option requires a valid,
    correctly spelled day of the week (case insensitive). If one wishes to
    see the availability by employee on that day, this can be run with both
    --day and --byempl.

    In conjunction with the --day option, one can use a --time option to see
    the availabilities at a certain time that day. The time should be in the
    format HH:MM, using 12-hour format (the schedule occurs between the hours
    of 8am and 8pm, so there is no ambiguity in the hours).

    An alternative to the --time option is the --name option, which lets one
    see all of a particular person's availability on that day. The --name
    option can also be used alone, displaying their ability for the entire
    week.

    Finally, it is often useful to count the hours each employee is available.
    This can be done with the --count flag; the --day option may optionally
    be used as well, to restrict counting to a particular day. By default,
    the hours are counted for every day.

    These usage patterns are listed above in "Usage."

Configuring employees to ignore:
    If there are employees you do not wish to include in the output of this
    script for some reason (e.g., they have no prefs and you don't need to see
    their name everywhere), then create a new file in this directory called
    ignore.py, with a list EMPLS_TO_IGNORE of the names to ignore.

    e.g., EMPLS_TO_IGNORE = ["Tushar Chandra", "Another Person"]

    This is included in .gitignore so that it remains private. 
"""

from collections import namedtuple
from docopt import docopt

try:
    from ignore import EMPLS_TO_IGNORE
except ImportError:
    EMPLS_TO_IGNORE = []

def read_prefs_file(day):
    """ Reads the prefs file for 'day' and returns the line-by-line text. """

    fname = "prefs/" + day + ".txt"
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
        # Ignore certain employees by setting their prefs to never working
        if empl.name in EMPLS_TO_IGNORE:
            empls[i] = Employee(empl.name, 'C' * 48)
            continue
        
        empls[i] = Employee(empl.name, prefs_line_to_string(empl.prefs))

    return empls


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
            return (ind - index) * 0.25

    # If we exhaust the string, return difference in hours as well; the +1 is
    # to account for the extra iteration that we would get if we weren't at the
    # end of the string.
    return (ind - index + 1) * 0.25


def when_employee_available(day, name):
    """ Prints availability of a given employee 'name' on 'day'. """

    employees = get_day_prefs(day)

    for empl in employees:
        if empl.name == name:
            read_prefs_string(empl.prefs)


def day_available_by_empl(day):
    """ Prints availability of all employees on 'day'. """

    employees = get_day_prefs(day)

    for empl in employees:
        print(empl.name)
        read_prefs_string(empl.prefs)
        print()


def day_available_by_time(day):
    """ Prints availability at all times on 'day'. """

    employees = get_day_prefs(day)
    times = ["8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", 
             "11:30", "12:00", "1:00", "1:30", "2:00", "2:30", "3:00",
             "3:30", "4:00", "4:30", "5:00", "5:30", "6:00", "6:30"]

    for time in times:
        print("Shifts starting at {0}".format(time))
        count = 0

        for empl in employees:
            hours_av = can_work(empl.prefs, time)

            if hours_av:
                end_time = decimal_to_time(time_to_decimal(time) + hours_av)
                print("{0}, until {1}".format(empl.name, end_time))
                count += 1

        print("{0} employees available\n".format(count))


def who_can_work(day, time):
    """ Prints those who can work, and for how long, on 'day' at 'time'. """

    employees = get_day_prefs(day)

    for empl in employees:
        hours_available = can_work(empl.prefs, time)

        # hours_available is either 0 or an amount of time they can work
        if hours_available:
            time2 = decimal_to_time(time_to_decimal(time) + hours_available)
            print("{0}, from {1} until {2}".format(empl.name, time, time2))


def hours_by_empl(day=None):
    """ Prints hours each employee can work on 'day' (default all days) """

    # Default: calculate for all days. Otherwise, just do the one
    if day is None:
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    else:
        days = [day]

    for day in days:
        print(day.title())
        employees = get_day_prefs(day)

        for empl in employees:
            chars = empl.prefs.count("P") + empl.prefs.count("X")
            hours = chars / 4
            print("{0}: {1} hours".format(empl.name, str(hours)))

    return


if __name__ == "__main__":
    args = docopt(__doc__)

    day, time, name = args["--day"], args["--time"], args["--name"]
    byemplflag, helpflag = args["--byempl"], args["--help"]
    countflag = args["--count"]

    # Convert day to lowercase
    if day:
        day = day.lower()

    valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

    # If they ask for help, or don't specify other options, display docs
    if helpflag or (not day and not time and not name):
        print(__doc__)

    if countflag:
        # If they specify a day and the count flag, count hours for that day
        if day in valid_days:
            hours_by_empl(day)

        # Otherwise, count hours for every day
        else:
            hours_by_empl()

    elif day in valid_days:
        # If they specify day and name, find name's availability that day
        if name:
            when_employee_available(day, name)

        # If they specify day and time, find all availability at that time
        elif time:
            who_can_work(day, time)

        # If they specify availability by empl, do that
        elif byemplflag:
            day_available_by_empl(day)

        # Otherwise, find all available on that day by time
        else:
            day_available_by_time(day)

    # If they just specify a name, print that person's availability all week.
    if name and not day:
        print(name)
        for day in valid_days:
            print(day.title())
            when_employee_available(day, name)
            print()