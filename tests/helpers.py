import os


def has_extension(expected_extension):
    def verify(filename):
        _, extension = os.path.splitext(filename)
        return extension == expected_extension
    return verify


def get_directory_path(directory):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        directory
    )


def get_files_with_extension(directory, extension=".cmake"):
    files = os.listdir(get_directory_path(directory))
    return list(filter(has_extension(extension), files))


def remove_extension(filename):
    result, _ = os.path.splitext(filename)
    return result


def get_content(filename, directory):
    with open(os.path.join(get_directory_path(directory), filename), 'r') as f:
        return f.read()

