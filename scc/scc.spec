# Generated by go2rpm 1.15.0
%bcond check 1
%bcond bootstrap 0

%if %{with bootstrap}
%global debug_package %{nil}
%endif

%if %{with bootstrap}
%global __requires_exclude %{?__requires_exclude:%{__requires_exclude}|}^golang\\(.*\\)$
%endif

# https://github.com/boyter/scc
%global goipath         github.com/boyter/scc
Version:                3.5.0

%gometa -f

%global common_description %{expand:
Sloc, Cloc and Code: scc is a very fast accurate code counter with complexity
calculations and COCOMO estimates written in pure Go.}

%global golicenses      LICENSE
%global godocs          README.md

Name:           scc
Release:        %autorelease
Summary:        Sloc, Cloc and Code: scc is a very fast accurate code counter with complexity calculations and COCOMO estimates written in pure Go

License:        MIT
URL:            %{gourl}
Source:         %{gosource}

BuildRequires: golang >= 1.24

%description %{common_description}

%gopkg

%prep
%goprep -k
%autopatch -p1

%if %{without bootstrap}
%build
%gobuild -o %{gobuilddir}/bin/scc %{goipath}
%endif

%install
%gopkginstall
%if %{without bootstrap}
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/
%endif

%if %{without bootstrap}
%if %{with check}
%check
%gocheck
%endif
%endif

%if %{without bootstrap}
%files
%license %{golicenses}
%doc %{godocs}
%{_bindir}/scc
%endif

%gopkgfiles

%changelog
%autochangelog
