%package -n plogr-libdnf5
Summary: DNF5 native plugin for plogr
Requires: plogr >= %{version}

%description -n plogr-libdnf5
Native libdnf5 plugin that forwards DNF5 transactions to plogr.

%install
%cmake --preset release libdnf5-plugin
%cmake --build build
%cmake_install
