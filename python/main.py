import sys
import time
import random
import readchar

def custom_random(n):
  if n > 0:
    return random.randrange(0, n)
  elif n < 0:
    return random.randrange(0, n, -1)
  else:
    return 0

class ForthInterpreter:
  def __init__(self):
    self.stack = []
    self.loop_stack = [] # stack for do loops
    self.begin_stack = [] # stack for begin loops
    
    # builtin words
    self.dictionary = {
      '+': self.add,
      '-': self.subtract,
      '*': self.multiply,
      '/': self.divide,
      '%': self.mod,
      '.': self.pop_and_print,
      '."': self.print_string,
      '=': self.equals,
      '<': self.less_than,
      '>': self.greater_than,
      '!': self.not_word,
      'and': self.and_word,
      'or': self.or_word,
      'dup': self.dup,
      'drop': self.drop,
      'swap': self.swap,
      'over': self.over,
      'rot': self.rot,
      'emit': self.emit,
      'rand': self.random,
      'empty': self.empty,
      ':': self.start_compile_mode,
      ';': self.end_compile_mode,
      'if': self.if_word,
      'then': self.then_word,
      'else': self.else_word,
      'do': self.do_word,
      'loop': self.loop_word,
      'i': self.i_word,
      '+loop': self.plus_loop_word,
      'bye': self.bye_word,
      'cr': self.cr_word,
      'let': self.var_word,
      'get': self.get_word,
      '->': self.set_word,
      'pop': self.pop, # TODO better name? Doesn't actually pop the stack
      'list': self.list_word,
      'len': self.len_word, # push length of list to stack
      'from': self.from_word, # index item into listname
      'into': self.into_word,
      'number': self.number_word,
      'key': self.get_key,
      'begin': self.begin_word,
      'until': self.until_word,
      'wait': self.wait_word,
      
      # some aliases
      'set': self.set_word,
      'not': self.not_word,
      'mod': self.mod,
      'free': self.pop,
      'sleep': self.wait_word,

      # these just get replaced with -1 and 0
      'true': self.true_word,
      'false': self.false_word,

      # commas can be used to improve readability, they just do nothing
      ',': self.comma,
    }
    
    self.source = ""
    self.is_file = False # flag for if we're running a file or the repl
    self.line = 1 # current line number
    self.position = 0 # position in source string
    self.compiling = False # compile mode flag
    self.current_word = None # name of the word being defined
    self.current_definition = [] # tokens for the word being defined
    self.user_words = {} # stores user-defined compiled words
    self.variables = {} # stores user variables
    self.lists = {} # stores user-defined lists  

  def wait_word(self):
    if not self.stack:
      self.panic("Not enough elements on stack for 'wait'")
      return

    ms = self.stack.pop() / 1000
    time.sleep(ms)

  def less_than(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on stack for '<'")
      return
    
    a = self.stack.pop()
    b = self.stack.pop()

    # 4 5 < should be "4 < 5"
    
    if b < a:
      self.stack.append(-1)
    else:
      self.stack.append(0)
    
  def greater_than(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on stack for '<'")
      return
    
    a = self.stack.pop()
    b = self.stack.pop()

    # 4 5 > should be "4 > 5"
    
    if b > a:
      self.stack.append(-1)
    else:
      self.stack.append(0)
  
  def begin_word(self):
    self.begin_stack.append(self.position) # just pop the loop start to the stack

  def until_word(self):
    if not self.begin_stack:
      self.panic("No loop in progress")
      return

    if not self.stack:
      self.panic("Stack is empty")
      return

    cond = self.stack.pop()
    start_pos = self.begin_stack[-1]

    if cond != 0: # pop condition, if non-zero, loop
      self.position = start_pos
    else:
      self.begin_stack.pop()
  
  def get_key(self):
    key = readchar.readkey() # TODO make this work a bit more async-like?
    # since it's kinda async it outputs the keycode at inconsistent times,
    # and it's blocking which isn't great
    try:
      key = ord(key)
    except:
      self.panic("Invalid keycode")
      return
    
    self.stack.append(key)
  
  def true_word(self):
    self.stack.append(-1)

  def false_word(self):
    self.stack.append(0)
  
  def number_word(self):
    num = 0
    
    try:
      num = int(input())
    except ValueError:
      self.panic("Invalid input (expected integer)")
      return
  
    self.stack.append(num)

  def and_word(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'and' (at least 2)")
      return

    a = self.stack.pop()
    b = self.stack.pop()

    if (a != 0) and (b != 0):
      self.stack.append(-1)
    else:
      self.stack.append(0)

  def or_word(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'or' (at least 2)")
      return

    a = self.stack.pop()
    b = self.stack.pop()

    if (a != 0) or (b != 0):
      self.stack.append(-1)
    else:
      self.stack.append(0)
  
  def comma(self):
    pass # does nothing
  
  # works for lists or variables
  def pop(self):
    name = self.get_next()

    if name in self.variables:
      self.stack.append(self.variables.pop(name))
    elif name in self.lists:
      self.stack.append(len(self.lists.pop(name)))
    else:
      self.panic(f"Variable/List '{name}' not found")

  # helper function to see if a word is already defined
  def already_defined(self, name):
    return (name in self.variables) or (name in self.lists) or (name in self.user_words) or (name in self.dictionary)
  
  def var_word(self):
    name = self.get_next()
    
    if name in self.dictionary:
      self.panic(f"'{name}' is a reserved word")
      return

    if self.already_defined(name):
      self.panic(f"Variable '{name}' already defined")
      return
    
    self.variables[name] = 0 # 0-initialized

  def list_word(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    size = self.stack.pop()

    if size <= 0:
      self.panic(f"Invalid list length {size}")
      return

    name = self.get_next()

    if self.already_defined(name):
      self.panic(f"'{name}' is already defined")
      return
    else:
      self.lists[name] = [0] * size

  def from_word(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    index = self.stack.pop() - 1 # REMEMBER, 1-indexed!!!
    name = self.get_next()
    
    if name not in self.lists:
      self.panic(f"List '{name}' not found")
      return

    if index < 0 or index > (len(self.lists[name]) - 1):
      self.panic(f"Index {index + 1} out of bounds for '{name}' (len {len(self.lists[name])})")
      return

    self.stack.append( (self.lists[name])[index] )

  # syntax: index item into listname
  # (n1 n2 -- )
  def into_word(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'put' (at least 2)")
      return

    new_item = self.stack.pop()

    name = self.get_next()
    if name not in self.lists:
      self.panic(f"List '{name}' not found")
      return

    index = self.stack.pop() - 1 # REMEMBER, 1-indexed!!!
    if index < 0 or index > (len(self.lists[name]) - 1):
      self.panic(f"Index {index + 1} out of bounds for '{name}' (len {len(self.lists[name])})")
      return

    (self.lists[name])[index] = new_item

  def len_word(self):
    name = self.get_next()

    if name not in self.lists:
      self.panic(f"List '{name}' not found")
      return

    self.stack.append(len(self.lists[name]))

  def get_word(self):
    name = self.get_next()

    if name in self.variables:
      self.stack.append(self.variables[name])
    else:
      self.panic(f"'{name}' not found")

  def set_word(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    val = self.stack.pop()
    name = self.get_next()

    if name not in self.variables:
      self.panic(f"'{name}' not found")
    else:
      self.variables[name] = val

  def print_string(self):
    output = []
    while self.position < len(self.source):
      char = self.source[self.position]
      self.position += 1

      if char == '"':
        msg = "".join(output)
        print(msg[1:], end="")
        return

      output.append(char)

    self.panic("Unterminated '.\"'")

  def empty(self):
    if not self.stack:
      self.stack.append(-1)
    else:
      self.stack.append(0)
  
  def random(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    bound = self.stack.pop()
    
    self.stack.append(custom_random(bound))
    

  def emit(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    print(chr(self.stack.pop()), end="")
  
  def over(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'over' (at least 2)")
      return

    second = self.stack[-2]
    self.stack.append(second)

  def rot(self):
    if len(self.stack) < 3:
      self.panic("Not enough elements on the stack for 'rot' (at least 3)")
      return

    third = self.stack.pop()
    second = self.stack.pop()
    first = self.stack.pop()

    self.stack.append(second)
    self.stack.append(third)
    self.stack.append(first)
  
  def swap(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'swap' (at least 2)")
      return

    a = self.stack.pop()
    b = self.stack.pop()

    self.stack.append(a)
    self.stack.append(b)
    
  
  def cr_word(self):
    print()

  def bye_word(self):
    print("Goodbye :)")
    sys.exit()
  
  def do_word(self):
    if len(self.stack) < 2:
      self.panic("Not enough elements on the stack for 'do' (at least 2)")
      return

    limit = self.stack.pop()
    index = self.stack.pop()
    self.loop_stack.append((index, limit, self.position))

  def loop_word(self):
    if not self.loop_stack:
      self.panic("No loop in progress")
      return

    index, limit, start_pos = self.loop_stack[-1]
    index += 1

    if index < limit:
      self.loop_stack[-1] = (index, limit, start_pos)
      self.position = start_pos
    else:
      self.loop_stack.pop()

  # ends a loop by incrementing with a stack value rather than by 1
  def plus_loop_word(self):
    if not self.loop_stack:
      self.panic("No loop in progress")
      return

    if not self.stack:
      self.panic("Stack is empty for '+loop'")
      return

    increment = self.stack.pop()
    index, limit, start_pos = self.loop_stack[-1]
    index += increment
    
    if (increment > 0 and index < limit) or (increment < 0 and index > limit):
      self.loop_stack[-1] = (index, limit, start_pos)
      self.position = start_pos
    else:
      self.loop_stack.pop()

  def i_word(self):
    if not self.loop_stack:
      self.panic("No loop in progress")
      return

    index, _, _ = self.loop_stack[-1]
    self.stack.append(index)

  def start_compile_mode(self):
    if self.compiling:
      self.panic("Already in compile mode")
      return

    # get name of new word
    word_name = self.get_next()
    if not word_name:
      self.panic("Expected word name after ':'")
      return

    # make sure it isn't a number
    if word_name.isdigit() or (word_name[0] == '-' and word_name[1:].isdigit()):
      self.panic("Word name cannot start with a number")
      return

    self.compiling = True
    self.current_word = word_name
    self.current_definition = []

  def end_compile_mode(self):
    if not self.compiling:
      self.panic("Not in compile mode")
      return

    # stitch current_definition tokens together and store in user_words[word]
    word_def = " ".join(self.current_definition)
    self.user_words[self.current_word] = word_def

    # reset compilation state
    self.compiling = False
    self.current_word = None
    self.current_definition = []

  def execute_word(self, word):
    if word not in self.user_words:
      self.panic("Unknown word {word}")
      return

    # save place
    saved_pos = self.position
    saved_src = self.source

    # switch source to the word's definition
    self.position = 0
    self.source = self.user_words[word]

    token = self.get_next() # exec definition
    while token:
      if token in self.dictionary:
        self.dictionary[token]()
      elif token in self.user_words:
        self.execute_word(token)
      elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
        self.stack.append(int(token))
      else:
        self.panic(f"Unknown word '{token}' in definition of '{word}'")

      token = self.get_next()

    # revert back to original source
    self.position = saved_pos
    self.source = saved_src
    
  
  def if_word(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    condition = self.stack.pop()

    if condition == 0: 
      nesting = 1 # track nested pairs
      saved_pos = self.position

      # look ahead for matching else/then
      while True:
        token = self.get_next()
        if not token:
          self.panic("'if' without matching 'then'")
          self.position = saved_pos
          return

        if token == 'if':
          nesting += 1
        elif token == 'then':
          nesting -= 1
          if nesting == 0:
            break
        elif token == 'else' and nesting == 1:
          break

  def else_word(self):
    # skip to matching 'then' if we executed the 'if' block
    nesting = 1
    while True:
      token = self.get_next()
      if not token:
        self.panic("'else' without matching 'then'")
        return

      if token == 'if':
        nesting += 1
      elif token == 'then':
        nesting -= 1
        if nesting == 0:
          break

  def then_word(self):
    # do nothing, it's just a marker
    pass

  def equals(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      if a == b:
        self.stack.append(-1)
      else:
        self.stack.append(0)

  def not_word(self):
    if not self.stack:
      self.panic("Stack is empty")
      return

    val = self.stack.pop()
    if val == 0:
      self.stack.append(-1)
    else:
      self.stack.append(0)

  def mod(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(b % a)
    else:
      self.panic("Not enough elements on the stack")

  def add(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(a + b)
    else:
      self.panic("Not enough elements on the stack")

  def subtract(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(b - a)
    else:
      self.panic("Not enough elements on the stack")

  def multiply(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(a * b)
    else:
      self.panic("Not enough elements on the stack")

  def divide(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(b // a)
    else:
      self.panic("Not enough elements on the stack")

  def pop_and_print(self):
    if self.stack:
      top = self.stack.pop()
      print(top, end="")
    else:
      self.panic("Stack is empty")

  def dup(self):
    if self.stack:
      self.stack.append(self.stack[-1])
    else:
      self.panic("Stack is empty")

  def drop(self):
    if self.stack:
      self.stack.pop()
    else:
      self.panic("Stack is empty")

  def panic(self, msg):
    if self.is_file: # error messages when running a file have line numbers
      print(f"Error on line {self.line}: {msg}")
      sys.exit()
    else:
      print(f"Error: {msg}")

  def skip_comment(self):
    self.position += 1 # move past (

    while self.position < len(self.source):
      if self.source[self.position] == '\n':
        self.line += 1
    
      if self.source[self.position] == ')':
        self.position += 1
        return True
        
      self.position += 1

    return False # reached end of source without closing )
  
  # get next word/instruction
  def get_next(self):
    while self.position < len(self.source):
      
      # skip whitespace and count newlines
      while self.position < len(self.source) and self.source[self.position].isspace():
        if self.source[self.position] == '\n':
          self.line += 1
        self.position += 1
      
      # Check if we've reached the end
      if self.position >= len(self.source):
        return None
      
      # check for comments
      if self.source[self.position] == '(':
        if not self.skip_comment():
          self.panic("Unterminated comment")
        continue
      
      # Find the end of the current token
      start = self.position
      while (self.position < len(self.source) and 
          not self.source[self.position].isspace() and
          self.source[self.position] != '('):
        self.position += 1
            
      # Extract the token
      return self.source[start:self.position]

    return None # no more tokens
    
  def interpret(self):
    self.position = 0
    
    token = self.get_next()
    while token:
      if self.compiling and token != ';':
        # while compiling, store tokens instead of executing them
        self.current_definition.append(token)
      else:
        if token in self.dictionary:
          self.dictionary[token]()
        elif token in self.user_words:
          self.execute_word(token)
        elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
          self.stack.append(int(token))
        else:
          self.panic(f"Unknown word '{token}'")

      token = self.get_next()

  def load_file(self, file_path):
    try:
      with open(file_path, 'r') as file:
        self.source = file.read()
        self.interpret()
    except FileNotFoundError:
      print(f"Error: File '{file_path}' not found")
    except Exception as e:
      print(f"Error: {e}")
  
  def run(self, file_path=None):
    if file_path:
      self.is_file = True
      self.load_file(file_path)
    else:
      self.is_file = False
      print("Welcome to the momforth REPL. Type 'bye' to exit.")
      while True:
        try:
          prompt = ""
          if len(self.stack) > 3:
            prompt = "..." + str(self.stack[-3]) + " " + str(self.stack[-2]) + " " + str(self.stack[-1]) + "] "
          else:
            for item in self.stack:
              prompt = prompt + str(item) + " "
            prompt = prompt[:-1] + "] "
          
          input_text = input(prompt)
          self.source = input_text.strip()
          self.interpret()
        except KeyboardInterrupt:
          print("\nProgram terminated by user.")
          sys.exit()
        except Exception as e:
          self.panic(f"Had exception {e}")


def usage():
  print("usage: momforth [flags] [script]")
  print("Available flags are:")
  print("  -h --help      print usage")
  print("  -v --version   show version information")

if __name__ == "__main__":
  interpreter = ForthInterpreter()

  args = sys.argv[1:]
  script = None
  show_help = False
  show_version = False

  for arg in args:
    if arg in ("-h", "--help"):
      show_help = True
    elif arg in ("-v", "--version"):
      show_version = True
    elif not script and arg[0] != '-': # first non-flag is script
      script = arg
    else:
      print(f"momforth: unrecognized option: {arg}")
      usage()
      sys.exit()

  if show_help:
    usage()
    sys.exit()

  if show_version:
    print("momforth 0.1.0-alpha (python)")
    sys.exit()

  if script:
    interpreter.run(script)
  else:
    interpreter.run()
