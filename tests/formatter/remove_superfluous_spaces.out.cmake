# Already formatted

include_guard()

set(bar)

set(bar "baz")

#[=[    spaces     in     bracket    comments   untouched     ]=]

#     spaces      in     line    comments     untouched    except     for   the    end

# To format

include_guard()

include_guard()

set(bar)

set(bar)

set(bar)

set(bar)

set(bar "baz")

set(#[=[some bracket comment]=] bar "baz")

#[=[some bracket comment]=] # followed by superfluous spaces and line comment

set(bar) # some comment following command invocation

set(bar baz)

include_guard()

if()
    message(STATUS "foo")
endif()
