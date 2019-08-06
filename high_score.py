from time import sleep

from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event1')

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 64 
matrix_columns = 64 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 1 
matrix_vertical = 1

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 

#options.hardware_mapping = 'adafruit-hat-pwm' 
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.hardware_mapping = 'regular'  

options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

###################################
# High Score data
#   High scores are stored as a list of (score,name) tuples
#   Initialize the list with some default data.
###################################
num_high_scores = 5
high_scores = \
[ \
  (10,"GLE"),  \
  (8,"DAW"),  \
  (6,"MOM"),  \
  (4,"DAD"),  \
  (2,"YYZ")   \
]


##################################
# Sort Scores
#  Want to sort based on first value
################################## 
def sort_scores(val):
  return(val[0])

##################################
# Show High Scores 
###################################
def show_high_scores():
  global high_scores

  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)
  row = 0
  row_size = 10 
  
  high_score_color = (255,0,0)
  
  
  temp_draw.text((0,row),"High Scores:", fill=(255,0,0))
  row += row_size

  high_scores.sort(key = sort_scores, reverse=True)

  for score in high_scores:
    temp_draw.text((0,row),score[1]+"  "+str(score[0]), fill=(255,0,0))
    row += row_size

  matrix.SetImage(temp_image, 0, 0)

##################################
# Eval score 
#   This function checks a passed score to see if it's worthy of our high-score
#   list. 
###################################
def eval_score(score):
  global high_scores
 
  # Make sure we're sorted properly
  high_scores.sort(key=sort_scores,reverse=True)

  if (score > high_scores[-1][0]):
    return True
  else:
    return False
  

##################################
# get_gamepad_input()
#   This is a blocking read to get a gamepad key 
#   Pass in the gamepad in question, and it will return 
#   a string representing the key pressed.
#   Current implementation is for PS3 USB Controller
###################################
def get_gamepad_input(my_gamepad):
  
  d_up = 544
  d_down = 545
  d_left = 546
  d_right = 547

  for event in my_gamepad.read_loop():
    if event.type ==ecodes.EV_KEY:
      if event.value == 1:
        if event.code == d_up:
          print("UP")
          return("D-up")
        elif event.code == d_down:
          print("DOWN")
          return("D-down")
        elif event.code == d_left:
          print("LEFT")
          return("D-left")
        elif event.code == d_right: 
          print("RIGHT")
          return("D-right")

##################################
# Input name 
#   This function will return a 3 character string
#   built on arcade-style PS3 inputs
###################################
def input_name():
  global gamepad
  blacklist_strings = ["ASS","SEX","FAG","FUK","FCK","FUC"]

  # Strings are immutable in Python, so I'm going to operate on this 
  # as a list, and only make it a string (via the "join" method) when needed.
  name = list("AAA")

  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)

  # Going to display the 3 chars in the middle, with a 'v' and '^' 
  # above and below to show which char the user is tweaking.
  top_row = 0
  string_row = 10
  bottom_row = 20
  current_char = 0
  column_spacing = 6
  column_offset = 10
  
  input_color = (0,255,0)
  highlight_color = (255,0,0)
  
  while current_char < 3:
    # Start by indicating which letter we're changing
    # we're gonna erase all three lines first, and then redraw
    temp_draw.rectangle((column_offset,top_row,3*column_spacing+column_offset,bottom_row+10), fill = (0,0,0))

    indicator_position = current_char*column_spacing+column_offset
    temp_draw.text((indicator_position,top_row),"v", highlight_color)
    temp_draw.text((column_offset,string_row), "".join(name), fill = input_color)
    temp_draw.text((indicator_position,bottom_row),"^", highlight_color)
    matrix.SetImage(temp_image, 0, 0)

    # now wait for an input from our gamepad.  
    current_input = get_gamepad_input(gamepad)
    
    #if it's an "up", decrement the character
    if (current_input == "D-up"):
      if (name[current_char] == "A"):
        name[current_char] = "Z"
      else:
        name[current_char] =chr(ord(name[current_char]) - 1)

    #if it's a "down", increment the character
    if (current_input == "D-down"):
      if (name[current_char] == "Z"):
        name[current_char] = "A"
      else:
        name[current_char] =chr(ord(name[current_char]) + 1)

    #if it's "left", go back one character (if you can). 
    if (current_input == "D-left"):
      if (current_char > 0):
        current_char = current_char - 1 
    
    #if it's "right", go to the next character
    # note our while loop will end when we finish the third char.
    if (current_input == "D-right"):
      current_char = current_char + 1
  
  # Now that we've built our string, make sure it's an appropriate 3 letters.
  name_string = "".join(name)
  for bad_name in blacklist_strings:
    if bad_name == name_string:
      return("XXX")
  
  # return our final string.
  return(name_string) 
  
##################################
# Main loop 
###################################
while True:
  show_high_scores()

  # Test harness: use keyboard to input score you want to insert.
  my_score = input("type in score (or ctl-c to quit):  ")

  # Is that score big enough to go into our list?
  if eval_score(my_score):
    my_name = input_name()
    high_scores.append([my_score,my_name]) 
    high_scores.sort(key=sort_scores,reverse=True)
    del high_scores[-1]

  else:
    print("not big enough to make list")

