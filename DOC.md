# momforth documentation

This documentation assumes you're familiar with how FORTH dialects work (i.e. 
stack-based programming) as well as the `( before -- after )` notation for the state of
the stack.

All language keywords/tokens are separated by at least one space, as per any
other FORTH dialect.

## Constants (Integers and Booleans)

To push a decimal number constant to the stack, simply enter the decimal
literal. This does not work for negative decimal values, as they must be
negated using a different keyword.

You can use `true` and `false` to push -1 and 0 to the stack, respectively.

## Stack Manipulation

### `dup ( a -- a a )`

This duplicates the value at the top of the stack.

### `drop ( a -- )`

This drops the top value off of the stack.

### `swap ( a b -- b a )`

This swaps the top and second-from-the-top elements of the stack

### `over ( a b -- a b a )`

This duplicates the second-from-the-top element of the stack and pushes
it to the top of the stack.

### `rot ( a b c -- b c a )`

This "rotates" the top three elements of the stack %% TODO %%

### `empty ( -- b ) `

If the stack is empty, this pushes 0 to the stack, otherwise it pushes -1 to
the stack.

## Compilation Mode

To enter compilation mode, use the `:` keyword followed by a "name". Write
whatever code you want after the "name" and then end with a `;` keyword- this
defines the keyword with that name as those instructions.

For example, we can define a `dup-three` keyword that copies and pushes the top 
of the stack three times like so:

```
: dup-three dup dup dup ;
```

When the momforth interpreter runs, every time it encounters `dup-three` after
this definition it will replace that keyword with the `dup dup dup` instructions
before continuing execution.

**A note on keywords:** user-defined keywords simply must be space-separated,
and must start with a letter or an underscore. Using hyphens or underscores in
variable names is completely fine.

## Math

### `+ ( a b -- n )`

Pops numbers a and b off of the stack and pushes b + a onto the stack.

### `- ( a b -- n )`

Pops numbers a and b off of the stack and pushes b - a onto the stack.

### `neg ( a -- n )`

Pops a off of the stack and pushes -a back onto the stack.

### `* ( a b -- n )`

Pops a and b off of the stack and pushes b * a onto the stack.

### `/ ( a b -- n )`

Pops a and b off of the stack and pushes b / a onto the stack (integer division)

### `% ( a b -- n )`

Pops a and b off of the stack and pushes b mod a onto the stack.
You can also use the `mod` keyword to achieve the same result

### `rand ( a -- n )`

Pops a "bound" off of the stack. If this "bound" is positive, it pushes a 
random positive integer between 0 and that bound onto the stack. If the bound 
is negative, it pushes a random negative integer between 0 and that bound to
the stack.

So, `3 rand` will generate either 0, 1, or 2, while `3 neg rand` will generate
either 0, -1, or -2.

If the bound is 0, it pushes 0.

## Comparison and Boolean Operators

### `= ( a b -- n )`

Pops a and b off of the stack, if they are equal then -1 is pushes to the stack,
otherwise 0 is pushed.

### `< ( a b -- n )`

Pops a and b off of the stack, if b < a then it pushes -1, otherwise it pushes
0.

### `> ( a b -- n )`

Pops a and b off of the stack, if b > a then it pushes -1, otherwise it pushes
0.

### `! ( a -- n )`

Pops a off of the stack, if a is 0 it pushes -1 to the stack, otherwise it
pushes 0 to the stack. You can also use `not` instead.

### `and ( a b -- n )`

Pops a and b off of the stack. If both a and b do not equal 0, then -1 is pushed
onto the stack, otherwise 0 is pushed to the stack.

### `or ( a b -- n )`

Pops a and b off of the stack. If either a or b or both are non-zero, then
-1 is pushed to the stack; otherwise 0 is pushed to the stack.

## Input and Output

### `. ( n -- )`

Pops the top off the stack and prints it to the standard output.

### `."`

Prints a string literal to the standard output, like so:

```
." Hello, world!"
```

### `cr`

Prints a carriage-return (new line) to the standard output.

### `emit ( c -- )`

Pops the top off the stack and prints it as a character, converting the
integer value into a unicode character value. For example, this will
print the letter 'A':

