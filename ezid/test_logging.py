import logging
import pdb

# this config may already be done for you, if you're working on a shared project
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# you'll have to do this to get the configured logger though
logger = logging.getLogger(__name__)

# variables we'll work with
my_message = "hello"
my_other_message = "world"
my_number = 123

# if all variables are strings, you can concatenate like so:

new_string = 'message 1: ' + my_message + ', message 2: ' +  my_other_message

# however, if one variable is not a string...

try:
    new_string = my_message + my_other_message + my_number
except TypeError:
    logger.debug("can't concat a string and an int")

# you can convert the value to a string:

new_string = my_message + my_other_message + str(my_number)

# or you can use string formatting (the old way):

# notice that the % operator is followed by an s, or a d, specifying the type,
# (%s for string, %d for int, %f for float), the string is followed by the %
# operator, which is followed by a tuple containing the variables.

new_string = 'message: %s, number: %d' % (my_message, my_number)

# i believe that there is an implicit object to string conversion, so although
# this wouldn't work:

try:
    new_string = my_message + {}
except TypeError:
    logger.debug("can't concat a string and a dict")

# this does work:

new_string = '%s %s' % (my_message, {})

# similarly to how this works:

new_string = my_message + str({})

# or you can use the newer string formatting:

# notice that the {} may be empty, or may contain a number, the number refers
# to the i-th variable in the call to format. i wouldn't mess with numbers,
# it's just bound to break at some point when you add another variable

new_string = 'message: {}, number: {}'.format(my_message, my_number)
new_string = 'message: {0}, number: {1}'.format(my_message, my_number)
new_string = 'message: {1}, number: {0}'.format(my_number, my_message)

# you can also get fancy with the formatting:

# in this example, the first variable will be centered within 20 spaces, the
# second is right aligned within 20 spaces. this kind of fancy formatting may be
# very useful when you're printing something like a table of results

new_string = 'message: {:^20} number: {:>20}'.format(my_number, my_message)

# note: print '' works in python 2, but python 3 requires paranthesis: print('')

# python 2

print new_string

# python 3

print(new_string)

# side note: you can stick your variables in kind of at any point

my_string = "var 1: {}, var 2: {}"
print(my_string.format('a', 'b'))

# you've seen an example of logging above, here are some more examples:

logging.info(new_string)
logging.warning(new_string)
logging.warning('warning!')
logging.warning('warning! %s' % 'big problem!')
logging.warning('warning! {}'.format('big problem!'))

try:
    logging.debug('going to try dividing by zero')
    1/0
except Exception as e:
    logging.error('division by zero!')

# debugging

# uncomment the next line

#pdb.set_trace()

# this creates a breakpoint and enters the python debugger at the console
# you can do things like check the value of variables:

# Example:

# (Pdb) my_message
# 'hello'
# (Pdb) exit

# you can read more about the debugger here:
# https://docs.python.org/2/library/pdb.html