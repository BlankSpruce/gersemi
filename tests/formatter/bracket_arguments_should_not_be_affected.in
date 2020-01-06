# Bracket arguments shouldn't be affected by reformatting because their
# formatting might be intentional and impactful, for instance:

set(SOME_FORMATTED_PYTHON_CODE [=[
def foo(bar, baz):
    for i, j in zip(bar, baz):
        print(i, j)
    print("DONE")
]=])

set(OTHER_FORMATTED_PYTHON_CODE [=[Foo = lambda Bar: Bar.something_to_be_done_on_Bar_object()]=])

# Here is configured some file based on template which may refer to
# SOME_FORMATTED_PYTHON_CODE and OTHER_FORMATTED_PYTHON_CODE variables. If these
# arguments were reformatted it could change the actual foo.py content

configure_file(foo.py.in foo.py @ONLY)