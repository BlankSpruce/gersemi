function(foo)
	bar(
	    # some comment with "quoted string"
	    # some comment with "quoted string"
	    # some comment with "quoted string"
	    # some comment with "quoted string"
	)
endfunction()

function(foo)
	bar(
	    #[[some comment with "quoted string"]]
	    #[[some comment with "quoted string"]]
	    #[[some comment with "quoted string"]]
	    #[[some comment with "quoted string"]]
	)
endfunction()
