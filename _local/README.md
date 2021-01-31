

# LocalTools


## Setup
Run as your user. 

```
make 
```
```
(inv)  < - command that's run
   |
   |
   ----> (base alias) for investigate command.  calling source shifts
          users pwd
              |
              |
              -----> (investigate) creates folder, 
                      using format YYYYMMDD-(DESCRIPTION), 
                      creates .invnotes file with some simple details
```


# Author Notes
Whenever I look at anything, it gets an investigation folder.  In these folders, I keep everything from scratch notes to samples.  In order to keep track of things, each has a name and a date.  I then sort the folders after a month in a format I'll document later. 



## Usage

Creates a folder, with a specifically formatted name, and automatically moves you into it.

Execute by running `inv DESCRIPTION`, you will be prompted to enter some quick notes.  I used to use this to track where the case came from - either email alert, VT notification, etc.

```
$ 
$ inv Test
Note:> test
c20210131-Test $
```