```
65 emit
```

### `number ( -- n )`

Stops program execution to wait for the user to input a number into the 
standard input. This number is then pushed onto the stack.

### `key ( -- k )`

Stops program execution to wait for the user to press a keyboard key. The 
keycode for this key is then pushed onto the stack (work in progress).

## If/Else

Here is an example of an if-then statement that prints "Is Even" if the top of
the stack is even:

```
2 % 0 = if ." Is Even" then
```

The `if` keyword pops the top off of the stack. If this value is non-zero,
then the instructions between `if` and `then` are evaluated, otherwise we skip
to the instructions after `then`.

For an if-else statement, it works very similarly:

```
2 % 0 = if ." Is Even" else ." Is Odd" then
```

If the top of the stack is non-zero, we run the block after `if` but before
`else`, and then skip to `then`. Otherwise, we run the block after `else` but
before `then`.

## Looping with Do-Loops

"do" loops are similar to for-loops in other languages. Here is an example:

`10 0 do i . cr loop`

This loop prints the numbers 0 through 9, each on their own line.

Upon encountering `do`, two values are popped off of the stack. The first value
is the starting index (in this case 0) and the second value is the limit (in 
this case 10). The `i` keyword pushes the current value of the loop index
onto the stack.

As the loop body executes, once the `loop` keyword is reached the program checks
if the index is still less than the limit. If it is, then we increment the index
and go back to repeat the loop body.

If you want, you can increment the loop index by what's on the top of the stack
rather than just by 1 every time using the `+loop` keyword. For example, this
loop will print only the even numbers from 0 through 10 by incrementing the 
index by two:

`11 0 do i . cr 2 +loop`

## Looping with Begin-Until

Begin-until loops work very similar to a "while" loop from other procedural 
programming languages. Every time the `until` keyword is reached, they pop
the top of the stack, and if this value is non-zero, the program loops back to 
the `begin` keyword again. 

Here is a begin-until loop that prints the numbers 0 through 9 on separate
lines:

`1 neg begin 1 + dup . cr dup 9 < until`

## Variables and Lists

### Variables

To declare a variable, use the `let` keyword:

```
let my_variable
```

Then, the `->` operator can be used to pop a value off of the stack and
assign it to that variable. The `set` keyword can also be used, so the following
lines are equivalent:

```
3 -> my_variable
3 set my_variable
```

To grab the value of a variable and push it onto the stack, use `get`:

```
get my_variable
```

### Lists

To declare a list, use the `list` keyword. This pops the top off of the stack
and creates a new list of that length. The following code creates a list with
four elements:

```
4 list my_list
```

New lists are filled with zeroes by default.

To push the size of a list to the top of the stack, use `len`:

```
len my_list
```

To get an element from a list and push it onto the stack, you use the `from`
keyword. This pops the top value off of the stack to be used as an index, and
the list element at that index is then pushed onto the stack. List indices
start at 1, so this gets the first element of a list:

```
1 from my_list
```

To assign a value to a specific list element, you use the `into` keyword, 
popping two values off of the stack and affecting the stack like so:

`( index value -- )`

The first number popped off of the stack is the new value going into the list.
The second number popped off of the stack is the index where that new value is
going. So, to set the second element of a list to 5, use the following code:

```
2 5 into my_list
```

### Popping

Lists and variables that you no longer need can be "popped" and removed from
the scope of the program, making them no-longer accessible and freeing them
from memory:

```
pop my_list
pop my_variable
```

You can use `free` to do the same thing, so the following lines are equivalent
to the previous ones:

```
free my_list
free my_variable
```

## Other Features

Comments are placed inside parentheses, like so:

```
." Hello world!" ( this is a comment )
```

Commas can be used as separators. They don't do anything, but they can make
programs more readable:

```
dup dup dup
dup , dup , dup ( These are equivalent )
```

To exit the program and print "Goodbye :)" simply use the `bye` keyword.

You can have the program wait a specified number of milliseconds with the `wait`
or `sleep` keywords- these are equivalent; they both pop the top off of the stack
and "wait" for that amount of milliseconds.
