# https://cmake.org/cmake/help/latest/module/FetchContent.html#commands
#
#     The <contentOptions> can be any of the download, update, or patch
#     options that the ExternalProject_Add() command understands.

FetchContent_Declare(
    ${fetchcontent_target}
    HTTP_USERNAME "$ENV{USERNAME}"
    HTTP_PASSWORD "$ENV{PASSWORD}"
    URL
        "${src_url}"
    DOWNLOAD_NO_EXTRACT TRUE
    URL_HASH SHA256=${exp_hash}
    DOWNLOAD_DIR ${dst_folder}
    DOWNLOAD_NAME ${download_name}
)
