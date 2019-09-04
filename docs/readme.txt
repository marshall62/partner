Getting rosters from Banner:

The admin section of the app (/admin) must be used to create course sections each semester.
Steps:

Use the sections tab to create the mapping from lab numbers to titles
e.g. 1 -> Thurs 1 PM

Once sections are created, use the roster tab to load the spreadsheet roster.
This will create Student objects and add them into the roster for the section.

Because the roster may be changing over time this process can be used repeatedly to update the roster
to reflect the current registration.  When the spreadsheet is reloaded it will reset the roster to empty and
then add the students back into it.   Student objects are not overloaded with new info.  This assumes that
basic data about students coming from the spreadsheet remains constant.
  The app does allow editing the student name and assumes that the first word in the name is a new nickname
  that is different from what came out of the spreadsheet.   Hand-edits will be placed in the nick_name field
  and should persist across roster reloads.

Instructions for getting a roster:

Go to Banner
Click Get *New* Class list.
Click in the first column (not shown as a link but clickable) to view the roster
Click Export in upper right
Select xlsx format
Download to the rosters directory within partner