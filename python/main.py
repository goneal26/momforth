import sys
import random

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
    self.loop_stack = [] # stack for loop indices and limits
    
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
      '!': self.not_word,
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
      
      # some aliases
      'set': self.set_word,
      'not': self.not_word,
      'mod': self.mod,
      'free': self.pop,

      # commas can be used to improve readability, they just do nothing
      ',': self.comma,
    }
    
    self.source = ""
    self.position = 0 # position in source string
    self.compiling = False # compile mode flag
    self.current_word = None # name of the word being defined
    self.current_definition = [] # tokens for the word being defined
    self.user_words = {} # stores user-defined compiled words
    
    self.variables = {} # stores user variables
    self.lists = {} # stores user-defined lists

  def comma(self):
    pass
  
  # works for lists or variables
  def pop(self):
    name = self.get_next()

    if name in self.variables:
      self.stack.append(self.variables.pop(name))
    elif name in self.lists:
      self.stack.append(len(self.lists.pop(name)))
    else:
      print(f"Error: Variable/List '{name}' not found")

  # helper function to see if a word is already defined
  def already_defined(self, name):
    return (name in self.variables) or (name in self.lists) or (name in self.user_words) or (name in self.dictionary)

  # helper function for evaluating a single (simple) token
  # i.e. not a compiler-flag set or anything like that
  def eval_token(self, token):
    if token in self.dictionary: # reserved word
      self.dictionary[token]()
    elif token in self.user_words: # compiled word
      self.execute_user_word(token)
    elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
      self.stack.append(int(token))
    else:
      print(f"Error: Unknown token '{token}' in definition of {word_name}")
  
  def var_word(self):
    name = self.get_next()
    
    if name in self.dictionary:
      print(f"Error: '{name}' is a reserved word")
      return

    if self.already_defined(name):
      print(f"Error: variable '{name}' already defined")
      return
    
    self.variables[name] = 0 # 0-initialized

  def list_word(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    size = self.stack.pop()

    if size <= 0:
      print(f"Error: Invalid list length {size}")
      return

    name = self.get_next()

    if self.already_defined(name):
      print(f"Error: '{name}' is already defined")
      return
    else:
      self.lists[name] = [0] * size

  def from_word(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    index = self.stack.pop() - 1 # REMEMBER, 1-indexed!!!
    name = self.get_next()
    
    if name not in self.lists:
      print(f"Error: List '{name}' not found")
      return

    if index < 0 or index > (len(self.lists[name]) - 1):
      print(f"Error: Index {index + 1} out of bounds for list '{name}' (length {len(self.lists[name])})")
      return

    self.stack.append( (self.lists[name])[index] )

  # syntax: index item into listname
  # (n1 n2 -- )
  def into_word(self):
    if len(self.stack) < 2:
      print("Error: Not enough elements on the stack for 'put' (at least 2)")
      return

    new_item = self.stack.pop()

    name = self.get_next()
    if name not in self.lists:
      print(f"Error: List '{name}' not found")
      return

    index = self.stack.pop() - 1 # REMEMBER, 1-indexed!!!
    if index < 0 or index > (len(self.lists[name]) - 1):
      print(f"Error: Index {index + 1} out of bounds for list '{name}' (length {len(self.lists[name])})")
      return

    (self.lists[name])[index] = new_item

  def len_word(self):
    name = self.get_next()

    if name not in self.lists:
      print(f"Error: List '{name}' not found")
      return

    self.stack.append(len(self.lists[name]))

  def get_word(self):
    name = self.get_next()

    if name in self.variables:
      self.stack.append(self.variables[name])
    else:
      print(f"Error: '{name}' not found")

  def set_word(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    val = self.stack.pop()
    name = self.get_next()

    if name not in self.variables:
      print(f"Error: '{name}' not found")
    else:
      self.variables[name] = val

  def print_string(self):
    output = []
    while self.position < len(self.source):
      char = self.source[self.position]
      self.position += 1

      if char == '"':
        print("".join(output), end="")
        return

      output.append(char)

    print("Error: Unterminated '.\"'")

  def empty(self):
    if not self.stack:
      self.stack.append(-1)
    else:
      self.stack.append(0)
  
  def random(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    bound = self.stack.pop()
    
    self.stack.append(custom_random(bound))
    

  def emit(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    print(chr(self.stack.pop()), end="")
  
  def over(self):
    if len(self.stack) < 2:
      print("Error: Not enough elements on the stack for 'over' (at least 2)")
      return

    second = self.stack[-2]
    self.stack.append(second)

  def rot(self):
    if len(self.stack) < 3:
      print("Error: Not enough elements on the stack for 'rot' (at least 3)")
      return

    third = self.stack.pop()
    second = self.stack.pop()
    first = self.stack.pop()

    self.stack.append(second)
    self.stack.append(third)
    self.stack.append(first)
  
  def swap(self):
    if len(self.stack) < 2:
      print("Error: Not enough elements on the stack for 'swap' (at least 2)")
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
      print("Error: Not enough elements on the stack for 'do' (at least 2)")
      return

    index = self.stack.pop()
    limit = self.stack.pop()
    self.loop_stack.append((index, limit, self.position))

  def loop_word(self):
    if not self.loop_stack:
      print("Error: No loop in progress")
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
      print("Error: No loop in progress")
      return

    if not self.stack:
      print("Error: Stack is empty for '+loop'")
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
      print("Error: No loop in progress")
      return

    index, _, _ = self.loop_stack[-1]
    self.stack.append(index)

  def start_compile_mode(self):
    if self.compiling:
      print("Error: Already in compile mode")
      return

    # get name of new word
    word_name = self.get_next()
    if not word_name:
      print("Error: Expected word name after ':'")
      return

    # make sure it isn't a number
    if word_name.isdigit() or (word_name[0] == '-' and word_name[1:].isdigit()):
      print("Error: Word name cannot be a number")
      return

    self.compiling = True
    self.current_word = word_name
    self.current_definition = []

  def end_compile_mode(self):
    if not self.compiling:
      print("Error: Not in compile mode")
      return

    # store as list of tokens
    self.user_words[self.current_word] = self.current_definition.copy()

    # reset compilation state
    self.compiling = False
    self.current_word = None
    self.current_definition = []

  
  def execute_user_word(self, word_name):
    if word_name not in self.user_words:
      print(f"Error: Word '{word_name}' not found")
      return

    definition = self.user_words[word_name]

    saved_pos = self.position
    saved_source = self.source

    # execute each token in definition
    for token in definition:
      if token in self.dictionary:
        self.dictionary[token]()
      elif token in self.user_words:
        self.execute_user_word(token)
      elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
        self.stack.append(int(token))
      else:
        print(f"Error: Unknown token '{token}' in definition of {word_name}")
  
  def if_word(self):
    if not self.stack:
      print("Error: Stack is empty")
      return

    condition = self.stack.pop()

    if condition == 0: 
      nesting = 1 # track nested pairs
      saved_pos = self.position

      # look ahead for matching else/then
      while True:
        token = self.get_next()
        if not token:
          print("Error: 'if' without matching 'then'")
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
        print("Error: 'else' without matching 'then'")
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
      print("Error: Stack is empty")
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
      print("Error: Not enough elements on the stack")

  def add(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(a + b)
    else:
      print("Error: Not enough elements on the stack")

  def subtract(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(b - a)
    else:
      print("Error: Not enough elements on the stack")

  def multiply(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(a * b)
    else:
      print("Error: Not enough elements on the stack")

  def divide(self):
    if len(self.stack) >= 2:
      a = self.stack.pop()
      b = self.stack.pop()
      self.stack.append(b // a)
    else:
      print("Error: Not enough elements on the stack")

  def pop_and_print(self):
    if self.stack:
      top = self.stack.pop()
      print(top, end=" ")
    else:
      print("Error: Stack is empty")

  def dup(self):
    if self.stack:
      self.stack.append(self.stack[-1])
    else:
      print("Error: Stack is empty")

  def drop(self):
    if self.stack:
      self.stack.pop()
    else:
      print("Error: Stack is empty")

  def skip_comment(self):
    self.position += 1 # move past (

    while self.position < len(self.source):
      if self.source[self.position] == ')':
        self.position += 1
        return True
      self.position += 1

    return False # reached end of source without closing )
  
  # get next word/instruction
  def get_next(self):
    while self.position < len(self.source):
      
      # skip whitespace
      while self.source[self.position].isspace():
        self.position += 1
      
      # Check if we've reached the end
      if self.position >= len(self.source):
        return None
      
      # check for comments
      if self.source[self.position] == '(':
        if not self.skip_comment():
          print("Warning: Unterminated comment")
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
          self.execute_user_word(token)
        elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
          self.stack.append(int(token))
        else:
          print(f"Error: Unknown word '{token}'")

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
      self.load_file(file_path)
    else:
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
          print(f"Error: {e}")

if __name__ == "__main__":
  interpreter = ForthInterpreter()

  # TODO help/usage info

  if len(sys.argv) == 2:
    file_path = sys.argv[1]
    interpreter.run(file_path)
  else:
    interpreter.run()
