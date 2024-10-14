cmake_pkg_config(EXTRACT foo REQUIRED ENV_MODE PKGCONF PC_PATH /foo/bar /foo/baz /bar /baz)

cmake_pkg_config(EXTRACT foo REQUIRED ENV_MODE PKGCONF PC_PATH /foo/bar /foo/baz /bar /baz /foo__________________________________________________)

cmake_pkg_config(EXTRACT foo 1.2.3 REQUIRED ENV_MODE PKGCONF PC_PATH /foo/bar /foo/baz /bar /baz /foo__________________________________________________)
