# scheduling
Tools to help build a schedule for student employees at Northwestern IT.

## Introduction

## Getting Started (for future schedulers)
### Pulling data from WhenToWork
Go to WhenToWork, and log in with the `lc2` account. In the top menu, `Schedules`, click `Availability / Coverage View`. Make sure to navigate to a week where everyone will have their prefs active (i.e., the first full week of the quarter). In the top right, select `TSC Hours` for `Display Time`. Click on the `Mon` tab, and open the page source. Around line 800 or so (as of August 2016), you should see employees' names, position names, and some numbers enclosed in `<script>` tags. 

Look for something in this format:

```
<script>avdh("23809818","Consultant",1,"Hrs Left");h("7");
h("8a");h("9");h("10");h("11");h("12");
h("1p");h("2");h("3");h("4");h("5");h("6");h("7");etr();
nm2("One Employee","",2,"160527290","");sc("40");
tb(0,6);tc(2,6,"3");tc(0,4,"2");tc(0,10,"3");tc(2,2,"2");tc(0,18,"3");tc(2,6,"2");etr();
(...)
nm2("Another Employee","",2,"125085768","");sc("50");
tb(0,8);tc(0,12,"3");tc(0,4,"2");tc(0,12,"1");tb(0,16);etr();
ft("Consultant - Available");dt("5<br>1","5<br>1","4<br>7","4<br>7");dt("4<br>5","4<br>5","4<br>1","4<br>1");dt("3<br>6","3<br>6","3<br>4","3<br>4");dt("3<br>5","3<br>5","3<br>0","3<br>0");dt("3<br>0","3<br>1","3<br>9","3<br>8");dt("3<br>2","3<br>1","2<br>8","2<br>8");dt("2<br>9","3<br>1","2<br>7","2<br>7");dt("2<br>7","2<br>8","3<br>4","3<br>4");dt("2<br>8","2<br>7","2<br>7","2<br>7");dt("3<br>2","3<br>2","3<br>2","3<br>2");dt("3<br>5","3<br>6","4<br>3","4<br>4");dt("4<br>6","4<br>6","4<br>8","4<br>8");dt("4<br>8","4<br>8","4<br>8","4<br>8");etr();
ft("Consultant - Working");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");dt("0","0","0","0");etr();
tbr();
</script>
```

Be sure that the position says `Consultant` at the top, and make sure that you have all of the employees included (the line `Consultant - Available` should appear at the bottom; the list will likely be broken up across several sequential `<script>` tags).

Paste the body of text into a directory `prefs`, and name it `monday.txt`. Repeat for the other days of the week.

### Parsing the preferences
The script does all of the work of parsing that mess above into a useful, human-readable form. There are several options available for running the script, depending on what one's needs are. These are detailed at the top of the script as usage instructions, and can also be seen by running `scheduler.py --help`. 

Options exist to:
* view availability on a particular day, by time (e.g., see, for each time on Monday, who can work a shift starting at that time) -- `scheduler.py --day <day>`
* view availability on a particular day, by employee (e.g., see the times that each employee is available on Monday) -- `scheduler.py --day <day> --byempl`
* view availability for a particular employee on a particular day (e.g., see when someone can work on Monday) -- `scheduler.py --day <day> --name <name>`
* view availability for a particular time on a particular day (e.g., see who can work Monday at 9:00 am) -- `scheduler.py --day <day> --time <time>`
* view availability for a particular employee on every day (e.g., see when someone can work all week)  -- `scheduler.py --name <name>`

This allows schedulers to go from a high-level view, answering questions like "When on Monday is going to be the tightest to schedule?", to a low-level view, giving information about specific times or people, with ease.