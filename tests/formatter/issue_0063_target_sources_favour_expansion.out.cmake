target_sources(
    runtimeCore
    PUBLIC
        FILE_SET modules
            TYPE CXX_MODULES
            FILES
                "runtimeCore.ixx"
                "setting.ixx"
                "foo__________________________________________________.ixx"
)

target_sources(
    runtimeCore
    PUBLIC
        FILE_SET
            modules______________________________________________________________________
            TYPE CXX_MODULES
            FILES
                "runtimeCore.ixx"
                "setting.ixx"
                "foo__________________________________________________.ixx"
)

target_sources(
    runtimeCore
    PUBLIC
        FILE_SET # comment
            modules
            TYPE CXX_MODULES
            FILES
                "runtimeCore.ixx"
                "setting.ixx"
                "foo__________________________________________________.ixx"
)

target_sources(
    runtimeCore
    PUBLIC
        FILE_SET
            # comment
            modules
            TYPE CXX_MODULES
            FILES
                "runtimeCore.ixx"
                "setting.ixx"
                "foo__________________________________________________.ixx"
)
