foo($(bar))

foo($(bar baz))

foo(${bar}=$(baz))

foo(var $(bar)$(baz))

foo(var0 $(var1)$(var2)/var3)

foo(var bar$(baz)$(qux)Foo)
