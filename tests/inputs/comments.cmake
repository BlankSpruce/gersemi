#[[Zero]]
#[=[One]=]
#[==[Two]==]
#[===[Three]===]

#Line comment one
#Line comment two

# Mixed comments
#[[First bracket comment]] # then line comment
#[[Zero equal signs]] #[=[One equal sign]=] #[==[Two equal signs]==] # and then line comment
#[[Single line bracket comment]] # with line comment
#[======[Multi line
bracket comment]======] # also with line comment

# Taken from CMake documentation
#[[This is a bracket comment.
It runs until the close bracket.]]
message("First Argument\n" #[[Bracket Comment]] "Second Argument")

# This is a line comment.
message("First Argument\n" # This is a line comment :)
        "Second Argument") # This is a line comment.
