Name:           bazel 
Version:        8.3.0
Release:        %autorelease
Summary:        Build and test software of any size, quickly and reliably. 
License:        Apache-2.0
URL:            https://bazel.build/ 
Source:         https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip 
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  zip
BuildRequires:  unzip
BuildRequires:  java-21-openjdk-devel
%if 0%{?el8}
BuildRequires:  python3
%else
BuildRequires:  python
%endif

# FIXME: should only disable stripping and keep everything else
%define __spec_install_post /bin/true

%description
Build and test software of any size, quickly and reliably.

%prep
unzip %{_sourcedir}/bazel-%{version}-dist.zip

%build
env EXTRA_BAZEL_ARGS="--tool_java_runtime_version=local_jdk" bash ./compile.sh
./output/bazel build //src:bazel //scripts:bazel-complete.bash --compilation_mode=opt --stamp --embed_label=%{version}

%install
install -Dpm 0755 ./bazel-bin/src/bazel                   -t %{buildroot}%{_bindir}
install -Dpm 0644 ./bazel-bin/scripts/bazel-complete.bash    %{buildroot}%{bash_completions_dir}/%{name}.bash
install -Dpm 0644 ./scripts/zsh_completion/_bazel         -t %{buildroot}%{zsh_completions_dir}

%files
%{_bindir}/bazel
%{zsh_completions_dir}/_%{name}
%{bash_completions_dir}/%{name}.bash
%doc 
%license LICENSE 

%changelog
%autochangelog
