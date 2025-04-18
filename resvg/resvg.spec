# Generated by rust2rpm 27
%bcond check 1

%global crate resvg

Name:           resvg
Version:        0.45.1
Release:        %autorelease
Summary:        SVG rendering library

License:        Apache-2.0 OR MIT
URL:            https://crates.io/crates/resvg
Source:         %{crates_source}

BuildRequires:  cargo-rpm-macros >= 24

%global _description %{expand:
An SVG rendering library.}

%description %{_description}

%files       -n %{crate}
%license LICENSE-APACHE
%license LICENSE-MIT
%license LICENSE.dependencies
%doc README.md
%{_bindir}/resvg

%prep
%autosetup -n %{crate}-%{version} -p1
# rust version too low for EPEL 9 and below
%if 0%{?el8} || 0%{?el9}
  bash <(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs) --profile=minimal -y
  %define __rustc $HOME/.cargo/bin/rustc
  %define __cargo /usr/bin/env CARGO_HOME=.cargo RUSTC_BOOTSTRAP=1 RUSTFLAGS='%{build_rustflags}' "$HOME/.cargo/bin/cargo"
  %define __rustdoc $HOME/.cargo/bin/rustdoc
%endif

%__cargo vendor
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license} > LICENSE.dependencies

%install
%define cargo_install_lib 0
%cargo_install

%if %{with check}
%check
%cargo_test
%endif

%changelog
%autochangelog
