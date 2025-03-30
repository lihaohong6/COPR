Name:           bazel7
Version:        7.6.0
Release:        %autorelease
Summary:        Build and test software of any size, quickly and reliably. 
License:        Apache-2.0
URL:            https://bazel.build/ 
Source:         https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip 
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python
BuildRequires:  zip
BuildRequires:  unzip
BuildRequires:  java-21-openjdk-devel

Patch0:         include_stdint.patch

# FIXME: should only disable stripping and keep everything else
%define __spec_install_post /bin/true

%description
Build and test software of any size, quickly and reliably.

%prep
unzip %{_sourcedir}/bazel-%{version}-dist.zip
%patch -P0

%build
env EXTRA_BAZEL_ARGS="--tool_java_runtime_version=local_jdk" bash ./compile.sh
./output/bazel build //src:bazel --compilation_mode=opt --stamp --embed_label=%{version}

%install
install -Dpm 0755 ./bazel-bin/src/bazel                  %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 ./scripts/zsh_completion/_bazel        %{buildroot}%{_datadir}/zsh/site-functions/_%{name}

%files
%{_bindir}/%{name}
%{_datadir}/zsh/site-functions/_%{name}
%doc 
%license LICENSE 

%changelog
%autochangelog
